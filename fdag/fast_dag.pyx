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

# cython: language_level=3
import cython

cdef class Node:
    """
    A C-level extension type representing a single node in the DAG.
    """
    cdef public str name
    cdef public object func
    cdef public list dependencies
    cdef public list dependents
    cdef public bint is_valid
    cdef public bint is_explicit
    cdef public object cached_value
    cdef public int flags
    cdef public list static_dependencies

    def __init__(self, str name, object func, bint is_explicit=False, object explicit_value=None, int flags=0):
        self.name = name
        self.func = func
        self.is_explicit = is_explicit
        self.is_valid = is_explicit
        self.cached_value = explicit_value
        self.dependencies = []
        self.dependents = []
        self.flags = flags
        self.static_dependencies = []

    cpdef void add_dependency(self, Node dep):
        """Creates a bidirectional edge. Prevents duplicates during dynamic access."""
        if dep not in self.dependencies:
            self.dependencies.append(dep)
            dep.dependents.append(self)

    cpdef void invalidate(self):
        """
        Fast C-level recursive invalidation.
        Uses bint (boolean integer) for 0-overhead checks.
        """
        cdef Node dep
        if self.is_explicit or not self.is_valid:
            return

        self.is_valid = False
        self.cached_value = None

        for dep in self.dependents:
            dep.invalidate()


cdef class DAGEngine:
    """Manages the lifecycle and topology of the graph."""
    cdef public dict nodes
    cdef public list call_stack

    def __init__(self):
        self.nodes = {}
        self.call_stack = []

    cpdef Node add_node(self, str name, object func, bint is_explicit=False, object explicit_value=None, int flags=0):
        cdef Node node = Node(name, func, is_explicit, explicit_value, flags)
        self.nodes[name] = node
        return node

    cpdef void add_edge(self, str dependent_name, str dependency_name):
        cdef Node dependent = <Node>self.nodes.get(dependent_name)
        cdef Node dependency = <Node>self.nodes.get(dependency_name)
        if dependent is not None and dependency is not None:
            dependent.add_dependency(dependency)

    cpdef void record_access(self, str accessed_node_name):
        if not self.call_stack:
            return
        cdef str caller = <str>self.call_stack[-1]
        if caller != accessed_node_name:
            self.add_edge(caller, accessed_node_name)

    cpdef void invalidate(self, str name):
        cdef Node node = <Node>self.nodes.get(name)
        if node is not None:
            node.invalidate()

    cpdef object evaluate(self, str name, object instance):
        cdef Node node = <Node>self.nodes.get(name)
        cdef str dep_name
        if node is None:
            raise ValueError(f"Node '{name}' not found in DAG")

        if node.is_valid:
            return node.cached_value

        for dep_name in node.static_dependencies:
            self.evaluate(dep_name, instance)

        self.call_stack.append(name)
        try:
            node.cached_value = node.func(instance)
            node.is_valid = True
            return node.cached_value
        finally:
            self.call_stack.pop()
