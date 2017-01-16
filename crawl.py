import requests
from lib.utils import read_config
from lib.graph import Graph
from lib.visualize import visualize_graph


def main():
    urls = read_config('urls.conf')
    graph = Graph()

    for url in urls:
        graph.add_node(requests.get(url))

    visualize_graph(graph, "test.png")


if __name__ == '__main__':
    main()
