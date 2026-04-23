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


import math

from fdag.dag import (
    CAN_OVERRIDE,
    ReactiveMixin,
    TrackerMixin,
    analyze_method_dependencies_1,
    analyze_method_dependencies_2,
    analyze_method_dependencies_3,
    get_edge_dependencies,
    node,
)
from fdag.dag_cython import ReactiveMixin as CythonReactiveMixin


# noinspection PyMethodMayBeStatic
class MyClass:
    def node_a(self):
        a = self.another_func()
        b = a - 2
        return self.node_b() + 1 + b

    def node_b(self):
        a = 120
        b = 123
        c = a + b
        d = 42 if c > 0 else 0
        return d

    def node_c(self):
        b = self.node_b()
        a = self.node_a()
        return b + 2 * a

    def another_func(self):
        return 2


class DagTest(ReactiveMixin):
    @node
    def node_a(self):
        print("Calculating A (Python)")
        return [1, 2]

    @node
    def node_b(self):
        print("Calculating B (Python)")
        return [i * i for i in self.node_a()]


class Scone(ReactiveMixin):
    @node
    def node_price(self) -> float:
        return (self.node_base_cost() + self.node_jam_cost()) * (1 + self.node_profit_margin())

    @node
    def node_price2(self) -> float:
        if self.node_has_jam():
            return self.node_base_cost() + self.node_jam_cost()
        return self.node_volume()

    @node
    def node_has_jam(self) -> bool:
        return True

    @node
    def node_base_cost(self) -> float:
        return self.node_volume() * 0.003

    @node
    def node_jam_cost(self) -> float:
        return self.node_volume() * 0.006

    @node
    def node_volume(self) -> float:
        return self.node_radius() * self.node_radius() * math.pi * self.node_height()

    @node(CAN_OVERRIDE)
    def node_radius(self) -> float:
        return 15

    @node
    def node_height(self) -> float:
        return 10

    @node
    def node_profit_margin(self) -> float:
        return 0.10


class SconeTracker(TrackerMixin, Scone):
    def __init__(self):
        Scone.__init__(self)
        TrackerMixin.__init__(self)


# --- Cython Implementation Examples ---


class CythonTest(CythonReactiveMixin):
    @node
    def node_a(self) -> list[int]:
        print("Calculating A (Cython)")
        return [1, 2]

    @node
    def node_b(self) -> list[int]:
        print("Calculating B (Cython)")
        return [i * i for i in self.node_a()]


class CythonScone(CythonReactiveMixin):
    @node
    def node_price(self) -> float:
        return (self.node_base_cost() + self.node_jam_cost()) * (1 + self.node_profit_margin())

    @node
    def node_price2(self) -> float:
        if self.node_has_jam():
            return self.node_base_cost() + self.node_jam_cost()
        return self.node_volume()

    @node
    def node_has_jam(self) -> bool:
        return True

    @node
    def node_base_cost(self) -> float:
        return self.node_volume() * 0.003

    @node
    def node_jam_cost(self) -> float:
        return self.node_volume() * 0.006

    @node
    def node_volume(self) -> float:
        return self.node_radius() * self.node_radius() * math.pi * self.node_height()

    @node(CAN_OVERRIDE)
    def node_radius(self) -> float:
        return 15.0

    @node
    def node_height(self) -> float:
        return 10.0

    @node
    def node_profit_margin(self) -> float:
        return 0.10


class Test(ReactiveMixin):
    @node
    def node_a(self):
        print("Calculating A")
        return [1, 2]

    @node
    def node_b(self):
        print("Calculating B")
        return [i * i for i in self.node_a()]


# --- Tests ---


def test_1():
    # Tests a broad AST visitor that finds ALL `self.method()` calls anywhere in the method body.
    # This is a shallow, static analysis that catches everything but lacks context.
    deps_a = analyze_method_dependencies_1(MyClass, "node_a")
    deps_b = analyze_method_dependencies_1(MyClass, "node_b")
    deps_c = analyze_method_dependencies_1(MyClass, "node_c")
    print("Dependencies of A():", deps_a)
    print("Dependencies of B():", deps_b)
    print("Dependencies of C():", deps_c)


def test_2():
    # Tests a restrictive AST visitor that ONLY looks for `self.method()` calls directly
    # inside `return` expressions. It will miss dependencies assigned to variables earlier.
    deps_a = analyze_method_dependencies_2(MyClass, "node_a")
    deps_b = analyze_method_dependencies_2(MyClass, "node_b")
    deps_c = analyze_method_dependencies_2(MyClass, "node_c")
    print("Dependencies of A():", deps_a)
    print("Dependencies of B():", deps_b)
    print("Dependencies of C():", deps_c)


