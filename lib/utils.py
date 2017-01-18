from threading import Lock

def read_config(config):
    config = open(config, 'r')
    urls = list()

    line = config.readline().strip()
    while line:
        urls.append(line)
        line = config.readline().strip()

    return urls


class RecursionInformation():
    def __init__(self, max_recursion, curr_count = 0):
        self.__max_recursion = max_recursion
        self.__recursion_count = Int(curr_count)

    def allow_new_recursion(self):
        return self.__recursion_count.raw < self.__max_recursion

    def copy(self):
        return RecursionInformation(self.__max_recursion, self.__recursion_count.raw + 1)

    @property
    def max_recursion(self):
        """Max recursion, this is immutable."""
        return self.__max_recursion

    @property
    def recursion_count(self):
        """Thread count, this is mutable."""
        return self.__recursion_count


class ThreadInformation():
    def __init__(self, max_threads):
        self.__max_threads = max_threads
        self.__thread_count = Int(0)

    def allow_new_thread(self):
        return self.__thread_count.raw < self.__max_threads

    @property
    def max_threads(self):
        """Max thread count, this is immutable."""
        return self.__max_threads

    @property
    def thread_count(self):
        """Thread count, this is mutable."""
        return self.__thread_count


class Int():
    """Thread safe mutable integer."""

    def __init__(self, i):
        self.__mutex = Lock()
        self.__i = i

    def __str__(self):
        return str(self.__i)

    def __repr__(self):
        return int(self.__i).__repr__()

    def increment(self):
        self.__mutex.acquire()
        self.__i += 1
        self.__mutex.release()

        return self.raw

    def decrement(self):
        self.__mutex.acquire()
        self.__i -= 1
        self.__mutex.release()

        return self.raw

    def set(self, i):
        self.__mutex.acquire()
        self.__i = i
        self.__mutex.release()

        return self.raw

    @property
    def raw(self):
        return self.__i
