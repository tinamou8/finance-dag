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


import ast
import contextlib
import functools
import inspect
import textwrap
from collections.abc import Callable
from typing import Any

_STATIC_DEPS_CACHE = {}

CAN_OVERRIDE = 1


def apply_cache(instance, name: str, func: Callable) -> Callable:
    """
    Wraps a method to add caching, dependency tracking, and eager evaluation
    tied to a specific ReactiveMixin instance.
    """

    # noinspection PyProtectedMember
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        cache = instance._cache  # noqa: SLF001
        invalidated_set = instance._invalidated  # noqa: SLF001
        stack = instance._call_stack  # noqa: SLF001

        if name in cache and name not in invalidated_set:
            return cache[name]

        cache_key = (instance.__class__.__name__, name)
        if cache_key not in _STATIC_DEPS_CACHE:
            try:
                deps = analyze_method_dependencies_1(instance.__class__, name)
            except (ValueError, TypeError, OSError):
                deps = set()

            _STATIC_DEPS_CACHE[cache_key] = deps

        static_deps = _STATIC_DEPS_CACHE[cache_key]

        for dep in static_deps:
            if dep not in cache and hasattr(instance, dep):
                getattr(instance, dep)()

        stack.append(name)
        try:
            result = func(*args, **kwargs)
            cache[name] = result
            invalidated_set.discard(name)
            return result
        finally:
            stack.pop()

    return wrapper


def node(arg: Callable | int | None = None) -> Callable:
    def decorator(func: Callable) -> Callable:
        flags = arg if isinstance(arg, int) else 0

        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            return func(*args, **kwargs)

        wrapper.__is_reactive_node__ = True  # type: ignore[attr-defined]
        wrapper.__node_flags__ = flags  # type: ignore[attr-defined]
        return wrapper

    if callable(arg):
        return decorator(arg)
    return decorator


class _FunctionDependencyVisitor(ast.NodeVisitor):
    def __init__(self):
        self.dependencies = set()

    def visit_Call(self, node):
        # Look for self.method() calls
        if (
            isinstance(node.func, ast.Attribute)
            and isinstance(node.func.value, ast.Name)
            and node.func.value.id == "self"
        ):
            self.dependencies.add(node.func.attr)
        self.generic_visit(node)


class _FunctionDependencyVisitor2(ast.NodeVisitor):
    def __init__(self):
        self.dependencies = set()

    def visit_Return(self, node):
        if node.value is not None:
            for child in ast.walk(node.value):
                if isinstance(child, ast.Call):
                    func = child.func
                    if isinstance(func, ast.Attribute) and isinstance(func.value, ast.Name) and func.value.id == "self":
                        self.dependencies.add(func.attr)


class _FunctionDependencyVisitor3(ast.NodeVisitor):
    def __init__(self):
        self.dependencies = {"input": set(), "edge": set()}

    def visit_If(self, node):
        for child in ast.walk(node.test):
            if isinstance(child, ast.Attribute) and isinstance(child.value, ast.Name) and child.value.id == "self":
                self.dependencies["edge"].add(child.attr)
        self.generic_visit(node)

    def visit_Return(self, node):
        if node.value is not None:
            for child in ast.walk(node.value):
                if isinstance(child, ast.Attribute) and isinstance(child.value, ast.Name) and child.value.id == "self":
                    self.dependencies["input"].add(child.attr)


def analyze_method_dependencies_1(cls: type, method_name: str) -> set:
    """
    Analyze and return the set of attribute or method dependencies used within a given method of a class.

    Args:
        cls: The class containing the method.
        method_name: The name of the method to analyze.

    Returns:
        set: A set of dependency names used in the specified method.
    """
    source = inspect.getsource(cls)
    tree = ast.parse(textwrap.dedent(source))

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == method_name:
            visitor = _FunctionDependencyVisitor()
            visitor.visit(node)
            return visitor.dependencies
    msg = f"Method '{method_name}' not found in class '{cls.__name__}'"
    raise ValueError(msg)


def analyze_method_dependencies_2(cls: type, method_name: str) -> set:
    """
    Analyze and return the set of attribute or method dependencies used within a given method of a class.

    Args:
        cls: The class containing the method.
        method_name: The name of the method to analyze.

    Returns:
        set: A set of dependency names used in the specified method.
    """
    source = inspect.getsource(cls)
    tree = ast.parse(source)

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == method_name:
            visitor = _FunctionDependencyVisitor2()
            visitor.visit(node)
            return visitor.dependencies
    msg = f"Method '{method_name}' not found in class '{cls.__name__}'"
    raise ValueError(msg)


def analyze_method_dependencies_3(cls: type, method_name: str) -> dict:
    source = inspect.getsource(cls)
    tree = ast.parse(source)

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == method_name:
            visitor = _FunctionDependencyVisitor3()
            visitor.visit(node)
            return {
                "edge": sorted(visitor.dependencies["edge"]),
                "input": sorted(visitor.dependencies["input"]),
            }
    msg = f"Method '{method_name}' not found in class '{cls.__name__}'"
    raise ValueError(msg)


