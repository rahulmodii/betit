#!/usr/bin/env python3
import json
import os
import sys
import time

STATE_DIR = os.path.expanduser("~/.claude/betit")
STATE_FILE = os.path.join(STATE_DIR, "state.json")

DEFAULT = {
    "points": 100,
    "wins": 0,
    "losses": 0,
    "streak": 0,
    "best_streak": 0,
    "worst_streak": 0,
    "pending": None,
    "history": [],
}


def load():
    if not os.path.exists(STATE_FILE):
        return dict(DEFAULT)
    try:
        with open(STATE_FILE) as f:
            s = json.load(f)
        for k, v in DEFAULT.items():
            s.setdefault(k, v)
        return s
    except Exception:
        return dict(DEFAULT)


def save(s):
    os.makedirs(STATE_DIR, exist_ok=True)
    tmp = STATE_FILE + ".tmp"
    with open(tmp, "w") as f:
        json.dump(s, f, indent=2)
    os.replace(tmp, STATE_FILE)


def rank(points):
    if points >= 500:
        return "ONE-SHOT LEGEND"
    if points >= 300:
        return "Sharpshooter"
    if points >= 200:
        return "Confident"
    if points >= 100:
        return "Grinder"
    if points >= 50:
        return "Shaky"
    if points > 0:
        return "On Tilt"
    return "BANKRUPT"


def scoreboard(s):
    total = s["wins"] + s["losses"]
    wr = f"{(s['wins'] / total * 100):.0f}%" if total else "—"
    lines = [
        "BETIT SCOREBOARD",
        f"  Points: {s['points']}  [{rank(s['points'])}]",
        f"  Record: {s['wins']}W - {s['losses']}L  (win rate {wr})",
        f"  Streak: {fmt_streak(s['streak'])}  |  Best: W{s['best_streak']}  Worst: L{abs(s['worst_streak'])}",
    ]
    if s["pending"]:
        p = s["pending"]
        lines.append(f"  PENDING BET: {p['wager']} pts on \"{p['task']}\"")
    return "\n".join(lines)


def fmt_streak(n):
    if n > 0:
        return f"W{n} 🔥" if n >= 3 else f"W{n}"
    if n < 0:
        return f"L{abs(n)} 🧊" if n <= -3 else f"L{abs(n)}"
    return "even"


def cmd_status():
    print(scoreboard(load()))


def cmd_context():
    s = load()
    out = [scoreboard(s), ""]
    if s["pending"]:
        out.append(
            "An unsettled bet exists. Before taking any new bet, ask the user for the verdict on the pending one "
            "(win / lose), then settle it with this script."
        )
    else:
        out.append(
            "BETIT PROTOCOL: If this message starts a NEW task (not a follow-up, question, or verdict), "
            "you must open with a bet BEFORE doing any work: state your confidence and wager 5-50 points "
            "that you complete it correctly in ONE shot. Register it via: betit.py bet <wager> \"<short task name>\". "
            "Higher wager = more confidence. Do not bet on trivial chat."
        )
    print("\n".join(out))


def cmd_bet(args):
    s = load()
    if s["pending"]:
        print(f"ERROR: pending bet already exists ({s['pending']['wager']} pts on \"{s['pending']['task']}\"). Settle it first with win/lose.")
        sys.exit(1)
    try:
        wager = int(args[0])
    except (IndexError, ValueError):
        print("Usage: betit.py bet <wager> \"<task>\"")
        sys.exit(1)
    if wager < 5 or wager > 50:
        print("ERROR: wager must be between 5 and 50.")
        sys.exit(1)
    task = args[1] if len(args) > 1 else "unnamed task"
    s["pending"] = {"wager": wager, "task": task[:120], "ts": int(time.time())}
    save(s)
    print(f"BET PLACED: {wager} pts on one-shotting \"{s['pending']['task']}\". Current bank: {s['points']} pts.")


def settle(result, note):
    s = load()
    if not s["pending"]:
        print("ERROR: no pending bet to settle.")
        sys.exit(1)
    p = s["pending"]
    wager = p["wager"]
    bonus = 0
    if result == "win":
        s["wins"] += 1
        s["streak"] = s["streak"] + 1 if s["streak"] > 0 else 1
        if s["streak"] >= 3:
            bonus = s["streak"]
        delta = wager + bonus
        s["points"] += delta
        s["best_streak"] = max(s["best_streak"], s["streak"])
    else:
        s["losses"] += 1
        s["streak"] = s["streak"] - 1 if s["streak"] < 0 else -1
        delta = -wager
        s["points"] = max(0, s["points"] + delta)
        s["worst_streak"] = min(s["worst_streak"], s["streak"])
    s["history"].append(
        {
            "ts": int(time.time()),
            "task": p["task"],
            "wager": wager,
            "result": result,
            "delta": delta,
            "note": note[:200] if note else "",
            "points_after": s["points"],
        }
    )
    s["history"] = s["history"][-100:]
    s["pending"] = None
    save(s)
    verdict = "WIN ✅" if result == "win" else "LOSS ❌"
    extra = f" (+{bonus} streak bonus)" if bonus else ""
    print(f"{verdict}  \"{p['task']}\"  {'+' if delta > 0 else ''}{delta} pts{extra}")
    print(scoreboard(s))


def cmd_history(n):
    s = load()
    rows = s["history"][-n:]
    if not rows:
        print("No settled bets yet.")
        return
    for h in rows:
        mark = "W" if h["result"] == "win" else "L"
        note = f"  — {h['note']}" if h.get("note") else ""
        print(f"[{mark}] {h['task']}  ({'+' if h['delta'] > 0 else ''}{h['delta']} → {h['points_after']}){note}")


def cmd_cancel():
    s = load()
    if not s["pending"]:
        print("No pending bet.")
        return
    p = s["pending"]
    s["pending"] = None
    save(s)
    print(f"Bet cancelled (no points moved): {p['wager']} pts on \"{p['task']}\"")


def cmd_reset():
    save(dict(DEFAULT))
    print("Betit reset. Bank restored to 100 pts, record wiped.")


def main():
    args = sys.argv[1:]
    if not args:
        cmd_status()
        return
    cmd, rest = args[0], args[1:]
    if cmd == "status":
        cmd_status()
    elif cmd == "context":
        cmd_context()
    elif cmd == "bet":
        cmd_bet(rest)
    elif cmd == "win":
        settle("win", " ".join(rest))
    elif cmd == "lose":
        settle("lose", " ".join(rest))
    elif cmd == "cancel":
        cmd_cancel()
    elif cmd == "history":
        n = int(rest[0]) if rest and rest[0].isdigit() else 10
        cmd_history(n)
    elif cmd == "reset":
        cmd_reset()
    else:
        print(f"Unknown command: {cmd}")
        sys.exit(1)


if __name__ == "__main__":
    main()
