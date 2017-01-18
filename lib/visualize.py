import networkx as nx
import matplotlib
import matplotlib.pyplot as plt


def visualize_graph(graph, filename):
    figure = plt.figure(figsize=(24, 24))
    nx.draw(graph, pos=nx.spring_layout(graph), ax=figure.add_subplot(), with_labels=True)
    figure.savefig(filename)
