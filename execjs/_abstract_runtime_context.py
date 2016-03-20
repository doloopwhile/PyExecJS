import execjs
from abc import ABCMeta, abstractmethod
import six


@six.add_metaclass(ABCMeta)
class AbstractRuntimeContext(object):
    '''
    Abstract base class for runtime context class.
    '''
    def exec_(self, source):
        '''Execute source by JavaScript runtime and return all output to stdout as a string.

        source -- JavaScript code to execute.
        '''
        if not self.is_available():
            raise execjs.RuntimeUnavailableError
        return self._exec_(source)

    def eval(self, source):
        '''Evaluate source in JavaScript runtime.

        source -- JavaScript code to evaluate.
        '''
        if not self.is_available():
            raise execjs.RuntimeUnavailableError
        return self._eval(source)

    def call(self, name, *args):
        '''Call a JavaScript function in context.

        name -- Name of funtion object to call
        args -- Arguments for the funtion object
        '''
        if not self.is_available():
            raise execjs.RuntimeUnavailableError
        return self._call(name, *args)

    @abstractmethod
    def is_available(self):
        raise NotImplementedError

    @abstractmethod
    def _exec_(self, source):
        raise NotImplementedError

    @abstractmethod
    def _eval(self, source):
        raise NotImplementedError

    @abstractmethod
    def _call(self, name, *args):
        raise NotImplementedError
