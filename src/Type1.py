import numpy as np


# type1: shortest path
def type1_shortest(graph, type1):
    satisfying_routes = []
    for src_des_tuple, util in type1.items():
        paths = [path for path in graph.dfs(*src_des_tuple)]
        found = False
        for path in paths:
            if graph.check_path_enough_capacity(path, util) == True:
                graph.take_path(path, util)
                satisfying_routes.append((path, util))
                found = True
                break
        if not found:
            raise Exception("Cannot Satisfy all Type 1")
    return satisfying_routes


# type1: least used capacity percentage along the path
def type1_least_used_capacity_percentage(graph, type1):
    satisfying_routes = []
    for src_des_tuple, util in type1.items():
        # find a path for this route: (src, des) util
        paths = [path for path in graph.dfs(*src_des_tuple)]

        min_index = -1
        min_used_percentage = float("inf")
        for i, path in enumerate(paths):
            if graph.check_path_enough_capacity(path, util) == True:
                all_capacity = sum([graph.edges[(u, v)]
                                   for u, v in zip(path, path[1:])])
                used_percentage = util*(len(path)-1)/all_capacity
                if used_percentage < min_used_percentage:
                    min_used_percentage = used_percentage
                    min_index = i

        if min_index == -1:
            # any path cannot serve for the pair
            raise Exception("Cannot Satisfy all Type 1")

        graph.take_path(paths[min_index], util)
        satisfying_routes.append((paths[min_index], util))

    return satisfying_routes


# type1: min of max percentage (util/capacity)
def type1_min_max_percentage(graph, type1):
    satisfying_routes = []
    for src_des_tuple, util in type1.items():
        # find a path for this route: (src, des) util
        paths = [path for path in graph.dfs(*src_des_tuple)]

        min_max_index = -1
        min_max_percentage = float("inf")
        for i, path in enumerate(paths):
            if graph.check_path_enough_capacity(path, util) == True:
                max_percentage = 0
                for u, v in zip(path, path[1:]):
                    if max_percentage < (util/graph.edges[(u, v)]):
                        max_percentage = (util/graph.edges[(u, v)])

                if max_percentage < min_max_percentage:
                    min_max_percentage = max_percentage
                    min_max_index = i

        if min_max_index == -1:
            # any path cannot serve for the pair
            raise Exception("Cannot Satisfy all Type 1")

        graph.take_path(paths[min_max_index], util)
        satisfying_routes.append((paths[min_max_index], util))
    return satisfying_routes


# type1: least conflict with type2
def type1_least_conflict(graph, type1, type2):
    satisfying_routes = []
    for src_des_tuple, util in type1.items():
        paths = [path for path in graph.dfs(*src_des_tuple)]

        conflict = []
        valid_index = []
        for i, path in enumerate(paths):
            if graph.check_path_enough_capacity(path, util) == True:
                valid_index.append(i)

                conflict_value = 0
                for src2, des2 in type2.keys():
                    if src2 not in path or des2 not in path:
                        continue
                    src_indices = np.where(np.array(path) == src2)[0]
                    des_indices = np.where(np.array(path) == des2)[0]

                    max_edge_dist = max(max(des_indices) - min(src_indices), 0)
                    conflict_value += type2[(src2, des2)] * max_edge_dist
                conflict.append(conflict_value)

        if len(valid_index) == 0:
            # any path cannot serve for the pair
            raise Exception("Cannot Satisfy all Type 1")

        path = paths[valid_index[np.argsort(conflict)[0]]]
        graph.take_path(path, util)
        satisfying_routes.append((path, util))

    return satisfying_routes
