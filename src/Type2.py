import collections
import copy
import itertools
import numpy as np


class Type2():
    def __init__(self, graph, type2):
        self.graph = graph
        self.type2 = type2
        self.solve_method = None
        self.max_sum_method = getattr(self, "max_streams_on_cycle")

    def solution(self, solve_method, max_sum_method, num_transfer, *args):
        pool = self.graph.get_unique_cycles()
        # cycles = utils.generate_transfer_cycle(cycles, num_transfer)

        try:
            self.solve_method = getattr(self, solve_method)
            self.max_sum_method = getattr(self, max_sum_method)

            type2_cycles, type2_routes = self.solve_method(pool, *args)
            return type2_cycles, type2_routes
        except Exception as inst:
            raise inst

    def brute_force(self, pool):
        for num_cycle in range(1, len(pool)):
            comb = itertools.combinations(pool, num_cycle)
            for one_combination in list(comb):
                # check cycles of one combination
                graph = copy.deepcopy(self.graph)
                type2 = copy.deepcopy(self.type2)
                type2_cycles = []
                type2_routes = []

                for c in one_combination:
                    Pi, routes = self.stuff_Type2_on_cycle(graph, type2, c)
                    if len(routes) != 0:
                        type2_cycles.append(Pi)
                        type2_routes.extend(routes)

                if not any(type2.values()):
                    return type2_cycles, type2_routes
        raise Exception("Cannot Satisfy all Type 2")

    def choose_cycle_cover_most(self, pool, type2):
        vertice_left = set().union(*[set((Sx, Dx))
                                     for (Sx, Dx) in type2.keys()])
        return pool[np.argmin([len(vertice_left - set(c))
                               for c in pool])]

    def greedy(self, pool):
        pool = copy.deepcopy(pool)
        graph = copy.deepcopy(self.graph)
        type2 = copy.deepcopy(self.type2)
        type2_cycles = []
        type2_routes = []

        while len(pool) != 0 and any(type2.values()):
            # greed selection method
            c = self.choose_cycle_cover_most(pool, type2)
            Pi, routes = self.stuff_Type2_on_cycle(graph, type2, c)

            if len(routes) != 0:
                type2_cycles.append(Pi)
                type2_routes.extend(routes)

            # if c holds max of which can contain, it cannot holds more
            # if c cannot hold any remainings, neither can it hold any in the future
            pool.remove(c)

        if any(type2.values()):
            raise Exception("Cannot Satisfy all Type 2")
        return type2_cycles, type2_routes

    # ================================================================
    # =============== Stuff Type2 streams on cycles ==================
    # ================================================================

    def stuff_Type2_on_cycle(self, graph, type2, c):
        cycle_util = collections.defaultdict(float)  # edge along the cycle
        max_capacity = graph.find_max_cycle_capacity(c)
        routes = []  # output for each pair Type 2

        for sigmax in list(type2.items()):
            (Sx, Dx), (Ux, dx) = sigmax
            if Sx not in c or Dx not in c or Ux == 0:
                continue

            # find a path for this stream and take path
            path = self.max_sum_method(c, max_capacity, cycle_util, sigmax)
            if path != None:
                type2.pop((Sx, Dx))
                routes.append((path, Ux))

        # no Type2 assigned
        if len(cycle_util.values()) == 0:
            return (c, 0), routes
        # assign util = max(cycle_util.values()) to this cycle
        graph.take_path(c + [c[0]], max(cycle_util.values()))
        return (c, max(cycle_util.values())), routes

    def sum_streams_on_cycle(self, c, max_capacity, cycle_util, sigmax):
        # find a path for this stream
        (Sx, Dx), (Ux, dx) = sigmax
        Sx_indices = np.where(np.array(c) == Sx)[0]
        Dx_indices = np.where(np.array(c) == Dx)[0]
        d = Dx_indices - Sx_indices[:, np.newaxis]  # d : edge difference
        d[d < 0] += len(c)
        rows, cols = np.unravel_index(np.argsort(d, axis=None), d.shape)
        for row, col in zip(rows, cols):
            if d[row][col] > dx:
                return None

            Sx_idx = Sx_indices[row]
            Dx_idx = Dx_indices[col]
            path = c[Sx_idx:Dx_idx +
                     1] if Sx_idx < Dx_idx else c[Sx_idx:]+c[:Dx_idx+1]

            # check enough
            enough = True
            for u, v in zip(path, path[1:]):
                if max_capacity < cycle_util[(u, v)] + Ux:
                    enough = False
                    break

            if enough == True:
                # take path on cycle
                if path != None:
                    for u, v in zip(path, path[1:]):
                        cycle_util[(u, v)] += Ux
                return path
        return None

    def max_streams_on_cycle(self, c, max_capacity, cycle_util, sigmax):
        # find a path for this stream
        (Sx, Dx), (Ux, dx) = sigmax
        if max_capacity < Ux:
            return None

        Sx_indices = np.where(np.array(c) == Sx)[0]
        Dx_indices = np.where(np.array(c) == Dx)[0]
        d = Dx_indices - Sx_indices[:, np.newaxis]
        d[d < 0] += len(c)
        row, col = np.unravel_index(d.argmin(), d.shape)

        # smallest edge difference > edge constrain
        if d[row][col] > dx:
            return None

        # solution path
        Sx_idx = Sx_indices[row]
        Dx_idx = Dx_indices[col]
        path = c[Sx_idx:Dx_idx +
                 1] if Sx_idx < Dx_idx else c[Sx_idx:]+c[: Dx_idx+1]

        # take path on cycle
        if path != None:
            for u, v in zip(path, path[1:]):
                cycle_util[(u, v)] = max(cycle_util[(u, v)], Ux)
        return path

    def big_cycle_and_small_from_src(self):

        graph = copy.deepcopy(self.graph)
        type2 = copy.deepcopy(self.type2)
        type2_cycles = []
        type2_routes = []

        # bigs = self.graph.get_big_cycles()
        big = None
        for path in self.graph.bfs(0, 0):
            if len(path) == len(self.graph.vertices):
                big = path
                break

        if big != None:
            Pi, routes = self.stuff_Type2_on_cycle(graph, type2, c)
            if len(routes) != 0:
                type2_cycles.append(Pi)
                type2_routes.extend(routes)

        for sigmax in list(type2.items()):
            (Sx, Dx), (Ux, dx) = sigmax
            if Sx not in c or Dx not in c or Ux == 0:
                continue

            cycles = [path for path in self.graph.bfs(Sx, Sx)]

            while len(cycles) != 0 and any(type2.values()):
                # greed selection method
                c = self.choose_cycle_cover_most(cycles, type2)
                Pi, routes = self.stuff_Type2_on_cycle(graph, type2, c)

                if len(routes) != 0:
                    type2_cycles.append(Pi)
                    type2_routes.extend(routes)

                # if c holds max of which can contain, it cannot holds more
                # if c cannot hold any remainings, neither can it hold any in the future
                cycles.remove(c)

        if any(type2.values()):
            print("type2 left:", type2)
            raise Exception("Cannot Satisfy all Type 2")
        return type2_cycles, type2_routes

    # Further thoughts
    # hamiliton path / spanning tree
