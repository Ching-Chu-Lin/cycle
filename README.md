### Program Usage & File Structure

```bash
$ python3 generate_test_case.py <output_file_name>
$ python3 main.py <input_file_name>
$ python3 cycle_finding.py <input_file_name>
```

##### src/Graph.py

1. class deal with reltead to graph / changing graph edge capacity ..
2. cycle visualizaiton

##### src/Type1.py

1. Type1 methods:
   - shortest_path
   - least_used_capacity_percentage
   - min_max_percentage
   - least_conflict_value

##### src/Type2.py

1. Assumptions:
   - sum_streams_on_cycle
   - max_streams_on_cycle (Type2 streams may or may not come at the same time)
2. Type2 methods
   - brute_force
   - greedy
     - choose_cycle_cover_most
   - big_cycle_and_small_from_src
     A big cycle means a cycle that covers all vertices. Then search from the unsatisfied Type2 streams.
3. Further thoughts: hamiliton path / spanning tree / ...

##### src/utils.py

1. functions unrelated to graph
