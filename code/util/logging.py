import logging

class Logger(logging.Logger):
    def __init__(self, params):
        super().__init__('Macaw Logger')
        self.params = params
        if 'logging_file' in params:
            self.handler_ = logging.FileHandler(params['logging_file'])
        else:
            self.handler_ = logging.StreamHandler()

        self.format = logging.Formatter('%(name)s - %(asctime)s - %(levelname)s - %(message)s')
        self.handler_.setFormatter(self.format)
        self.addHandler(self.handler_)
