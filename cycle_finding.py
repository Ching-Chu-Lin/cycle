import argparse
import collections
import matplotlib.pyplot as plt
import os
import pickle

from src import utils


def dfs_color_cycle_constant(graph, filepath):
    count_cycle = 0
    sum_length = 0
    coverage = set()
    length_frequency = collections.defaultdict(int)

    has_cycle = True
    constant_capacity = 0.5
    start_node = 0
    cycles_pickle = []

    while(has_cycle):
        find = False
        for node in range(start_node, len(graph.vertices)):
            # copy from get_unique_cycle (bfs vs. dfs)
            for c in graph.dfs(node, node):
                # no need to pop last duplicate vertex
                # remove constant capacity
                if graph.check_path_enough_capacity(c, constant_capacity):
                    graph.take_path(c, constant_capacity)

                    count_cycle += 1
                    sum_length += len(c)
                    coverage.update(c)
                    length_frequency[len(c)] += 1

                    # self.graph.printGraph()
                    print("c:", c)
                    print("# of cycles:", count_cycle)
                    print("avg len of cycles:", sum_length / count_cycle)
                    print("coverage:", coverage, "size:", len(coverage))

                    # visualize
                    graph.visualizeCycle(filepath+"/"+str(count_cycle), c)

                    # save pickle for cal avg. dist
                    c.pop()
                    cycles_pickle.append(c)
                    with open(filepath+'.pickle', 'wb') as p:
                        pickle.dump(cycles_pickle, p,
                                    protocol=pickle.HIGHEST_PROTOCOL)

                    # dfs from this node again since edges may change
                    start_node = node
                    find = True
                    break

            if find:
                break
        if not find:
            has_cycle = False

    graph.printGraph()
    plt.bar(list(length_frequency.keys()), length_frequency.values())
    plt.savefig(filepath+"/frequency")


def main(args):
    graph, _, _, _ = utils.parse_input_file(args.input_file_path)

    filepath = args.input_file_path.split("/")[-1].split(".")[0]
    if not os.path.exists(filepath):
        os.makedirs(filepath)
    dfs_color_cycle_constant(graph, filepath)
    return


def parse_args():
    parser = argparse.ArgumentParser(description="")
    parser.add_argument("input_file_path")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    main(args)
