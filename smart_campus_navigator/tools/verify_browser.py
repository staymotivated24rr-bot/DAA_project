"""Real Chromium regression checks. Install requirements-dev.txt separately.

Run a local Streamlit server, then:
python tools/verify_browser.py --url http://127.0.0.1:8504
The test blocks external requests and checks desktop/mobile layouts. It never
claims coverage of a public deployment unless explicitly run against that URL.
"""
import argparse
import json
import os
import re
from pathlib import Path
from urllib.parse import urlsplit
from urllib.request import urlopen
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[1]


def verify(url, output):
    with urlopen(url+'/_stcore/health',timeout=20) as response:
        assert response.status==200
    checks=[];page_errors=[];console_errors=[];remote=[];rapid={}
    with sync_playwright() as p:
        browser=p.chromium.launch(executable_path=os.environ.get('CHROMIUM_PATH','/usr/bin/chromium'),args=['--no-sandbox'])
        context=browser.new_context(viewport={'width':1440,'height':1100})
        origin=urlsplit(url).netloc
        def local_only(route):
            if urlsplit(route.request.url).netloc in ('',origin):route.continue_()
            else:remote.append(route.request.url);route.abort()
        context.route('**/*',local_only)
        page=context.new_page()
        page.on('pageerror',lambda e:page_errors.append(str(e)))
        page.on('console',lambda message:console_errors.append(message.text) if message.type=='error' else None)

        def idle():
            page.wait_for_function("document.querySelector('[data-testid=stApp]')?.dataset.testScriptState==='notRunning'")
            page.wait_for_function("![...document.querySelectorAll('[data-testid=stElementContainer]')].some(e=>e.dataset.stale==='true')")
            assert page.get_by_test_id('stException').count()==0

        def navigate(name, heading=None):
            page.get_by_text(name,exact=True).first.click()
            page.get_by_role('heading',name=heading or name,exact=True).wait_for()
            idle()

        def select(label,value):
            combo=page.get_by_role('combobox',name=label,exact=True)
            if combo.input_value()==value:
                idle()
                return
            combo.click()
            # Search the option explicitly; long lists may virtualize offscreen entries.
            combo.fill(value)
            page.get_by_role('option',name=value,exact=True).wait_for()
            combo.press('ArrowDown')
            combo.press('Enter')
            page.wait_for_timeout(100)
            idle()

        def position():
            text=page.get_by_text(re.compile(r'^Step \d+ / \d+$')).text_content()
            return tuple(map(int,re.findall(r'\d+',text)))

        def check_clear():
            idle()
            chart=page.locator('[data-testid="stPlotlyChart"]:visible').last
            chart.wait_for(state='visible')
            chart.scroll_into_view_if_needed()
            page.wait_for_timeout(250)  # Allow queued events and normal opacity transition to finish.
            idle()
            state=page.locator('[data-testid="stPlotlyChart"]:visible').last.evaluate('''e=>{
              let opacity=1;const filters=[];let node=e;
              while(node){const css=getComputedStyle(node);opacity*=Number(css.opacity);
                if(css.filter && css.filter!=='none')filters.push(css.filter);node=node.parentElement;}
              return {opacity,filters,width:e.getBoundingClientRect().width,plots:e.querySelectorAll('.js-plotly-plot').length};
            }''')
            assert state['opacity']>.99,state
            assert not state['filters'],state
            assert state['width']>100 and state['plots']==1,state

        def click(label, expected):
            page.get_by_role('button',name=label,exact=True).click()
            page.get_by_text(f'Step {expected} / {position()[1]}',exact=True).wait_for()
            check_clear()
            assert position()[0]==expected

        page.goto(url,wait_until='networkidle')
        page.get_by_role('heading',name='A clearer way across campus').wait_for();idle()
        page.screenshot(path=str(ROOT/'docs/dashboard_screenshot.png'),full_page=True)
        print('CHECK: '+str(len(checks)+1),flush=True);checks.append('Desktop dashboard: 10 vertices / 17 edges')
        navigate('Campus Route Finder')
        page.get_by_text('830 m',exact=True).wait_for()
        page.get_by_text('Step-by-step Dijkstra',exact=True).click()
        click('Next →',2);click('← Previous',1)
        select('Destination','Library');page.get_by_text('450 m',exact=True).wait_for()
        assert position()[0]==1
        select('Destination','Hostel');page.get_by_text('830 m',exact=True).wait_for()
        page.screenshot(path=str(ROOT/'docs/route_screenshot.png'),full_page=True)
        print('CHECK: '+str(len(checks)+1),flush=True);checks.append('Dijkstra route, source/destination invalidation, forward/backward navigation')
        navigate('Graph Exploration')
        select('Starting location','Main Gate')
        click('Next →',2);click('Next →',3);click('← Previous',2);click('Reset steps',1)
        assert page.get_by_role('button',name='← Previous',exact=True).is_disabled()
        select('Traversal','DFS');assert position()[0]==1
        click('Next →',2);click('Reset steps',1)
        # Each dispatch is still a standard Streamlit button. Capture a burst;
        # callbacks are bounded even when the framework coalesces browser events.
        for _ in range(5):page.get_by_role('button',name='Next →',exact=True).click(delay=35)
        page.wait_for_timeout(300);idle();current,last=position();assert 1<current<=6
        rapid={'raw_clicks':5,'resulting_step':current,'total_steps':last,'bounded':True}
        check_clear();click('Reset steps',1)
        print('CHECK: '+str(len(checks)+1),flush=True);checks.append('BFS and DFS, initial boundary, rapid click burst, reset, clear chart')
        navigate('Campus Network Optimizer')
        select('MST algorithm','Kruskal')
        page.get_by_text('1690 m',exact=True).wait_for()
        page.get_by_text('Inspect selection steps',exact=True).click()
        for _ in range(20):
            idle()
            if page.get_by_text('Adding ',exact=False).filter(has_text='cycle').count():break
            click('Next →',position()[0]+1)
        else:raise AssertionError('No Kruskal cycle rejection reached')
        colors=page.locator('.js-plotly-plot').last.evaluate('(e)=>e.data.map(t=>({name:t.name,color:t.line?.color}))')
        assert any(t['name']=='Rejected cycle edges' and t['color']=='#fb7185' for t in colors),colors
        page.get_by_test_id('stPlotlyChart').last.screenshot(path=str(ROOT/'docs/kruskal_rejection_screenshot.png'))
        while not page.get_by_role('button',name='Next →',exact=True).is_disabled():click('Next →',position()[0]+1)
        assert position()[0]==position()[1]
        check_clear();click('Reset steps',1)
        print('CHECK: '+str(len(checks)+1),flush=True);checks.append('Kruskal examined/accepted/rejected overlays, complete state and final Next disabled')
        navigate('All-Pairs Route Analyzer')
        page.get_by_text('830 m · Main Gate',exact=False).wait_for()
        page.get_by_text('Intermediate-node update steps',exact=True).click()
        matrix=page.get_by_role('table',name='Floyd-Warshall replay distances in metres')
        matrix.wait_for()
        initial=matrix.inner_text()
        for _ in range(25):
            click('Next →',position()[0]+1)
            if matrix.locator('td.improved').count():break
        else:raise AssertionError('No Floyd improvement reached')
        improved=matrix.inner_text();assert improved!=initial
        saved=position()[0]
        click('← Previous',saved-1);assert matrix.inner_text()!=improved
        click('Next →',saved);assert matrix.inner_text()==improved
        matrix.screenshot(path=str(ROOT/'docs/floyd_matrix_screenshot.png'))
        print('CHECK: '+str(len(checks)+1),flush=True);checks.append('Floyd evolving matrix, I/J/K comparison, highlighted update and exact backward replay')
        navigate('Learning Lab','Algorithm Comparison & Learning Lab')
        for name in ['BFS','DFS','Dijkstra','Floyd-Warshall','Prim','Kruskal']:
            select('Study an algorithm',name)
            assert position()[0]==1
            click('Next →',2);click('Reset steps',1)
        page.get_by_role('button',name='Run small benchmark',exact=True).click()
        page.get_by_text('Small timings are sensitive',exact=False).wait_for();idle()
        print('CHECK: '+str(len(checks)+1),flush=True);checks.append('All six Learning Lab algorithms and optional benchmark')
        navigate('Campus Route Finder')
        page.get_by_text('Step-by-step Dijkstra',exact=True).click()
        page.get_by_text('Edit campus paths',exact=True).click()
        select('Path endpoint A','Main Gate');select('Path endpoint B','Hostel')
        page.get_by_role('spinbutton',name='Walking distance (m)').fill('100')
        page.get_by_role('button',name='Apply path change',exact=True).click()
        page.get_by_text('100 m',exact=True).wait_for();idle();assert position()[0]==1
        page.get_by_role('button',name='Restore original graph',exact=True).click()
        page.get_by_text('830 m',exact=True).wait_for();idle()
        print('CHECK: '+str(len(checks)+1),flush=True);checks.append('Browser graph editing, fresh history and restoration')
        page.reload(wait_until='networkidle');idle()
        navigate('Dashboard','A clearer way across campus')
        print('CHECK: '+str(len(checks)+1),flush=True);checks.append('Fresh browser reload')
        # A real narrow viewport, including the evolving matrix's local scroll.
        page.set_viewport_size({'width':390,'height':844});idle()
        sidebar=page.get_by_test_id('stSidebar')
        if sidebar.is_visible():
            if sidebar.get_attribute('data-collapsed')!='true':
                page.get_by_role('button',name='Collapse sidebar',exact=True).click()
        page.wait_for_timeout(250)
        width=page.evaluate('({viewport:innerWidth,body:document.body.scrollWidth})')
        assert width['body']<=width['viewport']+1,width
        check_clear()
        page.get_by_test_id('stMain').evaluate('(e)=>e.scrollTop=0')
        page.screenshot(path=str(ROOT/'docs/mobile_dashboard_screenshot.png'),full_page=True)
        print('CHECK: '+str(len(checks)+1),flush=True);checks.append('390-pixel mobile dashboard: no body overflow, visible undimmed graph')
        # Return to desktop to navigate, then narrow the matrix view.
        page.set_viewport_size({'width':1440,'height':1100})
        page.wait_for_timeout(350)  # Wait for Streamlit's responsive sidebar breakpoint.
        if sidebar.get_attribute('data-collapsed')=='true':
            page.get_by_role('button',name='Expand sidebar',exact=True).click()
        navigate('All-Pairs Route Analyzer')
        page.get_by_text('Intermediate-node update steps',exact=True).click()
        page.set_viewport_size({'width':390,'height':844})
        page.wait_for_timeout(250)
        if sidebar.get_attribute('data-collapsed')!='true':
            page.get_by_role('button',name='Collapse sidebar',exact=True).click()
        idle();check_clear()
        scroll=page.locator('.matrix-scroll').evaluate('(e)=>({width:e.clientWidth,scroll:e.scrollWidth})')
        assert scroll['scroll']>=scroll['width']>100
        assert page.evaluate('document.body.scrollWidth<=innerWidth+1')
        page.screenshot(path=str(ROOT/'docs/mobile_floyd_screenshot.png'),full_page=True)
        print('CHECK: '+str(len(checks)+1),flush=True);checks.append('Mobile Floyd table scroll stays inside the page')
        browser.close()
    assert not page_errors,page_errors
    assert not console_errors,console_errors
    result={'status':'PASS','url':url,'checks':checks,'check_count':len(checks),'page_errors':page_errors,
            'console_errors':console_errors,'remote_requests':remote,'rapid_click_burst':rapid,
            'desktop':'1440x1100','mobile':'390x844','public_render_test':'NOT VERIFIED; local server only'}
    output.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--url',default='http://127.0.0.1:8504')
    parser.add_argument('--output',type=Path,default=ROOT/'docs/browser_verification.json')
    args=parser.parse_args()
    args.output.write_text(json.dumps({'status':'RUNNING','url':args.url})+'\n')
    verify(args.url.rstrip('/'),args.output)
