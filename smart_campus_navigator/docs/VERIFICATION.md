# Verification record

This is the recorded workspace run, not a promise of compatibility with every machine. See the raw logs and data alongside this file.

## User story
A student selects a location pair or edits a path in Streamlit. The session graph feeds handwritten algorithms. Their returned route/tree/events feed Plotly and the displayed metrics. Restore reloads the original JSON. All runtime data and assets are local.

| Boundary / check | Result | Evidence |
|---|---|---|
| Algorithm known answers and edge cases | PASS | 20 algorithm tests in tests/test_algorithms.py |
| Streamlit controls → computation → displayed result | PASS | 3 integration tests in tests/test_app.py; all six sections, algorithm choices, step callbacks, same-node routing, editor, restoration, disconnected warning, invalid self loop |
| Full unittest suite | PASS | **23 tests**, raw output in unit_test_results.txt |
| Python compilation | PASS | `python -m compileall -q app.py campus tests tools` |
| Actual server start | PASS | Streamlit CLI at localhost:8501; HTTP health returned 200; app reached by Chromium |
| Browser rendering and callbacks | PASS | tools/verify_browser.py; six sections, Dijkstra/exploration step buttons, timing button |
| Runtime external dependencies | PASS | Browser blocked all non-local requests; zero remote requests attempted; zero page-level JavaScript errors |
| Campus output | PASS | 830 m Main Gate–Hostel; both MST totals 1690 m, nine edges; computed_results.json |
| Real measurements | RECORDED | benchmark_results.csv: 18 rows, three sizes, six algorithms, seven measurements per workload |
| PDF | PASS | 12 readable pages, all with more than 500 extracted characters; four editable student fields; rendered for inspection |
| PPTX | PASS | 12 slides reopened using python-pptx; all shapes within slide bounds; native editable diagrams and timing chart |
| Screenshots | ACTUAL CAPTURES | dashboard_screenshot.png and route_screenshot.png from local Chromium |

## Reproduction
From the project directory with the environment interpreter:
```sh
python -m unittest discover -s tests -v
python -m compileall -q app.py campus tests tools
python -m streamlit run app.py
```
Optional browser checks require developer tooling (Playwright and Chromium), which is not needed to run or demonstrate the app. `requirements-tested.txt` lists the direct dependency versions used here. PDF text extraction and rendering were additionally checked with the environment's installed PyMuPDF; that tool is not an application dependency.

## Recorded limitations
- Verification host: Linux, Python 3.12.14. Windows batch files were reviewed but could not be executed on this Linux host. They invoke a project-local virtual environment and contain no deletion commands.
- The browser was Chromium at 1440 × 1100. It verifies the tested desktop flow, not every browser, mobile layout or assistive technology.
- The presentation was reopened and structurally inspected. PowerPoint/LibreOffice slide rendering was not available in this environment, so text appearance can vary with installed fonts. Editable text uses Aptos with normal application font fallback.
- Only the request's syllabus mapping was available. An original official syllabus document was not attached.
- Dependency installation needed the execution tool's network permission. Local sockets also needed that runtime capability for the server/browser checks. Both completed successfully; the finished app itself uses no external service.
- Streamlit AppTest can emit a missing ScriptRunContext warning outside a server; it did not cause any failing test. Manual step controls are provided; timed autoplay is omitted.
