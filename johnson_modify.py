from collections import defaultdict
from copy import copy
import sys
import networkx as nx
import matplotlib.pyplot as plt
import copy
import pickle

total_cycle_length = 0

class Graph:
    def __init__(self, vertices):
        #No. of vertices
        self.V= vertices
         
        # default dictionary to store graph (Adjacency list)
        self.graph = defaultdict(list)
        self.edgeList = []
        self.utilMap = [[0]*vertices for i in range(vertices)]

        self.reduceConstant = 0.5

        ''' below are for circuit finding '''
        self.find_this_round = False
        self.S = 0
        self.stack = []
        self.blocked = [False] * vertices
        self.B = [[] for i in range(vertices)]
        self.count = 0
        self.allCircuits = []
        self.included = [False] * vertices
        ''' end '''
    
    def addEdge(self, u, v, util):
        self.graph[u].append(v)
        self.edgeList.append([u, v])
        self.utilMap[u][v] = util

    #======================================  Below are for circuit finding  ======================================#
    def output(self):
        global total_cycle_length
        # print("[Circuit No.{}]".format(self.count))
        # print("circuit length : {}".format(len(self.stack)))
        self.count += 1
        self.allCircuits.append(copy.deepcopy(self.stack))
        self.allCircuits[-1].append(self.stack[0])

        circuitLen = len(self.stack)
        total_cycle_length += circuitLen

        for i in range(circuitLen):
            print("{} -->".format(self.stack[i]), end="")
            self.included[self.stack[i]] = True
            self.utilMap[self.stack[i]][self.stack[(i+1)%circuitLen]] -= self.reduceConstant
        print(self.stack[0])

    def unblock(self, u):
        self.blocked[u] = False
        while self.B[u]:
            w = self.B[u][-1]
            self.B[u].pop()
            if self.blocked[w] == True:
                self.unblock(w)
        return
        
    def circuit(self, v):
        f = False
        self.stack.append(v)
        self.blocked[v] = True

        for w in self.graph[v]:
            if self.find_this_round:
                return True
            if self.utilMap[v][w] > 0:
                if w == self.S:
                    if self.stack + [self.S] in self.allCircuits:
                        continue
                    self.output()
                    self.find_this_round = True
                    return True
                elif w > self.S and not self.blocked[w] and w not in self.stack:
                    f = self.circuit(w)
        
        if f:
            self.unblock(v)
        else:
            for w in self.graph[v]:
                if v not in self.B[w]:
                    self.B[w].append(v)
        
        self.stack.pop()
        return f


    def circuitFinding(self):
        self.S = 0
        
        while self.S < self.V - 1:
            self.find_this_round = False
            self.stack = []
            for i in range(self.S, self.V):
                self.blocked[i] = False
                self.B[i] = []

            dummy = self.circuit(self.S)
            if not dummy:
                self.S += 1


    #======================================  End of circuit finding  ======================================#

if __name__ == "__main__":
    inputFile = sys.argv[1]
    reduceConst = sys.argv[2]

    with open(inputFile, "r") as input_file:
        num_vertex = int(input_file.readline().strip())
        g = Graph(num_vertex)

        for i in range(num_vertex):
            start_vertex, neighbor_util = input_file.readline().strip().split(",")
            neighbor_util = neighbor_util.split(" ")
            j = 0
            for end_vertex, util in zip(neighbor_util[0::2], neighbor_util[1::2]):
                g.addEdge(int(start_vertex), int(end_vertex), int(util))
        g.circuitFinding()
    

        coverage = 0
        avg_cycle_length = 0

        for x in g.included:
            if x:
                coverage += 1
        avg_cycle_length = total_cycle_length / g.count
        
        print("[number of cycles] {}".format(g.count))
        print("[number of coverage] {}".format(coverage))
        print("[average cycle length] {}".format(avg_cycle_length))

        with open('cycle.pickle', 'wb') as f:
            pickle.dump(g.allCircuits, f)
        
        # All the circuits finded by graph.circuitFinding saved in Graph.allCiruits
        # print(g.allCircuits)