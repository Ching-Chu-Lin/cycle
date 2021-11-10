import collections
import numpy as np

from . import utils


class Graph():
    def __init__(self, num_vertex):
        self.vertices = list(range(num_vertex))  # [0, 1, ... ]
        self.edges = collections.defaultdict(list)  # default dict of []
        self.capacity = collections.defaultdict(float)  # edges[(u, v)] = 0

    def add_edge(self, u, v, c):
        self.edges[u].append(v)
        self.capacity[(u, v)] = c

    def printGraph(self):
        for u in self.vertices:
            for v in self.edges[u]:
                print(f"({u} —> {v}, {self.capacity[(u,v)]})", end=' ')
            print()

    def dfs(self, src, des):
        current = [[src]]
        while current:
            path = current.pop()

            for neighbor in self.edges[path[-1]]:
                if neighbor == des:
                    yield path+[neighbor]
                    continue

                if neighbor in path:
                    # no more loop
                    continue
                current.append(path+[neighbor])

    def take_path(self, path, U):
        for u, v in zip(path, path[1:]):
            self.capacity[(u, v)] = round(self.capacity[(u, v)] - U, 1)
            if self.capacity[(u, v)] == 0:
                self.edges[u].remove(v)
                self.capacity.pop((u, v), None)
        return

    def check_path_enough_capacity(self, path, util):
        for u, v in zip(path, path[1:]):
            if self.capacity[(u, v)] < util:
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
