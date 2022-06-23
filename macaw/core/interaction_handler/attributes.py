"""
The attribute singleton classes.

Authors: George Wei (gzwei@umass.edu)
"""


class Singleton:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

    def __new__(self, **kwargs):
        if not hasattr(self, "instance"):
            self.instance = super().__new__(self, **kwargs)
        return self.instance


class CurrentAttributes(Singleton):
    pass


class UserAttributes(Singleton):
    pass
