# Job Shop Scheduling Problem (JSP) using Genetic Algorithm

A lightweight, beginner-friendly Python implementation solving the classic **Job Shop Scheduling Problem ($3 \times 3$)** using a Genetic Algorithm (GA) with an operation-based permutation-with-repetition encoding. Built with **standard library only** (no classes, no NumPy, zero third-party dependencies).

---

## Table of Contents

- [Problem Statement](#problem-statement)
- [Research Reference](#research-reference)
- [Key Features](#key-features)
- [Tech Stack](#tech-stack)
- [Prerequisites & Quick Start](#prerequisites--quick-start)
- [Algorithm & Methodology](#algorithm--methodology)
  - [1. Chromosome Representation](#1-chromosome-representation)
  - [2. Schedule Decoding & Fitness Calculation](#2-schedule-decoding--fitness-calculation)
  - [3. Genetic Operators](#3-genetic-operators)
  - [4. Brute-Force Verification](#4-brute-force-verification)
- [Full Python Source Code](#full-python-source-code)
- [Sample Execution Output](#sample-execution-output)
- [Optimal Schedule & Gantt Timeline](#optimal-schedule--gantt-timeline)
- [Troubleshooting & Tuning](#troubleshooting--tuning)

---

## Problem Statement

### Job Shop Scheduling ($3 \text{ jobs} \times 3 \text{ machines}$)

There are **3 jobs** ($J_1, J_2, J_3$) and **3 machines** ($M_1, M_2, M_3$). 
- Each job consists of an ordered sequence of operations that must visit specific machines in a strict technological order.
- Each operation requires exclusive access to its designated machine for its specified duration without interruption (non-preemptive).
- Each machine can process at most one operation at any given time.
- **Objective:** Find an optimal operation sequence that minimizes the **makespan** ($C_{\max}$), which is the total completion time when the last operation finishes.

### Job Operation Matrix

| Job | Operation 1 | Operation 2 | Operation 3 | Total Job Workload |
| :---: | :---: | :---: | :---: | :---: |
| **$J_1$** | $M_1$ ($3$ units) | $M_2$ ($3$ units) | $M_3$ ($3$ units) | $9$ |
| **$J_2$** | $M_1$ ($2$ units) | $M_3$ ($3$ units) | $M_2$ ($4$ units) | $9$ |
| **$J_3$** | $M_2$ ($3$ units) | $M_1$ ($2$ units) | $M_3$ ($1$ unit)  | $6$ |

### Machine Workload Breakdown

- **Machine 1 ($M_1$):** $J_1(3) + J_2(2) + J_3(2) = 7$ units
- **Machine 2 ($M_2$):** $J_1(3) + J_2(4) + J_3(3) = 10$ units
- **Machine 3 ($M_3$):** $J_1(3) + J_2(3) + J_3(1) = 7$ units
- **Theoretical Lower Bound:** $\max(\text{Job lengths}, \text{Machine loads}) = \max(9, 10) = 10$. Due to machine conflicts and precedence constraints, the true global optimum is **12**.

---

## Research Reference

This implementation is based on the permutation-with-repetition encoding and genetic operators described in:

- **Paper:** *Genetic Algorithms for Job Shop Scheduling Problems*
- **Author:** Christian Bierwirth
- **Reference Link:** [https://www.academia.edu/62943863/Genetic_Algorithms_for_Job_Shop_Scheduling_Problems](https://www.academia.edu/62943863/Genetic_Algorithms_for_Job_Shop_Scheduling_Problems)

---

## Key Features

- **Standard Library Only:** Requires only Python's built-in `random` and `itertools` modules.
- **No Complex OOP / No NumPy:** Written using simple procedural functions and dictionaries for college lab records.
- **Guaranteed Valid Schedules:** Uses permutation-with-repetition encoding so that every candidate chromosome translates directly into a feasible schedule without needing repair algorithms.
- **Complete Verification:** Includes an exhaustive permutation search (`set(itertools.permutations(...))`) that tests all $1,680$ unique schedules to mathematically verify that the GA achieves the global optimum ($12$).

---

## Tech Stack

- **Language:** Python 3.8+ (compatible with Python 3.8, 3.9, 3.10, 3.11, 3.12, 3.13)
- **Dependencies:** None (Python Standard Library only)
- **Core Modules:** `random`, `itertools`

---

## Prerequisites & Quick Start

### 1. Prerequisites

Verify that Python 3 is installed on your system:

```bash
python --version
# or
python3 --version
```

### 2. Run the Script

Clone or navigate to the directory containing `job_shop_ga.py` and run:

```bash
python job_shop_ga.py
```

---

## Algorithm & Methodology

### 1. Chromosome Representation

A chromosome is represented as a list of 9 integers containing each job ID ($1, 2, 3$) repeated exactly 3 times.

$$\text{Chromosome} = [2, 1, 3, 3, 1, 2, 1, 2, 3]$$

- The $k$-th occurrence of integer $j$ denotes the $k$-th operation of job $j$.
- Because each job's operations appear in order, **precedence constraints are satisfied automatically**.
- The total search space consists of:

$$\frac{9!}{(3! \times 3! \times 3!)} = \frac{362,880}{6 \times 6 \times 6} = 1,680 \text{ unique schedules}$$

### 2. Schedule Decoding & Fitness Calculation

The fitness function decodes the chromosome from left to right into a semi-active schedule:

1. Maintain tracking dictionaries:
   - `job_step[j]`: Current operation index for job $j$ ($0, 1, 2$).
   - `job_ready_time[j]`: Earliest time job $j$ finishes its previous operation.
   - `machine_ready_time[m]`: Earliest time machine $m$ finishes its current assignment.
2. For each gene $j$:
   $$\text{start} = \max(\text{job\_ready\_time}[j],\, \text{machine\_ready\_time}[m])$$
   $$\text{end} = \text{start} + \text{duration}$$
   $$\text{job\_ready\_time}[j] = \text{end}$$
   $$\text{machine\_ready\_time}[m] = \text{end}$$
3. **Fitness (Makespan):**
   $$\text{Makespan} = \max_{m \in \{1, 2, 3\}}(\text{machine\_ready\_time}[m])$$

### 3. Genetic Operators

- **Selection:** Elitist selection where the population is sorted by makespan, choosing the best two individuals (`parent1 = population[0]`, `parent2 = population[1]`).
- **Order-Preserving Crossover:**
  1. Child takes the first half ($\lfloor 9 / 2 \rfloor = 4$ genes) directly from `parent1`.
  2. Remaining positions are filled sequentially using `parent2`'s gene order, only admitting a job if its count in the child is less than 3.
- **Swap Mutation:** With probability $0.3$, randomly selects two indices in the offspring and swaps their positions.
- **Replacement:** The weakest chromosome (highest makespan, at `population[-1]`) is replaced by the new child.

### 4. Brute-Force Verification

An exhaustive search explores all $1,680$ unique permutations generated by `set(itertools.permutations([1,1,1, 2,2,2, 3,3,3]))` and verifies that the minimum achievable makespan is exactly **12**.

---

## Full Python Source Code

The complete standalone file [`job_shop_ga.py`](job_shop_ga.py):

```python
# ==============================================================================
# Experiment: Job Shop Scheduling Problem (JSP) using Genetic Algorithm (GA)
# Description: Solves a 3-job x 3-machine scheduling problem minimizing makespan
# ==============================================================================

# Step 1: Import random and itertools (standard library only)
import random
import itertools

# Seed for reproducible lab record output (demonstrates convergence to 12)
random.seed(29)

# Algorithm Constants
POPULATION_SIZE = 6    # Increase to 10 if GA gets stuck above 12
GENERATIONS = 50       # Increase to 100 if GA gets stuck above 12
MUTATION_RATE = 0.3

# Step 2: Define jobs data and fitness(chromosome) function
# Each job is a list of (machine, processing_time) operations in fixed technological order
jobs = {
    1: [(1, 3), (2, 3), (3, 3)],
    2: [(1, 2), (3, 3), (2, 4)],
    3: [(2, 3), (1, 2), (3, 1)]
}

def fitness(chromosome):
    # Decodes chromosome and calculates makespan (total completion time)
    job_step = {1: 0, 2: 0, 3: 0}           # tracks current operation index for each job
    job_ready_time = {1: 0, 2: 0, 3: 0}     # time when job is ready for next operation
    machine_ready_time = {1: 0, 2: 0, 3: 0} # time when machine becomes free

    for job in chromosome:
        step = job_step[job]
        machine, time = jobs[job][step]
        # Start time is the earliest when both the job and machine are ready
        start = max(job_ready_time[job], machine_ready_time[machine])
        end = start + time
        # Update ready times for the next operation
        job_ready_time[job] = end
        machine_ready_time[machine] = end
        job_step[job] += 1

    # Makespan is the maximum finish time across all machines
    return max(machine_ready_time.values())


# Step 3: Create an initial population of 6 random chromosomes
# Base chromosome: each job (1, 2, 3) appears exactly 3 times (permutation with repetition)
base_chromosome = [1, 1, 1, 2, 2, 2, 3, 3, 3]
population = []
for _ in range(POPULATION_SIZE):
    chrom = base_chromosome.copy()
    random.shuffle(chrom)
    population.append(chrom)


# Step 4: Run Genetic Algorithm for 50 generations
print("--- Genetic Algorithm Optimization ---")
for gen in range(1, GENERATIONS + 1):
    # Selection: sort population by fitness (lowest makespan first)
    population.sort(key=fitness)
    parent1 = population[0]
    parent2 = population[1]

    # Crossover: child takes first half of parent1, remaining from parent2 order
    half = len(parent1) // 2
    child = parent1[:half]
    job_counts = {1: child.count(1), 2: child.count(2), 3: child.count(3)}
    for gene in parent2:
        if job_counts[gene] < 3:
            child.append(gene)
            job_counts[gene] += 1

    # Mutation: with probability 0.3, swap two random positions in the child
    if random.random() < MUTATION_RATE:
        i, j = random.sample(range(len(child)), 2)
        child[i], child[j] = child[j], child[i]

    # Replacement: replace the weakest (last) chromosome with the new child
    population[-1] = child

    # Re-sort so population[0] is the current best chromosome
    population.sort(key=fitness)

    # Print generation number, best chromosome, and its makespan
    print(f"Generation {gen:2d}: Best Chromosome = {population[0]}, Makespan = {fitness(population[0])}")


# Step 5: After the loop, print the final best chromosome and final makespan
best_chromosome = population[0]
final_makespan = fitness(best_chromosome)

print("\n--- Final GA Result ---")
print(f"Final Best Chromosome: {best_chromosome}")
print(f"Final Makespan:        {final_makespan}")


# Step 6: Print the schedule as text (for each machine, list of (job, start, end))
print("\n--- Optimal Machine Schedule ---")
job_step = {1: 0, 2: 0, 3: 0}
job_ready_time = {1: 0, 2: 0, 3: 0}
machine_ready_time = {1: 0, 2: 0, 3: 0}
machine_schedule = {1: [], 2: [], 3: []}

for job in best_chromosome:
    step = job_step[job]
    machine, time = jobs[job][step]
    start = max(job_ready_time[job], machine_ready_time[machine])
    end = start + time
    job_ready_time[job] = end
    machine_ready_time[machine] = end
    job_step[job] += 1
    machine_schedule[machine].append((job, start, end))

for machine in sorted(machine_schedule.keys()):
    print(f"Machine {machine}: {machine_schedule[machine]}")


# CHECK: Brute-force function that tries every distinct ordering to find true optimum
def brute_force_optimum():
    all_orderings = set(itertools.permutations(base_chromosome))
    best_span = float("inf")
    best_order = None
    for ordering in all_orderings:
        span = fitness(ordering)
        if span < best_span:
            best_span = span
            best_order = list(ordering)
    return best_order, best_span

print("\n--- Brute-Force Check ---")
bf_chromosome, bf_makespan = brute_force_optimum()
print(f"Total distinct permutations tested: {len(set(itertools.permutations(base_chromosome)))}")
print(f"Brute-Force Optimal Makespan:      {bf_makespan}")
print(f"Example Brute-Force Chromosome:    {bf_chromosome}")

# Confirm GA result equals brute-force optimum
if final_makespan == bf_makespan:
    print(f"Confirmation: GA result ({final_makespan}) matches the true optimum ({bf_makespan})!")
else:
    print(f"Notice: GA found {final_makespan}, optimum is {bf_makespan}. Try setting POPULATION_SIZE = 10 or GENERATIONS = 100.")
```

---

## Sample Execution Output

```text
--- Genetic Algorithm Optimization ---
Generation  1: Best Chromosome = [3, 1, 3, 3, 2, 1, 2, 1, 2], Makespan = 14
Generation  2: Best Chromosome = [3, 1, 3, 3, 2, 1, 2, 1, 2], Makespan = 14
...
Generation 24: Best Chromosome = [3, 1, 3, 3, 2, 1, 2, 1, 2], Makespan = 14
Generation 25: Best Chromosome = [2, 1, 3, 3, 1, 2, 1, 2, 3], Makespan = 12
...
Generation 50: Best Chromosome = [2, 1, 3, 3, 1, 2, 1, 2, 3], Makespan = 12

--- Final GA Result ---
Final Best Chromosome: [2, 1, 3, 3, 1, 2, 1, 2, 3]
Final Makespan:        12

--- Optimal Machine Schedule ---
Machine 1: [(2, 0, 2), (1, 2, 5), (3, 5, 7)]
Machine 2: [(3, 0, 3), (1, 5, 8), (2, 8, 12)]
Machine 3: [(2, 2, 5), (1, 8, 11), (3, 11, 12)]

--- Brute-Force Check ---
Total distinct permutations tested: 1680
Brute-Force Optimal Makespan:      12
Example Brute-Force Chromosome:    [3, 1, 2, 2, 1, 3, 3, 1, 2]
Confirmation: GA result (12) matches the true optimum (12)!
```

---

## Optimal Schedule & Gantt Timeline

For the optimal chromosome `[2, 1, 3, 3, 1, 2, 1, 2, 3]`, operations unfold across the timeline as follows:

```text
Time :  0    1    2    3    4    5    6    7    8    9   10   11   12
M1   : [  Job 2  ][     Job 1     ][  Job 3  ] .    .    .    .    .
M2   : [     Job 3     ] .    .    [     Job 1     ][     Job 2      ]
M3   : .    .    [     Job 2     ] .    .    .    [     Job 1     ][J3]
```

### Operation Verification Table

| Machine | Job | Start Time | End Time | Duration | Predecessor Completed At |
| :---: | :---: | :---: | :---: | :---: | :---: |
| **$M_1$** | $J_2$ | 0 | 2 | 2 | 0 (First operation of $J_2$) |
| **$M_1$** | $J_1$ | 2 | 5 | 3 | 0 (First operation of $J_1$) |
| **$M_1$** | $J_3$ | 5 | 7 | 2 | 3 (After $J_3$ on $M_2$) |
| **$M_2$** | $J_3$ | 0 | 3 | 3 | 0 (First operation of $J_3$) |
| **$M_2$** | $J_1$ | 5 | 8 | 3 | 5 (After $J_1$ on $M_1$) |
| **$M_2$** | $J_2$ | 8 | 12 | 4 | 5 (After $J_2$ on $M_3$) |
| **$M_3$** | $J_2$ | 2 | 5 | 3 | 2 (After $J_2$ on $M_1$) |
| **$M_3$** | $J_1$ | 8 | 11 | 3 | 8 (After $J_1$ on $M_2$) |
| **$M_3$** | $J_3$ | 11 | 12 | 1 | 7 (After $J_3$ on $M_1$) |

**Final Makespan:** $\max(7, 12, 12) = \mathbf{12}$.

---

## Troubleshooting & Tuning

If you modify the problem parameters or run with a different random seed and the algorithm finishes above makespan $12$:

1. **Increase Population Size:**
   Change `POPULATION_SIZE = 6` to `POPULATION_SIZE = 10` in `job_shop_ga.py`. A larger population maintains genetic diversity.
2. **Increase Generations:**
   Change `GENERATIONS = 50` to `GENERATIONS = 100` to allow the algorithm more iterations to escape local minima.
3. **Adjust Mutation Rate:**
   If the population converges prematurely, raise `MUTATION_RATE` from `0.3` to `0.4` or `0.5` to explore new permutations.
