# Abstract base error classes
class Error(Exception):
    pass

# Abstract class that represents errors of runtime engine.
# ex. Specified runtime engine is not installed, runtime engine aborted (by its bugs).
# By the way "RuntimeError" is bad name because it is confusing with the standard exception.
class RuntimeError(Error):
    pass

# Concrete runtime error classes
class RuntimeUnavailableError(RuntimeError): pass

class ProcessExitedWithNonZeroStatus(RuntimeError):
    def __init__(self, status, stdout, stderr):
        RuntimeError.__init__(self, status, stdout, stderr)
        self.status = status
        self.stdout = stdout
        self.stderr = stderr

# Errors due to JS script.
# ex. Script has syntax error, executed and raised exception.
class ProgramError(Error):
    pass
