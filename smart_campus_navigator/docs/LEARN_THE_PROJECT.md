# Learn the project from zero

## 1. Read this before opening the code
A campus is a network. A **vertex** is a place, such as the Library. An **edge** is a direct walking path between two places. A **weighted graph** gives each edge a number: walking distance in metres. **Undirected** means both directions have the same weight. An adjacency list stores each place's neighbors. In this project it is a Python dictionary of dictionaries, graph.adj[u][v] = weight.

A **path** is a sequence of adjacent locations. Its weighted length is the sum of its edge distances. A **cycle** returns to its starting point. A graph is **connected** when every pair is reachable. A **component** is one connected piece. A **tree** is connected and has no cycle; it has V-1 edges. A **forest** contains a tree for each component.

## 2. Data structures and strategies
A queue is like a line at the canteen: first in, first out. A stack is like a stack of trays: last in, first out. A min-heap retrieves the smallest item efficiently, without maintaining a completely sorted list. A greedy algorithm takes a locally best safe choice; correctness needs a proof, not merely intuition. Dijkstra and MST algorithms are greedy here; Floyd-Warshall is dynamic programming, solving overlapping subproblems by allowed intermediates.

## 3. Set up and follow the data
Run setup.bat and run.bat. The JSON dataset becomes a Graph in graph.py. A Streamlit selection calls a function in algorithms.py. That function returns a Result (or AllPairs) containing the answer and compact events. visualization.py draws that computed answer. app.py formats it for a reader. The logic never imports Streamlit, so tests run independently.

## 4. One tiny graph for all six algorithms
Use A-B=2, B-C=1, A-C=5. Draw a triangle and write the weights. This is a teaching example, separate from the single campus dataset. Neighbor order is alphabetical. Work through the six methods below with pencil and paper before trying the campus graph.

## BFS: Explore reachable vertices; minimum hop counts

**Hand-worked example.** Start A: queue [A]. Remove A; discover B then C, giving queue [B,C]. Remove B, then C. Order A,B,C. C is one hop away even though its direct edge weighs 5. Mark on enqueue so a second incoming edge does not duplicate C.

**Pseudocode**
```text
mark source; enqueue source
while queue is not empty:
  u = dequeue; output u
  for each neighbor v of u:
    if unseen: mark v; enqueue v
```

**Walk through the Python.** Read bfs in campus/algorithms.py. deque([source]) initializes FIFO storage; seen marks the source. popleft removes the oldest vertex. The neighbor loop marks unseen vertices before appending them. Result.order is the visit order; discover and visit events narrate the queue actions.

**Why it works.** The FIFO queue processes vertices in nondecreasing hop distance. A vertex is marked when enqueued, so its first discovery uses the minimum number of edges. Every reachable neighbor is eventually discovered.

**Efficiency.** O(V + E) time; O(V) auxiliary/result space with trace disabled. Simple level-by-level exploration. Limitation: Ignores walking distances.

## DFS: Explore reachable vertices deeply

**Hand-worked example.** Start A and enter B, its alphabetically first neighbor. From B enter C. C has no unseen neighbor, so pop its frame; then pop B and A. Order A,B,C. The stack stores suspended neighbor iterators, just as recursive calls would.

**Pseudocode**
```text
mark and output source; push (source, neighbors)
while stack is not empty:
  inspect next neighbor of top frame
  if exhausted: pop frame
  elif unseen: mark, output, push its frame
```

**Walk through the Python.** Read dfs. stack contains (vertex, neighbor_iterator) frames. next(neighbors, None) resumes the top frame; None means backtrack by pop. An unseen vertex is marked, appended to order, and pushed with its own iterator. No Python recursion is used, so a long chain does not hit the recursion limit.

**Why it works.** Each stack frame scans all neighbors of its vertex before backtracking. Every reachable vertex is therefore entered exactly once; marking prevents cycles from causing repeated visits.

**Efficiency.** O(V + E) time; O(V) auxiliary/result space with trace disabled. Natural backtracking and component exploration. Limitation: Does not optimize route length.

## Dijkstra: Single-source shortest distances

**Hand-worked example.** Initially d(A)=0, d(B)=infinity, d(C)=infinity. Settle A and propose B=2 and C=5. Pop B=2, improve C to 2+1=3 and parent[C]=B. Pop C=3 and settle it. The old heap entry C=5 is ignored. Reversing parents C,B,A gives A,B,C at distance 3.

**Pseudocode**
```text
distance[source] = 0; other distances = infinity
push (0, source)
while heap is not empty:
  pop minimum (distance, u); skip if settled
  settle u
  for (v, weight) adjacent to u:
    if distance[u] + weight < distance[v]:
      update distance[v], parent[v]; push new entry
```

