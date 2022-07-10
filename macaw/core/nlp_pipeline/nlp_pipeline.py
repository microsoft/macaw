import json
import logging
import multiprocessing
import time
from multiprocessing import Pool
from typing import List

import requests

from core.interaction_handler import Message


class RemoteModel:
    def __init__(self, model_name: str, endpoint: str):
        self.model_name = model_name
        self.endpoint = endpoint

    def run(self, request: dict) -> dict:
        try:
            response = requests.post(url=self.endpoint, data=json.dumps(request))
            return response.json()
        except Exception as e:
            return {
                "response": f"Error in post request call for {self.model_name}: {e}",
                "error": True
            }


class NlpPipeline:
    def __init__(self, modules: dict):
        self.modules = dict()
        self.logger = logging.getLogger("MacawLogger")
        for model_name, endpoint in modules.items():
            self.modules[model_name] = RemoteModel(model_name, endpoint)

    def run(self, conv_list: List[Message]):
        """
        Runs all the models and saves their results in the latest conversation (conv_list[0]) message.
        """
        nlp_pipeline_result = {}

        with Pool(processes=4) as pool:
            all_async_results = []
            for model_name, model in self.modules.items():
                # pass in required input to every model.
                model_input = {"text": "input text for model"}
                async_result = pool.apply_async(
                    func=model.run,
                    args=(model_input,)
                )
                all_async_results.append((model_name, async_result))
            pool.close()

            max_wait_time_in_secs = 10  # wait time for all modules combined.
            end_time = time.time() + max_wait_time_in_secs
            for model_name, async_result in all_async_results:
                try:
                    nlp_pipeline_result[model_name] = async_result.get(timeout=max(end_time - time.time(), 0))
                except multiprocessing.TimeoutError as te:
                    resp_msg = f"Module {model_name} timed out."
                    self.logger.error(f"{resp_msg} {te}")
                    nlp_pipeline_result[model_name] = {
                        "response": resp_msg,
                        "error": True,
                    }
            pool.join()

        conv_list[0].nlp_pipeline_result = nlp_pipeline_result
