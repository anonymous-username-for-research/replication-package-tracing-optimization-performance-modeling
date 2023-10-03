# Replication Package - Tracing Optimization for Performance Modeling and Regression Detection

**Description**: This repository contains the replication package for the paper "Tracing Optimization for Performance Modeling and Regression Detection" submitted to the FSE '24 conference.

## Structure
### Inputs
The (sample) inputs we used for the programs (mostly, binary inputs).

### Previous Parameters
The inputs that were previously used for the analysis dataset (i.e., running the programs with 2,500 inputs).

### Regression Injection
The scripts for injecting performance regressions into the programs. More details of this section is provided inside the folder.

### Trace-Data
Contains the trace data collected for each program. For each program we have:
- **vanilla**: Only the baseline information about the program's execution time for each input. It doesn't involve any tracing.
- **analysis**: The trace data which has been captured with full tracing enabled. It consist of 2500 executions (i.e., for each input).
- **optimized**: The trace data after applying the pruning algorithms. There are 333 executions (i.e., for each input) for each pruning method (i.e., entropy, cv, etc.).
- **regression**: Same as optimized, the collected trace data for each input and each pruning method. However, a performance regression was injected for each input.

### Analysis Jupyter Notebook
The complete notebook for analyzing the trace data (i.e., analysis trace datasets), determining performance-sensitive functions, building performance models (using the optimized trace data), and detecting performance regressions (using the regression trace data). Check the notebook for more details.

### Scripts
The scripts for running the programs and collecting the trace data. More information about how the scripts work is provided inside each file. **The scripts don't work without having the program's source code (e.g., SPEC CPU 2017)**

## Dependencies
We used Python 3.10 to run the scripts and the Jupyter notebook. The required libraries in order to run all of the files are provided in the `requirements.txt` file. You can install them using the following command:
```bash
pip install -r requirements.txt
```