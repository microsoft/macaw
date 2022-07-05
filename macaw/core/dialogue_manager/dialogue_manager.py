from core.dialogue_manager.dst import DST, State


class DialogManager(object):
    def __init__(self, dst=None):
        self.dst = DST() if dst is None else dst

    @classmethod
    def decode(cls, encoded: dict):
        return DialogManager(DST.decode(encoded["dst"]))

    def process_turn(self, nlp_pipeline):
        # Get these from the nlp_pipeline output.
        input_alphabet = None
        context = None

        new_state = self.dst.transition(input_alphabet, context)
        if isinstance(new_state, State):
            self.dst.update(new_state)
        else:
            # Save output result in conversation context.
            print(f"new_state={new_state}")
            pass

    def encode(self) -> dict:
        return {
            "dst": self.dst.encode()
        }
