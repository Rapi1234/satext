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
Runtime Statistics:
                            count       mean       std        min        25%        50%        75%        max
Method
Binary Search               100.0   1.007445  0.563428   0.411773   0.630405   0.871484   1.142933   3.098846
Linear Search SAT to UNSAT  100.0  41.385016  4.486095  34.693433  38.130008  40.813770  43.545779  58.885194
Linear Search UNSAT to SAT  100.0   0.110980  0.252286   0.013358   0.027040   0.047493   0.081817   1.946944
RC2                         100.0   0.033634  0.058430   0.004137   0.009207   0.014691   0.035384   0.370306

0 of 100 formulas where satisfiable
```