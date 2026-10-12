# Server Room Escape

A command-line **choose-your-own-adventure** game written in pure Python (no dependencies).
You are a junior security analyst locked inside Server Room B after a breach alert. Find the
door PIN, grab a keycard, silence the alarm, and escape, without pushing the alert level to
lockdown.

Made for the MLH **Global Hack Week: Hacktoberfest** challenge
*"Use GitHub Copilot to Build a Simple Application"*.

## Features

- 5 scenes to explore and **5 different endings**
- Inventory system (sticky note, USB drive, keycard)
- An **alert meter**: noisy actions raise it, and hitting 3/3 triggers a lockdown
- Locked choices that unlock once you hold the right item
- Clean separation of story data, game logic, and terminal UI
- 15 unit tests (`unittest`, no extra packages)

## Quick start

Requires Python 3.9+.

```bash
git clone https://github.com/Aakif-Kohari/copilot-server-room-escape.git
cd copilot-server-room-escape
python main.py
```

Controls: type a number to choose, `i` for inventory, `h` for help, `q` to quit.

## Sample session

```text
You wake up on the cold floor of Server Room B. A red light pulses
overhead and the door is sealed. Rack 7 hums in the corner, an admin
terminal blinks beside a cluttered desk, and a keypad glows by the door.

Alert: [...] 0/3
  1. Search the desk
  2. Inspect server rack 7
  3. Walk to the admin terminal
  4. Try the door keypad

> 1

A cold coffee, a locked drawer, and a sticky note stuck to the monitor.

Alert: [...] 0/3
  1. Read the sticky note
  2. Pick the drawer lock (it rattles loudly)
  3. Step back
```

## Run the tests

```bash
python -m unittest -v
```

## How it works

| Part | What it does |
| --- | --- |
| `SCENES` | A dictionary describing every scene, its choices, the items they need or give, and the alert they cost |
| `apply_choice()` | Applies a choice to the `State` (items, flags, alert, scene) and returns a message |
| `play()` | The game loop; takes `input_fn` / `output_fn` so tests can drive it without a terminal |

Adding a new room or ending only needs a new entry in `SCENES`.

## The five endings

<details>
<summary>Spoilers</summary>

1. **Ghost in the Machine**: get the PIN, the keycard and the USB, silence the terminal, then leave.
2. **Caught Red-Handed**: leave without silencing the alarm.
3. **Total Lockdown**: let the alert level reach 3/3.
4. **The Boring Ending**: send an SOS from the terminal.
5. **The Hacker's Way Out**: plug the USB into the keypad's service port.

</details>

## Copilot prompts

The prompts used to generate and extend the game are in [PROMPTS.md](PROMPTS.md).

## Project layout

```
main.py          the game
test_game.py     unit tests
PROMPTS.md       Copilot prompts
```

## License

MIT, see [LICENSE](LICENSE).
