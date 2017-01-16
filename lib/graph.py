import networkx as nx
from urllib.parse import urlsplit

class Graph(nx.Graph):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__internal_nodelist = dict()

    def __get_hostname(self, url):
        return "{0.scheme}://{0.netloc}/".format(urlsplit(url))

    def add_node(self, n, attr_dict=None, **attr):
        def __internal_add_node(resp):
            host = self.__get_hostname(resp.url)
            if not self.has_node(host):
                nx.Graph.add_node(self, host, attr_dict, **attr)
                self.__internal_nodelist[host] = resp

        if n.history:
            last_resp = None
            for resp in n.history:
                host = self.__get_hostname(resp.url)
                __internal_add_node(resp)

                if last_resp is not None:
                    self.add_edge(self.__get_hostname(last_resp.url), host)

                last_resp = resp
        else:
            __internal_add_node(n)
