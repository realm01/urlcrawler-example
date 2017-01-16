import networkx as nx
import matplotlib
import matplotlib.pyplot as plt


def visualize_graph(graph, filename):
    figure = plt.figure()
    nx.draw(graph, ax=figure.add_subplot(111))
    figure.savefig(filename)
