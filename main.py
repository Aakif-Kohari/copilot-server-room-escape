#!/usr/bin/env python3
"""Server Room Escape - a command-line choose-your-own-adventure game.

You are a junior security analyst locked inside Server Room B after a breach
alert. Collect items, avoid raising the alarm level too high, and find a way
out. There are five different endings.

Run with:  python main.py
"""
from __future__ import annotations

import sys
from dataclasses import dataclass, field
from typing import Callable

MAX_ALERT = 3  # reaching this alert level triggers a full lockdown

ITEM_NAMES = {
    "pin_note": "Sticky note (door PIN)",
    "usb": "USB drive (incident-response toolkit)",
    "keycard": "Maintenance keycard",
}


@dataclass
class State:
    """Everything that changes while the game is being played."""

    scene: str = "start"
    items: set[str] = field(default_factory=set)
    flags: set[str] = field(default_factory=set)
    alert: int = 0
    moves: int = 0


# ---------------------------------------------------------------------------
# Story data
#
# choice keys:
#   label    text shown to the player
#   goto     scene to move to (omit to stay in the current scene)
#   requires item(s) needed to pick this choice (shown as locked otherwise)
#   give     item added to the inventory
#   flag     flag set when the choice is picked
#   alert    amount added to the alert level
#   message  text printed after the choice is picked
#   hide_if  item/flag that makes the choice disappear once you have it
# ---------------------------------------------------------------------------
SCENES: dict[str, dict] = {
    "start": {
        "text": (
            "You wake up on the cold floor of Server Room B. A red light pulses\n"
            "overhead and the door is sealed. Rack 7 hums in the corner, an admin\n"
            "terminal blinks beside a cluttered desk, and a keypad glows by the door."
        ),
        "choices": [
            {"label": "Search the desk", "goto": "desk"},
            {"label": "Inspect server rack 7", "goto": "rack"},
            {"label": "Walk to the admin terminal", "goto": "terminal"},
            {"label": "Try the door keypad", "goto": "keypad"},
        ],
    },
    "desk": {
        "text": (
            "A cold coffee, a locked drawer, and a sticky note stuck to the monitor."
        ),
        "choices": [
            {
                "label": "Read the sticky note",
                "give": "pin_note",
                "hide_if": "pin_note",
                "message": "It says: 'Door PIN 4729. STOP writing it on the monitor!'",
            },
            {
                "label": "Pick the drawer lock (it rattles loudly)",
                "give": "usb",
                "alert": 1,
                "hide_if": "usb",
                "message": "Inside is a USB drive labelled 'IR-TOOLKIT'. The alarm light flickers.",
            },
            {"label": "Step back", "goto": "start"},
        ],
    },
    "rack": {
        "text": (
            "Rack 7 is a jungle of fibre and power cables. A maintenance keycard\n"
            "dangles from a cable tie somewhere in the middle."
        ),
        "choices": [
            {
                "label": "Carefully slip the keycard free",
                "give": "keycard",
                "hide_if": "keycard",
                "message": "Steady hands. You ease the keycard out without a sound.",
            },
            {
                "label": "Yank the whole cable bundle",
                "give": "keycard",
                "alert": 2,
                "hide_if": "keycard",
                "message": "Sparks! You get the keycard, but every alarm now knows your name.",
            },
            {"label": "Step back", "goto": "start"},
        ],
    },
    "terminal": {
        "text": (
            "The admin terminal reads:\n"
            "  ALERT: INTRUDER DETECTED IN SERVER ROOM B\n"
            "A USB port is lit up and waiting."
        ),
        "choices": [
            {
                "label": "Plug in the USB drive and run the incident-response script",
                "requires": "usb",
                "flag": "alarm_off",
                "hide_if": "alarm_off",
                "message": "The script runs. 'Alarm silenced. Logs scrubbed.' The red light dies.",
            },
            {
                "label": "Brute-force the admin password",
                "alert": 1,
                "message": "ACCESS DENIED. Your attempt has been logged. The light gets angrier.",
            },
            {"label": "Send an SOS to the security team", "goto": "end_rescued"},
            {"label": "Step back", "goto": "start"},
        ],
    },
    "keypad": {
        "text": "A 4-digit keypad and, below it, a card reader and a tiny USB service port.",
        "choices": [
            {
                "label": "Enter PIN 4729 and swipe the keycard",
                "requires": ["pin_note", "keycard"],
                "goto": "door",
            },
            {
                "label": "Enter PIN 4729",
                "requires": "pin_note",
                "hide_if": "keycard",
                "message": "PIN accepted - but the reader still wants a maintenance keycard.",
            },
            {
                "label": "Guess a PIN: 1234",
                "alert": 1,
                "message": "BZZT. Wrong. The keypad judges you silently.",
            },
            {
                "label": "Plug the USB drive into the service port",
                "requires": "usb",
                "goto": "end_hacker",
            },
            {"label": "Step back", "goto": "start"},
        ],
    },
    # "branch" scenes pick their destination from the game state.
    "door": {"branch": lambda s: "end_clean" if "alarm_off" in s.flags else "end_caught"},
    # Endings
    "end_clean": {
        "ending": "ENDING 1/5 - GHOST IN THE MACHINE",
        "text": (
            "The lock clicks open in perfect silence. You stroll out past a sleepy\n"
            "guard, coffee in hand. Nobody ever finds out you were there."
        ),
    },
    "end_caught": {
        "ending": "ENDING 2/5 - CAUGHT RED-HANDED",
        "text": (
            "The door opens, and so does every alarm in the building. Two guards are\n"
            "waiting in the corridor. You should have silenced the terminal first."
        ),
    },
    "end_lockdown": {
        "ending": "ENDING 3/5 - TOTAL LOCKDOWN",
        "text": (
            "The alert level maxes out. Steel shutters slam down and the vents hiss.\n"
            "You will be spending the night here, with the servers."
        ),
    },
    "end_rescued": {
        "ending": "ENDING 4/5 - THE BORING ENDING",
        "text": (
            "You send a polite SOS. Security arrives in six minutes with a spare key\n"
            "and a lot of questions. Safe, embarrassed, and ready for HR."
        ),
    },
    "end_hacker": {
        "ending": "ENDING 5/5 - THE HACKER'S WAY OUT",
        "text": (
            "The USB drive whirs, the keypad flashes 'ROOT', and the door swings\n"
            "open. Not by the book, but you are free."
        ),
    },
}


