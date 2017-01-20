import requests
from lib.utils import read_config, ThreadInformation, RecursionInformation
from lib.graph import Graph
from lib.visualize import visualize_graph
import argparse


def main():
    parser = argparse.ArgumentParser(description='URLCrawler which crawls stuff')
    parser.add_argument('--plot', '-p', type=str, metavar='FILE', default=False, help='Plot the graph')
    parser.add_argument('--serialize', '-s', type=str, metavar='FILE', default=False, help='Serialize graph')
    parser.add_argument('--deserialize', '-d', type=str, metavar='FILE', default=False, help='Deserialize graph')
    parser.add_argument('--threads', '-t', type=int, metavar='INT', default=400, help='Thread count')
    parser.add_argument('--recursions', '-r', type=int, metavar='INT', default=3, help='Recursion count')

    args = parser.parse_args()

    if isinstance(args.plot, bool) and isinstance(args.serialize, bool):
        print('If you wish to do not plot the graph then you need to serialize it, otherwise there is no reason to run this application.\n\n')
        parser.print_help()
        return

    if isinstance(args.plot, bool) and isinstance(args.deserialize, bool):
        print('If you wish to deserialize but not plot the graph then there is no need to run this application.\n\n')
        parser.print_help()
        return

    if isinstance(args.serialize, str) and isinstance(args.deserialize, str):
        print('It makes no sense to serialize and deserialize a graph at the same time.\n\n')
        parser.print_help()
        return

    thread_information = ThreadInformation(args.threads)
    rescursion_information = RecursionInformation(args.recursions)

    if isinstance(args.deserialize, str):
        graph = Graph.deserialize(args.deserialize)
    else:
        graph = Graph(thread_information, rescursion_information)
        urls = read_config('urls.conf')
        for url in urls:
            graph.start_crawl(requests.get(url))

        if isinstance(args.serialize, str):
            graph.serialize(args.serialize)

    if not isinstance(graph, bool) and isinstance(args.plot, str):
        visualize_graph(graph, args.plot)
        print('------------- SUMMARY -------------')
        print('Node Count:', len(graph.nodes()))

if __name__ == '__main__':
    main()
