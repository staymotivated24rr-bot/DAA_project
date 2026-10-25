# Demonstration script

## Before the examiner arrives
Run setup.bat before demo day. Run run.bat, open localhost:8501 and choose **Edit campus paths → Restore original graph**. Confirm Dashboard shows 10 locations and 17 paths. Keep this guide and the slides open. All names refer to the fictional dataset in data/campus.json. A weight label is metres, not measured travel time. All computations run locally.

## 60-second elevator pitch
“My project is Smart Campus Navigator, a graph algorithm visualizer for a fictional ten-location university. A location is a vertex and a walking path is an undirected weighted edge. I manually implemented six DAA algorithms. Dijkstra finds the shortest walking route: Main Gate to Hostel is 830 metres. Floyd-Warshall precomputes every pair of distances. BFS and DFS explain exploration using a queue and a stack. Prim and Kruskal solve a different problem: connecting all locations with minimum total pathway length, which is 1,690 metres here. The dashboard lets me step through decisions, edit distances and test disconnected cases. The Python logic is separate from the interface, and automated tests check known answers, reconstructed paths and minimum tree weights.”

## Natural three-minute explanation
**0:00–0:35 — Problem and model.**
“Finding one efficient route and planning an economical network are different problems. I modelled a fictional campus with ten vertices and seventeen undirected edges. Edge weights are nonnegative walking distances in metres. Coordinates only arrange the diagram; the supplied edge weights determine the route.”

**0:35–1:15 — Algorithms.**
“BFS uses a FIFO queue to explore one layer at a time; DFS uses stack frames to go deep and backtrack. They demonstrate reachability rather than weighted route optimization. Dijkstra repeatedly settles the smallest tentative distance and relaxes neighboring edges. Nonnegative weights make each settled distance final. Floyd-Warshall considers intermediate vertices and updates an all-pairs table.”

**1:15–1:55 — Network design.**
“Prim grows a tree with the cheapest crossing edge. Kruskal sorts all edges and uses Disjoint Set Union to reject cycles. The cut property explains why each accepted edge is safe. Both give the optimal total of 1,690 metres on this graph. If the graph is disconnected, I explicitly show a minimum forest instead of claiming a spanning tree exists.”

**1:55–2:30 — Software and evidence.**
“My algorithm module uses standard Python, not a graph algorithm library. A separate graph module validates editing. Streamlit controls the interface; Plotly highlights actual computed edges. Structured events power the manual step viewer. Tests check known routes, zero weights, disconnected graphs, restoration and an exhaustive tiny-graph MST oracle. Experimental timing is separate from theoretical complexity.”

**2:30–3:00 — Result and scope.**
“The shortest Main Gate–Hostel route is 830 metres through Academic Block, Library and Canteen. The nine-edge MST costs 1,690 metres of construction length. This demonstrates Unit 4 graph and greedy methods with Unit 1 efficiency analysis. The app runs offline after installation. A practical extension would add accessibility data, but the present model deliberately stays easy to inspect and explain.”

## Five-minute live demonstration
| Time | Exactly what to click | What should appear / what to say |
|---|---|---|
| 0:00–0:35 | Sidebar **Dashboard**; **Edit campus paths → Restore original graph** | 10 locations, 17 paths, 6 algorithms. “The dataset is fictional; edge labels are walking metres.” |
| 0:35–1:25 | Sidebar **Campus Route Finder**; Source **Main Gate**, Destination **Hostel** | **830 m**, 4 route edges, 10 settled nodes. Main Gate → Academic Block → Library → Canteen → Hostel. “Dijkstra completes the whole reachable source search here.” Expand **Step-by-step Dijkstra** and click **Next →** twice. “Main Gate first proposes Academic Block at 300 and Administrative Block at 140.” |
| 1:25–2:10 | Sidebar **Graph Exploration**; Traversal **BFS**, Starting location **Main Gate**; click **Next →**, then choose **DFS** | BFS begins Main Gate, Academic Block, Administrative Block. DFS begins Main Gate, Academic Block, Administrative Block, Auditorium. “These early orders partly coincide; BFS eventually visits Laboratory/Library before deep branches. BFS optimizes hops, not weighted distance.” Use **Reset steps**. |
| 2:10–3:00 | Sidebar **Campus Network Optimizer**; choose **Prim**, then **Kruskal** | Both show **1690 m**, **9 selected edges**. “This minimizes the whole network's length. Prim's first edge is Main Gate–Administrative Block, 140; Kruskal's first global edge is the same undirected path. Their acceptance orders differ.” |
| 3:00–3:40 | Sidebar **All-Pairs Route Analyzer**; Main Gate and Hostel | Matrix entry and reconstructed route show **830 m**. “The update is min(d[i,j], d[i,k]+d[k,j]); k is a permitted intermediate, not necessarily a neighbor.” |
| 3:40–4:25 | **Edit campus paths**; endpoint A **Main Gate**, endpoint B **Hostel**, Action **Add / update**, distance **100**; **Apply path change**; **Campus Route Finder** | Direct Main Gate → Hostel becomes **100 m**. “This deliberately unrealistic edit demonstrates recomputation; the production model is still the original illustrative dataset.” Then **Restore original graph** returns **830 m**. |
| 4:25–5:00 | Sidebar **Learning Lab**; choose **Dijkstra**; inspect pseudocode and complexity. Optionally click **Run small benchmark** | “Heap-based Dijkstra has O((V+E) log V) time. Lazy heap space is O(V+E). Timings are seven-run medians with event history disabled; an all-pairs algorithm does more work than a single-source algorithm.” |

## If asked to demonstrate disconnection
In Edit campus paths, remove Main Gate–Administrative Block, then Main Gate–Academic Block. Route Finder Main Gate → Hostel says unreachable. BFS reaches only Main Gate. Prim and Kruskal show **1550 m**, **8 edges**, and the disconnected minimum-forest warning. Restore original graph afterwards. The 1,550 total is the original 1,690 minus the isolated gate's 140-m tree edge.

## Optional source walkthrough
Open campus/graph.py (`Graph.set_edge` validates and sorts neighbors), campus/algorithms.py (`dijkstra` relaxes and records parents; `AllPairs.path` follows next hops; `DisjointSet.union` rejects cycles), then tests/test_algorithms.py. Explain one test before showing test output. Do not claim a score, optimality of all MST routes, or that benchmark timings prove Big O.
