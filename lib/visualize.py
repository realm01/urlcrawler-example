import networkx as nx
import matplotlib
import matplotlib.pyplot as plt


def visualize_graph(graph, filename):
    figure = plt.figure(figsize=(24, 24))
    degrees = nx.degree(graph)
    degree_map = [v * 100 for v in degrees.values()]

    nx.draw_spring(
        graph,
        ax=figure.add_subplot(),
        with_labels=True,
        font_size=8,
        linewidths=0.8,
        width=0.8,
        nodelist=degrees.keys(),
        node_size=degree_map,
        node_color=degree_map,
        edge_color='grey'
    )

    figure.savefig(filename)