class _EdgeDependencyVisitor(ast.NodeVisitor):
    def __init__(self):
        self.edge_deps = set()

    def visit_If(self, node):
        for child in ast.walk(node.test):
            if isinstance(child, ast.Attribute) and isinstance(child.value, ast.Name) and child.value.id == "self":
                self.edge_deps.add(child.attr)
        self.generic_visit(node)


def get_edge_dependencies(cls, method_name):
    source = inspect.getsource(getattr(cls, method_name))
    # dedent prevents IndentationError
    tree = ast.parse(textwrap.dedent(source))
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == method_name:
            visitor = _EdgeDependencyVisitor()
            visitor.visit(node)
            return visitor.edge_deps
    msg = f"Method '{method_name}' not found in class '{cls.__name__}'"
    raise ValueError(msg)


def record_dependencies(instance):
    accessed = set()
    originals = {}

    for name in dir(instance):
        if not name.startswith("__"):
            with contextlib.suppress(Exception):
                originals[name] = getattr(instance, name)

    def tracker(name):
        def wrapper(*args, **kwargs):
            accessed.add(name)
            attr = originals[name]
            return attr(*args, **kwargs) if callable(attr) else attr

        return wrapper

    for name, attr in originals.items():
        try:
            if callable(attr):
                setattr(instance, name, tracker(name))
            else:
                setattr(instance.__class__, name, property(lambda _self, n=name: tracker(n)()))
        except Exception:  # noqa: BLE001, S112
            continue

    return accessed


class ReactiveMixin:
    def __init__(self):
        super().__setattr__("_dag_dependencies", {})
        super().__setattr__("_call_stack", [])
        super().__setattr__("_cache", {})
        super().__setattr__("_invalidated", set())

    def __setattr__(self, name: str, value: Any) -> None:
        if name.startswith("_"):
            super().__setattr__(name, value)
            return

        cls_attr = getattr(self.__class__, name, None)
        if callable(cls_attr) and getattr(cls_attr, "__is_reactive_node__", False):
            if not (getattr(cls_attr, "__node_flags__", 0) & CAN_OVERRIDE):
                msg = f"Cannot override node '{name}' because it was not marked with @node(CAN_OVERRIDE)."
                raise AttributeError(msg)

            def override_wrapper(*_args, **_kwargs):
                return value

            override_wrapper.__is_reactive_node__ = True  # type: ignore[attr-defined]
            override_wrapper.__node_flags__ = getattr(cls_attr, "__node_flags__", 0)  # type: ignore[attr-defined]

            super().__setattr__(name, override_wrapper)
            self.invalidate(name)
            return

        super().__setattr__(name, value)

    def invalidate(self, name: str):
        """
        Recursively marks a node and all of its dependents as invalidated,
        clearing them from the cache so they recalculate on the next access.
        """
        invalidated_set = super().__getattribute__("_invalidated")
        cache = super().__getattribute__("_cache")
        deps = super().__getattribute__("_dag_dependencies")

        def cascade(node):
            invalidated_set.add(node)
            if node in cache:
                del cache[node]

            for dependent, dependencies in deps.items():
                if node in dependencies and dependent not in invalidated_set:
                    cascade(dependent)

        cascade(name)

    def __getattribute__(self, name):
        if name.startswith("__") or name in {
            "_dag_dependencies",
            "_call_stack",
            "_cache",
            "_invalidated",
            "invalidate",
        }:
            return super().__getattribute__(name)

        stack = super().__getattribute__("_call_stack")
        deps = super().__getattribute__("_dag_dependencies")
        cache = super().__getattribute__("_cache")
        invalidated_set = super().__getattribute__("_invalidated")

        # map edge from caller to this node
        if stack:
            caller = stack[-1]
            if caller != name:
                deps.setdefault(caller, set()).add(name)

        attr = super().__getattribute__(name)

        if callable(attr):
            if getattr(attr, "__is_reactive_node__", False):
                return apply_cache(self, name, attr)
            return attr

        if name in cache and name not in invalidated_set:
            return cache[name]

        return attr


class TrackerMixin:
    def __init__(self):
        super().__setattr__("_dependencies", set())
        super().__setattr__("_tracking", False)

    def _start_tracking(self):
        self._dependencies.clear()
        self._tracking = True

    def _stop_tracking(self):
        self._tracking = False

    def get_dependencies(self):
        return self._dependencies

    def __getattribute__(self, name):
        if name in {
            "_dependencies",
            "_tracking",
            "_start_tracking",
            "_stop_tracking",
            "get_dependencies",
            "__dict__",
            "__class__",
        }:
            return super().__getattribute__(name)

        if super().__getattribute__("_tracking"):
            super().__getattribute__("_dependencies").add(name)

        return super().__getattribute__(name)
