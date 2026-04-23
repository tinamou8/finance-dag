# Project Standards & Practices

This document outlines the coding standards, architectural patterns, and engineering practices for the `finance-dag` project. AI agents and contributors should adhere to these guidelines to ensure consistency and maintainability.

## 🎯 Project Overview
`finance-dag` is a Directed Acyclic Graph (DAG) management library specifically designed for financial data workflows. It features a dual-engine architecture:
1. **Pure Python Engine (`fdag.dag`)**: Flexible, lazy-evaluated dynamic graph tracking.
2. **Cython Engine (`fdag.fast_dag` & `fdag.dag_cython`)**: High-performance, lazy-evaluated C-extension for lightning-fast graph routing and pointer-based invalidation.

The library automatically falls back to the pure Python engine if the Cython extension is unavailable.

## 🐍 Python Coding Standards

- **Style Guide:** Follow PEP 8 strictly.
- **Typing:** Use modern Python type hints (Python 3.12+) for all function signatures and class attributes.
  - Prefer `list[str]` over `List[str]`.
  - Use `|` for unions (e.g., `int | None`) instead of `Optional[int]`.
- **Linting & Formatting:**
  - The project uses `ruff` for fast linting/formatting and `mypy` for strict type checking.
  - Due to the metaprogramming nature of the framework, `setattr` and specific `# noqa` / `# type: ignore` markers are used intentionally (e.g., bypassing `B010` for custom function attributes). Do not remove them blindly.
- **Docstrings:** Use Google-style docstrings for complex functions and classes.
- **Naming Conventions:**
  - `snake_case` for variables and functions.
  - `PascalCase` for classes.
  - `UPPER_CASE` for constants.
  - `node_snake_case` for in-graph methods decorated with `@node` in a `ReactiveMixin` derived class.
  - Standard `snake_case` for out-of-graph helper methods.

## 🏗️ Architecture & Core Concepts

- **Lazy Evaluation:** Both the Python and Cython engines wire their dependencies dynamically at runtime via a `call_stack`. This allows the framework to cleanly short-circuit expensive branches behind `if/else` logic without evaluating dead code.
- **Node Overrides:** Nodes can be explicitly overridden at runtime (e.g., `portfolio.node_equity = 3000`).
  - To protect the graph's integrity, nodes **must** be decorated with `@node(CAN_OVERRIDE)` to allow manual assignment. Attempting to override an unprotected node raises an `AttributeError`.
- **Data Processing:** For heavy mathematical operations, vectorize using Pandas/NumPy. Leave the DAG to handle the macro-routing, not the micro-math.

## ⚙️ Build System & Cython Integration

- **Toolchain:** The project uses `uv` for ultra-fast dependency management and `hatchling` (with `hatch-cython`) as the PEP 517 build backend.
- **Compilation:** Run `uv sync` to automatically resolve dependencies, build the Cython extension (`fast_dag.pyx`), and install the project in editable mode.
- **Distribution:** Running `uv build` compiles the C-extension directly into the distributed `.whl` file, eliminating the need for end-users to have a C++ compiler.

## 🧪 Testing Strategy

- **Framework:** Use `pytest` for all tests.
- **Structure:** Mirror the `fdag` directory structure in the `tests/` folder.
- **Matrix Testing:** The project uses `tox` combined with `tox-uv` to execute the test suite across multiple Python environments (3.12, 3.13, 3.14).
  - Command: `uv run tox`

## 🔄 Lifecycle & Deprecation Policy

- **Python Support:** The project supports at minimum the two latest minor versions of Python.
- **Deprecation:** Removal of deprecated functionality follows the [NumPy's approach](https://numpy.org/neps/nep-0023-backwards-compatibility.html):
  - Shall be done after at least 2 releases.
  - Shall be listed in the release notes of the release where the removal happened.
  - Can be done in any minor, but not bugfix, release.

## 🤖 AI Assistant Instructions

When working on this project:
1. **Metaprogramming Awareness:** Be extremely careful when modifying `__getattribute__` and `__setattr__` hooks in the `ReactiveMixin` classes. They are highly optimized to minimize routing overhead.
2. **Dual-Engine Parity:** Any new feature added to the pure Python engine (`dag.py`) must be mapped accurately to the compiled Cython engine (`fast_dag.pyx` & `dag_cython.py`).
3. **Typing and Linting:** Always satisfy `mypy` and `ruff`. If a strict rule conflicts with necessary dynamic behavior, use the explicit suppression markers (e.g., `# noqa: SLF001` or `# type: ignore[attr-defined]`).
4. **Cython Re-compilation:** Remember to instruct the user to run `uv sync` when providing modifications to `.pyx` files so the C-extension updates locally.

## Generated Summaries

When generating a summary of your work, consider these points:
- Describe the "why" of the changes, why the proposed solution is the right one.
- Highlight areas of the proposed changes that require careful review.
- Reduce the verbosity of your comments, more text and detail is not always better. Avoid flattery, avoid stating the obvious, avoid filler phrases, prefer technical clarity over marketing tone.
