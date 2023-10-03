import json
import os
from random import shuffle
import subprocess
import itertools

from uftrace_helper import trace

# Path to the regression injection script
regression_script_path = './regression-injection/regression_inserter.py'

# Path to the program source and build directories (it is different for each program)
program_source = '%PATH%/SPEC2017/benchspec/CPU/538.imagick_r/src'
program_build = '%PATH%/SPEC2017/benchspec/CPU/638.imagick_s/exe'

if __name__ == '__main__':
    # The name of the table to insert the data into (i.e., database table)
    table_name = '638_imagick_regression'
    # The name of the program
    program_name = '638.imagick_s'
    # The type of regression (i.e., const_delay, calculations, io, etc.)
    regression = 'const_delay'

    # Force the affinity of the process to the first 8 cores for the same environemnt comparison
    os.sched_setaffinity(0, list(range(0, 8)))

    # Load the candidate functions from the json file (i.e., entropy, cv, etc.)
    with open('candidate_functions.json', 'r') as f:
        candidate_functions = json.load(f)[program_name]

    # Options for the imagick program (i.e., randomization)
    options = {
        '-sharpen': ['0x4', '0x8', '0x12', '0x16', '0x20'],
        '-blur': ['0x4', '0x8', '0x12', '0x16', '0x20'],
        '-colorspace': ['Lab', 'CMYK'],
        '-channel': ['R', 'YK'],
        '-alpha': ['remove', 'transparent'],
        '-edge': list(range(3, 18, 3)),
        '-resize': ['10%', '15%', '20%', '25%', '30%', '35%', '40%', '45%', '50%', '55%', '60%', '65%', '70%', '75%', '80%', '85%', '90%', '95%', '100%'],
        '-quality': ['25', '50', '75', '100'],
        '-rotate': list(range(10, 50, 5)),
    }
    added_options = ['-contrast', '-enhance']
    inputs = ['image_1.tga', 'image_2.tga']

    """
    This line is for the case when we want to load the inputs from previous runs.
    The previous inputs are located in "previous-parameters/program_name.json" file.
    """
    loadFromPrevious = True
    if loadFromPrevious:
        with open(f'./previous-parameters/imagick.json', 'r') as f:
            previous_options = json.load(f)
        # Just shuffle the previous options for a better randomization
        shuffle(previous_options)

    # Iterate over all the options and create a new input file for each option
    combinations = [[value for value in option_values] for option_values in options.values()]
    combinations.append(added_options)
    combinations.append(inputs)
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

            # Inject the regression script into the source code
            if isRegression:
                subprocess.run(['python3', regression_script_path, regression, program_name,
                                                program_source, f'--range={range_c}'], capture_output=False)
            else:
                subprocess.run(['python3', regression_script_path, regression, program_name,
                                                program_source, f'--range={range_c}', '--reset'], capture_output=False)
            
            # Shuffle the options for better randomization
            shuffle(option_combinations)
            previous_options = option_combinations[:333]

            failures = {}
            for option_combination in previous_options:
                sharpen, blur, colorspce, channel, alpha, edge, resize, quality, rotate, added_options, input = option_combination
                new_options = [input, '-quality', quality, '-rotate', str(rotate), '-edge', str(edge), '-sharpen', sharpen, '-blur', blur, '-colorspace', colorspce, '-channel', channel, '-alpha', alpha, added_options]
                # new_options = option_combination

                # Removing -resize parameter since it will cause MemoryAllocationError in the program
                # new_options = [new_options[0]] + new_options[3:]

                # Run the program with the new options
                max_attempts = 2 # Number of attempts to run the program before failing
                for candidate_type, candidate_functions_list in candidate_functions.items():
                    # In order to run just some specific function sets (i.e., entropy, CV, etc.)
                    if candidate_type not in ['entropy', 'cv']:
                        continue

                    is_successful = False
                    current_attempt = 0

                    while not is_successful and current_attempt < max_attempts:
                        try:
                            # Run 638.imagick_s and instrument it
                            vanilla_command = ['uftrace', 'record','--no-libcall', '--time', '-P', 'main', './imagick_s_base.mytest-m64', '-limit', 'disk', '0']
                            vanilla_command.extend(new_options)
                            vanilla_command.append('output.tga')

                            full_command = ['uftrace', 'record', '--time', '--no-libcall', './imagick_s_base.mytest-m64', '-limit', 'disk', '0']
                            full_command.extend(new_options)
                            full_command.append('output.tga')

                            # Add the candidate functions with -P for each to the full command from second index
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
                            
                            # Run the program with the new options, and trace the execution
                            trace(vanilla_command, full_command, parameters, table_name, build, 
                                  cwd, skip_vanilla=False if candidate_type == 'full' else True)

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
                with open(f'failures.imagick.{range_c.replace("-","_")}.json', 'w') as f:
                    json.dump(failures, f, indent=4)