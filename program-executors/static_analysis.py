import json
import subprocess
from loess.loess_1d import loess_1d
from ckwrap import ckmeans

import numpy as np
from db import get_previous_parameters

analysis_path_path = 'srcml_analyzer.py'

program_src_paths = {
    '631_sjeng': 'SPEC_PATH_HERE/benchspec/CPU/531.deepsjeng_r/src',
    '638_imagick': 'SPEC_PATH_HERE/benchspec/CPU/538.imagick_r/src',
    '657_xz': 'SPEC_PATH_HERE/benchspec/CPU/557.xz_r/src',
    'su2_cfd': 'SU2_PATH_HERE',
    'parsec_freqmine': 'PARSEC_PATH_HERE/pkgs/apps/freqmine/src'
}

weights = {
    'line_of_codes': 0.25,
    'number_of_loops': 0.2,
    'number_of_nested_loops': 0.15,
    'number_of_calls': 0.15,
    'is_recursive': 0.1,
    'number_of_branches': 0.1,
    'number_of_parameters': 0.05
}

def normalize_metrics(data, metric_names):
    normalized_data = []
    for func in data:
        normalized_func = {}
        for metric in metric_names:
            # Calculate range only if it's not zero
            max_value = max(data, key=lambda x: x[metric])[metric]
            min_value = min(data, key=lambda x: x[metric])[metric]
            if max_value != min_value:
                normalized_value = (func[metric] - min_value) / (max_value - min_value)
            else:
                # Handle case where range is zero
                normalized_value = 0.0 if func[metric] == min_value else 1.0
            normalized_func[metric] = normalized_value
        normalized_func['name'] = func['name']
        normalized_data.append(normalized_func)
    return normalized_data

def rank_functions(data, metric_weights):
    scores = {}
    for func in data:
        score = sum(func[metric] * weight for metric, weight in metric_weights.items())
        scores[func['name']] = score

    sorted_functions = dict(sorted(scores.items(), key=lambda x: x[1], reverse=True))
    return sorted_functions

def get_smooth_dxdy_clusters(input, number_of_clusters = 2):
    xout, yout, _ = loess_1d(np.arange(len(list(input.keys()))), np.array(list(input.values())))
    dydx = np.gradient(yout,xout)
    clusters = ckmeans(dydx, number_of_clusters).labels

    return yout, dydx, clusters

def cluster_functions(input):
    clusters = {}
    for i in range(0, len(input)):
        if clusters.get(str(input[i]), 0) == 0:
            clusters[str(input[i])] = []
        clusters[str(input[i])].append(i)
    return clusters

if __name__ == "__main__":
    static_functions = {}
    for program, path in program_src_paths.items():
        docs = list(get_previous_parameters(f'reports-{program}_analysis'))
        program_intial_functions = set()
        for doc in docs:
            for function in list(doc['functions'].keys()):
                program_intial_functions.add(function.split('(')[0])
        program_intial_functions = list(program_intial_functions)

        function_data = subprocess.run(['python3', analysis_path_path, path], capture_output=True)
        function_data = json.loads(function_data.stdout.decode('utf-8'))

        candidate_functions = []
        for file_script in function_data:
            for function in file_script['functions']:
                if function['name'] in program_intial_functions:
                    function['number_of_branches'] = sum(list(function['number_of_branches'].values()))

                    # Keep only the metrics we are interested in (weights)
                    function = {k: v for k, v in function.items() if k in weights.keys() or k == 'name'}
                    candidate_functions.append(function)

        # How many repeated functions are there?
        # Based on the name of the function -> function['name']
        repeated_functions = set()
        for function in candidate_functions:
            f_name = function['name']
            if f_name in repeated_functions:
                continue

            for other_functions in candidate_functions:
                if other_functions['name'] == f_name and other_functions != function:
                    repeated_functions.add(other_functions['name'])
                    break

        # Combine the repeated functions and average their metrics
        for repeated_function in repeated_functions:
            new_function = {'name': repeated_function}
            repeated_function_data = [function for function in candidate_functions if function['name'] == repeated_function]
            for metric in weights.keys():
                if metric == 'is_recursive':
                    new_function[metric] = max([function[metric] for function in repeated_function_data])
                else:
                    new_function[metric] = sum([function[metric] for function in repeated_function_data]) / len(repeated_function_data)

            candidate_functions = [function for function in candidate_functions if function['name'] != repeated_function]
            candidate_functions.append(new_function)


        normalized_data = normalize_metrics(candidate_functions, list(weights.keys()))
        ranked_functions = rank_functions(normalized_data, weights)

        _, _, clusters = get_smooth_dxdy_clusters(ranked_functions, 2)
        cc = cluster_functions(clusters)
        for key,value in cc.items():
            threshold = value[0]

            final_functions = ([function for function, weight in ranked_functions.items() if weight >= list(ranked_functions.values())[threshold]])

        static_functions[program] = final_functions

    with open('static_functions.json', 'w') as f:
        json.dump(static_functions, f, indent=4)