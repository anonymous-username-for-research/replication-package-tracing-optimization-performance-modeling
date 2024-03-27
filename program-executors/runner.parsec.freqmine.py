import itertools
import os
from random import shuffle, sample, randint
import json
import random
import subprocess

from uftrace_helper import trace

# Path to the regression injection script
regression_script_path = '../regression-injection/regression_inserter.py'

# Path to the program source and build directories (it is different for each program)
program_source = 'PARSEC_PATH_HERE/pkgs/apps/freqmine/src'
program_build = 'PARSEC_PATH_HERE/pkgs/apps/freqmine/inst/amd64-linux.gcc/bin'

if __name__ == '__main__':
    # The name of the table to insert the data into (i.e., database table)
    table_name = 'reports-parsec_freqmine_optimized'
    # The name of the program
    program_name = 'freqmine'
    # The type of regression (i.e., const_delay, calculations, io, etc.)
    regression = 'const_delay'

    random.seed(42)

    # Force the affinity of the process to the first 8 cores for the same environemnt comparison
    os.sched_setaffinity(0, list(range(0, 8)))

    # Load the candidate functions from the json file (i.e., entropy, cv, etc.)
    with open('candidate_functions.json', 'r') as f:
        candidate_functions = json.load(f)[program_name]

    inputs = []
    for path, subdirs, files_ in os.walk(f'./inputs/{program_name}'):
        for name in files_:
            # Get the absolute path of the file
            inputs.append(os.path.abspath(os.path.join(path, name)))
    inputs.sort()
    shuffle(inputs)

    # If we want to inject regression or not
    isRegression = False

    # If we want to run the program with regression format, but as a baseline (i.e., no regression)
    isBaseline = False

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
    
    range_counter = 0
    for range_c in range_clusters:
        for range_i in range_indexes:
            range_c = f'{range_c.split("-")[0]}-{range_i}'

            # This program does not have a high-4 range
            if range_c == 'high-4':
                continue

            # Do we need to rebuild the program or not
            rebuild = True

            # Inject the regression script into the source code
            if rebuild:
                if isRegression:
                    subprocess.run(['python3', regression_script_path, regression, program_name,
                                    program_source, f'--range={range_c}'], capture_output=False)
                else:
                    subprocess.run(['python3', regression_script_path, regression, program_name,
                                    program_source, f'--range={range_c}', '--reset'], capture_output=False)

            if isBaseline:
                range_c = 'itself'

            
            start_index = 333 * range_counter
            end_index = start_index + 333
            failures = {}
            for input in inputs[start_index:end_index]:
                # Run the program with the new options
                max_attempts = 1 # The maximum number of attempts to run the program (i.e., if it fails)
                for candidate_type, candidate_functions_list in candidate_functions.items():
                    # In order to run just some specific function sets (i.e., entropy, CV, etc.)
                    if candidate_type not in ['static_pure']:
                        continue

                    is_successful = False
                    current_attempt = 0

                    support = int(input.split('_')[-1].split('.')[0])
                    file_name = input.split('/')[-1]

                    # Copy the input file to the build directory
                    output_name = f'{program_build}/inputs/{file_name}'
                    os.makedirs(f'{program_build}/inputs', exist_ok=True)
                    subprocess.run(['cp', input, output_name], capture_output=False)

                    parameters = {'file_name': file_name}
                    cwd = program_build

                    try:
                        # Try to see if the support is working
                        trace(vanilla_command=['./freqmine', f'./inputs/{file_name}', str(support)],
                              only_vanilla=True, not_insert=True, cwd=program_build,
                              parameters=parameters, table_name=table_name,
                              build={'type': 'test', 'range': range_c}, full_command=None)
                        
                    except Exception as e:
                        break

                    while not is_successful and current_attempt < max_attempts:
                        try:
                            vanilla_command = ['./freqmine', f'./inputs/{file_name}', str(support)]
                            full_command = ['uftrace', 'record', '--time', '--no-libcall', './freqmine', f'./inputs/{file_name}', str(support)]

                            # Add the candidate functions with -C for each to the full command from second index
                            for function in candidate_functions_list:
                                full_command.insert(4, '-P')
                                full_command.insert(5, function)

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

                            if isBaseline:
                                build['type'] = build['type'] + '_baseline'

                            # Run the program with the new options, and trace the execution
                            trace(vanilla_command, full_command, parameters, table_name, build,
                                  cwd, skip_vanilla=True,
                                  only_vanilla=True if candidate_type == 'vanilla' else False)

                            is_successful = True
                        except Exception as e:
                            print(e)
                            current_attempt += 1

                    if not is_successful:
                            print(f'Failed to run for file {input}')
                            if candidate_type not in failures:
                                failures[candidate_type] = []
                            failures[candidate_type].append(input)

                    # Remove the input file from the build directory
                    os.remove(output_name)

                print(inputs.index(input))
                print('----------------------------------')

            if len(list(failures.keys())) > 0:
                with open(f'failures.freqmine.{range_c.replace("-","_")}.json', 'w') as f:
                    json.dump(failures, f, indent=4)

            range_counter += 1