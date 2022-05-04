import copy
import numpy as np

from src.Graph import Graph


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

        # parse expected utilizations: type2 (util, edge constraint)
        N = int(input_file.readline().strip())
        type2 = {}
        for _ in range(N):
            src, des, util, edge_constraint = input_file.readline().strip().split(" ")
            type2[int(src), int(des)] = (float(util), int(edge_constraint))

        # parse constraint 2: max number of transfer
        num_transfer = int(input_file.readline().strip())

        # init graph visualization
        graph.initVisualization()

        return graph, type1, type2, num_transfer


def delete_same_cycle(cycles):
    # convert to string
    cycles = ["".join(map(str, c)) for c in cycles]

    # remove dulplicates & rotate
    cycles = sorted((set(cycles)))  # list

    for c in cycles:
        for shift in range(1, len(c)):
            if c[shift:] + c[:shift] in cycles:
                cycles.remove(c[shift:] + c[:shift])

    cycles = [list(map(int, list(c))) for c in cycles]
    return cycles


def merge_two_cycles(cycle1, cycle2):
    if cycle1 == cycle2:
        return []
    if len(set(cycle1) & set(cycle2)) == 0:
        # no transfer
        return []

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

    m = delete_same_cycle(m)
    return m


def generate_transfer_cycle(cycles, num_transfer):
    original_cycles = copy.deepcopy(cycles)

    # init
    to_be_merged = copy.deepcopy(cycles)

    # transfer : merge = 1 : 1
    for _ in range(num_transfer):
        merged_cycles = []
        for cycle1 in to_be_merged:
            for cycle2 in original_cycles:
                merged_cycles.extend(merge_two_cycles(cycle1, cycle2))

        merged_cycles = delete_same_cycle(merged_cycles)
        cycles.extend(merged_cycles)
        to_be_merged = merged_cycles

    cycles = delete_same_cycle(cycles)
    return cycles
