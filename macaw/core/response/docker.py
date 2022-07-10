import json

import requests

from core.response.response_generator import ResponseGenerator


class ResponseGeneratorDocker(ResponseGenerator):
    """
    A class that encapsulates an ML model running in a local docker container.
    """

    def __init__(self, name: str, endpoint: str):
        super().__init__(name)
        self.endpoint = endpoint

    def run(self, conv_list) -> dict:
        # extract request from the conversation.
        request = {
            "text": "input message for RG docker model."
        }

        try:
            response = requests.post(url=self.endpoint, data=json.dumps(request))
            return response.json()
        except Exception as e:
            return {
                "response": f"Error in post request call for {self.name}: {e}",
                "error": True
            }
