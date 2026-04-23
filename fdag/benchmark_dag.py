#  Copyright (c) 2026 finance-dag Contributors
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#  http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express
#  or implied. See the License for the specific language governing
#  permissions and limitations under the License.

import timeit

from fdag.dag import ReactiveMixin, node
from fdag.dag_cython import ReactiveMixin as CythonReactiveMixin
from fdag.examples import CythonScone, Scone

ITERATIONS = 10000
LARGE_ITERATIONS = 1000
LARGE_GRAPH_NODES = 100


def generate_large_graph(name, mixin, decorator_name, num_nodes):
    """Dynamically generates a deep chain graph class where node_i depends on node_i+1."""
    lines = [f"class {name}(mixin):"]
    for i in range(num_nodes - 1):
        lines.append(f"    @{decorator_name}")
        lines.append(f"    def node_{i}(self):")
        lines.append(f"        return self.node_{i + 1}() + 1")
    lines.append(f"    @{decorator_name}")
    lines.append(f"    def node_{num_nodes - 1}(self):")
    lines.append("        return 1")

    namespace = {"mixin": mixin, "node": node}
    exec("\n".join(lines), namespace)
    return namespace[name]


def benchmark_python():
    scone = Scone()
    scone.node_price()

    t_cache = timeit.timeit(lambda: scone.node_price(), number=ITERATIONS)

    def full_cycle():
        scone.invalidate("node_radius")
        return scone.node_price()

    t_cycle = timeit.timeit(full_cycle, number=ITERATIONS)
    return t_cache, t_cycle


def benchmark_large_python():
    large_graph = generate_large_graph("LargePythonGraph", ReactiveMixin, "node", LARGE_GRAPH_NODES)
    graph = large_graph()
    graph.node_0()

    t_cache = timeit.timeit(lambda: graph.node_0(), number=LARGE_ITERATIONS)

    def full_cycle():
        graph.invalidate(f"node_{LARGE_GRAPH_NODES - 1}")
        return graph.node_0()

    t_cycle = timeit.timeit(full_cycle, number=LARGE_ITERATIONS)
    return t_cache, t_cycle


def benchmark_large_cython():
    try:
        large_graph = generate_large_graph("LargeCythonGraph", CythonReactiveMixin, "node", LARGE_GRAPH_NODES)
        graph = large_graph()
        graph.node_0()

        t_cache = timeit.timeit(lambda: graph.node_0(), number=LARGE_ITERATIONS)

        def full_cycle():
            graph.invalidate(f"node_{LARGE_GRAPH_NODES - 1}")
            return graph.node_0()

        t_cycle = timeit.timeit(full_cycle, number=LARGE_ITERATIONS)
    except Exception as e:
        return f"Error: {e}", None
    else:
        return t_cache, t_cycle


def benchmark_cython():
    try:
        scone = CythonScone()
        scone.node_price()

        t_cache = timeit.timeit(lambda: scone.node_price(), number=ITERATIONS)

        def full_cycle():
            scone.invalidate("node_radius")
            return scone.node_price()

        t_cycle = timeit.timeit(full_cycle, number=ITERATIONS)
    except Exception as e:
        return f"Error: {e}", None
    else:
        return t_cache, t_cycle


if __name__ == "__main__":
    print("==================================================")
    print(f"Running small graph benchmarks ({ITERATIONS} iterations)...")

    py_cache, py_cycle = benchmark_python()
    cy_cache, cy_cycle = benchmark_cython()

    print("\n--- Python (dag.py) ---")
    print(f"Cache Hit:         {py_cache:.4f}s")
    print(f"Invalidate+Recalc: {py_cycle:.4f}s")

    if isinstance(cy_cache, str):
        print("\n--- Cython (dag_cython.py) ---")
        print(cy_cache)
        print("Note: Cython benchmark failed. Ensure 'Microsoft C++ Build Tools' are installed.")
    else:
        print("\n--- Cython (fast_dag.pyx) ---")
        print(f"Cache Hit:         {cy_cache:.4f}s")
        print(f"Invalidate+Recalc: {cy_cycle:.4f}s")

        print("\n--- Comparison ---")
        print(f"Cache Speedup: {py_cache / cy_cache:.2f}x")
        print(f"Recalc Speedup: {py_cycle / cy_cycle:.2f}x")

    print("\n==================================================")
    print(f"Running LARGE graph benchmarks ({LARGE_GRAPH_NODES} nodes, {LARGE_ITERATIONS} iterations)...")

    py_l_cache, py_l_cycle = benchmark_large_python()
    cy_l_cache, cy_l_cycle = benchmark_large_cython()

    print("\n--- Python (dag.py) ---")
    print(f"Cache Hit:         {py_l_cache:.4f}s")
    print(f"Invalidate+Recalc: {py_l_cycle:.4f}s")

    if isinstance(cy_l_cache, str):
        print("\n--- Cython (fast_dag.pyx) ---")
        print(cy_l_cache)
        print("Note: Cython benchmark failed. Ensure 'Microsoft C++ Build Tools' are installed.")
    else:
        print("\n--- Cython (fast_dag.pyx) ---")
        print(f"Cache Hit:         {cy_l_cache:.4f}s")
        print(f"Invalidate+Recalc: {cy_l_cycle:.4f}s")

        print("\n--- Comparison ---")
        cache_speedup = py_l_cache / cy_l_cache if cy_l_cache > 0 else float("inf")
        recalc_speedup = py_l_cycle / cy_l_cycle if cy_l_cycle > 0 else float("inf")
        print(f"Cache Speedup:  {cache_speedup:.2f}x")
        print(f"Recalc Speedup: {recalc_speedup:.2f}x")
    print("==================================================")
