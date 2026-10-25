"""Compare frame construction in isolated processes, not browser paint time.

python tools/measure_rendering.py --source /path/to/project --output result.json
Run separately against the baseline checkout and the repaired checkout.
"""
import argparse
import json
import statistics
import sys
from pathlib import Path
from time import perf_counter


def measure(source):
    sys.path.insert(0,str(source.resolve()))
    from campus.graph import load_campus
    from campus.algorithms import dijkstra
    from campus import visualization
    graph,coordinates=load_campus()
    route=dijkstra(graph,'Main Gate','Hostel')
    edges=list(zip(route.path,route.path[1:]))
    options={}
    if hasattr(visualization,'base_figure'):
        options['base']=visualization.base_figure(graph,coordinates)
    def construct():return visualization.campus_figure(graph,coordinates,edges,route.path,**options)
    for _ in range(5):construct()
    samples=[]
    for _ in range(50):
        start=perf_counter();figure=construct();samples.append((perf_counter()-start)*1000)
    return {'V':10,'E':17,'repeats':50,'warmups':5,'median_ms':round(statistics.median(samples),6),
        'figure_traces':len(figure.data),'cached_base':bool(options),
        'scope':'Plotly Python frame construction only; excludes UI/network/browser paint and one-time base preparation'}


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--source',type=Path,required=True);parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args();result=measure(args.source);args.output.write_text(json.dumps(result,indent=2)+'\n');print(result)
