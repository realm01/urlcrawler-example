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
        return url


class CrawlThread(Thread):
    def __init__(self, graph, resp, global_thread_information, rescursion_information, link_node=None):
        super().__init__()
        self.__graph = graph
        self.__curr_resp = resp
        self.__global_thread_information = global_thread_information
        self.__recursion_information = rescursion_information
        self.__link_node = link_node
        self.__thread_pool = list()
        self.__is_joining = False

    def join_threads(self):
        if self.__is_joining:
            return

        self.__is_joining = True
        # print('JOINING THREADS', self.__global_thread_information.thread_count)
        for t in self.__thread_pool:
            t.join()
            self.__global_thread_information.thread_count.decrement()
            print('COUTCOUTCOUT', self.__global_thread_information.thread_count)

        self.__thread_pool = list()

        self.__is_joining = False

    def gather_links(self, resp):
        resp_url = URLHelpers.get_hostname(resp.url)

        soup = BeautifulSoup(resp.text, 'html.parser')
        links = soup.find_all('a')

        print(len(links))

        for link in links:
            if self.__recursion_information.allow_new_recursion():
                new_url = link.get('href')
                new_host = URLHelpers.get_hostname(new_url)
                if new_url is not None and isinstance(new_url, str) and new_url.find('http://') == -1 and new_url.find('https://') == -1:
                    continue

                if new_host in self.__graph.internal_nodelist.keys():
                    continue

                try:
                    new_resp = requests.get(new_url)
                except:
                    continue

                if not self.__global_thread_information.allow_new_thread():
                    print('NOT ALLOWING NEW THREAD')
                    self.join_threads()

                if self.__global_thread_information.allow_new_thread():
                    self.__global_thread_information.thread_count.increment()
                    thread = CrawlThread(self.__graph, new_resp, self.__global_thread_information, self.__recursion_information.copy(), resp_url)
                    thread.start()
                    self.__thread_pool.append(thread)

        self.join_threads()

    def run(self):
        def __internal_add_node(resp):
            host = URLHelpers.get_hostname(resp.url)
            self.__graph.call_method('add_node', host)
            self.__graph.internal_nodelist[host] = resp
            print(host)

        if self.__curr_resp.history:
            if self.__link_node is not None:
                self.__graph.call_method('add_edge', self.__link_node, URLHelpers.get_hostname(self.__curr_resp.history[-1].url))

            last_resp = None
            for resp in self.__curr_resp.history:
                host = URLHelpers.get_hostname(resp.url)
                __internal_add_node(resp)
                if last_resp is not None:
                    self.__graph.call_method('add_edge', URLHelpers.get_hostname(last_resp.url), host)
                last_resp = resp

            __internal_add_node(self.__curr_resp)
            self.__graph.call_method('add_edge', URLHelpers.get_hostname(last_resp.url), URLHelpers.get_hostname(self.__curr_resp.url))
        else:
            if self.__link_node is not None:
                self.__graph.call_method('add_edge', self.__link_node, URLHelpers.get_hostname(self.__curr_resp.url))

            __internal_add_node(self.__curr_resp)

        self.gather_links(self.__curr_resp)


class Graph(nx.DiGraph):
    def __init__(self, thread_information, rescursion_information, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.internal_nodelist = dict()
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

    def call_method(self, method_name, *args, **kwargs):
        self.__mutex.acquire()
        r = getattr(self, method_name)(*args, **kwargs)
        self.__mutex.release()
        return r

    @property
    def get_respones(self):
        return self.__internal_nodelist
