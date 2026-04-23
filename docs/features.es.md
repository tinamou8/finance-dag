# Características

- [x] Arquitectura de doble motor: Python puro (`fdag.dag`) y Cython de alto rendimiento (`fdag.fast_dag`)
- [x] Transición automática al motor de Python si Cython no está disponible
- [x] Evaluación perezosa reactiva mediante el seguimiento dinámico de dependencias
- [x] Almacenamiento en caché inteligente e invalidación selectiva de nodos
- [x] Sobrescritura de nodos en tiempo de ejecución con `@node(CAN_OVERRIDE)`
- [x] Sugerencias de tipos de Python modernas (3.12+) y cumplimiento de PEP 8
- [ ] Integración fluida con Pandas y NumPy para operaciones matemáticas pesadas
- [ ] Gestión Avanzada de Grafos
    * [ ] Detección estricta y proactiva de ciclos (Ordenación Topológica)
    * [ ] Recorrido iterativo para invalidación para prevenir el desbordamiento de pila
    * [ ] Sobrescritura temporal de grafos para calcular deltas en el análisis de escenarios "what-if"
- [ ] Persistencia y Visualización
    * [ ] Almacenamiento en caché persistente de nodos (MongoDB/SQLite)
    * [ ] Exportación visual de grafos (Graphviz/Mermaid)
    * [ ] Visualización interactiva de grafos basada en web
- [ ] Control de Calidad y Distribución
    * [ ] Suite de pruebas de rendimiento automatizadas
    * [ ] Pipeline de CI/CD multiplataforma y distribución de wheels precompilados
