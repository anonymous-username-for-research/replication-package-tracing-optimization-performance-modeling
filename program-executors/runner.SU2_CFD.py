import json
import os
from random import shuffle
import random
import re
import subprocess
import itertools

from uftrace_helper import trace

# Path to the regression injection script
regression_script_path = '../regression-injection/regression_inserter.py'

# Path to the program source and build directories (it is different for each program)
program_source = 'SU2_PATH_HERE'
program_build = 'SU2_PATH_HERE/SU2_CFD/exe'

if __name__ == '__main__':
    # The name of the table to insert the data into (i.e., database table)
    table_name = 'reports-su2_cfd_optimized'
    # The name of the program
    program_name = 'su2_cfd'
    # The type of regression (i.e., const_delay, calculations, io, etc.)
    regression = 'const_delay'

    random.seed(42)

    # Force the affinity of the process to the first 8 cores for the same environemnt comparison
    os.sched_setaffinity(0, list(range(0, 8)))

    # Load the candidate functions from the json file (i.e., entropy, cv, etc.)
    with open('candidate_functions.json', 'r') as f:
        candidate_functions = json.load(f)[program_name]

    # Open the SU2_CFD input file and split it into lines
    with open('input.SU2_CFD.cfg', 'r') as f:
        lines = f.read().splitlines()
    
    # Define the options to be changed in the input file (i.e., randomization)
    options = {
        'MATH_PROBLEM= DIRECT': ['DIRECT', 'CONTINUOUS_ADJOINT'],
        'NUM_METHOD_GRAD= WEIGHTED_LEAST_SQUARES': ['WEIGHTED_LEAST_SQUARES', 'GREEN_GAUSS'],
        'LINEAR_SOLVER= FGMRES': ['FGMRES', 'BCGSTAB'],
        'MGCYCLE= W_CYCLE': ['W_CYCLE', 'V_CYCLE'],
        'MGLEVEL= 3': list(range(3, 6)),
        'LINEAR_SOLVER_ITER= 10': list(range(8, 12)),
        'ITER= 250': list(range(150, 300, 20)),
        'OBJECTIVE_FUNCTION= DRAG': ['DRAG', 'LIFT'],
        'SOLVER= EULER': ['EULER', 'NAVIER_STOKES'],
         'CONV_NUM_METHOD_FLOW= JST': ['JST', 'LAX-FRIEDRICH'],
    }

    # Iterate over all the options and create a new input file for each option
    combinations = [[value for value in option_values] for option_values in options.values()]
    option_combinations = list(itertools.product(*combinations))

    with open('su2_inputs.complete.new.json', 'r') as f:
        inputs = json.load(f)
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

            # Do we need to rebuild the program or not
            rebuild = False

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
                solver, math_problem, num_method_grad, objective_function, iter, linear_solver, linear_solver_iter, mgcycle, mglevel, conv_num_method_flow = option_combination.values()
                # math_problem, num_method_grad, linear_solver, mgcycle, mglevel, linear_solver_iter, iter, objective_function, solver, conv_num_method_flow = option_combination

                # Create a new options dictionary with the new values
                new_options = {
                    'SOLVER= EULER': solver,
                    'MATH_PROBLEM= DIRECT': math_problem,
                    'NUM_METHOD_GRAD= WEIGHTED_LEAST_SQUARES': num_method_grad,
                    'OBJECTIVE_FUNCTION= DRAG': objective_function,
                    'ITER= 250': iter,
                    'LINEAR_SOLVER= FGMRES': linear_solver,
                    'LINEAR_SOLVER_ITER= 10': linear_solver_iter,
                    'MGCYCLE= W_CYCLE': mgcycle,
                    'MGLEVEL= 3': mglevel,
                    'CONV_NUM_METHOD_FLOW= JST': conv_num_method_flow
                }
                
                # Replace the options in the input file with the new options
                new_lines = []
                for line in lines:
                    for option, value in new_options.items():
                        if line.startswith(option):
                            new_lines.append(str(option).split('=')[0] + '= ' + str(new_options[option]))
                            break
                    else:
                        new_lines.append(line)

                # Write the new lines to a new file (i.e., program's build directory)
                with open(program_build + '/SU2_CFD.cfg', 'w+') as f:
                    for line in new_lines:
                        f.write(f'{line}\n')

                # Run the program with the new options
                max_attempts = 2 # The maximum number of attempts to run the program (i.e., if it fails)
                for candidate_type, candidate_functions_list in candidate_functions.items():
                    # In order to run just some specific function sets (i.e., entropy, CV, etc.)
                    if candidate_type not in ['entropy_corr_and_cv_corr_and_model_importance']:
                        continue

                    is_successful = False
                    current_attempt = 0

                    while not is_successful and current_attempt < max_attempts:
                        try:
                            vanilla_command = ['SU2_CFD', './SU2_CFD.cfg']
                            full_command = ['uftrace', 'record', '--time', '--no-libcall', 'SU2_CFD', './SU2_CFD.cfg']
                            
                            # Add the candidate functions with -C for each to the full command from second index
                            for function in candidate_functions_list:
                                full_command.insert(4, '-P')
                                full_command.insert(5, function)

                            parameters = new_options
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

                # Print the index in option_combination in previous_options
                print(inputs.index(option_combination))
                print('----------------------------------')
                
            if len(list(failures.keys())) > 0:
                with open(f'failures.su2.{range_c.replace("-","_")}.json', 'w') as f:
                    json.dump(failures, f, indent=4)
            
            range_counter += 1