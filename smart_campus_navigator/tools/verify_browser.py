"""Optional UI smoke test. Server must already run at localhost:8501.

Development dependency: playwright; browser executable /usr/bin/chromium or
CHROMIUM_PATH. Not required for offline app use.
"""
import json
import os
from urllib.request import urlopen
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[1]
with urlopen('http://127.0.0.1:8501/_stcore/health') as response:
    assert response.status == 200

with sync_playwright() as p:
    browser=p.chromium.launch(executable_path=os.environ.get('CHROMIUM_PATH','/usr/bin/chromium'),headless=True,args=['--no-sandbox'])
    context=browser.new_context(viewport={'width':1440,'height':1100})
    # Block all remote requests to verify runtime does not depend on internet.
    remote=[]
    def local_only(route):
        if route.request.url.startswith(('http://127.0.0.1:8501','http://localhost:8501','data:','blob:')):
            route.continue_()
        else:
            remote.append(route.request.url)
            route.abort()
    context.route('**/*',local_only)
    page=context.new_page()
    errors=[]
    page.on('pageerror',lambda error:errors.append(str(error)))
    page.goto('http://127.0.0.1:8501',wait_until='networkidle')
    page.get_by_role('heading',name='A clearer way across campus').wait_for()
    page.locator('.js-plotly-plot').first.wait_for()
    page.wait_for_timeout(1200)
    page.screenshot(path=str(ROOT/'docs/dashboard_screenshot.png'),full_page=True)
    page.get_by_text('Campus Route Finder',exact=True).click()
    page.get_by_text('830 m',exact=True).wait_for()
    page.locator('.js-plotly-plot').first.wait_for()
    page.get_by_text('This implementation completes all reachable',exact=False).wait_for()
    page.wait_for_timeout(1200)
    page.screenshot(path=str(ROOT/'docs/route_screenshot.png'),full_page=True)
    page.get_by_text('Step-by-step Dijkstra',exact=True).click()
    page.get_by_role('button',name='Next →',exact=True).click()
    page.get_by_text('Step 2 / 21',exact=True).wait_for()
    page.get_by_text('Graph Exploration',exact=True).click()
    page.get_by_text('Step 1 / 20',exact=True).wait_for()
    page.get_by_role('button',name='Next →',exact=True).click()
    page.get_by_text('Step 2 / 20',exact=True).wait_for()
    page.get_by_text('Campus Network Optimizer',exact=True).click()
    page.get_by_text('1690 m',exact=True).wait_for()
    page.get_by_text('All-Pairs Route Analyzer',exact=True).click()
    page.get_by_text('830 m · Main Gate',exact=False).wait_for()
    page.get_by_text('Learning Lab',exact=True).click()
    page.get_by_role('button',name='Run small benchmark',exact=True).click()
    page.get_by_text('Small timings are sensitive',exact=False).wait_for()
    assert not errors,errors
    evidence={'status':'PASS','browser':'Chromium via Playwright','viewport':'1440 x 1100',
        'pages_verified':6,'javascript_errors':errors,'blocked_remote_requests':remote,
        'runtime_network':'All non-local HTTP requests blocked during smoke test',
        'screenshots':['dashboard_screenshot.png','route_screenshot.png']}
    (ROOT/'docs/browser_verification.json').write_text(json.dumps(evidence,indent=2),encoding='utf-8')
    print(json.dumps(evidence,indent=2))
    browser.close()
