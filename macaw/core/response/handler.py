import logging
from typing import List

from core.response.docker import ResponseGeneratorDocker
from core.response.response_generator import ResponseGenerator


class ResponseGeneratorHandler:
    def __init__(self, rg_models: dict):
        self.rg_models = dict()
        self.logger = logging.getLogger("MacawLogger")

        for model_name, model in rg_models.items():
            if isinstance(model, ResponseGenerator):
                self.rg_models[model_name] = model
            elif isinstance(model, str) and model.startswith("http://"):
                self.rg_models[model_name] = ResponseGeneratorDocker(model_name, model)
            else:
                self.logger.warning(f"Response generator {model_name}:{model} is not supported.")

    def models_selector(self, conv_list) -> List[str]:
        selected_models = []
        for model_name in self.rg_models:
            if model_name == "qa":
                # decide if qa RG should be run or not here.
                selected_models.append(model_name)
            elif model_name == "punctuation":
                selected_models.append(model_name)
            else:
                self.logger.warning(f"Model selector not written for {model_name}. Ignoring the model.")
        return selected_models

    def run_models(self, model_names: List[str], conv_list) -> dict:
        models_response = dict()
        for model_name in model_names:
            models_response[model_name] = self.rg_models[model_name].run(conv_list)
        return models_response
