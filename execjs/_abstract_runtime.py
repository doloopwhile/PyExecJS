import execjs


class AbstructRuntime:
    def exec_(self, source, cwd=None):
        if not self.is_available():
            raise execjs.RuntimeUnavailableError
        return self._exec_(source, cwd=cwd)

    def eval(self, source, cwd=None):
        if not self.is_available():
            raise execjs.RuntimeUnavailableError
        return self._eval(source, cwd=cwd)

    def compile(self, source, cwd=None):
        if not self.is_available():
            raise execjs.RuntimeUnavailableError
        return self._compile(source, cwd=cwd)

    def is_available(self):
        raise NotImplementedError

    def _exec_(self, source, cwd=None):
        raise NotImplementedError

    def _compile(self, source, cwd=None):
        raise NotImplementedError

    def _eval(self, source, cwd=None):
        raise NotImplementedError
