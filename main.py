import argparse

from src.Graph import Graph
from src import utils
from src.Type1 import Type1
from src.Type2 import Type2


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

    try:
        # type1: route input
        if args.Type1_method == "least_conflict_value":
            type1_ans = Type1(graph, type1).solution(
                "least_conflict_value", type2_util)
        else:
            type1_ans = Type1(graph, type1).solution("shortest_path")

        # type2: expected input
        type2_cycles, type2_routes = Type2(
            graph, type2_util, type2_edge_constraint).solution("greedy", num_transfer)
        # type2_cycles, type2_routes = Type2(
        #     graph, type2_util, type2_edge_constraint).solution("brute_force", num_transfer)

        print("type1 paths:", type1_ans)
        print("type2 routes:", type2_routes)
        print("type2 cycles:", type2_cycles)

    except Exception as inst:
        # TODO: define exception class for no solution
        print(inst)
        raise

    return


def parse_args():
    parser = argparse.ArgumentParser(description="")
    parser.add_argument("input_file_path")
    parser.add_argument("Type1_method")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    main(args)
