# Delivery Plan

Branching model for implementation:

- `main` is the stable branch.
- each roadmap step is developed on a dedicated English-named feature branch.
- changes are rebased from the latest `main` before a new step starts.

Quality gates for each step:

- lint
- format check
- typecheck
- automated tests relevant to the touched scope
