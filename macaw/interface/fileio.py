"""
The FileIO interface (for experimental batch interactions).

Authors: Hamed Zamani (hazamani@microsoft.com)
"""
import json
import time
from datetime import datetime

from macaw.core.interaction_handler.msg import Message
from macaw.interface.interface import Interface


class FileioInterface(Interface):
    def __init__(self, params):
        super().__init__(params)
        self.msg_id = int(time.time())

    def run(self):
        with open(self.params["output_file_path"], "w+") as output_file_handler, \
                open(self.params["verbose_output_file_path"], "w+") as verbose_file_handler, \
                open(self.params["input_file_path"]) as input_file:
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
                    output_msg,
                    {
                        "qid": qid,
                        "output_file_handler": output_file_handler,
                        "verbose_file_handler": verbose_file_handler
                    }
                )

    def result_presentation(self, response_msg: Message, additional_params: dict):
        """
        This method writes the result of this turn into output files. Files are already opened before calling this
        method and handlers passed in as arguments.

        response_msg: the result message generated for this turn.
        additional_params: dict having params required by this method not present in the self.params class variable.
        """
        qid = additional_params["qid"]
        output_fh = additional_params["output_file_handler"]
        verbose_fh = additional_params["verbose_file_handler"]

        verbose_fh.write(json.dumps(dict(response_msg)))
        verbose_fh.write("\n")

        if self.params["output_format"] == "trec":
            if response_msg.msg_info["msg_type"] == "options":
                for (i, (option_name, option_id, output_score)) in enumerate(
                    response_msg.msg_info["options"]
                ):
                    output_fh.write(
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
            msg_type = response_msg.msg_info["msg_type"]
            if msg_type == "text":
                output_fh.write(
                    qid
                    + "\t"
                    + response_msg.response.replace("\n", " ").replace("\t", " ")
                    + "\n"
                )
            else:
                raise Exception(
                    f"Text output format is only recognized for text outputs. Found {msg_type}."
                )
        else:
            raise Exception("Unknown output file format!")
