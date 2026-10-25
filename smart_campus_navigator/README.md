# Smart Campus Navigator
## Interactive Graph Algorithm Visualizer and Route Optimizer

A local, offline-capable DAA mini-project for course **01AI0506**, using six manually implemented graph algorithms. A fictional campus has 10 locations and 17 undirected weighted paths. Students minimize walking distance; administrators minimize the total length of a connected network.

**Verified sample:** Main Gate → Academic Block → Library → Canteen → Hostel is **830 m**. Prim and Kruskal each produce a **1,690 m** minimum spanning tree with 9 edges. The graph is illustrative and does not describe a real university.

## Features
- Navy/teal Streamlit dashboard and interactive Plotly campus diagram.
- Dijkstra route finder, all-source distance table, path reconstruction, and explanatory steps.
- BFS/DFS traversal order with Previous, Next, and Reset controls.
- Prim/Kruskal selection order and clear disconnected-forest warnings.
- Floyd-Warshall labelled all-pairs distance matrix and route reconstruction.
- Learning Lab: objectives, strategies, complexity, correctness, pseudocode, worked triangle, and repeated experimental timings.
- Add, update, remove paths and restore the dataset within the browser session.
- Actual PDF report, editable PPTX, beginner guide, viva preparation, and demonstration script.

## Academic scope
Focus: Unit 4, Greedy Method and Graph Algorithms, supported by Unit 1 algorithm efficiency and asymptotic analysis. Practical 8–11 relevance is taken from the user's supplied brief. **No separate official syllabus was attached**, so exact practical numbering should be checked against the department copy; this project does not invent official exercise titles. Floyd-Warshall uses dynamic programming although included in the requested six-algorithm scope.

## Stack and algorithm choices
Python **3.11+**, Streamlit, Plotly, standard-library `deque`, `heapq`, `perf_counter`, `unittest`; ReportLab for PDF and python-pptx for slides. No NetworkX, SciPy, map APIs, API keys, database, account, or remote service is used by the app.

| Algorithm | Objective | Time without history | Auxiliary/result space without history |
|---|---|---|---|
| BFS | Reachability / minimum unweighted hops | O(V + E) | O(V) |
| DFS | Depth-first exploration | O(V + E) | O(V) |
| Dijkstra | Single-source shortest distances | O((V + E) log V) | O(V + E) |
| Floyd-Warshall | All-pairs shortest distances | O(V³) | O(V²) |
| Prim | Minimum spanning tree / forest | O((V + E) log V) | O(V + E) |
| Kruskal | Minimum spanning tree / forest | O(V + E log E) | O(V + E) |

V = vertices, E = undirected edges. Graph storage is O(V + E). Lazy heaps can retain O(E) entries. For a simple graph log E = O(log V). Kruskal is usually O(E log E) on connected graphs; the O(V) term accounts for isolated vertices. Compact event history adds O(V + E) storage for the five non-Floyd algorithms and up to O(V³) for Floyd-Warshall. Neighbors are sorted during graph edits, outside timed computation. See the report and `campus/learning.py` for details.

## Windows: recommended launch
1. Install Python 3.11 or newer from https://www.python.org/downloads/ with the Python launcher enabled.
2. Extract the entire project folder. Double-click **setup.bat** (internet required once for dependencies).
3. Double-click **run.bat**. Open **http://localhost:8501** if the browser does not open automatically.
4. Leave the terminal open during the demo. Press Ctrl+C in that terminal to stop.

Manual Windows commands from the extracted project folder:
```bat
py -3 -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe -m streamlit run app.py
```
Once the dependencies are installed, disconnect the internet and run again; data, Plotly assets, and application code are local. Prepare dependencies before travelling to the lab. Batch helpers are provided for Windows; automated verification was executed on Linux/Python 3.12, not on Windows itself.

## macOS / Linux
```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m streamlit run app.py
```

