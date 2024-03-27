import json
import os
from random import shuffle
import subprocess

from uftrace_helper import trace

# Path to the regression injection script
regression_script_path = '../regression-injection/regression_inserter.py'

# Path to the program source and build directories (it is different for each program)
program_source = 'SPEC_PATH_HERE/benchspec/CPU/531.deepsjeng_r/src'
program_build = 'SPEC_PATH_HERE/benchspec/CPU/631.deepsjeng_s/exe'

if __name__ == '__main__':
    # The name of the table to insert the data into (i.e., database table)
    table_name = 'reports-631_sjeng_regression'
    # The name of the program
    program_name = '631.deepsjeng_s'
    # The type of regression (i.e., const_delay, calculations, io, etc.)
    regression = 'const_delay'

    # Force the affinity of the process to the first 8 cores for the same environemnt comparison
    os.sched_setaffinity(0, list(range(0, 8)))

    # Load the candidate functions from the json file (i.e., entropy, cv, etc.)
    with open('candidate_functions.json', 'r') as f:
        candidate_functions = json.load(f)[program_name]

    # This is for the optimization and regression datasets. It contains 25,000 positions.
    with open('sjeng_positions.complete.json', 'r') as f:
        inputs = json.load(f)

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

    range_counter = 15
    for range_c in range_clusters:
        for range_i in range_indexes:
            range_c = f'{range_c.split("-")[0]}-{range_i}'

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
            for option_combination in inputs[start_index:end_index]:
                new_options = option_combination

                # Write the new lines to a new file
                with open(program_build + '/input.txt', 'w+') as f:
                    f.write(f'{new_options["fen"]}\n')
                    f.write(f'{new_options["depth"]}')

                max_attempts = 1
                for candidate_type, candidate_functions_list in candidate_functions.items():
                    # In order to run just some specific function sets (i.e., entropy, CV, etc.)
                    if candidate_type not in ['correlation']:
                        continue

                    is_successful = False
                    current_attempt = 0

                    while not is_successful and current_attempt < max_attempts:
                        try:
                            # Run 631.sjeng and instrument it
                            vanilla_command = ['./deepsjeng_s_base.mytest-m64', 'input.txt']
                            full_command = [
                                'uftrace', 'record', '--time', '--no-libcall', './deepsjeng_s_base.mytest-m64', 'input.txt']

                            # Add the candidate functions with -P for each to the full command from second index
                            for function in candidate_functions_list:
                                full_command.insert(4, '-P')
                                full_command.insert(5, function)

                            parameters = {option: value for option,
                                          value in new_options.items()}
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

                            if isBaseline:
                                build['type'] = build['type'] + '_baseline'

                            # Run the program with the new options, and trace the execution
                            trace(vanilla_command, full_command, parameters, table_name, build,
                                  cwd, skip_vanilla=False if candidate_type == 'full' else True,
                                  only_vanilla=True if candidate_type == 'vanilla' else False)

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
                print(inputs.index(option_combination))
                print('----------------------------------')

            # If there are any failures, write them to a file to re-run them later
            if len(list(failures.keys())) > 0:
                with open(f'failures.sjeng.{range_c.replace("-","_")}.json', 'w') as f:
                    json.dump(failures, f, indent=4)

            range_counter += 1