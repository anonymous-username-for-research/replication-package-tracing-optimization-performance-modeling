# Program Executors

## Trace Data Collection Scripts
This directory contains the scripts for trace data collection of each program (i.e., `runner.PROGRAM.py`). The trace data collection is done by running the program with the `uftrace`. All the programs has the same structure of running procedure, but they vary regrading their input preparation and execution. You can find the details of each program in their corresponding script.

## Static Analysis Scripts
The two `static_analysis.py` and `srcml_analyzor.py` represents the procedure of static analysis of the programs. The former determines the performance-sensitive functions of each program based on its static features (e.g., line of codes, number of loops, etc.). The latter extracts the XML representation of the programs using `srcml` tool. Also, the former script uses the latter script to extract the XML representation of the programs. You can find the details of each script in their corresponding script.