import logging
import time

from macaw.util.custom_logging import LoggerFactory
from deepmultilingualpunctuation import PunctuationModel
from core.response.response_generator import ResponseGenerator


class ResponseGeneratorPunctuation(ResponseGenerator):
    def __init__(self, name):
        super().__init__(name)
        self.logger = LoggerFactory.create_logger(params={
            "logger_name": "macaw.core.response.response_generator.punctuation",
            "logger_level": logging.INFO
        })

        self.logger.info("Going to download punctuation ML model. This takes time.")
        # self.model = PunctuationModel()
        self.logger.info("Punctuation model loaded successfully.")

    def run(self, conv_list) -> dict:
        # generate input text from the input conversation.
        input_text = "My name is Clara and I live in Berkeley California Ist das eine Frage Frau Müller"

        t0 = time.time()
        # result = self.model.restore_punctuation(input_text)
        result = "punctuation model output."
        duration = time.time() - t0

        return {
            "response": f"Local RG: {self.name}. {result}",
            "error": False,
            "performance": duration
        }