## Tests, measurements and artifact generation
Use the virtual environment Python for these commands:
```sh
python -m unittest discover -s tests -v
python -m compileall -q app.py campus tests tools
python -m campus.benchmark
python tools/generate_deliverables.py
```
The benchmark overwrites the recorded CSV with new real measurements; regenerate the report/slides afterwards to keep the experimental values consistent. `requirements-tested.txt` records the four direct dependency versions used for verification. PDF/PPTX generation uses only the four declared dependencies and the standard library. Optional `tools/verify_browser.py` needs Playwright and an installed Chromium; it is a development check, not an app dependency.

## Expected demonstration
Open Dashboard (10 locations, 17 paths); choose Campus Route Finder with Main Gate and Hostel (830 m); choose Campus Network Optimizer (1,690 m); compare BFS/DFS; inspect Floyd-Warshall; modify a path and restore the original. Detailed click-by-click guidance is in `docs/DEMO_SCRIPT.md`.

## Project structure
```text
smart_campus_navigator/
  app.py                         Streamlit dashboard and controls
  campus/
    graph.py                     Validated graph editing, JSON loader
    algorithms.py                Six algorithms, DSU, structured result/events
    visualization.py             Plotly diagram and highlights
    learning.py                  Shared theory and pseudocode
    benchmark.py                 Seeded graphs and repeated timing
  data/campus.json                One fictional campus dataset
  tests/test_algorithms.py        Known answers, invariants, edge cases
  tests/test_app.py               Streamlit page/session integration
  tools/generate_deliverables.py  Reproducible report, slides and study guides
  tools/verify_browser.py         Optional browser smoke test
  docs/Project_Report.pdf         12-page report; editable student form fields
  docs/Project_Presentation.pptx  12-slide presentation; editable objects
  docs/VIVA_GUIDE.md
  docs/LEARN_THE_PROJECT.md
  docs/DEMO_SCRIPT.md
  docs/benchmark_results.csv
  docs/benchmark_environment.txt
  docs/unit_test_results.txt
  docs/VERIFICATION.md
  .streamlit/config.toml
  requirements.txt
  requirements-tested.txt
  setup.bat / run.bat
```

## Assumptions and limitations
- Weights are finite nonnegative metres; zero is accepted for algorithm teaching. Negative values, self loops, NaN, infinity, and unknown nodes are rejected. The graph is simple and undirected.
- BFS/DFS start in one component. MST algorithms return the minimum forest over all components and report that a complete spanning tree is impossible.
- Dijkstra completes all reachable single-source distances, so “Nodes settled” includes the complete search even when a destination was selected.
- Equal-weight shortest routes or MSTs can exist. Alphabetical neighbors and explicit heap/sort ties make this implementation deterministic; different correct implementations may select different equal-cost solutions.
- Session edits do not write to `campus.json`. They persist across sections of the same session and disappear on a new session or Restore. No file-upload or arbitrary-node editor is needed for this fixed campus.
- Construction cost is assumed proportional to length. Accessibility, congestion, slopes, and turn restrictions are outside scope.
- Step controls are manual; automatic playback is intentionally omitted to keep live demonstrations stable.

## Troubleshooting
- **`streamlit` not found:** use `python -m streamlit` with the virtual environment interpreter, or run setup.bat again.
- **Port 8501 occupied:** run `python -m streamlit run app.py --server.port 8502` and open localhost:8502.
- **App seems to show old edits:** use Restore original graph under Edit campus paths.
- **Unreachable route / forest warning:** this is expected if you removed connecting paths. Restore the graph.
- **Package installation blocked:** install dependencies on an internet-connected machine first; runtime needs no external connection.
- **Opening from the wrong folder:** change into the folder containing app.py. Batch helpers do this automatically.
- **PowerShell script policy:** activation is unnecessary; invoke `.venv\Scripts\python.exe` directly.
- **PDF identity details:** fill the title-page PDF fields in a compatible reader, or edit the generator and regenerate. Slide text boxes are directly editable in PowerPoint.

References: Cormen et al., *Introduction to Algorithms*, 4th ed., MIT Press, 2022; official Python, Streamlit, Plotly, ReportLab, and python-pptx documentation (links in report).
