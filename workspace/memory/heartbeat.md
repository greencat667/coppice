# Heartbeat

> Every scheduled task appends one line here each time it runs: date, task, result (`ran` / `skipped` / `failed`), and a few words. `coppice doctor` reads this file to spot tasks that have stopped running. Keep only the last 60 days; `archive-trim` deletes older lines.

| When | Task | Result | Note |
|---|---|---|---|
