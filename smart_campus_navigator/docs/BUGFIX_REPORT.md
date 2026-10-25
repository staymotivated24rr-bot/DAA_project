# Smart Campus Navigator — bug-fix and verification report

## Scope and audited revision

Repository: staymotivated24rr-bot/DAA_project. Baseline inspected: `78d7381` on
local branch `work` (the running application was deployed from `4f462c9`; the
following baseline commit only recorded deployment details). Repairs are on
`fix/algorithm-playback-and-state`. Main was not merged, force-pushed or changed
by this repair task. No production deployment or infrastructure change was made.
The pre-existing untracked Smart_Campus_Navigator.zip was preserved.

Reviewed: app.py, campus/algorithms.py, graph.py, visualization.py, learning.py,
benchmark.py, data/campus.json, tests/test_algorithms.py, test_app.py,
tools/verify_browser.py, tools/generate_deliverables.py, .streamlit/config.toml,
requirements.txt, requirements-tested.txt, root render.yaml and related guides.

Flow checked: input → session graph → manual algorithm → compact events → replay
frame → Plotly/table → navigation controls. The graph dataset and all six
handwritten algorithms remain; shortest routes and MST selection rules were not
replaced by library calls.

## Confirmed findings, causes and repairs

| Finding / baseline location | Established cause | Repair / resulting behavior |
|---|---|---|
| Full-page work for every Next click, app.py ~70–95 and algorithm calls below | Plain button callbacks reran app.py, repeated algorithm execution, constructed figures and serialized an entire event prefix. Browser sampled title-stale markers during those clicks. | ui/steps.py ~48 uses st.fragment. Only playback reruns. An unchanged algorithm result and base canvas are reused in the session. Full-prefix JSON was replaced by the current event. |
| Obsolete step indices, app.py ~76–85 | Each revision/parameter combination created a non-widget index key that was never removed. | campus/playback.py ~13–40 stores one active Execution. Context changes reset its index; actual graph fingerprints prevent stale answers. A one-time migration removes legacy indices while keeping graph edits. |
| Incorrect Floyd replay, app.py ~150–170 and old generic step_viewer | The page always displayed final distances; trace events lacked failed comparisons and before/operand fields. | algorithms.py ~121–149 records each actual I/J/K comparison. playback.py rebuilds tables from initialization plus compact improvements. ui/steps.py shows current before, operands, candidate, decision, matrix and reachable graph segments. Final summary is labelled separately. |
| Kruskal cycle rejection invisible, old generic viewer ~90 | Generic rendering collected accept/visit edges but ignored reject events. No separate examination or completion event existed. | Kruskal's DSU/sorting decisions remain unchanged. Its trace now separates examine, accept, reject and complete. The graph uses amber examined edges, teal accepted edges and rose dashed cycle rejections. |
| Dijkstra lost completed tree highlights during a relaxation, old viewer ~92 | The relaxation branch replaced selected edges with only the current edge. | Dedicated replay retains settled predecessor edges and shows the current tentative relaxation in amber, with tentative/settled distance rows. |
| BFS discovery / DFS backtracking lacked distinct state, old viewer ~88–93 | A shared event-name rule could not express frontier sets or an active DFS stack. | Algorithm-specific replay distinguishes discovered and visited BFS nodes, reconstructs DFS's active stack and removes completed frames on backtracking. |
| Extra full reruns after editing/restoring, app.py ~47–58 | Form/button events already caused a rerun, followed by an explicit st.rerun. | Removed those explicit reruns, clear the active execution and rebind the restored graph after sidebar processing. One normal event rerun recomputes the result. |
| Repeated graph preparation, visualization.py ~10–30 | Each path was a separate trace, rebuilt with all static annotations at every frame. | Reuse a session-local base canvas and group path overlays. Responsive short labels retain full names on hover. Pan, zoom, export and native Streamlit loading/error behavior remain available. |

### What the dimming investigation did and did not establish

The original browser run reproduced **full-page stale/loading markers**, not
persistent faded CSS. Across seven baseline clicks, minimum sampled element and
title opacity remained 1. The final chart had opacity 1 and filter none. It would
be inaccurate to say a persistent gray overlay was reproduced or to assign its
specific Render-side cause from that evidence alone.

The confirmed architectural problem was unnecessary whole-page rerunning. The
repair removes that pathway for step controls without overriding opacity,
brightness, stale-element CSS or Streamlit's running status. Temporary fragment
loading markers can still appear under load. In the repaired real-browser checks,
charts returned visible with effective ancestor opacity greater than 0.99 and no
brightness/filter effect; the page title was never marked stale during the timed
step run. No persistent dimming or page exception was observed in tested flows.

## Measured performance (actual recorded runs)

