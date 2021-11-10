import collections
import copy
import itertools
import numpy as np


from . import utils


class Type2():
    def __init__(self, graph, type2_util, type2_edge_constraint):
        self.graph = graph
        self.type2_util = type2_util
        self.type2_edge_constraint = type2_edge_constraint

    def solution(self, solve_method, num_transfer, *args):
        cycles = self.graph.get_unique_cycles()
        cycles = utils.generate_transfer_cycle(cycles, num_transfer)

        # TODO: cycle tuple from original -> merged ?
        # no need to consider (1,) and (1,6)
        # lst = [{1, 2, 3}, {1, 4}, {1, 2, 3}]
        # print(lst[0].intersection(*lst))

        f = getattr(self, solve_method)
        type2_cycles, type2_routes = f(cycles, *args)
        # TODO: type2 none throw exception: raise Exception("Cannot Satisfy all Type 1")
        return type2_cycles, type2_routes

    def sum_streams_on_cycle(self, graph, type2_util, c):
        routes = []
        cycle_util = collections.defaultdict(float)
        max_capacity = utils.find_max_cycle_capacity(c, graph.capacity)

        for (Sx, Dx), Ux in type2_util.items():
            if Sx not in c or Dx not in c:
                continue
            if Ux == 0:
                continue

            Sx_indices = np.where(np.array(c) == Sx)[0]
            Dx_indices = np.where(np.array(c) == Dx)[0]
            # d : edge difference
            d = Dx_indices - Sx_indices[:, np.newaxis]
            d[d < 0] += len(c)
            rows, cols = np.unravel_index(np.argsort(d, axis=None), d.shape)

            for row, col in zip(rows, cols):
                if d[row][col] > self.type2_edge_constraint[(Sx, Dx)]:
                    break

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

                # take path on cycle
                if enough == True:
                    for u, v in zip(path, path[1:]):
                        cycle_util[(u, v)] += Ux
                    type2_util[(Sx, Dx)] = 0
                    routes.append((path, Ux))
                    break

        if len(cycle_util.values()) == 0:
            return (c, 0), routes

        # assign util = cycle_util.max() to this cycle
        for u, v in zip(c, c[1:] + c[:1]):
            graph.capacity[(u, v)] = round(
                graph.capacity[(u, v)]-max(cycle_util.values()), 1)

        return (c, max(cycle_util.values())), routes

    def max_streams_on_cycle(self, graph, type2_util, c):
        routes = []
        cycle_util = collections.defaultdict(float)
        max_capacity = utils.find_max_cycle_capacity(c, graph.capacity)

        for (Sx, Dx), Ux in type2_util.items():
            if Sx not in c or Dx not in c:
                continue
            if Ux == 0 or max_capacity < Ux:
                continue

            # check edge constraint d : edge difference
            Sx_indices = np.where(np.array(c) == Sx)[0]
            Dx_indices = np.where(np.array(c) == Dx)[0]

            d = Dx_indices - Sx_indices[:, np.newaxis]
            d[d < 0] += len(c)
            row, col = np.unravel_index(d.argmin(), d.shape)
            if d[row][col] > self.type2_edge_constraint[(Sx, Dx)]:
                # smallest edge difference > edge constrain
                continue

            # solution path
            Sx_idx = Sx_indices[row]
            Dx_idx = Dx_indices[col]
            path = c[Sx_idx:Dx_idx +
                     1] if Sx_idx < Dx_idx else c[Sx_idx:]+c[: Dx_idx+1]

            # take path on cycle
            for u, v in zip(path, path[1:]):
                cycle_util[(u, v)] = max(cycle_util[(u, v)], Ux)
            type2_util[(Sx, Dx)] = 0
            routes.append((path, Ux))

        if len(cycle_util.values()) == 0:
            return (c, 0), routes

        # assign util = cycle_util.max() to this cycle
        for u, v in zip(c, c[1:] + c[: 1]):
            graph.capacity[(u, v)] = round(
                graph.capacity[(u, v)]-max(cycle_util.values()), 1)
        return (c, max(cycle_util.values())), routes

    def brute_force(self, cycles):
        for num_cycle in range(1, len(cycles)):
            comb = itertools.combinations(cycles, num_cycle)
            for one_combination in list(comb):
                # check cycles of one combination
                type2_cycles = []
                type2_routes = []
                graph = copy.deepcopy(self.graph)
                type2_util = copy.deepcopy(self.type2_util)

                for c in one_combination:
                    # TODO: sum stream to upper layer
                    Pi, routes = self.max_streams_on_cycle(
                        graph, type2_util, c)

                    if len(routes) != 0:
                        type2_cycles.append(Pi)
                        type2_routes.extend(routes)

                if not any(type2_util.values()):
                    return type2_cycles, type2_routes
        return None, None

    # ======================================================================
    # ========================= greedy =====================================
    # ======================================================================

    def choose_cycle_cover_most(self, pool, type2_util):
        vertice_left = set().union(
            *[set((Sx, Dx)) for (Sx, Dx), Ux in type2_util.items() if Ux != 0])
        return pool[np.argmin([len(vertice_left - set(c))
                               for c in pool])]

    def greedy(self, pool):
        pool = copy.deepcopy(pool)

        type2_cycles = []
        type2_routes = []
        graph = copy.deepcopy(self.graph)
        type2_util = copy.deepcopy(self.type2_util)

        while len(pool) != 0 and any(type2_util.values()):
            # greed selection method
            c = self.choose_cycle_cover_most(pool, type2_util)

            Pi, routes = self.sum_streams_on_cycle(graph, type2_util, c)

            if len(routes) != 0:
                type2_cycles.append(Pi)
                type2_routes.extend(routes)

            # if c holds max of which can contain, it cannot holds more
            # if c cannot hold any remainings, neither can it hold any in the future
            pool.remove(c)

        if any(type2_util.values()):
            return None, None
        return type2_cycles, type2_routes
