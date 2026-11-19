# Borrowed skills: lock file

source: https://github.com/mattpocock/skills
licence: MIT (the copy is saved here on the first update)
commit: each row has its own commit in "Status"
4ae2317: 4ae2317ddb22b046e26455e4f9c9b3aaaf62212d, dated 2026-10-31, fetched 2026-11-12
abeeaf9: abeeaf95660ba9e8b7c753eb38f441ca707a8823, dated 2026-11-19, fetched 2026-11-19

Run `/work-borrow-update` to update these files. If a file is missing, the step uses
the fallback that is written in its own skill.

| Borrowed skill | File in this folder | Used by | Status |
| -------------- | ------------------- | ------- | ------ |
| grilling | grilling.md | work-grill | fetched @ 4ae2317 |
| domain-modeling | domain-modeling.md | work-grill | fetched @ 4ae2317 |
| to-spec | to-spec.md | work-grill | fetched @ 4ae2317 |
| to-tickets | to-tickets.md | work-propose | fetched @ 4ae2317 |
| diagnosing-bugs | diagnosing-bugs.md | work-assess | fetched @ 4ae2317 |
| tdd | tdd.md (with tests.md, mocking.md) | work-build | fetched @ 4ae2317 |
| code-review | code-review.md | work-review | fetched @ 4ae2317 |
| prototype | prototype.md (with prototype/UI.md, prototype/LOGIC.md) | work-prototype | fetched @ abeeaf9 |

The names were checked on skills.sh on 12 November 2026. `grill-with-docs`
is not in the list because it only calls `grilling` and `domain-modeling`.