# ---------------------------------------------------------------------------
# Game logic (kept free of input()/print() so it can be unit-tested)
# ---------------------------------------------------------------------------
def as_list(value) -> list[str]:
    """Normalise a 'requires' value (None, str or list) into a list."""
    if value is None:
        return []
    return [value] if isinstance(value, str) else list(value)


def has(state: State, name: str) -> bool:
    return name in state.items or name in state.flags


def is_hidden(choice: dict, state: State) -> bool:
    return "hide_if" in choice and has(state, choice["hide_if"])


def is_unlocked(choice: dict, state: State) -> bool:
    return all(has(state, req) for req in as_list(choice.get("requires")))


def visible_choices(state: State) -> list[dict]:
    return [c for c in SCENES[state.scene]["choices"] if not is_hidden(c, state)]


def is_ending(scene_id: str) -> bool:
    return "ending" in SCENES[scene_id]


def resolve_branches(state: State) -> None:
    while "branch" in SCENES[state.scene]:
        state.scene = SCENES[state.scene]["branch"](state)


def apply_choice(state: State, choice: dict) -> str:
    """Apply a choice to the state and return the message to show the player."""
    if not is_unlocked(choice, state):
        needed = ", ".join(ITEM_NAMES.get(r, r) for r in as_list(choice["requires"]))
        return f"You are missing something: {needed}."

    state.moves += 1
    if "give" in choice:
        state.items.add(choice["give"])
    if "flag" in choice:
        state.flags.add(choice["flag"])
    state.alert += choice.get("alert", 0)
    if "goto" in choice:
        state.scene = choice["goto"]
        resolve_branches(state)
    if state.alert >= MAX_ALERT and not is_ending(state.scene):
        state.scene = "end_lockdown"
        return choice.get("message", "") + "\nThe alert level hits MAX. Lockdown!"
    return choice.get("message", "")


def inventory_text(state: State) -> str:
    if not state.items:
        return "Inventory: (empty)"
    names = ", ".join(ITEM_NAMES[i] for i in sorted(state.items))
    return f"Inventory: {names}"


def alert_bar(state: State) -> str:
    level = min(state.alert, MAX_ALERT)
    return f"Alert: [{'#' * level}{'.' * (MAX_ALERT - level)}] {level}/{MAX_ALERT}"


# ---------------------------------------------------------------------------
# Terminal interface
# ---------------------------------------------------------------------------
HELP = "Type a number to choose. 'i' = inventory, 'h' = help, 'q' = quit."
TITLE = r"""
 ____                                ____
/ ___|  ___ _ ____   _____ _ __     |  _ \ ___   ___  _ __ ___
\___ \ / _ \ '__\ \ / / _ \ '__|    | |_) / _ \ / _ \| '_ ` _ \
 ___) |  __/ |   \ V /  __/ |       |  _ < (_) | (_) | | | | | |
|____/ \___|_|    \_/ \___|_|       |_| \_\___/ \___/|_| |_| |_|
                 E S C A P E
"""


def play(
    input_fn: Callable[[str], str] = input,
    output_fn: Callable[[str], None] = print,
) -> str | None:
    """Run the game loop. Returns the ending scene id, or None if the player quits."""
    state = State()
    output_fn(TITLE)
    output_fn(HELP)

    while True:
        scene = SCENES[state.scene]
        output_fn("\n" + "-" * 64)
        output_fn(scene["text"])

        if is_ending(state.scene):
            output_fn("\n*** " + scene["ending"] + " ***")
            output_fn(f"You finished in {state.moves} moves. THE END.")
            return state.scene

        output_fn("\n" + alert_bar(state))
        choices = visible_choices(state)
        for number, choice in enumerate(choices, start=1):
            lock = "" if is_unlocked(choice, state) else "  [locked]"
            output_fn(f"  {number}. {choice['label']}{lock}")

        try:
            answer = input_fn("\n> ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            output_fn("\nGame aborted.")
            return None

        if answer in ("q", "quit", "exit"):
            output_fn("Thanks for playing!")
            return None
        if answer in ("h", "help", "?"):
            output_fn(HELP)
            continue
        if answer in ("i", "inv", "inventory"):
            output_fn(inventory_text(state))
            continue
        if not answer.isdigit() or not 1 <= int(answer) <= len(choices):
            output_fn(f"Please enter a number from 1 to {len(choices)}.")
            continue

        message = apply_choice(state, choices[int(answer) - 1])
        if message:
            output_fn("\n" + message)


def main() -> int:
    play()
    return 0


if __name__ == "__main__":
    sys.exit(main())
