import collections
import copy
import numpy as np

from . import utils


class Graph():
    def __init__(self, num_vertex):
        self.graph = collections.defaultdict(list)  # default dict of []
        self.vertices = list(range(num_vertex))  # [0, 1, ... ]
        self.edges = collections.defaultdict(float)  # edges[(u, v)] = 0

    def add_edge(self, u, v, capacity):
        self.graph[u].append(v)
        self.edges[(u, v)] = capacity

    def printGraph(self):
        for u in self.vertices:
            for v in self.graph[u]:
                print(f"({u} —> {v}, {self.edges[(u,v)]})", end=' ')
            print()

    def dfs(self, start, end):
        current = [(start, [start])]
        while current:
            state, path = current.pop()

            for next_state in self.graph[state]:
                if next_state == end:
                    yield path+[next_state]
                    continue
                elif next_state in path:  # no more loop
                    continue
                current.append((next_state, path+[next_state]))

    def get_unique_cycles(self):
        # find small cycles
        cycles = [path for node in range(len(self.vertices))
                  for path in self.dfs(node, node)]
        # pop last duplicate vertex
        for c in cycles:
            c.pop()
        cycles = utils.delete_same_cycle(cycles)
        return cycles

    def check_path_enough_capacity(self, path, util):
        for u, v in zip(path, path[1:]):
            if self.edges[(u, v)] < util:
                return False
        return True

    def take_path(self, path, util):
        for u, v in zip(path, path[1:]):
            self.edges[(u, v)] = round(self.edges[(u, v)] - util, 5)
            if self.edges[(u, v)] == 0:
                self.graph[u].remove(v)
                self.edges.pop((u, v), None)
        return

    # type2: check selected cycle satisfy
    def type2_sum(self, cycles, type2_util, type2_edge_constraint):
        # init
        type2_util_left = copy.deepcopy(type2_util)
        capacity_left = copy.deepcopy(self.edges)
        satisfying_cycle_cap = []

        for cycle in cycles:
            max_capacity = utils.find_max_cycle_capacity(cycle, capacity_left)
            cycle_util = collections.defaultdict(float)

            for src_des_tuple, util in type2_util_left.items():
                src_vertex, des_vertex = src_des_tuple
                if src_vertex not in cycle or des_vertex not in cycle:
                    continue
                if util == 0:
                    continue

                # find a path on a cycle to serve the (src_vertex, des_vertex) pair
                src_indices = np.where(np.array(cycle) == src_vertex)[0]
                des_indices = np.where(np.array(cycle) == des_vertex)[0]

                d = des_indices - src_indices[:, np.newaxis]
                d[d < 0] += len(cycle)  # d : edge difference
                # 2d arg sort
                row, col = np.unravel_index(np.argsort(d, axis=None), d.shape)

                for r, c in zip(row, col):
                    if d[r][c] > type2_edge_constraint[(src_vertex, des_vertex)]:
                        break

                    src_index = src_indices[r]
                    des_index = des_indices[c]

                    # check enough
                    if src_index < des_index:
                        enough = True
                        for u, v in zip(cycle[src_index:des_index], cycle[src_index+1:des_index+1]):
                            if cycle_util[(u, v)] + util > max_capacity:
                                enough = False

                        if enough == True:
                            for u, v in zip(cycle[src_index:des_index], cycle[src_index+1:des_index+1]):
                                cycle_util[(u, v)] += util
                            type2_util_left[(src_vertex, des_vertex)] = 0
                    else:
                        enough = True
                        for u, v in zip(cycle[src_index:]+cycle[:des_index], cycle[src_index+1:]+cycle[:des_index+1]):
                            if cycle_util[(u, v)] + util > max_capacity:
                                enough = False

                        if enough == True:
                            for u, v in zip(cycle[src_index:]+cycle[:des_index], cycle[src_index+1:]+cycle[:des_index+1]):
                                cycle_util[(u, v)] += util
                            type2_util_left[(src_vertex, des_vertex)] = 0

            if len(cycle_util.values()) == 0:
                # no route on this cycle
                return None

            # assign util = cycle_util.max() to this cycle
            for u, v in zip(cycle, cycle[1:] + cycle[:1]):
                capacity_left[(u, v)] = round(
                    capacity_left[(u, v)]-max(cycle_util.values()), 5)
            satisfying_cycle_cap.append((cycle, max(cycle_util.values())))

        if (np.array(list(type2_util_left.values())) == 0).all():
            return satisfying_cycle_cap
        return None

    # type2: selected cycle & max expected
    def type2_max(self, cycles, type2_util, type2_edge_constraint):
        # init
        type2_util_left = copy.deepcopy(type2_util)
        capacity_left = copy.deepcopy(self.edges)
        satisfying_cycle_cap = []

        for cycle in cycles:
            max_capacity = utils.find_max_cycle_capacity(cycle, capacity_left)
            cycle_util = collections.defaultdict(float)

            for src_des_tuple, util in type2_util_left.items():
                src_vertex, des_vertex = src_des_tuple
                if src_vertex not in cycle or des_vertex not in cycle:
                    continue
                if util == 0:
                    continue

                # find a path on a cycle to serve the (src_vertex, des_vertex) pair
                src_indices = np.where(np.array(cycle) == src_vertex)[0]
                des_indices = np.where(np.array(cycle) == des_vertex)[0]

                d = des_indices - src_indices[:, np.newaxis]
                d[d < 0] += len(cycle)  # d : edge difference
                # 2d arg sort
                row, col = np.unravel_index(np.argsort(d, axis=None), d.shape)

                for r, c in zip(row, col):
                    if d[r][c] > type2_edge_constraint[(src_vertex, des_vertex)]:
                        break

                    src_index = src_indices[r]
                    des_index = des_indices[c]

                    # check enough
                    if util > max_capacity:
                        continue

                    if src_index < des_index:
                        for u, v in zip(cycle[src_index:des_index], cycle[src_index+1:des_index+1]):
                            if cycle_util[(u, v)] < util:
                                cycle_util[(u, v)] = util
                        type2_util_left[(src_vertex, des_vertex)] = 0
                    else:
                        for u, v in zip(cycle[src_index:]+cycle[:des_index], cycle[src_index+1:]+cycle[:des_index+1]):
                            if cycle_util[(u, v)] < util:
                                cycle_util[(u, v)] = util
                        type2_util_left[(src_vertex, des_vertex)] = 0

            if len(cycle_util.values()) == 0:
                # no route on this cycle
                return None

            # assign util = cycle_util.max() to this cycle
            for u, v in zip(cycle, cycle[1:] + cycle[:1]):
                capacity_left[(u, v)] = round(
                    capacity_left[(u, v)]-max(cycle_util.values()), 5)
            satisfying_cycle_cap.append((cycle, max(cycle_util.values())))

        if (np.array(list(type2_util_left.values())) == 0).all():
            return satisfying_cycle_cap
        return None

    # type2: greedily include a cycle that cover the most # of vertices left in type2_util
    def type2_greedy_cover_most(self, cycles, type2_util, type2_edge_constraint):
        satisfying_routes = []

        type2_util_left = copy.deepcopy(type2_util)
        capacity_left = copy.deepcopy(self.edges)
        satisfying_cycle_cap = []

        while len(cycles) != 0 and any(type2_util_left.values()):
            type2_vertice_set = set().union(
                *[set(vertice_pair) for vertice_pair, util in type2_util_left.items() if util != 0])
            choosed_cycle = cycles[np.argmin([len(type2_vertice_set - set(c))
                                              for c in cycles])]

            # take all possible path (check edge constraint)
            max_capacity = utils.find_max_cycle_capacity(
                choosed_cycle, capacity_left)
            cycle_util = collections.defaultdict(float)

            for src_des_tuple, util in type2_util_left.items():
                src_vertex, des_vertex = src_des_tuple
                if src_vertex not in choosed_cycle or des_vertex not in choosed_cycle:
                    continue
                if util == 0:
                    continue
                src_indices = np.where(
                    np.array(choosed_cycle) == src_vertex)[0]
                des_indices = np.where(
                    np.array(choosed_cycle) == des_vertex)[0]

                d = des_indices - src_indices[:, np.newaxis]
                d[d < 0] += len(choosed_cycle)  # d : edge difference
                # 2d arg sort
                row, col = np.unravel_index(np.argsort(d, axis=None), d.shape)

                for r, c in zip(row, col):
                    if d[r][c] > type2_edge_constraint[(src_vertex, des_vertex)]:
                        break

                    src_index = src_indices[r]
                    des_index = des_indices[c]

                    # check enough
                    if util > max_capacity:
                        continue

                    if src_index < des_index:
                        for u, v in zip(choosed_cycle[src_index:des_index], choosed_cycle[src_index+1:des_index+1]):
                            if cycle_util[(u, v)] < util:
                                cycle_util[(u, v)] = util
                        type2_util_left[(src_vertex, des_vertex)] = 0
                        satisfying_routes.append(
                            (choosed_cycle[src_index:des_index+1], util))
                    else:
                        for u, v in zip(choosed_cycle[src_index:]+choosed_cycle[:des_index], choosed_cycle[src_index+1:]+choosed_cycle[:des_index+1]):
                            if cycle_util[(u, v)] < util:
                                cycle_util[(u, v)] = util
                        type2_util_left[(src_vertex, des_vertex)] = 0
                        satisfying_routes.append((
                            choosed_cycle[src_index:] +
                            choosed_cycle[:des_index+1], util))

            if len(cycle_util.values()) == 0:
                # this cycle cannot help
                cycles.remove(choosed_cycle)
                continue

            # assign util = cycle_util.max() to this cycle
            for u, v in zip(choosed_cycle, choosed_cycle[1:] + choosed_cycle[:1]):
                capacity_left[(u, v)] = round(
                    capacity_left[(u, v)]-max(cycle_util.values()), 5)

            satisfying_cycle_cap.append(
                (choosed_cycle, max(cycle_util.values())))
            cycles.remove(choosed_cycle)

        if any(type2_util_left.values()):
            return None
        return satisfying_cycle_cap, satisfying_routes
