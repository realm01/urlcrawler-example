import requests
from lib.utils import read_config
from lib.graph import Graph
from lib.visualize import visualize_graph


def main():
    urls = read_config('urls.conf')
    graph = Graph()

    max_recursion = 4
    max_threads = 20

    for url in urls:
        graph.start_crawl(requests.get(url))

    visualize_graph(graph, "test.png")


if __name__ == '__main__':
    main()
