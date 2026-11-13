# Particle Swarm Optimization for Economic Load Dispatch (ELD)

A lightweight, beginner-friendly Python implementation solving the **Economic Load Dispatch (ELD)** problem for a 3-generator power system using **Particle Swarm Optimization (PSO)**. Built with **standard library only** (no classes, no NumPy, zero third-party dependencies).

---

## Table of Contents

- [Problem Statement](#problem-statement)
- [Research Reference](#research-reference)
- [Key Features](#key-features)
- [Tech Stack](#tech-stack)
- [Prerequisites & Quick Start](#prerequisites--quick-start)
- [Mathematical Formulation](#mathematical-formulation)
  - [1. Objective Function](#1-objective-function)
  - [2. System Constraints](#2-system-constraints)
  - [3. Analytical Benchmark (Lambda-Iteration Method)](#3-analytical-benchmark-lambda-iteration-method)
- [PSO Algorithm & Methodology](#pso-algorithm--methodology)
  - [1. Particle & Swarm Representation](#1-particle--swarm-representation)
  - [2. Penalty-Based Fitness Function](#2-penalty-based-fitness-function)
  - [3. Velocity & Position Update Mechanics](#3-velocity--position-update-mechanics)
  - [4. Constraint Enforcement (Clamping)](#4-constraint-enforcement-clamping)
- [Full Python Source Code](#full-python-source-code)
- [Sample Execution Outputs (3 Independent Runs)](#sample-execution-outputs-3-independent-runs)
- [Performance & Consistency Analysis](#performance--consistency-analysis)
- [Troubleshooting & Hyperparameter Tuning](#troubleshooting--hyperparameter-tuning)

---

## Problem Statement

A thermal power generating station has **3 generators** ($G_1, G_2, G_3$) and must supply a total system load demand of **$P_D = 850\text{ MW}$**. Each generator has a quadratic fuel cost curve $FC_i(P_i)$ in dollars per hour ($\$/\text{hr}$) and strict operational generation bounds $[P_i^{\min}, P_i^{\max}]$.

**Objective:** Determine the optimal power allocation $[P_1, P_2, P_3]$ that minimizes the total generation fuel cost while strictly satisfying the power balance equality constraint and individual generator operating capacities.

### Generator Specifications & Cost Coefficients

The fuel cost of generator $i$ is modeled as:
$$FC_i(P_i) = a_i + b_i \cdot P_i + c_i \cdot P_i^2 \quad (\$/\text{hr})$$

| Generator | $a_i$ (\$/hr) | $b_i$ (\$/MWh) | $c_i$ (\$/$\text{MW}^2\text{h}$) | $P_i^{\min}$ (MW) | $P_i^{\max}$ (MW) |
| :---: | :---: | :---: | :---: | :---: | :---: |
| **$G_1$** | $561$ | $7.92$ | $0.001562$ | $150$ | $600$ |
| **$G_2$** | $310$ | $7.85$ | $0.001940$ | $100$ | $400$ |
| **$G_3$** | $78$  | $7.97$ | $0.004820$ | $50$  | $200$ |

- **Total Demand:** $P_D = 850\text{ MW}$
- **Swarm Particle:** A 3-dimensional vector $[P_1, P_2, P_3]$ representing generator power levels.
- **Fitness Evaluation:** Total fuel cost plus a high penalty factor for power balance violations ($\sum P_i \ne 850$).
- **Constraint Handling:** Clamping each output to $[P_i^{\min}, P_i^{\max}]$ after every velocity update.
- **Expected Benchmark:** The standard textbook optimum for this system is:
  $$P^* \approx [393.17,\, 334.60,\, 122.23]\text{ MW}, \quad \text{Cost}^* \approx \$8194.36/\text{hr}$$

---

## Research Reference

This experiment explores the application of Particle Swarm Optimization to non-linear power system dispatch problems as reviewed in:

- **Survey Article:** *State-of-the-Art Economic Load Dispatch of Power Systems Using Particle Swarm Optimization*
- **ArXiv Repository Link:** [https://ar5iv.arxiv.org/html/1812.11610](https://ar5iv.arxiv.org/html/1812.11610)

> *Note:* The test system parameters above represent a benchmark 3-unit power system commonly studied in power systems analysis and optimization curricula.

---

## Key Features

- **Pure Python Standard Library:** Uses only the built-in `random` module.
- **No NumPy / No Classes:** Implemented procedurally with straightforward lists and loops, ideal for college lab reports and educational demonstrations.
- **Consistent Constraint Handling:** Enforces box constraints via boundary clamping and power balance via penalty functions.
- **Built-in Verification Check:** Automatically compares PSO results with the analytical optimum and verifies power balance within a $0.5\text{ MW}$ tolerance.

---

## Tech Stack

- **Language:** Python 3.8+
- **Standard Library Modules:** `random`
- **Dependencies:** None

---

## Prerequisites & Quick Start

### 1. Prerequisites

Check your Python version:

```bash
python --version
# or
python3 --version
```

### 2. Run the Script

Run the standalone script from your terminal:

```bash
python eld_pso.py
```

---

## Mathematical Formulation

### 1. Objective Function

$$\min_{P_1, P_2, P_3} F_T = \sum_{i=1}^{3} FC_i(P_i) = \sum_{i=1}^{3} \left(a_i + b_i P_i + c_i P_i^2\right)$$

### 2. System Constraints

1. **Power Balance Equality Constraint (neglecting network losses):**
   $$\sum_{i=1}^{3} P_i - P_D = 0 \implies P_1 + P_2 + P_3 = 850\text{ MW}$$

2. **Generator Operating Limits (Inequality Constraints):**
   $$150 \le P_1 \le 600$$
   $$100 \le P_2 \le 400$$
   $$50 \le P_3 \le 200$$

### 3. Analytical Benchmark (Lambda-Iteration Method)

By the classical equal incremental fuel cost criterion (Lagrangian multiplier $\lambda$):

$$\frac{dFC_i}{dP_i} = b_i + 2 c_i P_i = \lambda \implies P_i = \frac{\lambda - b_i}{2 c_i}$$

Summing over all generators:

$$\sum_{i=1}^{3} P_i = \sum_{i=1}^{3} \frac{\lambda - b_i}{2 c_i} = 850 \implies \lambda = \frac{850 + \sum \frac{b_i}{2 c_i}}{\sum \frac{1}{2 c_i}} \approx 9.148263\text{ \$/MWh}$$

Substituting $\lambda$ back into the power equations yields the global theoretical minimum:
- $P_1^* = \frac{9.148263 - 7.92}{2 \times 0.001562} \approx \mathbf{393.17\text{ MW}}$
- $P_2^* = \frac{9.148263 - 7.85}{2 \times 0.001940} \approx \mathbf{334.60\text{ MW}}$
- $P_3^* = \frac{9.148263 - 7.97}{2 \times 0.004820} \approx \mathbf{122.23\text{ MW}}$
- $\sum P_i^* = \mathbf{850.00\text{ MW}}$
- $\text{Total Cost}^* = \mathbf{\$8194.36/\text{hr}}$

---

## PSO Algorithm & Methodology

### 1. Particle & Swarm Representation

- Swarm size: $N = 20$ particles.
- Particle position vector: $X_i = [P_{i,1},\, P_{i,2},\, P_{i,3}]$
- Particle velocity vector: $V_i = [v_{i,1},\, v_{i,2},\, v_{i,3}]$ (initialized to $[0, 0, 0]$).
- Personal best: $\text{pbest}_i = [P_{i,1}^{\text{best}},\, P_{i,2}^{\text{best}},\, P_{i,3}^{\text{best}}]$
- Global best: $\text{gbest} = [P_1^*,\, P_2^*,\, P_3^*]$

### 2. Penalty-Based Fitness Function

To guide particles toward feasible schedules satisfying the power balance:

$$\text{Fitness}(X_i) = \text{Total Cost}(X_i) + \text{PENALTY\_FACTOR} \times \left|\sum_{j=1}^{3} P_{i,j} - 850\right|$$

With $\text{PENALTY\_FACTOR} = 1000$, any particle violating the $850\text{ MW}$ balance incurs a steep penalty, driving the swarm to the balance hyper-plane.

### 3. Velocity & Position Update Mechanics

For each particle $i$ and dimension $d \in \{1, 2, 3\}$ at iteration $t$:

$$v_{i,d}^{(t+1)} = w \cdot v_{i,d}^{(t)} + c_1 r_1 \left(\text{pbest}_{i,d} - P_{i,d}^{(t)}\right) + c_2 r_2 \left(\text{gbest}_d - P_{i,d}^{(t)}\right)$$
$$P_{i,d}^{(t+1)} = P_{i,d}^{(t)} + v_{i,d}^{(t+1)}$$

**Parameters:**
- Inertia weight: $w = 0.7$
- Cognitive coefficient: $c_1 = 1.5$
- Social coefficient: $c_2 = 1.5$
- Stochastic variables: $r_1, r_2 \sim U(0, 1)$

### 4. Constraint Enforcement (Clamping)

After position updates, box constraints are strictly applied:

$$P_{i,d} = \max\left(P_d^{\min},\, \min\left(P_d^{\max},\, P_{i,d}\right)\right)$$

---

## Full Python Source Code

The complete standalone implementation [`eld_pso.py`](eld_pso.py):

```python
# ==============================================================================
# Experiment: Economic Load Dispatch (ELD) using Particle Swarm Optimization (PSO)
# Description: Minimizes total generation fuel cost for 3 generators supplying 850 MW
# ==============================================================================

# Step 1: Import random (standard library only)
import random

# PSO Parameters and Constants
N = 20                 # Number of particles in swarm
W = 0.7                # Inertia weight
C1 = 1.5               # Cognitive learning acceleration coefficient
C2 = 1.5               # Social learning acceleration coefficient
ITERATIONS = 200       # Maximum iterations (increase if power mismatch > 0.5 MW)
PENALTY_FACTOR = 1000  # Penalty for power balance mismatch (increase if mismatch > 0.5 MW)
DEMAND = 850           # Total power demand in MW

# Step 2: Define generator data and fitness function
# Each generator has cost coefficients a, b, c ($/hr) and operating limits [min, max] (MW)
# Cost equation: Cost = a + b*P + c*(P^2)
generators = [
    {"a": 561, "b": 7.92, "c": 0.001562, "min": 150, "max": 600},
    {"a": 310, "b": 7.85, "c": 0.001940, "min": 100, "max": 400},
    {"a": 78,  "b": 7.97, "c": 0.004820, "min": 50,  "max": 200}
]

def total_cost(position):
    # Calculates the pure fuel cost across all 3 generators ($/hr)
    cost = 0.0
    for g, p in zip(generators, position):
        cost += g["a"] + g["b"] * p + g["c"] * (p ** 2)
    return cost

def fitness(position):
    # Fitness = Total Fuel Cost + Penalty for violating power balance (sum(P) = 850 MW)
    # Lower fitness indicates a better solution
    power_mismatch = abs(sum(position) - DEMAND)
    return total_cost(position) + PENALTY_FACTOR * power_mismatch


# Step 3: Initialize each particle with random position inside limits and zero velocity
particles = []
velocities = []
pbests = []
pbest_fitnesses = []

for _ in range(N):
    # Random initial power generation within [min, max] for each unit
    pos = [random.uniform(g["min"], g["max"]) for g in generators]
    vel = [0.0, 0.0, 0.0]
    particles.append(pos)
    velocities.append(vel)
    pbests.append(list(pos))
    pbest_fitnesses.append(fitness(pos))

# Identify initial global best (gbest)
best_idx = pbest_fitnesses.index(min(pbest_fitnesses))
gbest = list(pbests[best_idx])
gbest_fitness = pbest_fitnesses[best_idx]


# Step 4: Run PSO for 200 iterations
print("--- Particle Swarm Optimization in Progress ---")
for it in range(1, ITERATIONS + 1):
    for i in range(N):
        for d in range(3):
            r1 = random.random()
            r2 = random.random()
            # Update velocity using inertia, cognitive, and social components
            velocities[i][d] = (
                W * velocities[i][d]
                + C1 * r1 * (pbests[i][d] - particles[i][d])
                + C2 * r2 * (gbest[d] - particles[i][d])
            )
            # Update position
            particles[i][d] += velocities[i][d]

            # Clamp each generator's output to its minimum and maximum limits
            if particles[i][d] < generators[d]["min"]:
                particles[i][d] = generators[d]["min"]
            elif particles[i][d] > generators[d]["max"]:
                particles[i][d] = generators[d]["max"]

        # Evaluate fitness of updated position
        current_fit = fitness(particles[i])

        # Update personal best (pbest) if current position is improved
        if current_fit < pbest_fitnesses[i]:
            pbests[i] = list(particles[i])
            pbest_fitnesses[i] = current_fit

            # Update global best (gbest) if personal best exceeds it
            if current_fit < gbest_fitness:
                gbest = list(particles[i])
                gbest_fitness = current_fit

    # Print iteration number and gbest cost every 20 iterations
    if it % 20 == 0:
        print(f"Iteration {it:3d}: gbest cost = {total_cost(gbest):.2f} $/hr (Power Sum = {sum(gbest):.2f} MW)")


# Step 5: Print final gbest outputs, power sum, and total fuel cost
final_outputs = [round(p, 2) for p in gbest]
final_power_sum = sum(gbest)
final_fuel_cost = total_cost(gbest)

print("\n--- Final PSO Result ---")
print(f"Optimal Generator Outputs (P1, P2, P3): {final_outputs} MW")
print(f"Total Power Generated:                {final_power_sum:.2f} MW")
print(f"Total Fuel Cost:                      {final_fuel_cost:.2f} $/hr")


# CHECK: Compare against known theoretical optimum
known_optimum_cost = 8194.36
cost_diff = final_fuel_cost - known_optimum_cost
power_mismatch = abs(final_power_sum - DEMAND)

print("\n--- Verification Check ---")
print(f"Theoretical Optimum:                  P = [393.17, 334.60, 122.23] MW, Cost = {known_optimum_cost:.2f} $/hr")
print(f"Difference in Fuel Cost:              {cost_diff:+.2f} $/hr")
print(f"Mismatch in Power Balance:            {power_mismatch:.4f} MW")

if power_mismatch > 0.5:
    print("WARNING: Power sum is off by > 0.5 MW. Please increase PENALTY_FACTOR or ITERATIONS.")
else:
    print("SUCCESS: Power balance constraint satisfied within 0.5 MW tolerance.")
```

---

## Sample Execution Outputs (3 Independent Runs)

### Run 1
```text
--- Particle Swarm Optimization in Progress ---
Iteration  20: gbest cost = 8210.31 $/hr (Power Sum = 849.97 MW)
Iteration  40: gbest cost = 8210.65 $/hr (Power Sum = 850.02 MW)
Iteration  60: gbest cost = 8210.25 $/hr (Power Sum = 850.00 MW)
Iteration  80: gbest cost = 8210.25 $/hr (Power Sum = 850.00 MW)
Iteration 100: gbest cost = 8210.25 $/hr (Power Sum = 850.00 MW)
Iteration 120: gbest cost = 8210.25 $/hr (Power Sum = 850.00 MW)
Iteration 140: gbest cost = 8210.25 $/hr (Power Sum = 850.00 MW)
Iteration 160: gbest cost = 8210.25 $/hr (Power Sum = 850.00 MW)
Iteration 180: gbest cost = 8210.25 $/hr (Power Sum = 850.00 MW)
Iteration 200: gbest cost = 8210.25 $/hr (Power Sum = 850.00 MW)

--- Final PSO Result ---
Optimal Generator Outputs (P1, P2, P3): [464.63, 272.44, 112.93] MW
Total Power Generated:                850.00 MW
Total Fuel Cost:                      8210.25 $/hr

--- Verification Check ---
Theoretical Optimum:                  P = [393.17, 334.60, 122.23] MW, Cost = 8194.36 $/hr
Difference in Fuel Cost:              +15.89 $/hr
Mismatch in Power Balance:            0.0000 MW
SUCCESS: Power balance constraint satisfied within 0.5 MW tolerance.
```

### Run 2
```text
--- Particle Swarm Optimization in Progress ---
Iteration  20: gbest cost = 8206.83 $/hr (Power Sum = 849.90 MW)
Iteration  40: gbest cost = 8207.74 $/hr (Power Sum = 850.00 MW)
Iteration  60: gbest cost = 8207.74 $/hr (Power Sum = 850.00 MW)
Iteration  80: gbest cost = 8207.73 $/hr (Power Sum = 850.00 MW)
Iteration 100: gbest cost = 8207.73 $/hr (Power Sum = 850.00 MW)
Iteration 120: gbest cost = 8207.73 $/hr (Power Sum = 850.00 MW)
Iteration 140: gbest cost = 8207.73 $/hr (Power Sum = 850.00 MW)
Iteration 160: gbest cost = 8207.73 $/hr (Power Sum = 850.00 MW)
Iteration 180: gbest cost = 8207.73 $/hr (Power Sum = 850.00 MW)
Iteration 200: gbest cost = 8207.73 $/hr (Power Sum = 850.00 MW)

--- Final PSO Result ---
Optimal Generator Outputs (P1, P2, P3): [341.64, 400.0, 108.36] MW
Total Power Generated:                850.00 MW
Total Fuel Cost:                      8207.73 $/hr

--- Verification Check ---
Theoretical Optimum:                  P = [393.17, 334.60, 122.23] MW, Cost = 8194.36 $/hr
Difference in Fuel Cost:              +13.37 $/hr
Mismatch in Power Balance:            0.0000 MW
SUCCESS: Power balance constraint satisfied within 0.5 MW tolerance.
```

### Run 3
```text
--- Particle Swarm Optimization in Progress ---
Iteration  20: gbest cost = 8236.72 $/hr (Power Sum = 850.09 MW)
Iteration  40: gbest cost = 8221.22 $/hr (Power Sum = 849.99 MW)
Iteration  60: gbest cost = 8221.55 $/hr (Power Sum = 850.00 MW)
Iteration  80: gbest cost = 8221.55 $/hr (Power Sum = 850.00 MW)
Iteration 100: gbest cost = 8221.55 $/hr (Power Sum = 850.00 MW)
Iteration 120: gbest cost = 8221.55 $/hr (Power Sum = 850.00 MW)
Iteration 140: gbest cost = 8221.55 $/hr (Power Sum = 850.00 MW)
Iteration 160: gbest cost = 8215.52 $/hr (Power Sum = 850.00 MW)
Iteration 180: gbest cost = 8213.48 $/hr (Power Sum = 850.00 MW)
Iteration 200: gbest cost = 8213.48 $/hr (Power Sum = 850.00 MW)

--- Final PSO Result ---
Optimal Generator Outputs (P1, P2, P3): [313.69, 400.0, 136.31] MW
Total Power Generated:                850.00 MW
Total Fuel Cost:                      8213.48 $/hr

--- Verification Check ---
Theoretical Optimum:                  P = [393.17, 334.60, 122.23] MW, Cost = 8194.36 $/hr
Difference in Fuel Cost:              +19.12 $/hr
Mismatch in Power Balance:            0.0008 MW
SUCCESS: Power balance constraint satisfied within 0.5 MW tolerance.
```

---

## Performance & Consistency Analysis

| Evaluation Metric | Run 1 | Run 2 | Run 3 | Analytical Optimum |
| :--- | :---: | :---: | :---: | :---: |
| **$P_1$ (MW)** | $464.63$ | $341.64$ | $313.69$ | $393.17$ |
| **$P_2$ (MW)** | $272.44$ | $400.00$ | $400.00$ | $334.60$ |
| **$P_3$ (MW)** | $112.93$ | $108.36$ | $136.31$ | $122.23$ |
| **Total Generation ($\sum P_i$)** | **850.00 MW** | **850.00 MW** | **850.00 MW** | **850.00 MW** |
| **Power Balance Error** | $0.0000$ MW | $0.0000$ MW | $0.0008$ MW | $0.0000$ MW |
| **Total Fuel Cost (\$/hr)** | **8210.25** | **8207.73** | **8213.48** | **8194.36** |
| **Deviation from Optimum** | $+15.89$ \$/hr | $+13.37$ \$/hr | $+19.12$ \$/hr | $0.00$ \$/hr |
| **Relative Error** | **0.19%** | **0.16%** | **0.23%** | **0.00%** |

### Observations

1. **Exact Power Balance Satisfaction:** Across all runs, the power balance error remains $\le 0.0008\text{ MW}$, vastly superior to the acceptable tolerance of $0.5\text{ MW}$.
2. **Stable Cost Optimization:** The cost obtained by PSO is consistently within **0.16% to 0.23%** of the theoretical global minimum of $\$8194.36/\text{hr}$.
3. **Flat Cost Surface:** The quadratic cost curve exhibits a relatively flat curvature near the minimum along the constraint hyper-plane $\sum P_i = 850$, allowing different generator allocations (such as $G_2$ reaching its upper bound of $400\text{ MW}$) to achieve near-identical operating costs.

---

## Troubleshooting & Hyperparameter Tuning

If you modify system parameters or apply this script to a larger system:

1. **Power Balance Mismatch $> 0.5\text{ MW}$:**
   - Increase `PENALTY_FACTOR` from `1000` to `5000` or `10000`.
   - Increase `ITERATIONS` from `200` to `400` or `500`.
2. **Premature Convergence / Trapping in Local Minima:**
   - Increase population size `N` from `20` to `40` or `50`.
   - Gradually reduce the inertia weight $w$ over iterations (e.g., linearly decaying from $0.9$ to $0.4$).
3. **Generator Violations:**
   - Operating limits are automatically clamped on each step; ensure that the total demand $P_D$ lies within $\left[\sum P_i^{\min},\, \sum P_i^{\max}\right] = [300\text{ MW},\, 1200\text{ MW}]$.
