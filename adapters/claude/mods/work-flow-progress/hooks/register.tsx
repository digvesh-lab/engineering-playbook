import { atom, read, update } from 'claude-code'
import type { Register } from 'claude-code'

import type { Mode, Run, Step, StepState } from '../types'

const RUNS_DIR = '.agents/work-flow/runs'
const ORDER = [
  'recall',
  'assess',
  'explain',
  'grill',
  'propose',
  'build',
  'test',
  'clean',
  'prune',
  'review',
  'ship',
  'remember',
]
const MODES: Mode[] = ['bar', 'steps', 'off']

// Change the tag when the run's fields change: it declines what an earlier version stored.
const run = atom({ plugin: 'work-flow-progress', key: 'run' } as const, null, {
  shape: 'run-1',
})
const mode = atom(
  { plugin: 'work-flow-progress', key: 'mode' } as const,
  'bar' as Mode,
  { shape: 'mode-1' },
)

const stateOf = (status: string): StepState => {
  const s = status.trim().toLowerCase()
  if (s.startsWith('passed') || s.startsWith('skip')) return 'done'
  if (s.startsWith('stopped') || s.startsWith('redo')) return 'blocked'
  if (s.startsWith('pending') || s === '') return 'pending'
  return 'active'
}

// Reads the `steps:` block of a work-flow state file; a step it does not list counts as pending.
const parseSteps = (text: string): Step[] => {
  const found = new Map<string, StepState>()
  let inBlock = false
  for (const line of text.split('\n')) {
    if (!inBlock) {
      inBlock = /^steps:/.test(line)
      continue
    }
    const m = /^\s{2,}([a-z][a-z.-]*):\s*(.*)$/.exec(line)
    if (!m) {
      if (/^\S/.test(line)) break
      continue
    }
    found.set((m[1] ?? '').split('.')[0] ?? '', stateOf(m[2] ?? ''))
  }
  return ORDER.map(name => ({ name, state: found.get(name) ?? 'pending' }))
}

const UUID = /[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}/

// Shows only the run whose `session:` line names this session (id taken from its scratchpad or transcript path).
const newestRun = async ($: any): Promise<Run | null> => {
  let entries: { name: string; kind: string; mtimeMs: number }[]
  try {
    const info = await $.session.info()
    var sid = UUID.exec(info.scratchpadDir || info.transcriptPath || '')?.[0]
    entries = await $.fs.list(RUNS_DIR)
  } catch {
    return null
  }
  if (!sid) return null
  const files = entries
    .filter(f => f.kind === 'file' && /\.md$/.test(f.name) && !/\.notes\.md$/.test(f.name))
    .sort((a, b) => b.mtimeMs - a.mtimeMs)
  for (const f of files) {
    try {
      const text: string = await $.fs.read(`${RUNS_DIR}/${f.name}`)
      if (new RegExp(`^session:\\s*${sid}\\s*$`, 'm').test(text)) {
        return { slug: f.name.replace(/\.md$/, ''), steps: parseSteps(text) }
      }
    } catch {}
  }
  return null
}

type Piece = { text: string; color?: string; bold?: boolean; dim?: boolean }

const COLOR: Record<StepState, string> = {
  done: 'green',
  active: 'yellow',
  blocked: 'red',
  pending: 'gray',
}

const pieces = (r: Run, m: Mode): Piece[] => {
  const done = r.steps.filter(s => s.state === 'done').length
  const next = r.steps.find(s => s.state !== 'done')
  const head: Piece[] = [
    { text: 'work-flow ', color: 'cyan', bold: true },
    { text: `${r.slug}  `, color: 'magenta' },
  ]
  const count: Piece = {
    text: ` ${done}/${r.steps.length}`,
    color: done === r.steps.length ? 'green' : 'white',
    bold: true,
  }

  if (m === 'steps') {
    const sign = { done: '✓', active: '▶', blocked: '!', pending: '·' }
    const marks: Piece[] = r.steps.map(s => ({
      text: `${sign[s.state]}${s.name} `,
      color: COLOR[s.state],
      bold: s.state === 'active' || s.state === 'blocked',
      dim: s.state === 'pending',
    }))

    return [...head, ...marks, count]
  }

  const glyph = { done: '█', active: '▓', blocked: '▒', pending: '░' }
  const bar: Piece[] = r.steps.map(s => ({ text: glyph[s.state], color: COLOR[s.state] }))
  const tail: Piece = next
    ? {
        text: `  next: ${next.name}${next.state === 'blocked' ? ' (stopped)' : ''}`,
        color: next.state === 'blocked' ? 'red' : 'yellow',
      }
    : { text: '  all steps done', color: 'green', bold: true }

  return [...head, ...bar, count, tail]
}

const refresh = async ($: any) => {
  const latest = await newestRun($)
  await update($, run, () => latest)
}

export const register: Register = on => {
  on('session.start', async ($, e, next) => {
    await $.command.register({
      name: 'wf-progress',
      description: 'Work-flow progress band: bar, steps or off (no argument cycles)',
    })
    await refresh($)

    return next(e)
  })

  on('prompt.submit', async ($, e, next) => {
    await refresh($)

    return next(e)
  })

  on('turn.complete', async ($, e, next) => {
    await refresh($)

    return next(e)
  })

  on('command.run', { command: 'wf-progress' }, async ($, e) => {
    const asked = e.args.trim().toLowerCase()
    const current = await read($, mode)
    const next = (MODES as string[]).includes(asked)
      ? (asked as Mode)
      : MODES[(MODES.indexOf(current) + 1) % MODES.length]
    await update($, mode, () => next)

    return { text: `Work-flow progress: ${next}` }
  })

  on('ui.render', { component: 'AbovePrompt' }, async ($, e, next) => {
    const r = await read($, run)
    const m = await read($, mode)
    if (e.props.hasSurvey || r === null || m === 'off') return next(e)

    const { Box, Text } = $.ui.resolve(e)

    return (
      <Box>
        {pieces(r, m).map((p, i) => (
          <Text key={`p${i}`} color={p.color} bold={p.bold} dimColor={p.dim}>
            {p.text}
          </Text>
        ))}
      </Box>
    )
  })
}
