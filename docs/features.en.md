# Features

- [x] Dual-engine architecture: Pure Python (`fdag.dag`) and High-performance Cython (`fdag.fast_dag`)
- [x] Automatic fallback to the Python engine if Cython is unavailable
- [x] Reactive lazy evaluation via dynamic dependency tracking
- [x] Intelligent caching and selective node invalidation
- [x] Node overrides at runtime with `@node(CAN_OVERRIDE)`
- [x] Modern Python type hints (3.12+) and PEP 8 compliance
- [ ] Seamless integration with Pandas and NumPy for heavy math operations
- [ ] Advanced Graph Management
    * [ ] Strict proactive cycle detection (Topological Sort)
    * [ ] Iterative traversal for invalidation to prevent stack overflow
    * [ ] Temporary graph overrides to calculate deltas in what-if scenario analysis
- [ ] Persistence & Visualization
    * [ ] Persistent node caching (MongoDB/SQLite)
    * [ ] Visual graph export (Graphviz/Mermaid)
    * [ ] Interactive web-based graph visualization
- [ ] Quality Assurance & Distribution
    * [ ] Automated performance benchmark suite
    * [ ] Cross-platform CI/CD pipeline and pre-compiled wheel distribution
