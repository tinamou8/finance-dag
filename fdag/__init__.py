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

import warnings

try:
    # Prefer the high-performance compiled engine
    from fdag.dag_cython import ReactiveMixin
except ImportError:
    # Fallback seamlessly to the pure Python engine if compilation fails
    from fdag.dag import ReactiveMixin  # type: ignore[assignment]

    warnings.warn("Cython extension not found. Falling back to pure Python DAG engine.", ImportWarning, stacklevel=2)

from fdag.dag import CAN_OVERRIDE, node

__all__ = ["CAN_OVERRIDE", "ReactiveMixin", "node"]
