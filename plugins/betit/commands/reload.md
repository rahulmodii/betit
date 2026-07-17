---
description: Pull the latest betit from the marketplace and update it
---

Update the plugin to the newest published version. Run these with the Bash tool and show the output:

1. `claude plugin marketplace update rahulmodi`
2. `claude plugin update betit@rahulmodi`

If either CLI command is unavailable in this environment, tell the user to run `/plugin marketplace update rahulmodi` followed by `/plugin` to update betit from the UI instead.

After a successful update, remind the user: hooks are loaded at session start, so a restart of the Claude Code session is needed for hook changes to take effect. Commands and skills refresh immediately.
