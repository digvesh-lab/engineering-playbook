export type StepState = 'done' | 'active' | 'blocked' | 'pending'
export type Step = { name: string; state: StepState }
export type Run = { slug: string; steps: Step[] }
export type Mode = 'bar' | 'steps' | 'off'

declare module 'claude-code' {
  interface PluginState {
    'work-flow-progress': { run: Shaped<Run | null>; mode: Shaped<Mode> }
  }
}
