"""
SOS-ACO for the Traveling Salesman Problem (TSP)
================================================
Hybrid of Ant Colony Optimization (ACO) and Symbiotic Organisms Search (SOS),
following the idea of Wang & Han, "Ant colony optimization for traveling
salesman problem based on parameters optimization", Applied Soft Computing 107 (2021) 107439:

  * ACO builds tours (pheromone + heuristic desirability).
  * SOS searches the space of ACO parameters (alpha, beta); the fitness of an
    SOS organism is the tour length ACO finds with those parameters.
  * A simple 2-opt local optimisation refines the ants' tours.

Usage
-----
    python sos_aco_tsp.py                       # random 50-city demo
    python sos_aco_tsp.py --tsp berlin52.tsp    # TSPLIB EUC_2D file
    python sos_aco_tsp.py --cities 80 --seed 3 --plot
"""
import argparse
import time
import numpy as np


# ----------------------------------------------------------------------------
# Problem helpers
# ----------------------------------------------------------------------------
def load_tsplib(path):
    """Minimal TSPLIB reader for NODE_COORD_SECTION (EUC_2D) files."""
    coords, reading = [], False
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line.startswith("NODE_COORD_SECTION"):
                reading = True
                continue
            if line.startswith("EOF") or not line:
                if line.startswith("EOF"):
                    break
                continue
            if reading:
                parts = line.split()
                coords.append((float(parts[1]), float(parts[2])))
    return np.array(coords)


def distance_matrix(coords):
    diff = coords[:, None, :] - coords[None, :, :]
    return np.sqrt((diff ** 2).sum(-1))


def tour_length(tour, D):
    return D[tour, np.roll(tour, -1)].sum()


def two_opt(tour, D, max_passes=3):
    """Simple 2-opt local search (first improvement)."""
    tour = tour.copy()
    n = len(tour)
    for _ in range(max_passes):
        improved = False
        for i in range(n - 1):
            for j in range(i + 2, n):
                if i == 0 and j == n - 1:
                    continue
                a, b = tour[i], tour[i + 1]
                c, d = tour[j], tour[(j + 1) % n]
                delta = D[a, c] + D[b, d] - D[a, b] - D[c, d]
                if delta < -1e-10:
                    tour[i + 1:j + 1] = tour[i + 1:j + 1][::-1]
                    improved = True
        if not improved:
            break
    return tour


# ----------------------------------------------------------------------------
# Ant Colony Optimization
# ----------------------------------------------------------------------------
class ACO:
    def __init__(self, D, n_ants=20, iterations=50, alpha=1.0, beta=3.0,
                 rho=0.5, Q=1.0, local_search=True, rng=None):
        self.D = D
        self.n = len(D)
        self.n_ants = n_ants
        self.iterations = iterations
        self.alpha, self.beta, self.rho, self.Q = alpha, beta, rho, Q
        self.local_search = local_search
        self.rng = rng or np.random.default_rng()
        with np.errstate(divide="ignore"):
            self.eta = 1.0 / (D + np.eye(self.n))      # heuristic info 1/d
        np.fill_diagonal(self.eta, 0.0)

    def _build_tour(self, tau):
        n, rng = self.n, self.rng
        start = rng.integers(n)
        tour = [start]
        visited = np.zeros(n, bool)
        visited[start] = True
        weight = (tau ** self.alpha) * (self.eta ** self.beta)
        for _ in range(n - 1):
            cur = tour[-1]
            w = weight[cur] * ~visited
            s = w.sum()
            if s <= 0:                                  # numerical safety
                nxt = rng.choice(np.flatnonzero(~visited))
            else:
                nxt = rng.choice(n, p=w / s)
            tour.append(nxt)
            visited[nxt] = True
        return np.array(tour)

    def run(self, history=False):
        n = self.n
        # initial pheromone from a nearest-neighbour tour length
        nn_len = tour_length(self._build_tour(np.ones((n, n))), self.D)
        tau = np.full((n, n), self.n_ants / nn_len)
        best_tour, best_len = None, np.inf
        curve = []
        for _ in range(self.iterations):
            tours, lens = [], []
            for _a in range(self.n_ants):
                t = self._build_tour(tau)
                if self.local_search:
                    t = two_opt(t, self.D, max_passes=1)
                tours.append(t)
                lens.append(tour_length(t, self.D))
            k = int(np.argmin(lens))
            if lens[k] < best_len:
                best_len, best_tour = lens[k], tours[k].copy()
            # evaporation + deposit (all ants, as in Ant System)
            tau *= (1.0 - self.rho)
            for t, L in zip(tours, lens):
                dep = self.Q / L
                a, b = t, np.roll(t, -1)
                tau[a, b] += dep
                tau[b, a] += dep
            # elitist reinforcement of the global best
            a, b = best_tour, np.roll(best_tour, -1)
            tau[a, b] += self.Q / best_len
            tau[b, a] += self.Q / best_len
            tau = np.clip(tau, 1e-12, None)
            curve.append(best_len)
        return (best_tour, best_len, curve) if history else (best_tour, best_len)


