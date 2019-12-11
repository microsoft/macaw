"""
The conversation (or interaction) database implemented using MongoDB.

Authors: Hamed Zamani (hazamani@microsoft.com)
"""

from pymongo import MongoClient

from code import util
from code.util.msg import Message


class InteractionDB:
    def __init__(self, host, port, dbname):
        self.client = MongoClient(host, port)
        self.db = self.client[dbname]
        self.col = self.db['macaw_msgs']

    def insert_one(self, msg):
        if msg.user_id is None or msg.text is None or msg.timestamp is None or msg.user_interface is None:
            raise Exception('Each message should include a user_interface, user_id, text, and timestamp.')
        self.col.insert_one(msg.__dict__)

    def get_all(self):
        print('Using get_all is only recommended for development purposes. It is not efficient!')
        return self.dict_list_to_msg_list(self.col.find({}))

    def get_conv_history(self, user_id, max_time, max_count):
        if max_time is None:
            res = self.col.find({'user_id': user_id}).sort([('timestamp', -1)])
        else:
            res = self.col.find({'user_id': user_id,
                                 'timestamp': {'$gt': util.current_time_in_milliseconds() - max_time}}).sort([('timestamp', -1)])

        if max_count is not None:
            res = res.limit(max_count)
        return self.dict_list_to_msg_list(res)

    def close(self):
        self.client.close()

    @staticmethod
    def dict_list_to_msg_list(msg_dict_list):
        return [Message.from_dict(msg_dict) for msg_dict in msg_dict_list]




