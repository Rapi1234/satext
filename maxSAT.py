import time
import random
import matplotlib.pyplot as plt
import pandas as pd
import os
import argparse
from pysat.formula import CNF
from pysat.solvers import Minisat22
from pysat.card import CardEnc, EncType
from pysat.examples.rc2 import RC2

gen_random_dimacs = True # Might want to be deactivated for testing
read_test_data = False

def check_satisfiability(cnf):
    with Minisat22(bootstrap_with=cnf) as solver:
        return solver.solve()
    
def get_ith_cnf(folder_name, i):
    # Get a list of all CNF files in the folder
    cnf_files = [f for f in os.listdir(folder_name) if f.endswith('.cnf')]
    
    # Sort the list to ensure consistent ordering
    cnf_files.sort()
    
    # Check if the index i is within bounds
    if i < 0 or i >= len(cnf_files):
        raise IndexError(f"Index {i} is out of range for the folder containing {len(cnf_files)} files.")
    
    # Get the i-th CNF file's path
    cnf_file_path = os.path.join(folder_name, cnf_files[i])
    
    # Load the CNF file using PySAT's CNF class
    cnf = CNF(from_file=cnf_file_path)
    
    return cnf

############################################
# Functions to add cardinality constraints #
############################################

# This method introduces an indicator variable for each clause that is true if and only if
# the clause is satisfied.
# This is done by adding a new literal 'indicator' to the clause C = (l_1 and l_2 ... and 
# l_j) (note that thie indiator must be unique). This indicator is conjungated with the 
# clause C (l_1 and l_2 ... and l_j and i_1) and additionaly for each literal a new clause
# is created in the following way:
# Then a constraint is added s.t. the indicator is only ture iff the clause is true. This
# way it is possible to tell the solver which clauses must be fulfilled.
def add_clause_satisfaction_indicators(cnf):
    indicators = []
    new_clauses = CNF()

    for i, clause in enumerate(cnf.clauses):
        # Introduce a new unique indicator variable
        indicator = max(cnf.nv, max(indicators or [0])) + 1
        indicators.append(indicator)

        # Extend the clause s.t. the clause is sat iff the indicator is set to true
        # (use: x <-> y   <==>   (not x or y) and (x or not y)) 
        negated_clause = [-lit for lit in clause]
        c1 = negated_clause + [indicator]
        c2 = clause + [-indicator]
        new_clauses.append(c1)
        new_clauses.append(c2)
    
    return new_clauses, indicators

# This method adds the cardinality constraints to the set of clauses. It utilizes the
# method 'add_clause_satisfaction_indicators(...)' and the CardEnc functionality from
# pySAT. The indicators are cardianlity constrainted to check how many clauses have 
# been satisfied.  
# cnf      - The original formula to be evaluated
# bound    - The upper or lower bound
def apply_cardinality_constraint(cnf, bound):
    # Add clause satisfaction indicators
    cnf_with_indicators, indicators = add_clause_satisfaction_indicators(cnf)
    # Add cardinality constraint on indicators
    card_constraint = CardEnc.atleast(lits=indicators, bound=bound, encoding=EncType.seqcounter)
    # Add cardinality constraints to the CNF formula
    cnf_with_indicators.extend(card_constraint)
    
    return cnf_with_indicators

############################################
#          MaxSAT solving methods          #
############################################

def linear_search_unsat_to_sat(cnf):
    # To speed up the solver I tried to check for satisfiability first since then the cost are trivially zero
    if check_satisfiability(cnf):
            return (None, 0)
    
    for k in range(len(cnf.clauses), -1, -1):
        # Apply cardinality constraint to ensure at least `k` clauses are satisfied
        constrained_cnf = apply_cardinality_constraint(cnf, k)

        with Minisat22(bootstrap_with=constrained_cnf) as solver:
            if solver.solve():
                model = solver.get_model()
                return model, len(cnf.clauses) - k
            
    return None, 0

