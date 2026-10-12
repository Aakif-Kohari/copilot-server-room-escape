"""Unit tests for Server Room Escape. Run with:  python -m unittest -v"""
import unittest

import main
from main import SCENES, State, apply_choice, play, visible_choices


def pick(state: State, snippet: str) -> str:
    """Pick the visible choice whose label contains `snippet`."""
    for choice in visible_choices(state):
        if snippet.lower() in choice["label"].lower():
            return apply_choice(state, choice)
    raise AssertionError(f"No visible choice containing {snippet!r} in {state.scene!r}")


def run_script(*steps: str) -> State:
    state = State()
    for scene_snippet in steps:
        pick(state, scene_snippet)
    return state


class StoryDataTests(unittest.TestCase):
    def test_every_goto_points_to_a_real_scene(self):
        for scene_id, scene in SCENES.items():
            for choice in scene.get("choices", []):
                if "goto" in choice:
                    self.assertIn(choice["goto"], SCENES, f"{scene_id} -> {choice['goto']}")

    def test_every_item_reference_is_known(self):
        for scene in SCENES.values():
            for choice in scene.get("choices", []):
                for key in ("give", "requires"):
                    for item in main.as_list(choice.get(key)):
                        self.assertIn(item, main.ITEM_NAMES)

    def test_five_endings_exist(self):
        self.assertEqual(sum(main.is_ending(s) for s in SCENES), 5)


class GameplayTests(unittest.TestCase):
    def test_clean_escape(self):
        state = run_script(
            "desk", "sticky note", "step back",
            "rack", "carefully", "step back",
            "desk", "drawer", "step back",
            "terminal", "plug in the usb", "step back",
            "keypad", "swipe the keycard",
        )
        self.assertEqual(state.scene, "end_clean")
        self.assertEqual(state.alert, 1)  # only the noisy drawer

    def test_caught_if_alarm_not_silenced(self):
        state = run_script(
            "desk", "sticky note", "step back",
            "rack", "carefully", "step back",
            "keypad", "swipe the keycard",
        )
        self.assertEqual(state.scene, "end_caught")

    def test_hacker_ending_needs_usb(self):
        state = State(scene="keypad")
        message = pick(state, "service port")
        self.assertIn("missing", message)
        self.assertEqual(state.scene, "keypad")
        state.items.add("usb")
        pick(state, "service port")
        self.assertEqual(state.scene, "end_hacker")

    def test_rescue_ending(self):
        self.assertEqual(run_script("terminal", "sos").scene, "end_rescued")

    def test_lockdown_when_alert_maxes_out(self):
        state = run_script("terminal", "brute-force", "brute-force", "brute-force")
        self.assertEqual(state.scene, "end_lockdown")

    def test_items_cannot_be_taken_twice(self):
        state = run_script("desk", "sticky note")
        labels = [c["label"] for c in visible_choices(state)]
        self.assertFalse(any("sticky note" in label.lower() for label in labels))

    def test_partial_pin_message_without_keycard(self):
        state = State(scene="keypad", items={"pin_note"})
        message = pick(state, "Enter PIN 4729")
        self.assertIn("keycard", message)
        self.assertEqual(state.scene, "keypad")


class InterfaceTests(unittest.TestCase):
    def play_inputs(self, inputs):
        feed = iter(inputs)
        output = []
        result = play(lambda _prompt: next(feed), output.append)
        return result, "\n".join(output)

    def test_quit(self):
        result, text = self.play_inputs(["q"])
        self.assertIsNone(result)
        self.assertIn("Thanks for playing", text)

    def test_invalid_input_is_handled(self):
        _, text = self.play_inputs(["banana", "99", "0", "q"])
        self.assertEqual(text.count("Please enter a number"), 3)

    def test_inventory_and_help_commands(self):
        _, text = self.play_inputs(["i", "h", "q"])
        self.assertIn("Inventory: (empty)", text)
        self.assertIn("'q' = quit", text)

    def test_full_playthrough_reaches_an_ending(self):
        # 3 -> terminal, 3 -> SOS
        result, text = self.play_inputs(["3", "3"])
        self.assertEqual(result, "end_rescued")
        self.assertIn("THE END", text)

    def test_eof_aborts_cleanly(self):
        def raise_eof(_prompt):
            raise EOFError

        self.assertIsNone(play(raise_eof, lambda _t: None))


if __name__ == "__main__":
    unittest.main()
