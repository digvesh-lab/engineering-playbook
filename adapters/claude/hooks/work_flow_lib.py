"""Decision logic for the work-flow guard hooks. Text in, decision out; git and fs go through small helpers."""
import json
import fnmatch
import os
import re
import subprocess
import time
from datetime import datetime, timezone

ORDER = ['recall', 'assess', 'explain', 'grill', 'propose', 'build', 'test',
         'clean', 'prune', 'review', 'ship', 'remember']
OPEN = ('pending', 'stopped', 'redo')
DONE = ('passed', 'skip')
FINISHED = ('aborted',)
BASE_NAMES = ('main', 'master', 'dev', 'develop')
TMP_ROOTS = ('/tmp',)
NO_BRANCH = ('none', 'not', 'n/a', 'na', '-', 'tbd')
MARKER_MAX_AGE = 7 * 24 * 3600

SID_RE = re.compile(r'^[0-9a-fA-F-]{8,64}$')
REF_RE = re.compile(r'^[A-Za-z0-9_][\w./-]*$')
HEX_RE = re.compile(r'(?<![0-9A-Za-z])[0-9a-f]{7,40}(?![0-9A-Za-z])')
PROD_LINE_RE = re.compile(r'^\s*[-*]?\s*`?work-flow-prod-files:\s*(.+?)`?\s*$', re.M)
PROD_FILES_IN_REPO = ('AGENTS.md', 'CLAUDE.md', 'CLAUDE.local.md', os.path.join('.claude', 'CLAUDE.md'))
TOKEN_SPLIT_RE = re.compile(r'[\s=:\'"`<>(),]+')
RUN_FILE_RE = re.compile(r'^(.*)/\.agents/work-flow/runs/[^/]+\.md$')


# ---------- run files ----------

def valid_session(sid):
    return sid if isinstance(sid, str) and SID_RE.match(sid) else None


def names_session(text, sid):
    return bool(sid) and re.search(rf'^session:\s*{re.escape(sid)}\s*$', text, re.M) is not None


def field(text, name):
    m = re.search(rf'^{name}:[ \t]*(.*)$', text, re.M)
    return m.group(1).strip() if m else None


def _first_token(value):
    if not value:
        return None
    value = re.sub(r'\([^)]*\)', ' ', value)
    parts = value.split()
    return parts[0].rstrip(',;') if parts else None


def parse_base(value):
    tok = _first_token(value)
    if not tok:
        return None
    tok = re.sub(r'^(?:origin|upstream)/', '', tok)
    return tok if REF_RE.match(tok) else None


def parse_branch(value):
    tok = _first_token(value)
    if not tok or tok.lower() in NO_BRANCH or not REF_RE.match(tok):
        return None
    return tok


def parse_env(value):
    if not value:
        return []
    return [t.lower() for t in re.split(r'[\s,\[\]]+', value) if t]


def _split_top(body):
    parts, depth, cur = [], 0, ''
    for ch in body:
        if ch == '(':
            depth += 1
        elif ch == ')':
            depth = max(0, depth - 1)
        if ch == ',' and depth == 0:
            parts.append(cur)
            cur = ''
        else:
            cur += ch
    parts.append(cur)
    return parts


def steps_of(text):
    """Return (steps dict name -> lowercased first word of state, has steps block)."""
    found, in_block, has = {}, False, False
    for line in text.splitlines():
        if not in_block:
            m = re.match(r'^steps:\s*(.*)$', line)
            if not m:
                continue
            has = True
            rest = m.group(1)
            if rest.startswith('{'):
                body = rest[1:rest.rfind('}')] if '}' in rest else rest[1:]
                for part in _split_top(body):
                    k, _, v = part.partition(':')
                    k, v = k.strip(), v.strip()
                    if re.fullmatch(r'[a-z.]+', k) and v:
                        found[k] = v.split()[0].lower()
                return found, has
            in_block = True
            continue
        m = re.match(r'^\s+([a-z.]+):\s*(\S+)', line)
        if m:
            found[m[1]] = m[2].lower()
        elif line.strip() and not line.startswith((' ', '\t')):
            break
    return found, has


def kind(state):
    if state is None:
        return None
    if state.startswith(OPEN):
        return 'open'
    if state.startswith(DONE):
        return 'done'
    if state.startswith(FINISHED):
        return 'finished'
    return 'other'


