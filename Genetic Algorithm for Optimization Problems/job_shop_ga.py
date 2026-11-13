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
