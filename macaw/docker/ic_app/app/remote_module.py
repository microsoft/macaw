
required_context = ["text"]


def get_required_context():
    return required_context


def handle_message(msg: dict) -> dict:
    """
    Returns the response dictionary. Throws appropriate error if the model cannot generate a response.
    """
    return {
        "response": "okay from ic model."
    }
