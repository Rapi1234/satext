import os

def remove_last_four_lines_if_percent(filepath):
    # Read the file and store all lines in a list
    with open(filepath, 'r') as file:
        lines = file.readlines()

    # Check if the file has at least four lines
    if len(lines) >= 4:
        # Check if the fourth last line contains a '%'
        if '%' in lines[-3]:
            # Remove the last four lines
            lines = lines[:-3]

            # Write the modified content back to the file
            with open(filepath, 'w') as file:
                file.writelines(lines)
            print(f"Last four lines removed from {filepath}")
        else:
            print(f"The fourth-last line does not contain '%'. No lines were removed from {filepath}")
    else:
        print(f"{filepath} has less than four lines. No lines were removed.")

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
    
    return cnf_file_path

for i in range(100):
    filepath= get_ith_cnf("./testdata/uuf75-325", i)
    remove_last_four_lines_if_percent(filepath)
