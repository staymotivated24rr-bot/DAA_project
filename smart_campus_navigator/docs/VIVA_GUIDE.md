# Viva preparation guide

Answers refer to the original fictional campus. Say distances in metres and distinguish a route from a network.

## 1. [Basics] What is a graph?

A collection of vertices and edges. Here vertices are campus locations and edges are walkable paths.

## 2. [Basics] What are V and E?

V counts vertices and E counts undirected edges once. Our original campus has V=10 and E=17.

## 3. [Basics] Why is this graph undirected and weighted?

Each path can be walked both ways at the same modelled distance. A numerical weight records metres.

## 4. [Basics] What is an adjacency list?

For each location, a dictionary stores its neighbors and distances. An undirected edge appears in two neighbor dictionaries.

## 5. [Basics] What is Big O?

An upper bound on resource growth as input size increases. O(V+E) grows with vertices plus edges; it is not an exact duration.

## 6. [Basics] What is the difference between time and space complexity?

Time counts how computational work grows. Space counts memory growth. State whether graph storage, results and tracing are included.

## 7. [Basics] How do a queue and stack differ?

A queue removes the oldest item (FIFO). A stack resumes the newest item (LIFO). BFS uses a queue; DFS uses stack frames.

## 8. [Algorithms] Why select BFS?

It makes layered exploration and connectivity easy to demonstrate and guarantees minimum hop distance on an unweighted graph.

## 9. [Algorithms] Why select DFS?

It demonstrates deep exploration and backtracking with a stack, complementing BFS on the same graph.

## 10. [Algorithms] Does BFS find the shortest walking route?

Not in general: it minimizes edge count, not weight. In the A-B=2, B-C=1, A-C=5 triangle it reaches C directly in one edge, although walking through B costs only 3.

## 11. [Algorithms] Why are BFS and DFS O(V+E)?

Each reachable vertex is processed once. Each undirected edge is examined from both endpoints. Two times E is still O(E).

## 12. [Algorithms] Why select Dijkstra?

Distances are nonnegative, and the campus is a small sparse weighted graph. A min-heap efficiently selects the next nearest unsettled vertex.

## 13. [Algorithms] What is relaxation?

Try candidate = distance[u] + weight(u,v). If it is smaller than distance[v], update v and its parent.

## 14. [Algorithms] Why does Dijkstra need nonnegative weights?

Its greedy proof settles the smallest tentative distance permanently. A later negative edge could improve a settled vertex and break that argument.

## 15. [Algorithms] Why use heapq?

It implements a binary min-heap. Push and pop cost logarithmic time. This project uses lazy entries and skips vertices already settled.

## 16. [Algorithms] What is Dijkstra complexity here?

O((V+E) log V) time for a simple graph and O(V+E) extra/result space because lazy heap entries may reach O(E). Tracing adds O(V+E) events.

## 17. [Algorithms] Why select Floyd-Warshall?

It exposes dynamic programming and produces one small distance matrix answering all pairs of campus queries, with next-hop reconstruction.

## 18. [Algorithms] What does the Floyd-Warshall recurrence mean?

d[i,j] = min(d[i,j], d[i,k]+d[k,j]). Compare the previous best route with one passing through the newly allowed intermediate k.

## 19. [Algorithms] Why is Floyd-Warshall O(V cubed)?

The three nested loops each iterate over all V vertices. Matrices require O(V squared) space; our optional comparison trace can need O(V cubed).

## 20. [Algorithms] Does Floyd-Warshall support negative edges?

In general it supports negative directed edges if there is no negative cycle, and negative diagonals can detect such cycles. This undirected campus model rejects negatives: a negative undirected edge creates a negative closed walk.

## 21. [Algorithms] What is a spanning tree?

A connected acyclic subgraph containing every vertex. A tree on V vertices has V-1 edges. A minimum spanning tree minimizes their total weight.

## 22. [Algorithms] Why select Prim?

