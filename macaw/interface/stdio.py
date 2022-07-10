"""
The STDIO interface for interactive CIS.

Authors: Hamed Zamani (hazamani@microsoft.com), George Wei (gzwei@umass.edu)
"""
import json
import time
import traceback
from datetime import datetime

from macaw.core.interaction_handler.msg import Message
from macaw.interface.interface import Interface


class StdioInterface(Interface):
    def __init__(self, params):
        super().__init__(params)
        self.msg_id = int(time.time())

    def run(self):
        print(f"Inside StdioInterface run method.")
        with open(self.params["verbose_output_file_path"], "w+") as verbose_file:
            while True:
                try:
                    request = input("ENTER YOUR COMMAND (type 'exit' to leave): ").strip()
                    if request == "exit":
                        break
                    if len(request) == 0:
                        continue
                    user_info = {"first_name": "STDIO", "is_bot": "False"}
                    msg_info = {
                        "msg_id": self.msg_id,
                        "msg_type": "command" if request.startswith("#") else "text",
                        "msg_source": "user",
                    }
                    self.msg_id += 1
                    msg = Message(
                        user_interface="stdio",
                        user_id=-1,
                        text=request,
                        timestamp=datetime.utcnow(),
                        user_info=user_info,
                        msg_info=msg_info,
                    )
                    output = self.params["live_request_handler"](msg)
                    self.result_presentation(output, {"verbose_file_handler": verbose_file})
                except Exception as ex:
                    traceback.print_exc()

    def result_presentation(self, response_msg: Message, additional_params: dict):
        verbose_fh = additional_params["verbose_file_handler"]
        verbose_fh.write(json.dumps(dict(response_msg)) + "\n")

        try:
            print("THE RESPONSE STARTS")
            print(
                "----------------------------------------------------------------------"
            )
            if response_msg.msg_info["msg_type"] == "text":
                print(response_msg.response)
            elif response_msg.msg_info["msg_type"] == "options":
                for (option_text, option_data, output_score) in response_msg.msg_info[
                    "options"
                ]:
                    print(option_data, " | ", option_text)
            elif response_msg.msg_info["msg_type"] == "error":
                print("ERROR: NO RESULT!")
            else:
                raise Exception(
                    "The msg_type is not recognized:", response_msg.msg_info["msg_type"]
                )
            print(
                "----------------------------------------------------------------------"
            )
            print("THE RESPONSE ENDS")
        except Exception as ex:
            traceback.print_exc()
