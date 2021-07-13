import argparse
import collections
import copy
import itertools
import numpy as np
import dijkstar

from Graph import Graph


def parse_input_file(input_file_path):
    with open(input_file_path) as input_file:
        # parse number of vertex
        num_vertex = int(input_file.readline().strip())

        # parse graph
        graph = Graph(num_vertex)
        for i in range(num_vertex):
            start_vertex, neighbor_util = input_file.readline().strip().split(",")
            neighbor_util = neighbor_util.split(" ")
            for end_vertex, util in zip(neighbor_util[0::2], neighbor_util[1::2]):
                graph.add_edge(int(start_vertex), int(end_vertex), float(util))

        # parse input to be routed: type1
        M = int(input_file.readline().strip())
        type1 = {}
        for _ in range(M):
            src, des, util = input_file.readline().strip().split(" ")
            type1[int(src), int(des)] = float(util)

        # parse expected utilizations: type2 + edge upper bound constraint
        N = int(input_file.readline().strip())
        type2_util = {}
        type2_edge_constraint = {}
        for _ in range(N):
            src, des, util, edge_constraint = input_file.readline().strip().split(" ")
            type2_util[int(src), int(des)] = float(util)
            type2_edge_constraint[int(src), int(des)] = int(edge_constraint)

        # parse constraint 2: max number of transfer
        num_transfer = int(input_file.readline().strip())

        return graph, type1, type2_util, type2_edge_constraint, num_transfer


def calculate_distance_in_cycle(graph, cycle):
    # init distance
    num_vertex = len(graph)
    cycle_distance = np.full((num_vertex, num_vertex), np.inf)

    np_cycle = np.array(cycle)

    for start in graph:
        for end in graph:
            start_indices = np.where(np_cycle == start)[0]
            end_indices = np.where(np_cycle == end)[0]

            if start_indices.shape == (0,) or end_indices.shape == (0,):
                # start_index / end_index not in cycle
                continue

            d = end_indices - start_indices[:, np.newaxis]
            d[d < 0] += len(np_cycle)
            cycle_distance[start][end] = d.min()

    return cycle_distance


def merge_two_cycles(cycle1, cycle2):
    if cycle1 == cycle2:
        return
    if len(set(cycle1) & set(cycle2)) == 0:
        # no transfer
        return

    m = []
    for transfer_vertex in list(set(cycle1) & set(cycle2)):

        # cut cycle2 at intersection
        for i in list(np.where(np.array(cycle2) == transfer_vertex)[0]):
            # no need add intersection
            cut_cycle2 = cycle2[i:] + cycle2[:i]

            # cut cycle1 at intersection
            for j in list(np.where(np.array(cycle1) == transfer_vertex)[0]):
                new_cycle = copy.deepcopy(cycle1)
                new_cycle[j:j] = cut_cycle2
                # pop one intersection
                # a = [0, 1, 2]
                # b = [4, 5, 6]
                # a[0:0] = b
                # print(a) #[4, 5, 6, 0, 1, 2]

                m.append(new_cycle)

    # delete same cycle
    for c in m:
        for shift in range(1, len(c)):
            same_cycle = collections.deque(c)
            same_cycle.rotate(shift)
            same_cycle = list(same_cycle)
            if same_cycle in m:
                m.remove(same_cycle)
    return m


def generate_transfer_cycle(cycles, num_transfer):
    original_cycles = copy.deepcopy(cycles)

    # init
    to_be_merged = copy.deepcopy(cycles)

    for _ in range(num_transfer):  # transfer : merge = 1 : 1
        # merge cycles
        merged_cycles = []
        for cycle1 in to_be_merged:
            for cycle2 in original_cycles:
                m = merge_two_cycles(cycle1, cycle2)

                if m != None:
                    merged_cycles.extend(m)

        # delete same cycle
        for c in merged_cycles:
            for shift in range(1, len(c)):
                same_cycle = collections.deque(c)
                same_cycle.rotate(shift)
                same_cycle = list(same_cycle)
                if same_cycle in merged_cycles:
                    merged_cycles.remove(same_cycle)

        cycles.extend(merged_cycles)
        to_be_merged = merged_cycles

    # delete same cycle
    for c in cycles:
        for shift in range(1, len(c)):
            same_cycle = collections.deque(c)
            same_cycle.rotate(shift)
            same_cycle = list(same_cycle)
            if same_cycle in cycles:
                cycles.remove(same_cycle)

    return cycles


def main(args):
    graph, type1, type2_util, type2_edge_constraint, num_transfer = parse_input_file(
        args.input_file_path)

    # type1: route input shortest path ( can satisfy )
    type1_ans = graph.type1_shortest(type1)
    if type1_ans == None:
        print("Cannot Satisfy all Type 1.")
        exit(1)

    cycles = graph.get_unique_cycles()
    print("cycles:", cycles)

    # add transfer cycles: merging cycles
    print("add transfer cycles")
    generate_transfer_cycle(cycles, num_transfer)
    print("cycles:", cycles)

    type2_cycles = []
    for num_cycle in range(1, len(cycles)):
        if len(type2_cycles) != 0:  # find ans for type 2
            break
        comb = itertools.combinations(cycles, num_cycle)

        for one_combination in list(comb):
            # no need to consider (1,) and (1,6)
            # but check tuple disjoint? No (2, 3) and (3, 7)
            # max len tuple contains others: max(map(len,tup)) ?
            #lst = [{1, 2, 3}, {1, 4}, {1, 2, 3}]
            # print(lst[0].intersection(*lst))

            type2_ans = graph.type2_check_satisfy(
                one_combination, type2_util, type2_edge_constraint)

            if type2_ans == None:
                continue

            type2_cycles.append(type2_ans)

    print("type1 paths:", type1_ans)
    print("type2 cycles:", type2_cycles)
    return


def parse_args():
    parser = argparse.ArgumentParser(description="")
    parser.add_argument("input_file_path")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    main(args)
