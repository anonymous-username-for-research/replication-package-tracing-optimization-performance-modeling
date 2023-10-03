import itertools
import os
from random import shuffle, randint
import json
import random
import subprocess

from uftrace_helper import trace

# Path to the regression injection script
regression_script_path = './regression-injection/regression_inserter.py'

# Path to the program source and build directories (it is different for each program)
program_source = '%PATH%/PARSEC/pkgs/apps/freqmine/src'
program_build = '%PATH%/PARSEC/pkgs/apps/freqmine/inst/amd64-linux.gcc/bin'

if __name__ == '__main__':
    # The name of the table to insert the data into (i.e., database table)
    table_name = 'parsec_freqmine_regression'
    # The name of the program
    program_name = 'freqmine'
    # The type of regression (i.e., const_delay, calculations, io, etc.)
    regression = 'const_delay'

    # Force the affinity of the process to the first 8 cores for the same environemnt comparison
    os.sched_setaffinity(0, list(range(0, 8)))

    # Load the candidate functions from the json file (i.e., entropy, cv, etc.)
    with open('candidate_functions.json', 'r') as f:
        candidate_functions = json.load(f)[program_name]

    # Options for the Kosarak algorithm (i.e., randomization)
    options = {
        'support': list(range(2, 200, 15)),
        'min_items': list(range(2, 600, 4)),
        'max_items': list(range(6000, 7500, 250)),
        'num_items': list(range(30, 60, 5)),
        'num_transactions': list(range(400000, 950000, 50000))
    }

    """
    This line is for the case when we want to load the inputs from previous runs.
    The previous inputs are located in "previous-parameters/program_name.json" file.
    """
    loadFromPrevious = True
    if loadFromPrevious:
        with open(f'./previous-parameters/freqmine.json', 'r') as f:
            previous_options = json.load(f)
        # Just shuffle the previous options for a better randomization
        shuffle(previous_options)

    # Iterate over all the options and create a new input file for each option
    combinations = [[value for value in option_values] for option_values in options.values()]
    option_combinations = list(itertools.product(*combinations))
    shuffle(option_combinations)

    # If we want to inject regression or not
    isRegression = False

    """
    Run the programs with:
        - if no regression: with the specified inputs (i.e., 333 inputs)
        - if regression: with the specified inputs (i.e., 333 inputs)
                            + for each regression cluster (i.e., low, medium, high)
                            + for each function in the cluster (i.e., low-0, low-1, etc.)

    The range_counter is used to slice the inputs based on the regression cluster and index.
    """
    if isRegression:
        range_clusters = ['low', 'medium', 'high']
        range_indexes = list(range(5))
    else:
        # We use "low" just for the regression injection script to work (i.e., input validation), but no regression is injected
        range_clusters = ['low']
        range_indexes = [0]
    
    for range_c in range_clusters:
        for range_i in range_indexes:
            range_c = f'{range_c.split("-")[0]}-{range_i}'

            # Skip the high-4 regression cluster for this program since there are not enough functions
            if range_c == 'high-4':
                continue

            # Inject the regression script into the source code
            if isRegression:
                inject_process = subprocess.run(['python3', regression_script_path, regression, program_name,
                                                program_source, f'--range={range_c}'], capture_output=False)
            else:
                inject_process = subprocess.run(['python3', regression_script_path, regression, program_name,
                                                program_source, f'--range={range_c}', '--reset'], capture_output=False)

            failures = {}
            for option_combination in previous_options:
                support, max_items, min_items,  num_items, num_transactions = option_combination.values()
                
                if loadFromPrevious:
                    new_options = {
                        'support': support,
                        'max_items': max_items,
                        'min_items': min_items,
                        'num_items': num_items,
                        'num_transactions': num_transactions
                    }
                else:
                    new_options = {
                        'support': random.randint(2, 40),
                        'max_items': max_items,
                        'min_items': min_items,
                        'num_items': random.choice(list(range(4, 50, 4))),
                        'num_transactions': random.randint(50000, 400000)
                    }

                # Generate the transactions
                transactions = []
                for i in range(new_options['num_transactions']):
                    items = set()
                    while len(items) < randint(1, new_options['num_items']):
                        items.add(randint(min_items, max_items))
                    transactions.append(list(items))

                # Write the transactions to a file (i.e., build directory)
                with open(program_build + "/kosarak.dat", "w") as f:
                    for items in transactions:
                        line = " ".join(str(i) for i in items)
                        f.write(line + "\n")
                
                # Run the program with the new options
                max_attempts = 1 # The maximum number of attempts to run the program (i.e., if it fails)
                for candidate_type, candidate_functions_list in candidate_functions.items():
                    # In order to run just some specific function sets (i.e., entropy, CV, etc.)
                    if candidate_type not in ['entropy', 'cv']:
                        continue

                    is_successful = False
                    current_attempt = 0

                    while not is_successful and current_attempt < max_attempts:
                        try:
                            vanilla_command = ['uftrace', 'record', '--time', '--no-libcall', '-P', 'main', './freqmine', 'kosarak.dat', str(new_options['support'])]
                            full_command = ['uftrace', 'record', '--time', '--no-libcall', './freqmine', 'kosarak.dat', str(new_options['support'])]
                            
                            # Add the candidate functions with -P for each to the full command from second index
                            for function in candidate_functions_list:
                                full_command.insert(4, '-P')
                                full_command.insert(5, function)
                            
                            parameters = {option: value for option, value in new_options.items()}
                            cwd = program_build

                            """
                            The buid specifications of the program.
                            The type: 
                                - if no regression: pruning method name (i.e., entropy, cv, etc.)
                                - if regression: pruning method name + regression type (i.e., entropy_const_delay)
                            The range:
                                - if no regression: 'itself'
                                - if regression: the cluster of the regression and the target function's index
                                                    in the cluster (i.e., 'low-0', 'low-1', etc.)
                            """
                            build = {
                                'type': str(candidate_type + '_' + regression) if isRegression else candidate_type,
                                'range': range_c if isRegression else 'itself'
                            }

                            # Run the program with the new options, and trace the execution
                            trace(vanilla_command, full_command, parameters, table_name, build, cwd=cwd,
                                skip_vanilla=False if candidate_type == 'full' else True)
                            is_successful = True
                        except Exception as e:
                            print(e)
                            current_attempt += 1

                    if not is_successful:
                        print(f'Failed to run new options {new_options}')
                        if candidate_type not in failures:
                            failures[candidate_type] = []
                        failures[candidate_type].append(new_options)

                # Print the index in option_combination in previous_options (just to check the progress)
                print(previous_options.index(option_combination))
                print('----------------------------------')

            # If there are any failures, write them to a file to re-run them later
            if len(list(failures.keys())) > 0:
                with open(f'failures.freqmine.{range_c.replace("-","_")}.json', 'w') as f:
                    json.dump(failures, f, indent=4)