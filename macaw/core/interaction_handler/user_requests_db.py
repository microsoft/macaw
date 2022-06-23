"""
The conversation (or interaction) database implemented using MongoDB.

Authors: Hamed Zamani (hazamani@microsoft.com), George Wei (gzwei@umass.edu)
"""

from datetime import datetime, timedelta

from pymongo import MongoClient

from macaw.core.interaction_handler.msg import Message


class InteractionDB:
    def __init__(self, host, port, dbname):
        self.client = MongoClient(host, port)
        self.db = self.client[dbname]
        self.col = self.db["macaw_msgs"]

    def insert_one(self, msg):
        self.col.insert_one(dict(msg))

    def update_one(self, user_id, updates):
        self.col.find_one_and_update(
            {"user_id": user_id}, updates, sort=[("timestamp", -1)]
        )

    def get_all(self):
        print(
            "Using get_all is only recommended for development purposes. It is not efficient!"
        )
        return self.dict_list_to_msg_list(self.col.find({}))

    def get_conv_history(self, user_id, max_time, max_count):
        if max_time is None:
            res = self.col.find({"user_id": user_id}, sort=[("timestamp", -1)])
        else:
            res = self.col.find(
                {
                    "user_id": user_id,
                    "timestamp": {
                        "$gt": datetime.utcnow() - timedelta(minutes=max_time)
                    },
                },
                sort=[("timestamp", -1)],
            )

        if max_count is not None:
            res = res.limit(max_count)
        return self.dict_list_to_msg_list(res)

    def close(self):
        self.client.close()

    @staticmethod
    def dict_list_to_msg_list(msg_dict_list):
        msg_list = []
        for msg_dict in msg_dict_list:
            msg_dict.pop("_id")
            msg_list.append(Message.from_dict(msg_dict=msg_dict))
        return msg_list
