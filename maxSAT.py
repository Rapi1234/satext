import time
import random
import matplotlib.pyplot as plt
import pandas as pd
from pysat.formula import CNF
from pysat.solvers import Minisat22
from pysat.card import CardEnc

def parse_dimacs(file_path):
    cnf = CNF(from_file=file_path)
    return cnf

# MaxSAT solving methods

def linear_search_unsat_to_sat(cnf):
    with Minisat22(bootstrap_with=cnf.clauses) as solver:
        for k in range(len(cnf.clauses) + 1):
            card_constraint = CardEnc.atleast(lits=range(1, len(cnf.clauses) + 1), bound=k, encoding=0)
            solver.append_formula(card_constraint.clauses)
            if solver.solve():
                return k
    return 0

def linear_search_sat_to_unsat(cnf):
    with Minisat22(bootstrap_with=cnf.clauses) as solver:
        for k in range(len(cnf.clauses), -1, -1):
            card_constraint = CardEnc.atmost(lits=range(1, len(cnf.clauses) + 1), bound=k, encoding=0)
            solver.append_formula(card_constraint.clauses)
            if not solver.solve():
                return k + 1
    return 0

def binary_search(cnf):
    low, high = 0, len(cnf.clauses)
    with Minisat22(bootstrap_with=cnf.clauses) as solver:
        while low < high:
            mid = (low + high) // 2
            card_constraint = CardEnc.atleast(lits=range(1, len(cnf.clauses) + 1), bound=mid, encoding=0)
            solver.append_formula(card_constraint.clauses)
            if solver.solve():
                low = mid + 1
            else:
                high = mid
    return low - 1

# Random DIMACS Generator

def generate_random_dimacs(num_vars, num_clauses, file_path):
    with open(file_path, 'w') as f:
        f.write(f"p cnf {num_vars} {num_clauses}\n")
        for _ in range(num_clauses):
            clause = [random.choice([i, -i]) for i in random.sample(range(1, num_vars + 1), random.randint(1, num_vars))]
            f.write(" ".join(map(str, clause)) + " 0\n")

# Test Environment with Visualizations and Statistics

def test_environment(num_vars, num_clauses, iterations=5):
    file_path = "random.cnf"
    results = {"Method": [], "Iteration": [], "Runtime (s)": []}
    
    for i in range(iterations):
        generate_random_dimacs(num_vars, num_clauses, file_path)
        cnf = parse_dimacs(file_path)
        
        # Linear Search UNSAT to SAT
        start_time = time.time()
        linear_search_unsat_to_sat(cnf)
        runtime = time.time() - start_time
        results["Method"].append("Linear Search UNSAT to SAT")
        results["Iteration"].append(i + 1)
        results["Runtime (s)"].append(runtime)
        
        # Linear Search SAT to UNSAT
        start_time = time.time()
        linear_search_sat_to_unsat(cnf)
        runtime = time.time() - start_time
        results["Method"].append("Linear Search SAT to UNSAT")
        results["Iteration"].append(i + 1)
        results["Runtime (s)"].append(runtime)
        
        # Binary Search
        start_time = time.time()
        binary_search(cnf)
        runtime = time.time() - start_time
        results["Method"].append("Binary Search")
        results["Iteration"].append(i + 1)
        results["Runtime (s)"].append(runtime)
    
    # Convert results to DataFrame
    df = pd.DataFrame(results)
    
    # Display basic statistics
    print("\nRuntime Statistics:")
    print(df.groupby("Method")["Runtime (s)"].describe())
    
    # Plot results
    plt.figure(figsize=(10, 6))
    for method in df["Method"].unique():
        subset = df[df["Method"] == method]
        plt.plot(subset["Iteration"], subset["Runtime (s)"], marker='o', label=method)
    
    plt.title("MaxSAT Solver Runtime Comparison")
    plt.xlabel("Iteration")
    plt.ylabel("Runtime (seconds)")
    plt.legend()
    plt.grid(True)
    plt.show()

if __name__ == "__main__":
    num_vars = 20
    num_clauses = 50
    iterations = 5
    
    test_environment(num_vars, num_clauses, iterations)
