# GitHub Copilot prompts

Prompts for GitHub Copilot Chat (Agent or Edit mode) in VS Code, in the order they are meant to be used.

## 1. Generate the game

```
Build a command-line "choose your own adventure" game in Python 3 with no
external dependencies, in a single file called main.py.

Theme: a junior security analyst is locked inside a server room after a breach
alert and must escape.

Requirements:
- Store the story as a dictionary of scenes. Each scene has text and a list of
  choices. A choice can have a label, a destination scene, an item it gives, an
  item it requires, and an alert cost.
- Track an inventory and an "alert level" from 0 to 3. Reaching 3 triggers a
  lockdown ending.
- Include at least 4 different endings.
- Show locked choices as "[locked]" until the player has the required item.
- Keep game logic separate from input()/print() by passing input_fn and
  output_fn into a play() function so it can be unit tested.
- Validate input; support 'i' for inventory, 'h' for help and 'q' to quit.
- Add a main() function and a __main__ guard.
```

## 2. Add tests

```
Write unittest tests in test_game.py for main.py. Cover: every goto points to a
real scene, a full winning path, the lockdown ending, items that cannot be taken
twice, invalid input handling, and quitting. Use scripted inputs instead of
real input().
```

## 3. Polish

```
Add an ASCII-art title screen and an alert meter that is printed above the
choices, for example "Alert: [#..] 1/3".
```

## 4. Documentation

```
Write a README.md for this project with a short description, features, quick
start, how to run the tests, a short explanation of the SCENES structure, and a
collapsed spoiler list of the endings.
```
