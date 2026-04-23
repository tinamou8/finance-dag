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


from typing import Any

try:
    from fdag import fast_dag  # type: ignore[import-untyped, attr-defined]
except ImportError:
    # fallback to JIT compilation
    import pyximport  # type: ignore[import-untyped]

    pyximport.install(language_level=3)
    from fdag import fast_dag  # type: ignore[import-untyped, attr-defined]

from fdag.dag import CAN_OVERRIDE, analyze_method_dependencies_1


class ReactiveMixin:
    """
    A mixin that wires up Python class methods to the fast Cython DAGEngine.
    """

    def __init__(self) -> None:
        super().__setattr__("_dag", fast_dag.DAGEngine())
        dag = super().__getattribute__("_dag")

        for name in dir(self.__class__):
            if name.startswith("__"):
                continue

            attr = getattr(self.__class__, name)
            if callable(attr) and getattr(attr, "__is_reactive_node__", False):
                is_explicit = getattr(attr, "__is_explicit__", False)
                explicit_val = getattr(attr, "__explicit_value__", None)
                flags = getattr(attr, "__node_flags__", 0)
                dag.add_node(name, attr, is_explicit, explicit_val, flags)

        for name in dag.nodes:
            try:
                deps = analyze_method_dependencies_1(self.__class__, name)
            except (ValueError, TypeError, OSError):
                deps = set()
            for dep in deps:
                if dep in dag.nodes:
                    dag.nodes[name].static_dependencies.append(dep)

    def __setattr__(self, name: str, value: Any) -> None:
        if name.startswith("_"):
            super().__setattr__(name, value)
            return

        cls_attr = getattr(self.__class__, name, None)
        if callable(cls_attr) and getattr(cls_attr, "__is_reactive_node__", False):
            if not (getattr(cls_attr, "__node_flags__", 0) & CAN_OVERRIDE):
                msg = f"Cannot override node '{name}' because it was not marked with @node(CAN_OVERRIDE)."
                raise AttributeError(msg)

            dag = super().__getattribute__("_dag")
            if name in dag.nodes:
                node_obj = dag.nodes[name]
                # force cascade invalidation
                node_obj.is_explicit = False
                node_obj.is_valid = True
                node_obj.invalidate()

                node_obj.is_explicit = True
                node_obj.cached_value = value
                node_obj.is_valid = True
            return

        super().__setattr__(name, value)

    def invalidate(self, name: str) -> None:
        """Delegates invalidation entirely to C-speed execution."""
        super().__getattribute__("_dag").invalidate(name)

    def __getattribute__(self, name: str) -> Any:
        if name.startswith("__") or name in {"_dag", "invalidate"}:
            return super().__getattribute__(name)

        dag = super().__getattribute__("_dag")
        if name in dag.nodes:
            dag.record_access(name)
            return lambda *_args, **_kwargs: dag.evaluate(name, self)

        return super().__getattribute__(name)
