class Error(Exception):
    pass


class RuntimeError(Error):
    pass


class ProgramError(Error):
    pass


class RuntimeUnavailableError(RuntimeError):
    pass
