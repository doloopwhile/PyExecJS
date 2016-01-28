import execjs


class UnavailableRuntime:
    def __init__(self, name):
        self.name = name

    def exec_(self, source):
        raise execjs.RuntimeUnavailableError

    def eval(self, source):
        raise execjs.RuntimeUnavailableError

    def compile(self, source):
        raise execjs.RuntimeUnavailableError

    def is_available(self):
        return False
