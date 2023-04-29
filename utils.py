import numpy as np


class Node:
    def __init__(self, i):
        self.id = i
        self.pos = np.zeros(2)
        self.disp = np.zeros(2)

    def __eq__(self, other):
        return self.id == other.id


def component_search(u, adj_list, visited, comp):
    """ 
    Helper function for find_components() function
    Searches through single component from node u in DFS manner
    """

    visited[u] = True 
    comp.append(u)
    for v in adj_list[u]:
        if not visited[v]:
            component_search(v, adj_list, visited, comp)


def find_components(G):
    """
    Finds all connected components in G (numpy adjacency matrix)

    Args:
        G: numpy.array - ajacency matrix
    Returns:
        list(list(int)) - connected components
    """

    # Build adjacency list for easier manipulation
    adj_list = []
    for i in range(G.shape[0]):
        adj_list.append(list(np.where(G[i] == 1)[0]))
    
    visited = [False] * len(adj_list)
    all_components = []
    
    # Get all connected components
    for i in range(len(adj_list)):
        comp = []
        if not visited[i]:
            component_search(i, adj_list, visited, comp)
            all_components.append(comp)
    return all_components


def map2color(G):
    """
    Maps the nodes to color based on the size of the component containing the node

    Args:
        G: numpy.array - ajacency matrix
    Returns:
        list(str) - mapping to color for each node
    """
    components = find_components(G)

    # Get all unique sizes of components
    lens = set()
    for c in components:
        lens.add(len(c))
    lens = sorted(list(lens))

    # Map each component size to color
    len2color_id = dict()
    c = 0
    for l in lens:
        len2color_id[l] = c
        c += 1

    # Colorscale generated from http://tristen.ca/hcl-picker
    # We have 19 components
    colors = ["#2F1410", "#3E1C1C", "#4C242B", "#572D3B", "#60394E",
              "#654662", "#665575", "#626587", "#587597", "#4B86A3",
              "#3A97AA", "#2AA7AD", "#28B7AB", "#3BC6A5", "#58D49B",
              "#7AE18F", "#9FEC82", "#C7F675", "#F1FE6C"]

    node_colors = [None] * G.shape[0]

    # Assign color to each node
    for comp in components:
        comp_color = colors[len2color_id[len(comp)]]
        for i in comp:
            node_colors[i] = comp_color
    return node_colors
