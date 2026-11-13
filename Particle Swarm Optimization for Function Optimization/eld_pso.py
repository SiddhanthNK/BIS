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