# ----------------------------------------------------------------------------
# Symbiotic Organisms Search over ACO parameters (alpha, beta)
# ----------------------------------------------------------------------------
class SOS:
    """Symbiotic Organisms Search (Cheng & Prayogo, 2014) – minimisation."""

    def __init__(self, fitness, bounds, pop_size=8, iterations=8, rng=None):
        self.f = fitness
        self.lb = np.array([b[0] for b in bounds], float)
        self.ub = np.array([b[1] for b in bounds], float)
        self.dim = len(bounds)
        self.N = pop_size
        self.iters = iterations
        self.rng = rng or np.random.default_rng()

    def _clip(self, x):
        return np.clip(x, self.lb, self.ub)

    def _eval(self, x):
        return self.f(x)

    def run(self):
        rng = self.rng
        X = self.lb + rng.random((self.N, self.dim)) * (self.ub - self.lb)
        F = np.array([self._eval(x) for x in X])
        for _ in range(self.iters):
            for i in range(self.N):
                best = X[np.argmin(F)]

                # ---- 1. Mutualism ----
                j = rng.choice([k for k in range(self.N) if k != i])
                mutual = (X[i] + X[j]) / 2
                bf1, bf2 = rng.integers(1, 3, 2)        # benefit factors 1 or 2
                xi_new = self._clip(X[i] + rng.random(self.dim) * (best - mutual * bf1))
                xj_new = self._clip(X[j] + rng.random(self.dim) * (best - mutual * bf2))
                fi, fj = self._eval(xi_new), self._eval(xj_new)
                if fi < F[i]:
                    X[i], F[i] = xi_new, fi
                if fj < F[j]:
                    X[j], F[j] = xj_new, fj

                # ---- 2. Commensalism ----
                j = rng.choice([k for k in range(self.N) if k != i])
                xi_new = self._clip(X[i] + (rng.random(self.dim) * 2 - 1) * (best - X[j]))
                fi = self._eval(xi_new)
                if fi < F[i]:
                    X[i], F[i] = xi_new, fi

                # ---- 3. Parasitism ----
                j = rng.choice([k for k in range(self.N) if k != i])
                parasite = X[i].copy()
                d = rng.integers(self.dim)
                parasite[d] = self.lb[d] + rng.random() * (self.ub[d] - self.lb[d])
                fp = self._eval(parasite)
                if fp < F[j]:
                    X[j], F[j] = parasite, fp
        k = int(np.argmin(F))
        return X[k], F[k]


# ----------------------------------------------------------------------------
# SOS-ACO driver
# ----------------------------------------------------------------------------
def sos_aco(D, n_ants=20, final_iters=100, tune_iters=10, sos_pop=6, sos_iters=6,
            alpha_bounds=(0.1, 5.0), beta_bounds=(0.5, 10.0), rho=0.5, seed=0):
    rng = np.random.default_rng(seed)

    def fitness(params):
        a, b = params
        aco = ACO(D, n_ants=n_ants, iterations=tune_iters, alpha=a, beta=b,
                  rho=rho, rng=np.random.default_rng(rng.integers(1 << 31)))
        return aco.run()[1]

    sos = SOS(fitness, [alpha_bounds, beta_bounds], sos_pop, sos_iters, rng)
    (alpha, beta), tune_len = sos.run()
    final = ACO(D, n_ants=n_ants, iterations=final_iters, alpha=alpha, beta=beta,
                rho=rho, rng=np.random.default_rng(rng.integers(1 << 31)))
    tour, length, curve = final.run(history=True)
    return tour, length, curve, (alpha, beta)


def main():
    p = argparse.ArgumentParser(description="SOS-ACO for TSP")
    p.add_argument("--tsp", help="TSPLIB file (EUC_2D). Default: random cities")
    p.add_argument("--cities", type=int, default=50)
    p.add_argument("--seed", type=int, default=0)
    p.add_argument("--ants", type=int, default=20)
    p.add_argument("--iters", type=int, default=100, help="final ACO iterations")
    p.add_argument("--plot", action="store_true")
    args = p.parse_args()

    rng = np.random.default_rng(args.seed)
    coords = load_tsplib(args.tsp) if args.tsp else rng.random((args.cities, 2)) * 100
    D = distance_matrix(coords)
    print(f"Instance: {len(coords)} cities")

    t0 = time.time()
    base = ACO(D, n_ants=args.ants, iterations=args.iters, alpha=1.0, beta=2.0,
               rng=np.random.default_rng(args.seed))
    b_tour, b_len, b_curve = base.run(history=True)
    print(f"Plain ACO (alpha=1, beta=2)     : {b_len:10.2f}   [{time.time()-t0:.1f}s]")

    t0 = time.time()
    tour, length, curve, (a, b) = sos_aco(D, n_ants=args.ants, final_iters=args.iters,
                                           seed=args.seed)
    print(f"SOS-ACO (alpha={a:.2f}, beta={b:.2f}) : {length:10.2f}   [{time.time()-t0:.1f}s]")
    print("Best tour:", tour.tolist())

    if args.plot:
        import matplotlib.pyplot as plt
        fig, ax = plt.subplots(1, 2, figsize=(12, 5))
        closed = np.append(tour, tour[0])
        ax[0].plot(coords[closed, 0], coords[closed, 1], "-o", ms=4)
        ax[0].set_title(f"SOS-ACO tour (length {length:.1f})")
        ax[1].plot(b_curve, label="Plain ACO")
        ax[1].plot(curve, label="SOS-ACO")
        ax[1].set_xlabel("Iteration"); ax[1].set_ylabel("Best tour length")
        ax[1].legend(); ax[1].set_title("Convergence")
        plt.tight_layout(); plt.savefig("result.png", dpi=150)
        print("Saved result.png")


if __name__ == "__main__":
    main()
