import argparse
import itertools
import math
import numpy as np
import random


def parse_args():
    parser = argparse.ArgumentParser(description="")
    parser.add_argument("output_file_path")
    return parser.parse_args()


def generate_graph(output_file):
    # generate vertices
    num_vertex = random.randrange(3, 10)
    num_vertex = 10
    print(num_vertex, file=output_file)

    # generate edge of each vertex
    for vertex in range(num_vertex):
        print(vertex, file=output_file, end=",")
        num_edges = random.randrange(1, num_vertex)

        outneighbor_pool = list(range(num_vertex))
        outneighbor_pool.remove(vertex)  # no edge to itself
        # sample: no repetition
        neighbors = sorted(random.sample(outneighbor_pool, num_edges))
        util = [1 for _ in range(len(neighbors))]

        for v, u in zip(neighbors, util):
            print("{} {}".format(v, u), file=output_file, end=" ")
        print("", file=output_file)

    return num_vertex


def generate_type1(num_vertex, output_file):
    M = random.randrange(1, math.perm(num_vertex, 2))
    M = 2
    print(M, file=output_file)

    pair = list(itertools.permutations(range(num_vertex), 2))

    src_des_tuples = sorted(random.sample(pair, k=M))
    util = [round(random.uniform(0.001, 0.005), 4)for _ in range(M)]
    for src_des, u in zip(src_des_tuples, util):
        src, des = src_des
        print("{} {} {}".format(src, des, u), file=output_file)

    return


def generate_type2(num_vertex, output_file):
    N = random.randrange(1, math.perm(num_vertex, 2))
    N = 50
    print(N, file=output_file)

    pair = list(itertools.permutations(range(num_vertex), 2))
    # edge constraint (5, V+1)
    edge_constraint_pool = list(range(5, num_vertex+1))

    src_des_tuples = sorted(random.sample(pair, k=N))
    util = [round(random.uniform(0.001, 0.005), 4)for _ in range(N)]
    edge_constraint = random.choices(edge_constraint_pool, k=N)

    for src_des, u, c in zip(src_des_tuples, util, edge_constraint):
        src, des = src_des
        print("{} {} {} {}".format(src, des, u, c,), file=output_file)

    return


def main(args):
    with open(args.output_file_path, "w") as output_file:
        num_vertex = generate_graph(output_file)

        generate_type1(num_vertex, output_file)
        generate_type2(num_vertex, output_file)

        # generate constraint 2: max number of transfer
        num_transfer = random.randrange(3)
        print(num_transfer, file=output_file)

    return


if __name__ == "__main__":
    # random.seed(0)
    args = parse_args()
    main(args)