class Run:
    def __init__(self, path, text, mtime=0.0, repo=None):
        self.path = path
        self.text = text
        self.mtime = mtime
        m = RUN_FILE_RE.match(path)
        self.repo = repo or (m.group(1) if m else os.path.dirname(path))
        self.slug = os.path.basename(path)[:-3] if path.endswith('.md') else os.path.basename(path)
        self.branch = parse_branch(field(text, 'branch'))
        self.base = parse_base(field(text, 'base'))
        self.env = parse_env(field(text, 'env'))
        self.type = (field(text, 'type') or '').split('|')[0].strip().lower()
        self.steps, self.has_steps = steps_of(text)

    @property
    def aborted(self):
        return any(kind(s) == 'finished' for s in self.steps.values())

    @property
    def has_open(self):
        return any(kind(s) == 'open' for s in self.steps.values())

    def done(self, step):
        return kind(self.steps.get(step)) == 'done'


def list_run_files(repo):
    d = os.path.join(repo, '.agents', 'work-flow', 'runs')
    try:
        names = sorted(os.listdir(d))
    except OSError:
        return []
    return [os.path.join(d, n) for n in names if n.endswith('.md') and not n.endswith('.notes.md')]


def load_runs(repo):
    out = []
    for p in list_run_files(repo):
        try:
            with open(p, encoding='utf-8') as fh:
                text = fh.read()
            out.append(Run(p, text, os.path.getmtime(p), repo=repo))
        except (OSError, UnicodeDecodeError):
            continue
    return out


def choose_active(runs, branch_of):
    """Branch match first, else the newest run with an open step. Aborted runs are over."""
    live = [r for r in runs if not r.aborted]
    for r in live:
        cur = branch_of(r.repo)
        if r.branch and cur and r.branch == cur:
            return r
    cands = [r for r in live if r.has_open]
    return max(cands, key=lambda r: r.mtime) if cands else None


# ---------- Stop ----------

def order_problems(steps):
    out, first_open = [], None
    for name in ORDER:
        state = steps.get(name)
        if state is None:
            continue
        if state.startswith(OPEN) and first_open is None:
            first_open = (name, state)
        elif state.startswith(DONE) and first_open:
            out.append(f'{name} is {state} but earlier step {first_open[0]} is still {first_open[1]}')
    return out


def index_has_final_line(index_text, slug):
    pat = re.compile(rf'^\s*-?\s*\S+\s+{re.escape(slug)}\s*\|')
    for line in (index_text or '').splitlines():
        if pat.search(line) and not re.search(r'\|\s*in-progress\s*\|', line):
            return True
    return False


def stop_problems(run, git, read_text):
    if not run.has_steps:
        return ['no steps: block']
    out = []
    beyond_assess = any(n in run.steps for n in ORDER[2:])
    if run.type != 'question' and not run.aborted and (beyond_assess or run.branch):
        missing = [n for n in ORDER if n not in run.steps]
        if missing:
            out.append('steps: block lacks ' + ', '.join(missing))
    out += order_problems(run.steps)
    if run.branch:
        head = git.commit(run.repo, f'refs/heads/{run.branch}')
        if head:
            base = None
            if run.base:
                base = (git.commit(run.repo, f'refs/heads/{run.base}')
                        or git.commit(run.repo, f'refs/remotes/origin/{run.base}'))
            if base and git.merge_base(run.repo, head, base) != head:
                if not any(head.startswith(t) for t in HEX_RE.findall(run.text)):
                    out.append(f'commit {head[:7]} on {run.branch} is not recorded')
    if run.done('ship') or run.done('remember'):
        index = os.path.join(run.repo, '.agents', 'work-flow', 'memory', 'index.md')
        if not index_has_final_line(read_text(index), run.slug):
            out.append(f'step 12 not run (no final line for {run.slug} in {index})')
    return out


def stop_message(issues):
    return ('work-flow state check failed. Fix each item (steps: line passed (user) only for an explicit yes, '
            'else passed (auto: reason), or skip with a reason; record each commit hash; run step 12): '
            + '; '.join(issues))


# ---------- PreToolUse gates ----------

def under(path, root):
    return path == root or path.startswith(root.rstrip(os.sep) + os.sep)


def repo_of(path, repos):
    hits = [r for r in repos if under(path, r)]
    return max(hits, key=len) if hits else None


def base_set(run_base, origin_head):
    names = set(BASE_NAMES)
    if run_base:
        names.add(run_base)
    if origin_head:
        names.add(origin_head)
    return names


def no_run_reason(sid, what):
    return (f'work-flow: this session started work-flow but no state file in .agents/work-flow/runs/ '
            f'has the line `session: {sid}`. Create the state file first, then {what}.')


