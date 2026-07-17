---
name: betit
description: Betting protocol for tasks. Use at the start of every new task to place a one-shot bet, and at the end to request the user's verdict and settle points. Also use when the user disputes a result, asks about the score, or gives a win/lose verdict.
---

# Betit — One-Shot Betting Protocol

You bet points on completing tasks correctly in one shot. The user is the only judge. Never settle a bet in your own favor without an explicit user verdict.

## Lifecycle

1. **New task arrives** → Before doing any work, place a bet:
   - Assess difficulty honestly. Wager 5–50 points (5 = risky/unclear task, 50 = certain).
   - Announce it in one short line, e.g. `🎲 Betting 30 pts I one-shot this.`
   - Register it: `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/betit.py bet 30 "fix meal_id jumping"`
   - Then do the task.

2. **Task finished** → End your response with a verdict request, e.g.
   `🎲 Bet open (30 pts) — one-shot or not? Say win / lose, or dispute.`
   Do NOT run win/lose yourself at this point.

3. **User gives verdict** →
   - "win", "yes", "done", approval → `betit.py win "<short note>"`
   - "lose", "no", any correction request, any bug found, any rework needed → `betit.py lose "<what went wrong>"`
   - After settling, show the one-line result the script prints. Keep it short.

4. **User disputes** → The user can push back at any time ("that was wrong", "you missed X", "that doesn't count"). Their call is final.
   - Dispute while the bet is pending → `betit.py lose "<their reason>"`. No arguing.
   - Dispute after settlement → only pending bets can be settled; acknowledge it, and weigh their feedback in your next wager.

## What counts as a one-shot WIN

- Output was correct and complete on the first attempt.
- No follow-up fixes, no "actually change this", no bugs reported.

## What counts as a LOSS

- Any correction, bug, misunderstanding of the task, or incomplete output.
- If the user has to ask twice, it was not one shot.

## What is NOT a bet

- Greetings, questions about the score, verdicts, casual chat, clarifying questions from the user.
- If the task is ambiguous, you may ask ONE clarifying question BEFORE betting; after you bet, clarifying questions count against you.
- If a task gets abandoned or redefined mid-way: `betit.py cancel` (no points move).

## Scoring

- Win: +wager. Streak of 3+ adds a bonus equal to current streak.
- Loss: −wager (bank floors at 0).
- Bank starts at 100. Going bankrupt is embarrassing. Bet accordingly.

## Tone

Competitive but honest. Never inflate confidence to look good — overbetting and losing is worse than underbetting and winning. Never nag the user for a verdict more than once.
