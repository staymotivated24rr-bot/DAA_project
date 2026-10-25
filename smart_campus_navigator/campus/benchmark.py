"""Deterministic inputs, warm-up, repeated median timings; no plotting needed."""
import csv
import platform
import random
import statistics
from time import perf_counter
from .graph import Graph
from .algorithms import bfs, dfs, dijkstra, floyd_warshall, prim, kruskal


def generated_graph(size):
    rng = random.Random(506 + size)
    nodes = [f'N{i:03}' for i in range(size)]
    graph = Graph(nodes, [(nodes[i-1],nodes[i],rng.randint(1,100)) for i in range(1,size)])
    for i in range(size):
        for j in range(i+2,size):
            if rng.random() < .12:
                graph.set_edge(nodes[i],nodes[j],rng.randint(1,100))
    return graph


def measure(sizes=(12,24,48), repeats=7):
    rows=[]
    for size in sizes:
        graph = generated_graph(size)
        runners = {'BFS':lambda:bfs(graph,graph.nodes[0],False),
            'DFS':lambda:dfs(graph,graph.nodes[0],False),
            'Dijkstra':lambda:dijkstra(graph,graph.nodes[0],trace=False),
            'Floyd-Warshall':lambda:floyd_warshall(graph,False),
            'Prim':lambda:prim(graph,trace=False), 'Kruskal':lambda:kruskal(graph,False)}
        for name, runner in runners.items():
            runner()
            times=[]
            for _ in range(repeats):
                start=perf_counter()
                runner()
                times.append((perf_counter()-start)*1000)
            rows.append({'Algorithm':name,'V':size,'E':len(graph.edges()),'Repeats':repeats,'Median ms':round(statistics.median(times),6)})
    return rows


if __name__ == '__main__':
    from pathlib import Path
    output=Path(__file__).resolve().parents[1]/'docs'
    rows=measure()
    with (output/'benchmark_results.csv').open('w',newline='',encoding='utf-8') as file:
        writer=csv.DictWriter(file,fieldnames=rows[0].keys(),lineterminator='\n');writer.writeheader();writer.writerows(rows)
    (output/'benchmark_environment.txt').write_text(f'Python {platform.python_version()}\n{platform.platform()}\nperf_counter; 1 warm-up; 7 repetitions per workload; medians in milliseconds.\nGraphs: chain plus seeded random edges (p=0.12); graph generation and trace allocation excluded.\n',encoding='utf-8')
    print(f'Wrote {len(rows)} experimental measurements.')
