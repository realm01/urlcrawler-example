import networkx as nx
from urllib.parse import urlsplit
from lib.utils import ThreadInformation
from threading import Thread, Lock
from bs4 import BeautifulSoup
import requests


class URLHelpers():
    @classmethod
    def get_hostname(cls, url):
        # return "{0.scheme}://{0.netloc}/".format(urlsplit(url))
        if URLHelpers.is_string(url):
            return url.strip()
        else:
            return url

    @classmethod
    def is_string(cls, url):
        return url is not None and isinstance(url, str) and url.find('http://') == -1 and url.find('https://') == -1


class CrawlThread(Thread):
    def __init__(self, graph, resp, global_thread_information, rescursion_information, link_node=None):
        super().__init__()
        self.__graph = graph
        self.__curr_resp = resp
        self.__global_thread_information = global_thread_information
        self.__recursion_information = rescursion_information
        self.__link_node = link_node
        self.__thread_pool = list()
        self.__thread_pool_link_evaluation = list()
        self.__is_joining = False

    def join_threads(self, thread_pool):
        if self.__is_joining:
            return

        self.__is_joining = True
        for t in thread_pool:
            t.join()
            self.__global_thread_information.thread_count.decrement()

        del(thread_pool[:])

        self.__is_joining = False

    def gather_links(self, resp):
        resp_url = URLHelpers.get_hostname(resp.url)

        soup = BeautifulSoup(resp.text, 'html.parser')
        links = soup.find_all('a')

        for link in links:
            def __link_thread():
                if self.__recursion_information.allow_new_recursion():
                    new_url = link.get('href')
                    new_host = URLHelpers.get_hostname(new_url)
                    if URLHelpers.is_string(new_url):
                        return

                    if self.__graph.has_node(new_url):
                        return

                    try:
                        new_resp = requests.get(new_url)
                    except:
                        return

                    def __start_crawl_thread():
                        self.__global_thread_information.thread_count.increment()
                        thread = CrawlThread(self.__graph, new_resp, self.__global_thread_information, self.__recursion_information.copy(), resp_url)
                        thread.start()
                        self.__thread_pool.append(thread)

                    if not self.__global_thread_information.allow_new_thread():
                        self.join_threads(self.__thread_pool)
                        __start_crawl_thread()
                    else:
                        __start_crawl_thread()

            def __start_link_evaluation_thread():
                t = Thread(target=__link_thread)
                self.__thread_pool.append(t)
                t.start()

            if not self.__global_thread_information.allow_new_thread():
                self.join_threads(self.__thread_pool_link_evaluation)
                __start_link_evaluation_thread()
            else:
                __start_link_evaluation_thread()

        self.join_threads(self.__thread_pool)
        self.join_threads(self.__thread_pool_link_evaluation)

    def run(self):
        def __internal_add_node(resp):
            host = URLHelpers.get_hostname(resp.url)
            self.__graph.add_node(host)

        if self.__curr_resp.history:
            last_resp = None
            for resp in self.__curr_resp.history:
                host = URLHelpers.get_hostname(resp.url)
                __internal_add_node(resp)
                if last_resp is not None:
                    if not self.__graph.add_edge(URLHelpers.get_hostname(last_resp.url), host):
                        return
                last_resp = resp

            __internal_add_node(self.__curr_resp)

            if self.__link_node is not None:
                if not self.__graph.add_edge(self.__link_node, URLHelpers.get_hostname(self.__curr_resp.history[-1].url)):
                    return

            if not self.__graph.add_edge(URLHelpers.get_hostname(last_resp.url), URLHelpers.get_hostname(self.__curr_resp.url)):
                return
        else:
            if self.__link_node is not None:
                if not self.__graph.add_edge(self.__link_node, URLHelpers.get_hostname(self.__curr_resp.url)):
                    return

            __internal_add_node(self.__curr_resp)

        self.gather_links(self.__curr_resp)


class Graph(nx.DiGraph):
    def __init__(self, thread_information, rescursion_information, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__mutex = Lock()
        self.__global_thread_information = thread_information
        self.__recursion_information = rescursion_information

    def start_crawl(self, resp):
        if self.__global_thread_information.allow_new_thread():
            self.__global_thread_information.thread_count.increment()
            thread = CrawlThread(self, resp, self.__global_thread_information, self.__recursion_information)
            thread.start()
            thread.join()
            self.__global_thread_information.thread_count.decrement()
        else:
            thread = CrawlThread(self, resp, self.__global_thread_information, self.__recursion_information)
            thread.run()

    def add_node(self, n, *args, **kwargs):
        with self.__mutex:
            if nx.DiGraph.has_node(self, n):
                return False
            else:
                nx.DiGraph.add_node(self, n, *args, **kwargs)
                print(n)
                return True

    def add_edge(self, n1, n2, *args, **kwargs):
        with self.__mutex:
            if nx.DiGraph.has_edge(self, n1, n2):
                return False
            else:
                nx.DiGraph.add_edge(self, n1, n2, *args, **kwargs)
                return True

    def call_method(self, method_name, *args, **kwargs):
        """Call a method in Graph thread safe using reflection, not used atm."""
        self.__mutex.acquire()
        r = getattr(self, method_name)(*args, **kwargs)
        self.__mutex.release()
        return r
