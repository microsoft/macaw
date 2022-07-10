import enum

from typing import Union


class State(enum.Enum):
    launch = 1
    recipe_selection = 2
    ingredients = 3
    show_steps = 4
    goodbye = 5


class DST:
    def __init__(self, state=None):
        self.curr_state = State.launch if state is None else state

    @classmethod
    def decode(cls, encoded: dict):
        return DST(State(encoded["curr_state"]))

    def transition(self, input_alphabet, context) -> Union[str, State]:
        """
        Given the input alphabet and context (and thing that tells about the ongoing conversation), it returns what
        should the destination state be. Returns message str if there is no valid transition.
        """
        if self.curr_state == State.launch:
            if input_alphabet == 'recipe_question':
                return State.recipe_selection
        elif self.curr_state == State.recipe_selection:
            if input_alphabet == 'option_selection':
                return State.ingredients
        return f"Could not make a transition from {self.curr_state} using input {input_alphabet}."

    def update(self, new_state: State):
        self.curr_state = new_state

    def encode(self) -> dict:
        return {
            "curr_state": self.curr_state.value
        }

