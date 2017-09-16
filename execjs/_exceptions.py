class Error(Exception):
    pass


class RuntimeError(Error):
    def __init__(self, status, stdout, stderr):
        Error.__init__(self, status, stdout, stderr)
        self.status = status
        self.stdout = stdout
        self.stderr = stderr


class ProgramError(Error):
    pass


class RuntimeUnavailableError(RuntimeError):
    pass
