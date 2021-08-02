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

    # type1: shortest path
    def type1_shortest(self, type1):
        satisfying_routes = []
        for src_des_tuple, util in type1.items():
            # find a path for this route: (src, des) util
            paths = [path for path in self.dfs(*src_des_tuple)]

            for path in paths:
                if self.check_path_enough_capacity(path, util) == True:
                    self.take_path(path, util)
                    satisfying_routes.append((path, util))
                    break

        if len(satisfying_routes) == len(type1.keys()):
            return satisfying_routes
        return None

    # type1: least used capacity percentage
    def type1_least_used_capacity_percentage(self, type1):
        satisfying_routes = []
        for src_des_tuple, util in type1.items():
            # find a path for this route: (src, des) util
            paths = [path for path in self.dfs(*src_des_tuple)]

            min_index = -1
            min_used_percentage = float("inf")
            for i, path in enumerate(paths):
                if self.check_path_enough_capacity(path, util) == True:
                    all_capacity = 0
                    for u, v in zip(path, path[1:]):
                        all_capacity += self.edges[(u, v)]
                    used_percentage = util*(len(path)-1)/all_capacity
                    if used_percentage < min_used_percentage:
                        min_used_percentage = used_percentage
                        min_index = i

            # cannot serve
            if min_index == -1:
                break
            self.take_path(paths[min_index], util)
            satisfying_routes.append((paths[min_index], util))

        if len(satisfying_routes) == len(type1.keys()):
            return satisfying_routes
        return None

    # type1: min of max percentage (util/capacity)
    def type1_min_max_percentage(self, type1):
        satisfying_routes = []
        for src_des_tuple, util in type1.items():
            # find a path for this route: (src, des) util
            paths = [path for path in self.dfs(*src_des_tuple)]

            min_max_index = -1
            min_max_percentage = float("inf")
            for i, path in enumerate(paths):
                if self.check_path_enough_capacity(path, util) == True:
                    max_percentage = 0
                    for u, v in zip(path, path[1:]):
                        if max_percentage < (util/self.edges[(u, v)]):
                            max_percentage = (util/self.edges[(u, v)])

                    if max_percentage < min_max_percentage:
                        min_max_percentage = max_percentage
                        min_max_index = i

            # cannot serve
            if min_max_index == -1:
                break
            self.take_path(paths[min_max_index], util)
            satisfying_routes.append((paths[min_max_index], util))

        if len(satisfying_routes) == len(type1.keys()):
            return satisfying_routes
        return None

    # type1: least conflict with type2
    def type1_least_conflict(self, type1, type2):
        satisfying_routes = []
        for src_des_tuple, util in type1.items():
            # find a path for this route: (src, des) util
            paths = [path for path in self.dfs(*src_des_tuple)]

            conflict = []
            valid_index = []
            for i, path in enumerate(paths):
                if self.check_path_enough_capacity(path, util) == True:
                    valid_index.append(i)
                    # calculate conflict value
                    c = 0
                    for src_des_tuple2, util2 in type2.items():
                        src_vertex2, des_vertex2 = src_des_tuple2
                        if src_vertex2 not in path or des_vertex2 not in path:
                            continue
                        src_indices = np.where(
                            np.array(path) == src_vertex2)[0]
                        des_indices = np.where(
                            np.array(path) == des_vertex2)[0]

                        max_edge_difference = max(
                            des_indices) - min(src_indices)
                        max_edge_difference = max(max_edge_difference, 0)
                        c += util2 * max_edge_difference
                    conflict.append(c)

            # cannot serve
            if len(valid_index) == 0:
                break
            path = paths[valid_index[np.argsort(conflict)[0]]]
            self.take_path(path, util)
            satisfying_routes.append((path, util))

        if len(satisfying_routes) == len(type1.keys()):
            return satisfying_routes
        return None

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
