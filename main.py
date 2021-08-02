import argparse
import collections
import copy
import itertools
import numpy as np
import dijkstar

from src.Graph import Graph
from src import utils


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


def main(args):
    graph, type1, type2_util, type2_edge_constraint, num_transfer = parse_input_file(
        args.input_file_path)

    # type1: route input
    #type1_ans = graph.type1_shortest(type1)
    type1_ans = graph.type1_least_conflict(type1, type2_util)
    if type1_ans == None:
        print("Cannot Satisfy all Type 1.")
        exit(1)

    print("type1_ans:", type1_ans)
    cycles = graph.get_unique_cycles()
    print("cycles:", cycles)
    # add transfer cycles: merging cycles
    cycles = utils.generate_transfer_cycle(cycles, num_transfer)
    print("add transfer cycles:", cycles, end="\n\n")

    # type2: expected input
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

            type2_ans = graph.type2_max(
                one_combination, type2_util, type2_edge_constraint)

            if type2_ans == None:
                continue

            type2_cycles.append(type2_ans)

    print("type1 paths:", type1_ans)
    print("# type2 sol:", len(type2_cycles))
    print("type2 cycles:", type2_cycles)
    return


def parse_args():
    parser = argparse.ArgumentParser(description="")
    parser.add_argument("input_file_path")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    main(args)
