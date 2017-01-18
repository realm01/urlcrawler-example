import requests
from lib.utils import read_config, ThreadInformation, RecursionInformation
from lib.graph import Graph
from lib.visualize import visualize_graph


def main():
    urls = read_config('urls.conf')

    thread_information = ThreadInformation(200)
    rescursion_information = RecursionInformation(4)
    graph = Graph(thread_information, rescursion_information)

    for url in urls:
        graph.start_crawl(requests.get(url))

    visualize_graph(graph, "test.png")
    print('------------- SUMMARY -------------')
    print('Node Count:', len(graph.internal_nodelist.keys()))

if __name__ == '__main__':
    main()