**Walk through the Python.** Read dijkstra. Result.distances starts at infinity except source. heappop selects a minimum pair; settled filters lazy duplicates. candidate adds one edge cost. A strict improvement updates the distance and parent and pushes a new pair. After the search, target is followed backwards through parent and the list is reversed. Omitting target requests only the complete source distance table.

**Why it works.** When the smallest tentative distance is settled, no route through an unsettled vertex can improve it: reaching that vertex already costs at least as much, and remaining edges are nonnegative. Relaxation preserves upper bounds until all reachable distances are final.

**Efficiency.** O((V + E) log V) time; O(V + E) auxiliary/result space with trace disabled. Efficient sparse weighted routing. Limitation: Requires nonnegative weights.

## Floyd-Warshall: All-pairs shortest distances

**Hand-worked example.** Initially d(A,C)=5, d(A,B)=2, d(B,C)=1, with diagonal zero. When B is allowed as an intermediate, compare 5 with 2+1=3. Store d(A,C)=3 and next[A,C]=B. Follow A→B→C to reconstruct. The reverse pair also becomes 3 in this undirected graph.

**Pseudocode**
```text
initialize direct distances and zero diagonal
for each intermediate k:
  for each source i:
    for each destination j:
      if d[i,k] + d[k,j] < d[i,j]:
        d[i,j] = d[i,k] + d[k,j]
        next[i,j] = next[i,k]
```

**Walk through the Python.** Read floyd_warshall and AllPairs.path. Two nested dictionary comprehensions initialize distances and next_hop, then direct edges replace infinity. The k/u/v loops try each intermediate and record before, candidate and improvement fields for every comparison when tracing is enabled. A strict improvement copies next_hop[u][k] as the first hop toward v. AllPairs.path repeatedly follows those first hops; None means unreachable.

**Why it works.** After intermediate k, d[i,j] is the shortest distance using only the intermediates processed so far. An optimal path either avoids k or splits into i-to-k and k-to-j subpaths. The minimum of these two cases preserves the invariant.

**Efficiency.** O(V³) time; O(V²) auxiliary/result space with trace disabled. One table answers every pair. Limitation: Cubic time limits large graphs.

## Prim: Minimum spanning tree / forest

**Hand-worked example.** Start A. The crossing heap offers A-B=2 and A-C=5. Accept A-B=2; B exposes B-C=1. Accept B-C=1. The total is 3 with two edges. Prim does not sort all graph edges globally; each chosen edge crosses its current visited cut.

**Pseudocode**
```text
for each component root not yet visited:
  push (0, root, no parent)
  while heap is not empty:
    pop cheapest connection; skip visited endpoint
    visit endpoint; accept edge if parent exists
    push its edges to unvisited vertices
```

**Walk through the Python.** Read prim. roots starts with the requested source and then lists other vertices. An unseen root gets a (0, root, None) heap entry. Popping a new vertex accepts its parent edge, if present, then pushes outgoing edges toward unvisited vertices. The outer root loop handles disconnected components. len(edges)==V-1 and a nonempty graph determines the connected flag.

**Why it works.** At each step, the chosen edge is a cheapest edge crossing the cut between visited and unvisited vertices in the component. The cut property guarantees that adding it can be extended to an MST. Restarting gives a minimum forest.

**Efficiency.** O((V + E) log V) time; O(V + E) auxiliary/result space with trace disabled. Grows connectivity from a location. Limitation: MST routes need not be shortest.

## Kruskal: Minimum spanning tree / forest

**Hand-worked example.** Sort B-C=1, A-B=2, A-C=5. Initially {A},{B},{C}. Accept B-C and merge {B,C}. Accept A-B and merge all three. Reject A-C because its endpoints already have the same DSU root. Total 1+2=3.

**Pseudocode**
```text
make a separate set for every vertex
for edges in increasing (weight, endpoints) order:
  if endpoint roots differ:
    accept edge; union the two sets
  else: reject cycle edge
```

**Walk through the Python.** Read DisjointSet then kruskal. parent and rank are dictionaries. find first locates a root, then compresses the traversed path. union rejects equal roots and otherwise joins by rank. kruskal sorts (weight, endpoint names), accepts edges whose union succeeds, and records reject events for cycle edges.

**Why it works.** The next accepted edge is a cheapest edge connecting two current components. The cut property makes it safe; DSU rejects edges that would form cycles. Connected input finishes with V-1 safe edges.

**Efficiency.** O(V + E log E) time; O(V + E) auxiliary/result space with trace disabled. Simple edge-based global selection. Limitation: Requires edge sorting.

