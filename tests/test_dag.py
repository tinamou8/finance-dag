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

import pytest

from fdag import CAN_OVERRIDE, ReactiveMixin, node
from fdag.dag import ReactiveMixin as PythonReactiveMixin


class Portfolio(ReactiveMixin):
    @node
    def node_total_value(self) -> float:
        return self.node_cash() + self.node_equity()

    @node
    def node_cash(self) -> float:
        return 1000.0

    @node(CAN_OVERRIDE)
    def node_equity(self) -> float:
        return 5000.0


def test_dag_evaluation_and_caching():
    portfolio = Portfolio()

    # Initial evaluation
    assert portfolio.node_total_value() == 6000.0

    # Verify nodes were cached (implementation specific check for Python engine)
    if hasattr(portfolio, "_cache"):
        assert "node_total_value" in portfolio._cache
        assert "node_cash" in portfolio._cache
        assert "node_equity" in portfolio._cache
        assert portfolio._cache["node_total_value"] == 6000.0
    elif hasattr(portfolio, "_dag"):
        nodes = portfolio._dag.nodes
        assert nodes["node_total_value"].is_valid
        assert nodes["node_cash"].is_valid
        assert nodes["node_equity"].is_valid
        assert nodes["node_total_value"].cached_value == 6000.0


def test_cascade_invalidation():
    portfolio = Portfolio()
    portfolio.node_total_value()  # Hydrate the DAG

    # Invalidate a base metric
    portfolio.invalidate("node_cash")

    if hasattr(portfolio, "_cache"):
        assert "node_cash" not in portfolio._cache
        assert "node_total_value" not in portfolio._cache
        assert "node_equity" in portfolio._cache  # Unaffected sibling node remains cached
    elif hasattr(portfolio, "_dag"):
        nodes = portfolio._dag.nodes
        assert not nodes["node_cash"].is_valid
        assert not nodes["node_total_value"].is_valid
        assert nodes["node_equity"].is_valid


def test_node_override():
    portfolio = Portfolio()
    assert portfolio.node_total_value() == 6000.0

    # Override node explicitly
    portfolio.node_equity = 3000.0

    # It should invalidate the dependent node
    if hasattr(portfolio, "_cache"):
        assert "node_total_value" not in portfolio._cache
    elif hasattr(portfolio, "_dag"):
        assert not portfolio._dag.nodes["node_total_value"].is_valid

    # DAG recalculates correctly with the new override
    assert portfolio.node_total_value() == 4000.0


def test_cannot_override_without_flag_python():
    class CannotOverrideNodeClass(PythonReactiveMixin):
        @node
        def node_a(self) -> float:
            return 42.0

    instance = CannotOverrideNodeClass()
    with pytest.raises(AttributeError, match=r"Cannot override node 'node_a' because it was not marked with @node\(CAN_OVERRIDE\)\."):
        instance.node_a = 100.0


def test_cannot_override_without_flag_cython():
    try:
        from fdag.dag_cython import ReactiveMixin as CythonReactiveMixin
    except ImportError:
        pytest.skip("Cython extension not found. Skipping Cython-specific override test.")

    class CannotOverrideNodeClass(CythonReactiveMixin):
        @node
        def node_a(self) -> float:
            return 42.0

    instance = CannotOverrideNodeClass()
    with pytest.raises(AttributeError, match=r"Cannot override node 'node_a' because it was not marked with @node\(CAN_OVERRIDE\)\."):
        instance.node_a = 100.0
