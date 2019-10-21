class Message:
    def __init__(self, user_interface, user_id, user_info, msg_info, text, timestamp):
        self.user_id = user_id
        self.user_info = user_info
        self.msg_info = msg_info
        self.text = text
        self.timestamp = timestamp
        self.user_interface = user_interface

    @classmethod
    def from_dict(cls, msg_dict):
        user_interface = msg_dict['user_interface'] if 'user_interface' in msg_dict else None
        user_id = msg_dict['user_id'] if 'user_id' in msg_dict else None
        user_info = msg_dict['user_info'] if 'user_info' in msg_dict else None
        msg_info = msg_dict['msg_info'] if 'msg_info' in msg_dict else None
        text = msg_dict['text'] if 'text' in msg_dict else None
        timestamp = msg_dict['timestamp'] if 'timestamp' in msg_dict else None
        return cls(user_interface, user_id, user_info, msg_info, text, timestamp)