def linear_search_sat_to_unsat(cnf):
    model = None
    # To speed up the solver I tried to check for satisfiability first since then the cost are trivially zero
    if check_satisfiability(cnf):
            return (None, 0)
    
    for k in range(0, len(cnf.clauses) + 1):
        # Apply cardinality constraint to ensure at least `k` clauses are satisfied
        constrained_cnf = apply_cardinality_constraint(cnf, k)

        with Minisat22(bootstrap_with=constrained_cnf) as solver:
            if not solver.solve():
                return model, len(cnf.clauses) - (k - 1)
            else:
                model = solver.get_model()
            
    return model, 0

def binary_search(cnf):
    low, high = 0, len(cnf.clauses)
    model = None
    # To speed up the solver I tried to check for satisfiability first since then the cost are trivially zero
    if check_satisfiability(cnf):
            return (None, 0)
        
    # Otherwise I continue until I find the maximum value of satifiable soft clauses
    while low <= high:
        mid = (low + high) // 2
        # Apply cardinality constraint to ensure at most `mid` clauses are satisfied
        constrained_cnf = apply_cardinality_constraint(cnf, mid)
        with Minisat22(bootstrap_with=constrained_cnf) as solver:
            if solver.solve():
                low = mid + 1
                model = solver.get_model()
            else:
                high = mid - 1

    return model, len(cnf.clauses) - (low - 1)

def validation_rc2(cnf): 
    wcnf = cnf.weighted()
    rc2 = RC2(wcnf)
    model = rc2.compute()
    return model, rc2.cost

############################################
#            DIMACS Functions              #
############################################

# Generate a random dimacs file
def generate_random_dimacs(num_vars, num_clauses, file_path):
    if gen_random_dimacs:
        with open(file_path, 'w') as f:
            f.write(f"p cnf {num_vars} {num_clauses}\n")
            for _ in range(num_clauses):
                clause = [random.choice([i, -i]) for i in random.sample(range(1, num_vars + 1), random.randint(1, num_vars))]
                f.write(" ".join(map(str, clause)) + " 0\n")
    # else:
    #     print("random disabled")

# Parse a file as pySAT CNF
def parse_dimacs(file_path, read_test_data=False, foulder="", i=0):
    if not read_test_data:
        cnf = CNF(from_file=file_path)
    else:
        cnf = get_ith_cnf(foulder, i)
    return cnf

############################################
#   Test Environment with Visualizations   #
#              and Statistics              #
############################################

def test_environment(num_vars, num_clauses, iterations=5):
    file_path = "random.cnf"
    results = {"Method": [], "Iteration": [], "Runtime (s)": []}
    satisfiable_formula_cnt = 0
    
    for i in range(iterations):
        print(f'iteration {i+1} of {iterations}')
        generate_random_dimacs(num_vars, num_clauses, file_path)
        cnf = parse_dimacs(file_path, read_test_data=read_test_data, foulder="./testdata/uuf75-325", i=i)

        # Check if formula is satisfiable
        if check_satisfiability(cnf):
            satisfiable_formula_cnt += 1
        
        # Linear Search UNSAT to SAT
        start_time = time.time()
        (model_ls_u2s, cost_ls_u2s) = linear_search_unsat_to_sat(cnf)
        runtime = time.time() - start_time
        results["Method"].append("Linear Search UNSAT to SAT")
        results["Iteration"].append(i + 1)
        results["Runtime (s)"].append(runtime)
        
        # Linear Search SAT to UNSAT
        start_time = time.time()
        (model_ls_s2u, cost_ls_s2u) = linear_search_sat_to_unsat(cnf)
        runtime = time.time() - start_time
        results["Method"].append("Linear Search SAT to UNSAT")
        results["Iteration"].append(i + 1)
        results["Runtime (s)"].append(runtime)
        
        # Binary Search
        start_time = time.time()
        (model_bs, cost_bs) = binary_search(cnf)
        runtime = time.time() - start_time
        results["Method"].append("Binary Search")
        results["Iteration"].append(i + 1)
        results["Runtime (s)"].append(runtime)

        # PySAT RC2 solver
        start_time = time.time()
        (model_rc2, cost_rc2) = validation_rc2(cnf)
        runtime = time.time() - start_time
        results["Method"].append("RC2")
        results["Iteration"].append(i + 1)
        results["Runtime (s)"].append(runtime)

        # Validate if impelemnted solver return the same result as the RC2 solver
        if cost_ls_s2u != cost_rc2:
            print("Error! did not find correct solution with linear search sat to unsat!")
        if cost_ls_u2s != cost_rc2:
            print("Error! did not find correct solution with linear search unsat to sat!")
        if cost_bs != cost_rc2:
            print("Error! did not find correct solution with binary search!")
    
    # Convert results to df
    df = pd.DataFrame(results)
    
    # Display runtime statistics
    print("\nRuntime Statistics:")
    print(df.groupby("Method")["Runtime (s)"].describe())
    print(f'\n{satisfiable_formula_cnt} of {iterations} formulas where satisfiable')
    
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
    plt.savefig("comparison.png")

