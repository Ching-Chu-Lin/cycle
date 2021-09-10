import collections
import numpy as np

from . import utils


class Graph():
    def __init__(self, num_vertex):
        self.vertices = list(range(num_vertex))  # [0, 1, ... ]
        self.adjacent = collections.defaultdict(list)  # default dict of []
        self.edges = collections.defaultdict(float)  # edges[(u, v)] = 0

    def add_edge(self, u, v, capacity):
        self.adjacent[u].append(v)
        self.edges[(u, v)] = capacity

    def printGraph(self):
        for u in self.vertices:
            for v in self.adjacent[u]:
                print(f"({u} —> {v}, {self.edges[(u,v)]})", end=' ')
            print()

    def dfs(self, src, des):
        current = [[src]]
        while current:
            path = current.pop()

            for neighbor in self.adjacent[path[-1]]:
                if neighbor == des:
                    yield path+[neighbor]
                    continue

                if neighbor in path:
                    # no more loop
                    continue
                current.append(path+[neighbor])

    def take_path(self, path, U):
        for u, v in zip(path, path[1:]):
            self.edges[(u, v)] = round(self.edges[(u, v)] - U, 1)
            if self.edges[(u, v)] == 0:
                self.adjacent[u].remove(v)
                self.edges.pop((u, v), None)
        return

    def check_path_enough_capacity(self, path, util):
        for u, v in zip(path, path[1:]):
            if self.edges[(u, v)] < util:
                return False
        return True

    def get_unique_cycles(self):
        # find small cycles
        cycles = [path for node in range(len(self.vertices))
                  for path in self.dfs(node, node)]
        # pop last duplicate vertex
        for c in cycles:
            c.pop()
        cycles = utils.delete_same_cycle(cycles)
        return cycles
