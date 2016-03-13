import execjs


class AbstructRuntime:
    def exec_(self, source):
        if not self.is_available():
            raise execjs.RuntimeUnavailableError
        return self._exec_(source)

    def eval(self, source):
        if not self.is_available():
            raise execjs.RuntimeUnavailableError
        return self._eval(source)

    def compile(self, source):
        if not self.is_available():
            raise execjs.RuntimeUnavailableError
        return self._compile(source)

    def is_available(self):
        raise NotImplementedError

    def _exec_(self, source, cwd):
        raise NotImplementedError

    def _compile(self, source, cwd):
        raise NotImplementedError

    def _eval(self, source, cwd):
        raise NotImplementedError
