from abc import ABCMeta, abstractmethod
import six
import execjs._exceptions as exceptions


@six.add_metaclass(ABCMeta)
class AbstractRuntime(object):
    '''
    Abstract base class for runtime class.
    '''
    def exec_(self, source, cwd=None):
        '''Execute source by JavaScript runtime and return all output to stdout as a string.

        source -- JavaScript code to execute.
        cwd -- Directory where call JavaScript runtime. It may be ignored in some derived class.
        '''
        return self.compile('', cwd=cwd).exec_(source)

    def eval(self, source, cwd=None):
        '''Evaluate source in JavaScript runtime.

        source -- JavaScript code to evaluate.
        cwd -- Directory where call JavaScript runtime. It may be ignored in some derived class.
        '''
        return self.compile('', cwd=cwd).eval(source)

    def compile(self, source, cwd=None):
        '''Bulk source as a context object. The source can be used to execute another code.

        source -- JavaScript code to bulk.
        cwd -- Directory where call JavaScript runtime. It may be ignored in some derived class.
        '''
        if not self.is_available():
            raise exceptions.RuntimeUnavailableError
        return self._compile(source, cwd=cwd)

    @abstractmethod
    def is_available(self):
        raise NotImplementedError

    @abstractmethod
    def _compile(self, source, cwd=None):
        raise NotImplementedError
