import requests
from lib.utils import read_config, ThreadInformation, RecursionInformation
from lib.graph import Graph
from lib.visualize import visualize_graph
import argparse


def main():
    parser = argparse.ArgumentParser(description='URLCrawler which crawls stuff')
    parser.add_argument('--serialize', '-s', action='store_true', help='Serialize graph')
    parser.add_argument('--deserialize', '-d', action='store_true', help='Deserialize graph')

    args = parser.parse_args()

    thread_information = ThreadInformation(400)
    rescursion_information = RecursionInformation(1)

    if args.deserialize:
        graph = Graph.deserialize('ser')
    else:
        graph = Graph(thread_information, rescursion_information)
        urls = read_config('urls.conf')
        for url in urls:
            graph.start_crawl(requests.get(url))

        if args.serialize:
            graph.serialize('ser')

    if not isinstance(graph, bool):
        visualize_graph(graph, "test.png")
        print('------------- SUMMARY -------------')
        print('Node Count:', len(graph.nodes()))

if __name__ == '__main__':
    main()