| Measurement | Baseline | Repaired | Interpretation |
|---|---:|---:|---|
| Median Next click → progress update and Streamlit idle, 7 clicks | 293.690 ms | 284.300 ms | About 3.2% lower in this small local sample; not evidence of a robust network/Render latency gain. |
| Page-title stale samples (8 ms sampling requested) | 12 | 0 | Confirms the removal of unrelated page reruns in this run. Timers can miss brief states. |
| Python Plotly frame-construction median, 50 runs after 5 warmups | 24.005 ms | 7.666 ms | About 68.1% lower; excludes browser paint, transport, UI and one-time base preparation. |
| Traces in the route frame used above | 18 | 3 | Same campus/route; grouped paths and cached base. Labels and styling also improved. |
| Retained revision-index keys after 12 graph edits | 13 | 0 | One active execution replaces previous runs. Total user state keys were 20 → 10 in isolated AppTest processes. |

The browser timing workload uses Graph Exploration/BFS's default start and steps
2–8, 1440×1100 Chromium, on the same local host, without CPU/network throttling.
It measures steady-state interaction, not cold start. Figure construction was
measured in separate Python processes against the preserved baseline checkout
and repaired checkout. Raw arrays, sampling scope and methods are retained in
interaction_baseline.json, interaction_after.json, rendering_baseline.json,
rendering_after.json and session_lifecycle_measurements.json. Results depend on
machine load and are experimental, not complexity proofs.

Floyd's 10-vertex traced execution has 1,002 compact events: initialization,
1,000 comparisons and completion. A tracemalloc run measured peak allocation
637,776 bytes (about 623 KiB), versus 6,680 bytes with tracing off, excluding the
preloaded graph/UI/browser. No matrix snapshot is stored per event. A seek to
event t reconstructs tables using O(V²+t) work and O(V²) replay table space;
retained comparison history is O(V³). This is suitable for the fixed ten-location
teaching graph. Benchmark workloads keep tracing off.

## Tests and actual outcomes

Baseline: **23 tests passed**. Final expanded suite: **50 tests passed, 0 failed**.

| Group | Test methods | Evidence |
|---|---:|---|
| Existing algorithm regression tests | 20 | Known answers, edits/restoration, invalid inputs, zero weights, disconnected/empty/singleton graphs, ties, path reconstruction, DSU, iterative DFS chain |
| Independent oracles | 2 | All 64 edge subsets on four vertices; enumerate simple paths and candidate spanning forests; float/equal-cost regression |
| Streamlit AppTest | 10 | All pages, every algorithm's boundaries, graph edits, sources/destinations, 36 algorithm switches, no recomputation of cached history/canvas, two-session isolation, legacy-state migration |
| Replay / visualization tests | 16 | Every forward/backward frame for all six methods on a small graph; every Floyd comparison; full campus final matrix; exact paths, colors, stack/frontier, invalid index, late callback guard, cached-base immutability |
| Deployment/config tests | 2 | YAML paths, free plan, autoDeploy false, PORT/address, health path, tested requirements, telemetry and separate developer dependencies |

Run with the installed environment interpreter:

```sh
python -m unittest discover -s tests -v
python -m compileall -q app.py campus ui tests tools
python -c 'import campus.algorithms, campus.playback, ui.steps, app'
```

All ran successfully. Bare imports/AppTest can emit missing ScriptRunContext
warnings; these were not app exceptions. Raw final results: unit_test_results.txt.
The application also started as a real local Streamlit server; the browser's
health request returned HTTP 200.

### Real browser regression

**PASS: 10 scenarios**, Chromium, desktop 1440×1100 and mobile 390×844. See
browser_verification.json and tools/verify_browser.py. The test blocks all
non-local HTTP requests; none were attempted. Captured page exceptions: 0;
console errors: 0. It exercises all sections, all six lab algorithms, Next,
Previous, Reset, first/final disabled boundaries, source/destination changes,
Kruskal examination/rejection/completion, Floyd improvement and backward replay,
editor/restoration, reload, optional benchmark, and mobile table scrolling.

Five rapid clicks in the recorded run advanced from step 1 to step 6 without an
index error or lost graph. The viewer clamps indices and changes them once per
accepted callback; this is not a guarantee about every possible browser/network
scheduling condition. Full opacity and no filtering were checked after each
settled interaction. Mobile tests found no body-level horizontal overflow; the
matrix scrolls inside its own container with sticky location labels.

Browser captures are actual screenshots: dashboard_screenshot.png,
route_screenshot.png, kruskal_rejection_screenshot.png,
floyd_matrix_screenshot.png, mobile_dashboard_screenshot.png and
mobile_floyd_screenshot.png.

### Failures encountered while developing the checks

