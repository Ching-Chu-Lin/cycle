from hashlib import new
import pickle
import sys

INF = 9999


class Graph:
    def __init__(self, num_of_vertice):
        self.num_of_vertice = num_of_vertice
        self.adj_list = {}  # key : (n, c), value : [(n, c), cost]
        self.index_map = {}  # key : (n, c), value : index
        self.count = [0] * self.num_of_vertice
        self.vertex_count = 0
        self.dist = []

        self.edge_over = False  # control
        self.dist_over = False  # control
        self.min_cost_over = False  # control

    def addEdge(self, n1, n2, cost, c1, c2):  # add an edge from n1 to n2
        # print("{} {} {} {}".format(n1, c1, n2, c2))
        if (n1, c1) not in self.adj_list:
            self.adj_list[(n1, c1)] = [[(n2, c2), cost]]
        else:
            self.adj_list[(n1, c1)].append([(n2, c2), cost])

        if (n1, c1) not in self.index_map:
            self.vertex_count += 1
            self.index_map[(n1, c1)] = self.vertex_count

        if (n2, c2) not in self.index_map:
            self.vertex_count += 1
            self.index_map[(n2, c2)] = self.vertex_count

    # call this function only after all edges had been added to the graph
    def constructDistArray(self):
        if not self.edge_over:
            return
        self.dist = [[INF for x in range(self.vertex_count+1)]
                     for y in range(self.vertex_count+1)]

        for key in self.adj_list:  # key : (n,c)
            v_from = self.index_map[key]
            for val in self.adj_list[key]:  # val : [(n, c), cost]
                v_to = self.index_map[val[0]]
                # print("from {}:{} to {}:{}, cost = {}".format(key, v_from, val[0], v_to, val[1]))
                self.dist[v_from][v_to] = val[1]
                self.dist[v_from][v_from] = 0.0
                self.dist[v_to][v_to] = 0.0
        self.dist_over = True

    def allPairShortestPath(self):
        if not self.dist_over:
            return
        # Floyd Warshall DP Algorithm
        for k in range(self.vertex_count+1):
            for i in range(self.vertex_count+1):
                for j in range(self.vertex_count+1):
                    self.dist[i][j] = min(
                        self.dist[i][j], self.dist[i][k] + self.dist[k][j])
            print("[shortest path] k = ", k)
        self.min_cost_over = True
        print("[All pair shortest path complete]")

    def getPairMinCost(self, from_vertex, to_vertex):
        min_cost = INF
        for i in range(self.count[from_vertex]):

            from_index = self.index_map[(from_vertex, i)]
            for j in range(self.count[to_vertex]):
                # print("[get] dist[{}][{}] = {}".format(from_index, to_index))
                to_index = self.index_map[(to_vertex, j)]
                min_cost = min(min_cost, self.dist[from_index][to_index])
        return min_cost


'''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
'                                                               '
'   Input       :   cycle_List                                  '        
'   Type        :   2D list,                                    '
'   Discription :   Each element of cycle_list is a             '
'                   list of vertice in order in a cycle.        '
'                                                               '
'''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''


def reconstructGraph(num_of_vertice, cycle_list, normal_cost, transfer_cost):
    new_graph = Graph(num_of_vertice)

    for cycle in cycle_list:
        for i in range(len(cycle)-1):
            new_graph.addEdge(cycle[i], cycle[i+1], normal_cost,
                              new_graph.count[cycle[i]], new_graph.count[cycle[i+1]])
            new_graph.count[cycle[i]] += 1
        new_graph.addEdge(cycle[-1], cycle[0], normal_cost,
                          new_graph.count[cycle[-1]], new_graph.count[cycle[0]])
        new_graph.count[cycle[-1]] += 1

    # complete subgraph for transfer
    for i in range(num_of_vertice):
        for j in range(new_graph.count[i]):
            for k in range(new_graph.count[i]):
                if j != k:
                    new_graph.addEdge(i, i, transfer_cost, j, k)
    new_graph.edge_over = True
    return new_graph


if __name__ == "__main__":
    V = int(sys.argv[1])
    originalGrpahFile = sys.argv[2]

    with open(originalGrpahFile, 'rb') as f:
        cycle_list = pickle.load(f)
        # print("[cycle list]\n", cycle_list)
        g = reconstructGraph(V, cycle_list, 0.5, 10)
        g.constructDistArray()
        # print(g.count)
        # print("dist[180][181] = ", g.dist[180][181])
        # print("[test] ", g.getPairMinCost(9, 17))
        print(g.count)
        print(g.vertex_count)
        g.allPairShortestPath()

        count = 0
        sum = 0.0
        for v in range(g.num_of_vertice):
            for u in range(g.num_of_vertice):
                if v != u:
                    c = g.getPairMinCost(v, u)
                    # print("Min cost from {} to {} = {}".format(v, u, c))
                    count += 1
                    sum += c
        print("Avarage distance between two vertice is ", sum / count)
