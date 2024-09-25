# This repository contains an implementaion of maxSAT

## Usage

run: maxSAT.py [-h] [--method {0,1,2}] [file_path]

positional arguments:
  file_path             Path to a CNF file to solve the MaxSAT problem.

options:
  -h, --help            show this help message and exit
  --method {0,1,2}, -m {0,1,2}
                        Specify the MaxSAT solving method: 0 = linear UNSAT to SAT, 1 = linear SAT to UNSAT, 2 = binary search.

If no file path is provided, the script will run the test enviornment.

Example usage:
```
python3 maxSAT.py testdata/uuf75-325/uuf75-01.cnf -m 0
```

## Operation

The script maxSAT.py has three different maxSAT methods implemented:\
1. linear UNSAT to SAT: This executes a linear search from UNSAT to SAT to find the costs for satisfying the clause
2. linear SAT to UNSAT: Also executes a linear search but this time from SAT to UNSAT.
3. binary search: uses binary search to solve the problem.

The script will also print some information about the runtime and also solves the problem with the RC2 solver to verify that the returned costs are correct.

The solver uses Minisat22 to solve the cnf encoded problem. Therefore the caridinality constraint must be added. To do so an additional literal for each clause is included, which must be true if and only if the clause is true. With this extra literal, it is possible to specify which clauses, or how many, are satisfied.

## Testenvironment

This is only used for testing. I challenged the solver to solve some benchmark cnf problems (source: https://www.cs.ubc.ca/~hoos/SATLIB/benchm.html). In the folder _testdata/uf75-325_ are only satisfiable instances while the _testdata/uu75-325_ contains unsatisfiable ones. Both only uses problems with 75 variables, 325 clauses and there are 100 instances each. The runtime and the costs returned of the solver is compared to the RC2 solver results. The runtime of all unsat instances can be seen in the following image.

![plot](./comparision_uuf75-325.png?raw=true)

Since the linear search sat to unsat is extremly large compared to others, I also ran it without this method

![plot](./comparision_uuf75-325_no_sat2unsat.png?raw=true)

The output is given next:
```
uuf75-325 without sat2unsat

Runtime Statistics:
                            count       mean       std        min        25%        50%        75%        max
Method                                                                                                       
Binary Search               100.0   0.826595  0.509808   0.396945   0.532988   0.643181   0.923771   4.098735
Linear Search SAT to UNSAT  100.0  38.391988  2.564815  32.732038  36.821270  38.393613  40.370913  48.084874
Linear Search UNSAT to SAT  100.0   0.088561  0.273392   0.011622   0.021904   0.034318   0.065464   2.628341
RC2                         100.0   0.022646  0.041704   0.002813   0.005854   0.009529   0.021461   0.272438

0 of 100 formulas where satisfiable
```