############################################
#          Function for running            #
#             individual files             #
############################################

def solve_maxSat(file_path, method):
    if not os.path.isfile(file_path):
        print(f"Error: {file_path} is not a valid file.")
        return
    
    cnf = CNF(from_file=file_path)

    results = {"Method": [], "Runtime (s)": [], "Costs" :[]}
    if method == 0: # Linear Search UNSAT to SAT
        start_time = time.time()
        (model_ls_u2s, cost) = linear_search_unsat_to_sat(cnf)
        runtime = time.time() - start_time
    elif method == 1: # Linear Search SAT to UNSAT
        start_time = time.time()
        (model_ls_s2u, cost) = linear_search_sat_to_unsat(cnf)
        runtime = time.time() - start_time
    elif method == 2: # Binary Search
        start_time = time.time()
        (model_bs, cost) = binary_search(cnf)
        runtime = time.time() - start_time
    # Store result
    results["Method"].append("Linear Search UNSAT to SAT")
    results["Runtime (s)"].append(runtime)
    results["Costs"].append(cost)

    start_time = time.time()
    (model_rc2, cost_rc2) = validation_rc2(cnf)
    runtime = time.time() - start_time
    results["Method"].append("RC2")
    results["Runtime (s)"].append(runtime)
    results["Costs"].append(cost_rc2)

    print(pd.DataFrame(results))

############################################
#               Main method                #
############################################

if __name__ == "__main__":
    # Create an argument parser to explain the usage
    parser = argparse.ArgumentParser(
        description='Solve a MaxSAT problem from a CNF file or run a test environment.',
        epilog='If no file path is provided, the script will run the test enviornment.'
    )

    # Add an optional argument for the file path
    parser.add_argument(
        'file_path', 
        nargs='?',  # Optional argument, '?' means it's optional (0 or 1 value)
        help='Path to a CNF file to solve the MaxSAT problem.'
    )
     # Add an optional argument for the MaxSAT solving method
    parser.add_argument(
        '--method', '-m',
        type=int,
        choices=[0, 1, 2],
        default=0,
        help='Specify the MaxSAT solving method: 0 = linear UNSAT to SAT, 1 = linear SAT to UNSAT, 2 = binary search.'
    )

    args = parser.parse_args()

     # If a file path is provided, call the solve_maxSat
    if args.file_path:
        solve_maxSat(args.file_path, args.method)
    else: # If no file path is provided, prompt the user for input
        try:
            num_vars = int(input("Enter the number of variables: ")) # 25
            num_clauses = int(input("Enter the number of clauses: ")) # 100 
            iterations = int(input("Enter the number of iterations (max_k): ")) # 100
            test_environment(num_vars, num_clauses, iterations)
        except ValueError:
            print("Please enter valid integer values for number of variables, clauses, and iterations.")