def test_3():
    # Applies the restrictive "return-only" AST analysis to the DagScone class.
    deps = analyze_method_dependencies_2(Scone, "node_price")
    deps2 = analyze_method_dependencies_2(Scone, "node_base_cost")
    deps3 = analyze_method_dependencies_2(Scone, "node_profit_margin")
    deps4 = analyze_method_dependencies_2(Scone, "node_jam_cost")
    print("Dependencies of node_price():", deps)
    print("Dependencies of node_base_cost():", deps2)
    print("Dependencies of node_profit_margin():", deps3)
    print("Dependencies of node_jam_cost():", deps4)


def test_4():
    # Applies the broad "anywhere-in-body" AST analysis to the DagScone class.
    deps = analyze_method_dependencies_1(Scone, "node_price")
    deps2 = analyze_method_dependencies_1(Scone, "node_base_cost")
    deps3 = analyze_method_dependencies_1(Scone, "node_profit_margin")
    deps4 = analyze_method_dependencies_1(Scone, "node_jam_cost")
    print("Dependencies of node_price():", deps)
    print("Dependencies of node_base_cost():", deps2)
    print("Dependencies of node_profit_margin():", deps3)
    print("Dependencies of node_jam_cost():", deps4)


def test_5():
    # Tests if the "return-only" AST visitor can successfully parse dependencies
    # hidden inside list comprehensions (e.g., `return [i * i for i in self.node_a()]`).
    deps = analyze_method_dependencies_2(DagTest, "node_b")
    print("Dependencies of node_b():", deps)


def test_6():
    # Tests an AST visitor that categorizes dependencies into distinct buckets:
    # "edge" (used in `if` conditions) and "input" (used in `return` expressions).
    deps = analyze_method_dependencies_3(Scone, "node_price2")
    print("Dependencies of node_price2():", deps)


def test_7():
    # Tests the hybrid approach:
    # 1. Dynamically executes the method to hydrate the DAG graph.
    # 2. Uses AST statically to find control-flow ("edge") dependencies.
    # 3. Subtracts the edge dependencies from the dynamic ones to isolate data ("input") dependencies.
    scone = Scone()
    print("\nScone price:", scone.node_price2())  # Hydrates the entire graph automatically behind the scenes

    print("--- Fully Hydrated DAG ---")
    for node_name, deps in scone._dag_dependencies.items():
        print(f"{node_name} -> {deps}")

    # Get the direct runtime dependencies specifically for node_price2
    runtime_deps = scone._dag_dependencies.get("node_price2", set())

    print("\nDirect Runtime Dependencies for node_price2:", runtime_deps)

    edge_deps = get_edge_dependencies(Scone, "node_price2")
    print("Static Edge Dependencies (Shallow):", edge_deps)

    input_deps = runtime_deps - edge_deps
    print("Input Dependencies:", input_deps)

    # test override value
    scone.node_radius = 20
    print("\nScone price:", scone.node_price2())


def test_8():
    # Tests Cython
    scone = CythonScone()
    print("\nScone price:", scone.node_price2())  # Hydrates the entire graph automatically behind the scenes

    print("--- Fully Hydrated Cython DAG ---")
    cy_deps = {
        name: {dep.name for dep in node.dependencies} for name, node in scone._dag.nodes.items() if node.dependencies
    }
    for node_name, deps in cy_deps.items():
        print(f"{node_name} -> {deps}")

    # Get the direct runtime dependencies specifically for node_price2
    runtime_deps = cy_deps.get("node_price2", set())

    print("\nDirect Runtime Dependencies for node_price2 (Cython):", runtime_deps)

    edge_deps = get_edge_dependencies(CythonScone, "node_price2")
    print("Static Edge Dependencies (Shallow):", edge_deps)

    input_deps = runtime_deps - edge_deps
    print("Input Dependencies:", input_deps)

    # test override value
    scone.node_radius = 20
    print("\nScone price:", scone.node_price2())


if __name__ == "__main__":
    print("=== Python implementation test ===")
    test = DagTest()
    print("--- Evaluating node_b (Dependencies run first) ---")
    print(test.node_b())
    print("Cached node_b:", test.node_b())

    print("\n--- Testing Cascading Invalidation ---")
    test.invalidate("node_a")
    print(f"Currently Invalidated Nodes: {test._invalidated}")

    print("Recalculating node_b (will also recalculate node_a):")
    print(test.node_b())

    print("\n\n=== Cython implementation test ===")
    cy_test = CythonTest()
    print("--- Evaluating node_b (Dependencies run first) ---")
    print(cy_test.node_b())
    print("Cached node_b:", cy_test.node_b())

    print("\n--- Testing Cascading Invalidation ---")
    cy_test.invalidate("node_a")

    print("Recalculating node_b (will also recalculate node_a):")
    print(cy_test.node_b())

    print("\n\n=== Running static analysis tests ===")
    test_1()
    test_2()
    test_3()
    test_4()
    test_5()
    test_6()
    test_7()
