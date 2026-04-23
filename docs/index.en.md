# Getting started

finance-dag is a Python library for managing Directed Acyclic Graphs (DAGs) specifically built for financial data workflows, such as portfolio rebalancing and risk calculations.

## Documentation

There is documentation available:

- [Quickstart guide](#quickstart-guide)
- [API documentation](api.md)

## Quickstart guide

Simple guide.

## Example graph

``` mermaid
graph TB
  A[Start] --> B{Error?};
  B -->|Yes| C[Hmm...];
  C --> D[Debug];
  D --> B;
  B ---->|No| E[Yay!];
```
