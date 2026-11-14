# SOS-ACO for the Traveling Salesman Problem

Python implementation of a hybrid **Symbiotic Organisms Search + Ant Colony Optimization (SOS-ACO)**
for the Traveling Salesman Problem, based on:

> Y. Wang, Z. Han, *Ant colony optimization for traveling salesman problem based on parameters
> optimization*, **Applied Soft Computing**, vol. 107, 107439 (2021).
> https://doi.org/10.1016/j.asoc.2021.107439

## Problem Statement

Given a set of **n cities** and the pairwise distances `d(i, j)` between them, find the shortest
closed tour that visits **every city exactly once** and returns to the starting city.

Formally, find a permutation `π` of `{1, …, n}` minimising

```
L(π) = Σ_{k=1..n-1} d(π_k, π_{k+1}) + d(π_n, π_1)
```

TSP is a classic **NP-hard** combinatorial optimisation problem: the number of possible tours is
`(n-1)!/2`, so exact methods become impractical for large `n`. Metaheuristics such as ACO provide
high-quality near-optimal tours in reasonable time.

### The sub-problem this project addresses

ACO's performance depends strongly on its parameters (pheromone importance **α**, heuristic
importance **β**, evaporation rate **ρ**, ...). Hand-tuning them is tedious and instance-dependent.
**Goal:** automatically find good ACO parameters *and* a short tour, by letting SOS tune the key
ACO parameters while ACO solves the TSP.

## Approach

| Component | Role |
|-----------|------|
| **ACO (Ant System + elitist)** | Ants build tours using `τ^α · η^β` (η = 1/distance); pheromone evaporates (ρ) and is deposited on good tours. |
| **SOS (Symbiotic Organisms Search)** | Population-based optimiser whose organisms encode `(α, β)`. Uses *mutualism*, *commensalism* and *parasitism* phases. Fitness of an organism = best tour length found by a short ACO run with those parameters. |
| **2-opt local search** | Simple local optimisation applied to each ant's tour to remove crossing edges. |

Workflow:
1. SOS searches the `(α, β)` space (α ∈ [0.1, 5], β ∈ [0.5, 10] by default); other ACO parameters (ρ, Q, ants) are fixed.
2. The best `(α, β)` found is used for a final, longer ACO run.
3. The result is compared against plain ACO with fixed default parameters (α=1, β=2).

> Note: the paper's full text was not accessible when this was written (the abstract states SOS
> optimises two key ACO parameters and a simple local optimisation is added). Choosing α and β as
> the two tuned parameters, and 2-opt as the local optimisation, are my interpretation. This is a
> faithful-in-spirit re-implementation, not a line-by-line reproduction of the paper's results.

## Files

- `sos_aco_tsp.py` – ACO, SOS, 2-opt, TSPLIB loader and command-line driver
- `requirements.txt` – `numpy`, `matplotlib` (plotting only)

## Installation

```bash
pip install -r requirements.txt
```

## Usage

```bash
# random 50-city instance
python sos_aco_tsp.py

# more cities, fixed seed, save tour + convergence plot to result.png
python sos_aco_tsp.py --cities 80 --seed 3 --plot

# TSPLIB instance (EUC_2D), e.g. berlin52.tsp
python sos_aco_tsp.py --tsp berlin52.tsp --ants 30 --iters 150 --plot
```

Options: `--tsp`, `--cities`, `--seed`, `--ants`, `--iters`, `--plot`.

Use as a library:

```python
from sos_aco_tsp import distance_matrix, sos_aco
import numpy as np

coords = np.random.rand(40, 2) * 100
D = distance_matrix(coords)
tour, length, curve, (alpha, beta) = sos_aco(D, n_ants=20, final_iters=100, seed=1)
```

## Key parameters (in `sos_aco`)

| Parameter | Default | Meaning |
|-----------|---------|---------|
| `n_ants` | 20 | Ants per iteration |
| `final_iters` | 100 | ACO iterations for the final run |
| `tune_iters` | 10 | ACO iterations per SOS fitness evaluation |
| `sos_pop`, `sos_iters` | 6, 6 | SOS population size / generations |
| `alpha_bounds`, `beta_bounds` | (0.1,5), (0.5,10) | SOS search ranges |
| `rho` | 0.5 | Pheromone evaporation rate (fixed) |

## Notes

- SOS tuning multiplies runtime (each organism evaluation is a full short ACO run). Reduce
  `sos_pop`/`sos_iters`/`tune_iters` for speed, or increase them for better parameters.
- On small instances (≈30 cities) plain ACO + 2-opt often already reaches the same optimum; the
  benefit of parameter tuning is expected to show on larger instances.
- Pure Python/NumPy; for large instances (>200 cities) consider vectorising ant construction or
  using a candidate-list neighbourhood.
