import math
import random
import numpy as np
from tqdm import tqdm
from utils import Node


class FruchtermanReingold:
    def __init__(self, area=20, gravity=1, speed=0.01):
        """
        Args:
            area: float - Hyperparameter proportional to the size of the area occupied
                          by the layout
            gravity: float - The amout of the gravity force. The force dragging the
                             nodes to the center of the layout 
            speed: float - The multiplier applied to the displacement in the
                           direction of combined forces
        """

        self.area = area
        self.gravity = gravity
        self.speed = speed
        self.AREA_MULTIPLIER = 1000000

    def __initialize(self, G, pos):
        nodes = []
        for i in range(G.shape[0]):
            n = Node(i)
            if pos:
                n.pos[0] = pos[i][0]
                n.pos[1] = pos[i][1]
            else:
                n.pos[0] = random.random()
                n.pos[1] = random.random()
            nodes.append(n)

        edges = []
        all_edges = np.asarray(G.nonzero()).T
        for e in all_edges:
            if e[1] <= e[0]:
                continue  # Skip duplicate edges
            edges.append((e[0], e[1]))

        return nodes, edges

    def __attraction(self, x):
        return x**2 / self.k

    def __repulsion(self, x):
        return self.k**2 / x

    def layout(self, G, iterations=1000, pos=None):
        """
        Computes the graph layout using Fruchterman-Reingold algorithm with some
        modifications inspired by the implementation of Gephi's (https://gephi.org/)
        implementation of Fruchterman-Reingold. Namely the gravity force and the
        maximum displacement were added to the original algorithm.

        Args:
            G: numpy.array - ajacency matrix
            iterations: int - number of iterations
            pos: list(tuple) - list of initial node positions (optional)
        Returns:
            list(tuple) - computed node positions
        """

        nodes, edges = self.__initialize(G, pos)
        degrees = G.sum(axis=0)
        
        self.k = math.sqrt((self.AREA_MULTIPLIER * self.area) / len(nodes))
        max_displace = math.sqrt((self.AREA_MULTIPLIER * self.area)) / 10

        for it in tqdm(range(iterations)):

            # Repulsive forces

            # Precompute everything to avoid the slow double loop
            pos = np.zeros((len(nodes), 2))
            for v in nodes:
                v.disp.fill(0)
                pos[v.id] = v.pos

            # There will be some divides by zero which will be taken care of 
            # by nansum but we don't want to show the warnings
            with np.errstate(divide='ignore', invalid='ignore'):
                delta = (pos[:,None,:] - pos)
                dist = np.linalg.norm(delta, axis=2)
                repulsion = self.__repulsion(dist)
                displacement = delta / dist[:,:,None] * repulsion[:,:,None]
                displacement = np.nansum(displacement, axis=1)
                for v in nodes:
                    v.disp += displacement[v.id]


            # Attractive forces
            for e in edges:
                v = nodes[e[0]]
                u = nodes[e[1]]
                delta = v.pos - u.pos
                dist = np.linalg.norm(delta)
                if dist > 0:
                    attractive_force = self.__attraction(dist)

                    v.disp -= (delta / dist) * attractive_force 
                    u.disp += (delta / dist) * attractive_force

            # Gravity
            for v in nodes:
                dist = np.linalg.norm(v.pos)
                gf = 0.01 * self.k * self.gravity * dist;
                v.disp[0] -= gf * v.pos[0] / dist;
                v.disp[1] -= gf * v.pos[1] / dist;

            # Apply forces
            for v in nodes:
                v.disp *= self.speed
                disp_mag = np.linalg.norm(v.disp)
                if disp_mag > 0:
                    limited_dist = min(max_displace * self.speed, disp_mag);
                    v.pos += v.disp / disp_mag * limited_dist

        return [(n.pos[0], n.pos[1]) for n in nodes]
