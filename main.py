import argparse

from src import utils
from src.Type1 import Type1
from src.Type2 import Type2


def main(args):
    graph, type1, type2, num_transfer = utils.parse_input_file(
        args.input_file_path)

    # # Type1
    # try:
    #     arguments = [args.Type1_method]
    #     if args.Type1_method == "least_conflict_value":
    #         arguments.append(type2)

    #     type1_ans = Type1(graph, type1).solution(*arguments)

    # except Exception as i:
    #     print(i)
    #     exit(1)

    # print("find type1")
    # print("type1 paths:", type1_ans)
    # Type2: expected input
    # try:
    #     # type2_cycles, type2_routes = Type2(
    #     #     graph, type2).solution("greedy", "max_streams_on_cycle", num_transfer)

    #     type2_cycles, type2_routes = Type2(
    #         graph, type2).big_cycle_and_small_from_src()

    # except Exception as i:
    #     print(i)
    #     exit(2)
    #Type2(graph, type2).dfs_color_cycle_constant()

    # # output answer
    # print(args.Type1_method)
    # print("type1 paths:", type1_ans)
    # print("type2 routes:", type2_routes)
    # print("type2 cycles:", type2_cycles)

    return 0


def parse_args():
    parser = argparse.ArgumentParser(description="")
    parser.add_argument("input_file_path")
    parser.add_argument("Type1_method")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    main(args)
