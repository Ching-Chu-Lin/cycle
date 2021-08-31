### Program Usage & File Structure

```bash
$ python3 generate_test_case.py <output_file_name>
$ python3 main.py <input_file_name>
```

utils.py

> unrelated to graph

Graph.py 

> class deal with reltead to graph / changing graph edge capacity ..

Type1.py

Type2.py

### Pseudo Code

```pseudocode
procedure G.find_paths(S, D)
return [path for path in graph.dfs(Sk, Dk)]
會依長度排順序

procedure G.take_path(p, U)
```

#### Type1

##### solution

```pseudocode
procedure type1_shortest_path(f, *args)
		for Lambdak in self.type1.items()
    		// change select path method: f
        path = f(Lambdak, *args)
        self.graph.take_path(path, Uk)
        type1_ans.append((path, Uk))
		end for
		return type1_ans
```

##### Type1: select path method: `shortest_path` 

```pseudocode
procedure shortest_path(Lambdak):
    (Sk, Dk), Uk = Lambdak
		paths = G.find_paths(Sk, Dk)
    for path in paths:
        if path has enough capacity for Lambdak:
            return path
        end if
    end for
    raise Exception("Cannot Satisfy all Type 1")
    end 
```

##### Type1: select path method: `least_used_capacity_percentage` 

$$
\text{used percentage of path $p$}
$$

```pseudocode
procedure least_used_capacity_percentage(Lambdak):
    (Sk, Dk), Uk = Lambdak
   	paths = G.find_paths(Sk, Dk)
   	
    initialize min_index, min_percentage
    for path in paths:
        if path has enough capacity for Lambdak:
            // calculate used percentage of p
            used_percentage = Uk * (# edge of path) / all_capacity
            if used_percentage < min_percentage:
                min_percentage = used_percentage
                set min_index
            end if
        end if
		end for
    if min_index == -1:
        raise Exception("Cannot Satisfy all Type 1")
    end if
    return paths[min_index]
```

##### Type1: select path method: `min_max_percentage` 

```pseudocode
procedure min_max_percentage(Lambdak)
		(Sk, Dk), Uk = Lambdak
   	paths = G.find_paths(Sk, Dk)

    initialize min_max_index, min_max_percentage
    for path in paths:
        if path has enough capacity for Lambdak:
        		// calculate max percentage of single edge along p
            max_percentage = 0
            for u, v in zip(path, path[1:]):
                if max_percentage < (Uk/G.edges[(u, v)]):
                    max_percentage = (Uk/G.edges[(u, v)])
                end if
            end for
        		// select path with min (max percentage)
            if max_percentage < min_max_percentage:
                min_max_percentage = max_percentage
                set min_max_index
            end if
				end if
		end for
    if min_max_index == -1:
        raise Exception("Cannot Satisfy all Type 1")
		end if
    return paths[min_max_index]
```



##### Type1: select path method: `type1_least_conflict` 

$$
\text{edge distance$(p, S, D)$} = \text{# edge for any subpath $q$ on path $p$ from src $S$ to $D$}\\
\text{conflict value of path } p = \sum_{\forall x} U_x \cdot \max(\text{edge distance$(p, S_x, D_x)$})
$$

```pseudocode
procedure least_conflict_value(Lambdak, type2)
		Sk, Dk, Uk = Lambdak
		paths = G.find_paths(Sk, Dk)
		
		initialize min_index, min_conflict_value
    for path in paths:
        if path has enough capacity for Lambdak:
        		// calculate conflict value of p
        		conflict_value = 0
            for Sigmax in type2:
            		Sx, Dx, Ux = Sigmax
                if exist subpath q from Sx to Dx:
                    max_edge_dist = max(max(Dx index) - min(Sx index), 0)
                    conflict_value += Ux * max_edge_dist
                end if
            end for
            
						if conflict_value < min_conflict_value:
                conflict_value = min_conflict_value
                set min_index
            end if
        end if
    end for
		if min_index == -1:
        raise Exception("Cannot Satisfy all Type 1")
		end if
		return path[min_index]
```