## 5. Walk through the real campus
The original graph has 10 locations and 17 paths. Dijkstra from Main Gate first proposes Academic Block=300 and Administrative Block=140. It settles Administrative Block first; that gives Auditorium=380. Academic Block remains 300 because 140+160 ties the current distance, so the parent is unchanged. Academic Block proposes Library=450 and Laboratory=470. Auditorium proposes Canteen=640. Library later improves Canteen to 630 and Medical Centre to 730. Canteen improves Hostel to 830. The reconstructed route is Main Gate → Academic Block → Library → Canteen → Hostel: 300+150+180+200=830 m.

**Prim selection from Main Gate:**
1. Main Gate — Administrative Block: 140 m
2. Administrative Block — Academic Block: 160 m
3. Academic Block — Library: 150 m
4. Academic Block — Laboratory: 170 m
5. Library — Canteen: 180 m
6. Canteen — Hostel: 200 m
7. Academic Block — Auditorium: 210 m
8. Auditorium — Sports Ground: 210 m
9. Hostel — Medical Centre: 270 m

Total = 1690 m. Kruskal reaches the same total but accepts edges in global nondecreasing weight order. The original campus has a unique MST despite some equal-weight edges; the complete equal-weight test graph demonstrates non-unique choices. Equal-weight shortest routes also exist: Main Gate to Academic Block can be direct (300) or via Administrative Block (140+160).

## 6. Shortest route versus minimum network
Suppose the university builds only the MST. Its total construction length is minimal. A journey inside that tree may still be longer: Main Gate to Auditorium follows Main Gate–Administrative Block–Academic Block–Auditorium for 140+160+210=510 m. The full graph has a shorter Main Gate–Administrative Block–Auditorium route of 380 m. Minimize one journey with Dijkstra; minimize total network length with an MST.

## 7. Understand complexity without memorizing symbols
For BFS/DFS, count one processing step per visited vertex and two adjacency checks per undirected edge: V+2E becomes O(V+E). Floyd has three V loops: V×V×V. Heap pushes/pops cost logarithmic time; Dijkstra and lazy Prim do O(V+E) such work, giving O((V+E) log V) on simple graphs. Kruskal sorts E edges, O(E log E), and initializes V DSU entries. Big O omits constants and lower-order terms; it describes growth, not exact seconds. O(V²) space means that doubling V roughly quadruples table entries.

V is the number of locations; E is the number of undirected paths. Bounds describe computation with trace=False, exclude graph storage O(V + E), and include returned results. The simple graph is prepared with sorted neighbors at edit time. Lazy heaps may retain O(E) entries; log E = O(log V) for simple graphs. Kruskal is typically written O(E log E) for connected graphs; O(V) initializes DSU for isolated vertices. Compact history adds O(V + E) for BFS/DFS/Dijkstra/Prim/Kruskal, and up to O(V³) for Floyd-Warshall. Enabling history preserves asymptotic running time but adds event-object allocation and storage costs. Displaying a long history prefix also costs time beyond the algorithm itself.

## 8. Read and trust tests
Run python -m unittest discover -s tests -v using your installed environment. A known-answer test asserts an independently worked result. The A-B-C-D graph has shortest A-to-D distance 6 and MST weight 6. A disconnected graph keeps infinity for unreachable pairs; its MST result is a forest. An exhaustive small-graph oracle enumerates candidate three-edge trees. Agreement between Dijkstra and Floyd across generated graphs checks more cases, but no finite set of tests is a universal proof.

## 9. Common mistakes and memory cues
BFS: “breadth before depth,” use a queue. DFS: “finish the branch,” use a stack. Dijkstra: “nearest unsettled first.” Floyd: “could k help i reach j?” Prim: “grow one connected patch.” Kruskal: “sort and join components.” Do not mix up a parent pointer for single-source reconstruction with the next-hop table for all-pairs reconstruction. Do not treat infinity as an actual path length or assume a forest is a spanning tree.

## 10. A practical learning session
First draw the triangle and calculate all answers manually. Next run the route finder and predict the next event before clicking Next. Then remove both gate edges and explain why the source is isolated. Restore the original graph, run the tests, and practise the five-minute script. Finish by explaining one relaxation and one DSU rejection without looking at the screen.

## 11. How the repaired step viewer works
The fragment in ui/steps.py reruns only its controls and visualization. campus/playback.py keeps one execution per browser session and replays compact events into a Frame. A different page, algorithm, source, destination or actual graph fingerprint resets the index. Unchanged results and a base graph canvas are reused within that session. There is no global mutable graph cache. BFS distinguishes discovered nodes from visited nodes; DFS shows the active stack; Dijkstra shows tentative versus settled distances; Kruskal separates examining, accepting and rejecting an edge. Floyd records every I/J/K comparison and reconstructs a matrix from direct distances plus earlier improvements. Previous applies a shorter event prefix, so it restores exactly the earlier state. This takes O(V²+t) work for a Floyd seek to event t, with O(V²) replay tables instead of storing a full matrix at every step. The final summary matrix and the replay matrix are labelled separately.
