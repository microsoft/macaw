"""
The FileIO interface (for experimental batch interactions).

Authors: Hamed Zamani (hazamani@microsoft.com)
"""

import time
from datetime import datetime

from macaw.core.interaction_handler.msg import Message
from macaw.interface.interface import Interface


class FileioInterface(Interface):
    def __init__(self, params):
        super().__init__(params)
        self.msg_id = int(time.time())

    def run(self):
        output_file = open(self.params["output_file_path"], "w+")
        with open(self.params["input_file_path"]) as input_file:
            for line in input_file:
                str_list = line.strip().split("\t")
                if len(str_list) != 2:
                    raise Exception(
                        f"Each input line should contain at least 2 elements: a query ID and a query text."
                        f"Invalid line: {line}"
                    )
                qid = str_list[0]

                user_info = {"first_name": "NONE"}
                msg_info = {"msg_id": qid, "msg_type": "text", "msg_source": "user"}
                msg = Message(
                    user_interface="fileio",
                    user_id=-1,
                    user_info=user_info,
                    msg_info=msg_info,
                    text=str_list[1],
                    timestamp=datetime.utcnow(),
                )
                output_msg = self.params["experimental_request_handler"](msg)
                self.result_presentation(
                    output_msg, {"output_file": output_file, "qid": qid}
                )
        output_file.close()

    def result_presentation(self, output_msg, params):
        qid = params["qid"]
        output_file = params["output_file"]
        if self.params["output_format"] == "trec":
            if output_msg.msg_info["msg_type"] == "options":
                for (i, (option_name, option_id, output_score)) in enumerate(
                    output_msg.msg_info["options"]
                ):
                    output_file.write(
                        qid
                        + "\tQ0\t"
                        + option_name
                        + "\t"
                        + str(i + 1)
                        + "\t"
                        + str(output_score)
                        + "\tmacaw\n"
                    )
            else:
                raise Exception(
                    "TREC output format is only recognized for retrieval results. "
                    "Therefore, the message type should be options."
                )
        elif self.params["output_format"] == "text":
            if output_msg.msg_info["msg_type"] == "text":
                output_file.write(
                    qid
                    + "\t"
                    + output_msg.response.replace("\n", " ").replace("\t", " ")
                    + "\n"
                )
            else:
                raise Exception(
                    "text output format is only recognized for text outputs."
                )
        else:
            raise Exception("Unknown output file format!")