def edit_decision(path, repos, sid, marker_exists, session_runs, branch_of, origin_head_of,
                  allow_roots=TMP_ROOTS, ignored=lambda repo, path: False):
    """Return a deny reason, or None to allow."""
    if any(under(path, r) for r in allow_roots):
        return None
    repo = repo_of(path, repos)
    if repo is None:
        return None
    if under(path, os.path.join(repo, '.agents')) or under(path, os.path.join(repo, '.git')):
        return None
    if not session_runs:
        return no_run_reason(sid, f'edit {path}') if marker_exists else None
    active = choose_active([r for r in session_runs if r.repo == repo], branch_of)
    if active is None:
        return None
    if not active.done('propose'):
        return (f'work-flow: propose has not passed in {active.path} '
                f'(propose: {active.steps.get("propose", "missing")}). '
                f'Finish propose and update its steps: line before editing {path}.')
    cur = branch_of(repo)
    if cur and cur in base_set(active.base, origin_head_of(repo)) and not ignored(repo, path):
        return (f'work-flow: on base branch {cur} for run {active.path}; build creates the work branch '
                f'first (git switch -c <branch>) and records it in branch:.')
    return None


_GIT_OPTS_WITH_VALUE = ('-C', '-c', '--git-dir', '--work-tree', '--namespace')
_BRANCH_NOT_CREATE = {'-a', '-r', '-d', '-D', '--delete', '--show-current', '-v', '-vv', '--verbose',
                      '--list', '-l', '--all', '--remotes', '-m', '-M', '--move', '--contains',
                      '--no-contains', '--merged', '--no-merged', '--points-at', '-u',
                      '--set-upstream-to', '--unset-upstream', '--edit-description'}


def _git_argv(tokens):
    """Return the args after `git [global options]`, or None if tokens are not a git command."""
    if not tokens or os.path.basename(tokens[0]) != 'git':
        return None
    i = 1
    while i < len(tokens) and tokens[i].startswith('-'):
        i += 2 if tokens[i] in _GIT_OPTS_WITH_VALUE else 1
    return tokens[i:]


def _tokens(segment):
    import shlex
    try:
        return shlex.split(segment)
    except ValueError:
        return segment.split()


def creates_branch(command):
    for seg in re.split(r'&&|\|\||[;|&\n]', command or ''):
        toks = _tokens(seg)
        while toks and re.match(r'^\w+=', toks[0]):
            toks = toks[1:]
        args = _git_argv(toks)
        if not args:
            continue
        sub, rest = args[0], args[1:]
        if sub == 'switch' and any(a in ('-c', '-C', '--create', '--force-create') or a.startswith('--create=')
                                   for a in rest):
            return True
        if sub == 'checkout' and any(a in ('-b', '-B') for a in rest):
            return True
        if sub == 'worktree' and rest[:1] == ['add'] and any(a in ('-b', '-B') for a in rest[1:]):
            return True
        if sub == 'branch':
            opts = {a.split('=')[0] for a in rest if a.startswith('-')}
            positional = [a for a in rest if not a.startswith('-')]
            if positional and not (opts & _BRANCH_NOT_CREATE):
                return True
    return False


def branch_decision(command, sid, marker_exists, session_runs, active):
    if not creates_branch(command):
        return None
    if marker_exists and not session_runs:
        return no_run_reason(sid, 'create the branch')
    if active is not None and not active.done('propose'):
        return (f'work-flow: propose has not passed in {active.path} '
                f'(propose: {active.steps.get("propose", "missing")}). '
                f'Finish propose before build creates the branch.')
    return None


MESSAGE_CMDS = (('git', 'commit'), ('git', 'log'), ('git', 'tag'))


def parse_prod_files(text):
    pats = []
    for m in PROD_LINE_RE.finditer(text or ''):
        pats += [p for p in re.split(r'[,\s]+', m.group(1)) if p]
    return pats


def prod_patterns(repos, env, reader=None):
    reader = reader or read_text
    paths = [os.path.join(r, f) for r in repos for f in PROD_FILES_IN_REPO]
    paths.append(os.path.join(claude_home(env), 'CLAUDE.md'))
    out = []
    for p in paths:
        for pat in parse_prod_files(reader(p)):
            if pat not in out:
                out.append(pat)
    return out


def prod_match(text, patterns):
    if not patterns or not text:
        return None
    for seg in re.split(r'[;&|\n]', text):
        words = seg.split()
        if tuple(os.path.basename(w) for w in words[:2]) in MESSAGE_CMDS:
            continue
        for tok in TOKEN_SPLIT_RE.split(seg):
            if tok and any(fnmatch.fnmatchcase(os.path.basename(tok), p) or fnmatch.fnmatchcase(tok, p)
                           for p in patterns):
                return tok
    return None


def prod_decision(texts, active, patterns):
    if active is None or any(e in ('prod', 'production') for e in active.env):
        return None
    for t in texts:
        hit = prod_match(t, patterns)
        if hit:
            return (f'work-flow: this command reads a production file ({hit}, listed in work-flow-prod-files) and run {active.path} '
                    f'does not permit production. Ask the user first. Only after the user permits it, '
                    f'add prod to env: in the state file. This guard matches the listed file names only; a '
                    f'script that loads production settings by default is not detected.')
    return None


# ---------- UserPromptSubmit / Skill ----------

