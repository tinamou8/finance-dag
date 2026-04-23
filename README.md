# finance-dag: a finance focused DAG library for Python

[![Test status](https://github.com/tinamou8/finance-dag/workflows/CI/badge.svg)](https://github.com/tinamou8/finance-dag/actions)
[![PyPI package](https://badge.fury.io/py/finance-dag.svg)](https://pypi.python.org/pypi/finance-dag)
[![Docs](https://readthedocs.org/projects/finance-dag/badge/?version=latest)](https://finance-dag.readthedocs.io/en/latest/)

## Introduction

finance-dag is a Python library for managing Directed Acyclic Graphs (DAGs) specifically built for financial data workflows, such as portfolio rebalancing and risk calculations.

## Installing

Requires Python 3.12+. Download and install the latest release:

```bash
pip install finance-dag
```

## Quick Start

Define your financial logic using the `ReactiveMixin` and decorate your nodes with `@node`. Dependencies are resolved automatically.

```python
from fdag import ReactiveMixin, node


class Portfolio(ReactiveMixin):
    @node
    def node_total_value(self) -> float:
        return self.node_cash() + self.node_equity()

    @node
    def node_cash(self) -> float:
        return 1000.0

    @node
    def node_equity(self) -> float:
        return 5000.0


if __name__ == "__main__":
    portfolio = Portfolio()

    # Calculates cash, equity, and total_value automatically
    print("Total Value:", portfolio.node_total_value())  # 6000.0

    # Cached access (instantaneous)
    print("Cached Value:", portfolio.node_total_value())

    # Changing value invalidates a base node; cascades to dependent nodes
    portfolio.node_equity = 3000

    # Recalculates total_value on next access
    print("Recalculated Value:", portfolio.node_total_value())  # 4000.0
```

## [Documentation](https://finance-dag.readthedocs.io/en/latest/)

- [Changelog](https://finance-dag.readthedocs.io/en/latest/changelog.html)

## Features

- Application Modeling: model relationships between entities in a straight-forward way
- Dependency Tracking: automatically infers and tracks dependencies between nodes
- Caching and Recalculation: caches computed values, invalidates only affected dependent nodes, and recomputes them when needed
- Graph Evaluation: eagerly evaluates static parts of the graph while lazily computing reactive nodes on demand

## License

This project is licensed under the Apache License, Version 2.0. See `LICENSE.txt` for the full text.