An added state test initially used an obsolete AppTest accessor and failed; it
was changed to the installed version's public to_dict accessor. A mixed-process
baseline/fixed state probe reused Python's imported campus package and failed to
find the new module; measurements now run in separate processes. Browser fixture
runs initially failed on virtualized dropdown options, a detached/hidden chart
sample during queued callbacks, and old/resizing sidebar selectors. The fixture
now searches/selects options using keyboard interaction, waits for a real visible
chart after queued work, and uses accessible sidebar controls after breakpoint
settling. Those aborted runs are not counted as passes. The final complete run
and final suite passed as recorded above.

## Algorithm and academic audit

No incorrect shortest-path or MST answer was found. All six production
algorithms remain handwritten. BFS minimizes hops in unweighted graphs; DFS
explores/backtracks; Dijkstra requires nonnegative weights; Floyd-Warshall uses
dynamic programming; Prim and Kruskal use the cut property and greedy choices.
The graph contract still rejects negative/nonfinite weights, self loops and
unknown locations and allows zero weights. Lazy-heap space and separate tracing
costs are described consistently with the implementation.

Unchanged campus: 10 vertices, 17 undirected edges. Main Gate → Academic Block →
Library → Canteen → Hostel = **830 m**. Prim and Kruskal = **1,690 m**, nine edges.
Tests assert these computed outputs; no answer is hardcoded into production logic.

Regenerated Project_Report.pdf (12 readable pages, four editable identity fields),
Project_Presentation.pptx (12 slides, reopened with python-pptx), LEARN_THE_PROJECT.md
and VIVA_GUIDE.md to explain fragment-based replay and comparison events. The
slide shapes are in bounds. Native PowerPoint rendering was not available.

## Render readiness and production boundary

The existing service is srv-dbf43fqvcj2c73eou7e0 in the already confirmed
workspace, region Singapore, compute plan free. Read-only service inspection
confirmed autoDeploy is off. No infrastructure or production settings changed.
The existing direct-created service starts from repository root and its commands
enter smart_campus_navigator; render.yaml's rootDir supplies the equivalent
working directory for a future Blueprint. Do not apply that Blueprint to create
a duplicate service.

Local configuration/path checks **PASS**. Runtime dependency versions are
unchanged and the new ui package is ordinary source, not a new external service.
The startup command still binds 0.0.0.0 on the host-provided PORT. The Blueprint
uses /_stcore/health; the already-live direct-created service uses default TCP
readiness, as previously documented. No paid plan is required by these changes.

Existing production error-level logs returned no entries during inspection.
Observed five-minute samples of the existing application ranged from about
84.5–146.6 MiB memory against the reported 512 MiB limit, and roughly
0.00376–0.0570 CPU cores. These are existing-production samples, not a load test
of the repaired code; they do not establish future capacity or interaction
latency. A local traced Floyd history is separately measured above.

**NOT VERIFIED:** Render CLI/official schema validation (CLI unavailable and
Render documentation/schema hosts blocked by outbound policy); public Render
HTTP/browser tests (proxy 403); repaired production runtime (not deployed).
The current official platform references could not be fetched, so no changeable
platform defaults were inferred or changed.

Publishing remains a separate authorized action: review/merge this fix branch's
PR into main, then manually deploy main on the existing Render service. Automatic
deployment remains disabled. Verify the public 830-m route, 1,690-m MSTs, matrix
replay and navigation after that release. The live website still runs the prior
revision until those actions occur.

## Acceptance checklist

- PASS: app imports, compilation, server startup and local HTTP health.
- PASS: six manual algorithms, independent references and campus answers.
- PASS: Next/Previous/Reset, first/final boundaries, graph/context invalidation.
- PASS: session isolation, bounded history and old-state migration.
- PASS: genuine Floyd matrix replay and final-table agreement.
- PASS: Kruskal examine/accept/reject/complete colors and explanations.
- PASS: BFS frontier, DFS backtracking, Dijkstra settled/tentative, Prim forest.
- PASS: browser desktop/mobile flows, no persistent dimming in tested runs,
  visible graphs, no captured page exceptions or console errors.
- PASS: updated learning artifacts and local deployment-config checks.
- NOT VERIFIED: official Render schema validation and public deployment/browser
  checks; deployment of repaired code is intentionally pending review/release.

## Remaining limitations

The user's specific persistent production dimming could not be reproduced
locally; the confirmed whole-page rerun pathway was removed and local regression
checks pass. Ordinary fragment loading may still briefly appear on a slow host.
Timings are small local samples, not a Render performance guarantee. Browser
coverage is Chromium at two widths, not every device or assistive technology.
Floyd's trace is cubic in the vertex count; the application keeps a fixed small
campus. Windows batch files were preserved, not executed on this Linux host.
No new public release, paid service, auto-deploy change or main-branch merge was
performed during this task.
