import numpy as np


class Type1():
    def __init__(self, graph, type1):
        self.graph = graph
        self.type1 = type1
        self.select_method = None

    def solution(self, select_method, *args):
        try:
            self.select_method = getattr(self, select_method)

            type1_ans = []
            for lambdak in self.type1.items():
                # change decide path methods
                (Sk, Dk), Uk = lambdak
                path = self.select_method(lambdak, *args)
                self.graph.take_path(path, Uk)
                type1_ans.append((path, Uk))

            return type1_ans
        except Exception:
            raise

    def shortest_path(self, lambdak):
        (Sk, Dk), Uk = lambdak

        for path in self.graph.bfs(Sk, Dk):
            if self.graph.check_path_enough_capacity(path, Uk) == True:
                return path
        raise Exception("Cannot Satisfy all Type 1")

    def least_used_capacity_percentage(self, lambdak):
        (Sk, Dk), Uk = lambdak
        paths = [path for path in self.graph.bfs(Sk, Dk)]

        min_index, min_percentage = -1, float("inf")
        for i, path in enumerate(paths):
            if self.graph.check_path_enough_capacity(path, Uk) == True:
                all_capacity = sum([self.graph.capacity[(u, v)]
                                    for u, v in zip(path, path[1:])])
                used_percentage = Uk*(len(path)-1)/all_capacity
                if used_percentage < min_percentage:
                    min_percentage = used_percentage
                    min_index = i

        if min_index == -1:
            # no path has enough capacity
            raise Exception("Cannot Satisfy all Type 1")

        return paths[min_index]

    def min_max_percentage(self, lambdak):
        (Sk, Dk), Uk = lambdak
        paths = [path for path in self.graph.bfs(Sk, Dk)]

        min_max_index, min_max_percentage = -1, float("inf")
        for i, path in enumerate(paths):
            if self.graph.check_path_enough_capacity(path, Uk) == True:
                max_percentage = 0
                for u, v in zip(path, path[1:]):
                    if max_percentage < (Uk/self.graph.capacity[(u, v)]):
                        max_percentage = (Uk/self.graph.capacity[(u, v)])

                if max_percentage < min_max_percentage:
                    min_max_percentage = max_percentage
                    min_max_index = i

        if min_max_index == -1:
            raise Exception("Cannot Satisfy all Type 1")

        return paths[min_max_index]

    def least_conflict_value(self, lambdak, type2):
        (Sk, Dk), Uk = lambdak
        paths = [path for path in self.graph.bfs(Sk, Dk)]

        min_index, min_conflict_value = -1, float("inf")
        for i, path in enumerate(paths):
            if self.graph.check_path_enough_capacity(path, Uk) == True:

                conflict_value = 0
                for sigmax in type2.items():
                    (Sx, Dx), (Ux, dx) = sigmax
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
