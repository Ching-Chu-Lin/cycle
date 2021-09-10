import numpy as np


class Type1():
    def __init__(self, graph, type1):
        self.graph = graph
        self.type1 = type1

    def solution(self, select_func_name, *args):
        f = getattr(self, select_func_name)

        type1_ans = []
        for Lambdak in self.type1.items():
            # change select path methods
            (Sk, Dk), Uk = Lambdak
            path = f(Lambdak, *args)
            self.graph.take_path(path, Uk)
            type1_ans.append((path, Uk))
        return type1_ans

    # type1: select path method: shortest path
    def shortest_path(self, Lambdak):
        (Sk, Dk), Uk = Lambdak
        paths = [path for path in self.graph.dfs(Sk, Dk)]
        for path in paths:
            if self.graph.check_path_enough_capacity(path, Uk) == True:
                return path
        raise Exception("Cannot Satisfy all Type 1")

    # type1: select path method: least used capacity percentage along the path
    def least_used_capacity_percentage(self, Lambdak):
        (Sk, Dk), Uk = Lambdak
        paths = [path for path in self.graph.dfs(Sk, Dk)]

        min_index, min_percentage = -1, float("inf")
        for i, path in enumerate(paths):
            if self.graph.check_path_enough_capacity(path, Uk) == True:
                all_capacity = sum([self.graph.edges[(u, v)]
                                    for u, v in zip(path, path[1:])])
                used_percentage = Uk*(len(path)-1)/all_capacity
                if used_percentage < min_percentage:
                    min_percentage = used_percentage
                    min_index = i

        if min_index == -1:
            # no path has enough capacity
            raise Exception("Cannot Satisfy all Type 1")

        return paths[min_index]

    # type1: select path method: min of max percentage (util/capacity)
    def min_max_percentage(self, Lambdak):
        (Sk, Dk), Uk = Lambdak
        paths = [path for path in self.graph.dfs(Sk, Dk)]

        min_max_index, min_max_percentage = -1, float("inf")
        for i, path in enumerate(paths):
            if self.graph.check_path_enough_capacity(path, Uk) == True:
                max_percentage = 0
                for u, v in zip(path, path[1:]):
                    if max_percentage < (Uk/self.graph.edges[(u, v)]):
                        max_percentage = (Uk/self.graph.edges[(u, v)])

                if max_percentage < min_max_percentage:
                    min_max_percentage = max_percentage
                    min_max_index = i

        if min_max_index == -1:
            raise Exception("Cannot Satisfy all Type 1")

        return paths[min_max_index]

    # type1: select path method: least conflict with type2
    def least_conflict_value(self, Lambdak, type2):
        (Sk, Dk), Uk = Lambdak
        paths = [path for path in self.graph.dfs(Sk, Dk)]

        min_index, min_conflict_value = -1, float("inf")
        for i, path in enumerate(paths):
            if self.graph.check_path_enough_capacity(path, Uk) == True:

                conflict_value = 0
                for Sigmax in type2.items():
                    (Sx, Dx), Ux = Sigmax
                    if Sx not in path or Dx not in path:
                        continue
                    src_indices = np.where(np.array(path) == Sx)[0]
                    des_indices = np.where(np.array(path) == Dx)[0]

                    max_edge_dist = max(max(des_indices) - min(src_indices), 0)
                    conflict_value += Ux * max_edge_dist

                if conflict_value < min_conflict_value:
                    conflict_value = min_conflict_value
                    min_index = i

        if min_index == -1:
            raise Exception("Cannot Satisfy all Type 1")

        return paths[min_index]