It explains growing an economical connected campus network from a starting location by repeatedly choosing a cheapest crossing edge.

## 23. [Algorithms] Why select Kruskal?

It gives a contrasting edge-oriented MST strategy: sort all edges and accept only those joining different components.

## 24. [Algorithms] What is Disjoint Set Union?

A structure representing components. find returns a representative; union merges components. Equal representatives mean an edge would create a cycle.

## 25. [Algorithms] What do path compression and union by rank do?

Compression makes visited nodes point toward the root. Rank attaches the shallower root beneath the deeper root. Together operations take nearly constant amortized time, O(alpha(V)).

## 26. [Algorithms] Why are Prim and Kruskal correct?

The cut property says a cheapest edge crossing a cut is safe for some MST. Prim uses the visited cut; Kruskal uses cuts between current components.

## 27. [Algorithms] Must Prim and Kruskal choose identical edges?

No. They must obtain the same optimal total weight. Ties may produce distinct MSTs; this code uses deterministic tie rules.

## 28. [Algorithms] Why is Kruskal usually O(E log E)?

Sorting dominates. DSU initialization is O(V), so the disconnected-input bound is O(V + E log E), with near-linear union/find work.

## 29. [Project] What exact result should I demonstrate?

Main Gate → Academic Block → Library → Canteen → Hostel costs 300+150+180+200 = 830 m. Both MST algorithms return 1690 m with nine edges.

## 30. [Project] How is an MST different from a shortest route?

An MST minimizes the sum of its network edges. Dijkstra minimizes one source-to-destination journey. On this campus the tree journey Main Gate to Hostel is 830 m, but Main Gate to Auditorium along the MST is 510 m versus a 380 m shortest route.

## 31. [Project] Why does the route finder settle ten vertices?

This implementation completes all reachable single-source distances even when a target is selected. The node count represents the entire source search.

## 32. [Project] How are unreachable destinations represented?

Distances remain math.inf and the reconstructed path is empty. The UI says unreachable instead of drawing an invented route.

## 33. [Project] What happens on a disconnected graph?

A traversal reaches only its starting component. Prim restarts in other components; Kruskal naturally returns a minimum forest. Both explicitly report that no complete spanning tree exists.

## 34. [Project] What if source equals destination?

The route is just the one source vertex and its distance is zero. No edges are highlighted.

## 35. [Project] Are zero-weight edges allowed?

Yes, all six algorithms support them in this nonnegative model. They are useful for testing, though distinct campus sites realistically have positive walking distances.

## 36. [Project] How do path edits work?

Graph.set_edge validates and updates both directions. remove_edge deletes both directions. Session state retains changes across pages; Restore reloads the original JSON dataset.

## 37. [Project] Are the coordinates real?

No. They are fictional local diagram coordinates in metres. Route calculations use explicit edge weights, not a real map or straight-line heuristic.

## 38. [Project] How did you test correctness?

Known-answer tests check small graphs. All-pairs distances agree with independent Dijkstra runs. A tiny MST is checked by enumerating every V-1 edge subset and testing connectivity. UI tests exercise pages and editing.

## 39. [Project] Do measured timings prove Big O?

No. They are seven-run perf_counter medians on seeded graphs with tracing disabled. Machine load and Python overhead matter; theoretical growth follows from operation counts.

## 40. [Project] Why is this syllabus aligned?

It implements the six graph algorithms requested for Unit 4 and explains efficiency and Big O from Unit 1. Practical 8-11 mapping is user-provided; no separate official syllabus was supplied.

## 41. [Project] What are the major limitations?

Fictional static distances, symmetric paths, length-proportional cost, no accessibility or congestion model, session-only edits and small-graph visualization.

## 42. [Project] Where should I start explaining the code?

Start with data/campus.json and Graph.adj, then dijkstra: initialize, pop nearest, settle, relax, record parent, reconstruct. Explain a small test before showing the interface.
