"""Measure real Chromium step navigation against a running local app.

Usage: python tools/measure_interactions.py --url http://127.0.0.1:8503
       --output docs/interaction_baseline.json
Only steady-state Next clicks are timed; cold startup/navigation is excluded.
"""
import argparse
import json
import os
import statistics
from pathlib import Path
from time import perf_counter
from playwright.sync_api import sync_playwright


def measure(url, repeats=7):
    with sync_playwright() as p:
        browser=p.chromium.launch(executable_path=os.environ.get('CHROMIUM_PATH','/usr/bin/chromium'),args=['--no-sandbox'])
        page=browser.new_page(viewport={'width':1440,'height':1100})
        errors=[]
        page.on('pageerror',lambda error:errors.append(str(error)))
        page.goto(url,wait_until='networkidle')
        page.get_by_text('Graph Exploration',exact=True).click()
        page.get_by_text('Step 1 / 20',exact=True).wait_for()
        page.wait_for_function("document.querySelector('[data-testid=stApp]').dataset.testScriptState === 'notRunning'")
        # Sample actual computed opacity and Streamlit's stale-element markers.
        page.evaluate('''() => {
          window.samples=[];
          window.sampler=setInterval(()=>{
            const els=[...document.querySelectorAll('[data-testid="stElementContainer"]')];
            const heading=document.querySelector('h1');
            const parent=heading?.closest('[data-testid="stElementContainer"]');
            const values=els.map(e=>Number(getComputedStyle(e).opacity));
            window.samples.push({t:performance.now(),minimumOpacity:Math.min(1,...values),
              stale:els.filter(e=>e.dataset.stale==='true').length,
              titleStale:parent?.dataset.stale==='true',titleOpacity:parent?Number(getComputedStyle(parent).opacity):1});
          },8);
        }''')
        times=[]
        for step in range(2,repeats+2):
            start=perf_counter()
            page.get_by_role('button',name='Next →',exact=True).click()
            page.get_by_text(f'Step {step} / 20',exact=True).wait_for()
            page.wait_for_function("document.querySelector('[data-testid=stApp]').dataset.testScriptState === 'notRunning'")
            page.wait_for_function("![...document.querySelectorAll('[data-testid=stElementContainer]')].some(e=>e.dataset.stale==='true')")
            times.append(round((perf_counter()-start)*1000,3))
        page.wait_for_timeout(300)
        samples=page.evaluate('() => {clearInterval(window.sampler);return window.samples;}')
        final=page.locator('[data-testid="stPlotlyChart"]').first.evaluate('''e=>({opacity:getComputedStyle(e).opacity,filter:getComputedStyle(e).filter,visible:e.getBoundingClientRect().width>0})''')
        browser.close()
        return {'url':url,'viewport':'1440x1100','repeats':repeats,'next_click_to_idle_ms':times,
            'median_ms':round(statistics.median(times),3),
            'samples':len(samples),'sampling_interval_ms':8,
            'stale_samples':sum(s['stale']>0 for s in samples),
            'title_stale_samples':sum(s['titleStale'] for s in samples),
            'minimum_opacity':min(s['minimumOpacity'] for s in samples),
            'title_minimum_opacity':min(s['titleOpacity'] for s in samples),
            'final_chart':final,'javascript_errors':errors,
            'method':'Seven sequential Next clicks after page load; time to progress update and Streamlit idle; actual DOM sampled every 8 ms. Local machine, no CPU/network throttle.'}


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--url',required=True);parser.add_argument('--output',required=True)
    args=parser.parse_args();result=measure(args.url)
    Path(args.output).write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))
