# work-flow-progress

Shows how far a /work-flow run is, as a colored band above the prompt. It reads the newest
`.agents/work-flow/runs/*.md` in the working directory whose `session:` line names this session (the uuid in the scratchpad path), parses its `steps:` block and counts the
12 steps (recall to remember): green done, yellow active, red stopped, gray pending.
Use `/wf-progress bar`, `/wf-progress steps` or `/wf-progress off`; with no argument it cycles.
The band stays hidden when no run file names this session, so a session never shows another session's run.
Install: `claude plugin marketplace add <folder that holds a marketplace.json listing ./work-flow-progress>`, then `/plugin install work-flow-progress`.
