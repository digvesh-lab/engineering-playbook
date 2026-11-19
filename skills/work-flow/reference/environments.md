# Environments: detail

Part of the `work-flow` contract. The rules in `SKILL.md` have priority.

| Environment | Default | With the switch |
| ----------- | ------- | --------------- |
| `local` code | run, change | always permitted |
| `local` data | ask one time for each task | `disposable` in the instruction file: read, write, reset |
| `dev` | ask first | `env:dev`: read and write |
| `staging` | ask first | `env:staging`: read; `env:staging(write)`: write |
| `production` | ask each time | `env:prod`: read only (logs, metrics, traces) |

No switch permits these: a write to production, a change to production
data, or a reproduction of a bug in production. No preset sets an `env:` switch.

Local data can be a copy of production data, or costly to rebuild. So
local data is not free by default:

- Ask one time for each task before you read or write a local database.
  Record the answer in the state file.
- A local database is free only if `environments.local` in the instruction
  file marks it `disposable`. Then you can read, write, reset, and reseed it.
- A check command that resets a test database is part of the checks. It
  needs a question only if it resets a database that is not `disposable`.
- Data that the run creates in a test database, fixtures, and mocks are
  always permitted. Prefer them for a reproduction.

The instruction file says how to get to each environment and how to run the checks:

```
environments:
  local: npm run dev            # seed: npm run db:seed; data: disposable
  dev: https://dev.example.com  # logs: <command>
  staging: https://staging.example.com
  production: logs only, with <command>
checks:
  test: npm test
  lint: npm run lint
  types: npm run typecheck
  build: npm run build
```

If an environment is not in that block, ask the user. Never guess a host, a
credential, or a command.

Prove the change on the environment where you reproduced the problem. Say
so in the report. A local test does not prove a fix for a problem that you
reproduced only on staging.
