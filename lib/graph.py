import networkx as nx
from urllib.parse import urlsplit
from threading import Thread, Lock

class URLHelpers():
    @classmethod
    def get_hostname(cls, url):
        return "{0.scheme}://{0.netloc}/".format(urlsplit(url))


class RootThread(Thread):
    def __init__(self, graph, first_resp):
        super().__init__()
        self.__graph = graph
        self.__first_resp = first_resp

    def run(self):
        def __internal_add_node(resp):
            host = URLHelpers.get_hostname(resp.url)
            if not self.__graph.call_method('has_node', host):
                self.__graph.call_method('add_node', host)
                self.__graph.internal_nodelist[host] = resp

        if self.__first_resp.history:
            last_resp = None
            for resp in self.__first_resp.history:
                host = URLHelpers.get_hostname(resp.url)
                __internal_add_node(resp)
                if last_resp is not None:
                    self.__graph.call_method('add_edge', URLHelpers.get_hostname(last_resp.url), host)
                last_resp = resp

            self.__graph.call_method('add_edge', URLHelpers.get_hostname(last_resp.url), URLHelpers.get_hostname(self.__first_resp.url))
        else:
            __internal_add_node(self.__first_resp)


class Graph(nx.DiGraph):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.internal_nodelist = dict()
        self.__mutex = Lock()

    def start_crawl(self, resp):
        thread = RootThread(self, resp)
        thread.start()
        thread.join()

    def call_method(self, method_name, *args, **kwargs):
        self.__mutex.acquire()
        r = getattr(self, method_name)(*args, **kwargs)
        self.__mutex.release()
        return r

    @property
    def get_respones(self):
        return self.__internal_nodelist