def prompt_starts_work_flow(prompt):
    p = prompt or ''
    return bool(re.match(r'^\s*/work-flow(?=\s|$)', p)) and not re.match(r'^\s*/work-flow\s+status\b', p)


def skill_starts_work_flow(tool_input):
    if not isinstance(tool_input, dict) or tool_input.get('skill') != 'work-flow':
        return False
    return not str(tool_input.get('args') or '').strip().startswith('status')


def start_context(skill_real):
    return (f'work-flow started: create or resume the state file before any other tool. '
            f'Read the reference files at {skill_real}/reference/.')


def read_block_warning(skill_real):
    return (f'work-flow reference files: {skill_real}/reference/. If a Read of them is denied, read them '
            f'through this path; if it is outside the working directories, ask the user to add it with '
            f'/add-dir. Do not rebuild a template from memory.')


# ---------- settings, marker, git ----------

def claude_home(env):
    return env.get('CLAUDE_HOME') or os.path.join(os.path.expanduser('~'), '.claude')


def read_permissions(env):
    """Return (additionalDirectories as absolute real paths, blockReadsOutsideWorkingDirectories)."""
    try:
        with open(os.path.join(claude_home(env), 'settings.json'), encoding='utf-8') as fh:
            perms = json.load(fh).get('permissions') or {}
    except (OSError, ValueError, AttributeError):
        return [], False
    dirs = []
    for d in perms.get('additionalDirectories') or []:
        if isinstance(d, str):
            d = os.path.expanduser(d)
            if os.path.isabs(d):
                dirs.append(os.path.realpath(d))
    return dirs, perms.get('blockReadsOutsideWorkingDirectories') is True


def marker_dir(env):
    base = env.get('XDG_STATE_HOME') or os.path.join(os.path.expanduser('~'), '.local', 'state')
    return os.path.join(base, 'work-flow-guard')


def marker_path(env, sid):
    return os.path.join(marker_dir(env), f'{sid}.json')


def read_marker(env, sid):
    try:
        with open(marker_path(env, sid), encoding='utf-8') as fh:
            data = json.load(fh)
        return data if isinstance(data, dict) else {'repos': []}
    except (OSError, ValueError):
        return None


def write_marker(env, sid, repos, create=True, now=None):
    now = time.time() if now is None else now
    data = read_marker(env, sid)
    if data is None:
        if not create:
            return None
        data = {'started': datetime.now(timezone.utc).isoformat(timespec='seconds'), 'repos': []}
    known = [r for r in data.get('repos') or [] if isinstance(r, str)]
    for r in repos:
        if r and r not in known:
            known.append(r)
    data['repos'] = known
    d = marker_dir(env)
    os.makedirs(d, exist_ok=True)
    for name in os.listdir(d):
        p = os.path.join(d, name)
        try:
            if name.endswith('.json') and now - os.path.getmtime(p) > MARKER_MAX_AGE:
                os.remove(p)
        except OSError:
            pass
    tmp = marker_path(env, sid) + '.tmp'
    with open(tmp, 'w', encoding='utf-8') as fh:
        json.dump(data, fh)
    os.replace(tmp, marker_path(env, sid))
    return data


def delete_marker(env, sid):
    try:
        os.remove(marker_path(env, sid))
    except OSError:
        pass


def read_text(path):
    try:
        with open(path, encoding='utf-8') as fh:
            return fh.read()
    except (OSError, UnicodeDecodeError):
        return None


def run_git(args, cwd):
    try:
        p = subprocess.run(['git', '-C', cwd, *args], capture_output=True, text=True, timeout=2,
                           env={**os.environ, 'GIT_OPTIONAL_LOCKS': '0'})
    except (OSError, subprocess.SubprocessError):
        return None
    return p.stdout.strip() if p.returncode == 0 else None


class Git:
    def __init__(self, runner=run_git):
        self.run = runner
        self.cache = {}

    def _q(self, cwd, *args):
        key = (cwd, args)
        if key not in self.cache:
            self.cache[key] = self.run(list(args), cwd) if os.path.isdir(cwd) else None
        return self.cache[key] or None

    def toplevel(self, d):
        top = self._q(d, 'rev-parse', '--show-toplevel')
        return os.path.realpath(top) if top else None

    def branch(self, repo):
        return self._q(repo, 'symbolic-ref', '--short', '-q', 'HEAD')

    def origin_head(self, repo):
        ref = self._q(repo, 'symbolic-ref', '--short', '-q', 'refs/remotes/origin/HEAD')
        return ref.split('/', 1)[1] if ref and '/' in ref else None

    def commit(self, repo, ref):
        return self._q(repo, 'rev-parse', '--verify', '-q', f'{ref}^{{commit}}')

    def merge_base(self, repo, a, b):
        return self._q(repo, 'merge-base', a, b)
