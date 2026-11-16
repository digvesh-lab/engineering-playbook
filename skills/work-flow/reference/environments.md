# Environments: detail

Part of the `work-flow` contract. The rules in `SKILL.md` have priority.

| Environment | Default | With the switch |
| ----------- | ------- | --------------- |
| `local` | run, change, seed, reset | always permitted |
| `dev` | ask first | `env:dev`: read and write |
| `staging` | ask first | `env:staging`: read; `env:staging(write)`: write |
| `production` | ask each time | `env:prod`: read only (logs, metrics, traces) |

No switch permits these: a write to production, a change to production
data, or a reproduction of a bug in production. No preset sets an `env:` switch.

`CLAUDE.md` says how to get to each environment and how to run the checks:

```
environments:
  local: npm run dev            # seed: npm run db:seed
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
