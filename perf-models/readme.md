# Performance Models

This directory contains performance models that were built through our study. The models are groupped into two categories: (1) optimized performance models (i.e., built using the performance-sensitive functions identified by pruning approaches, such as entropy or coefficient of variation) and (2) regression-based performance models (i.e., similar to optimized performance models, but are built on top of programs that contains performance regression).

## Structure of the Models
Each program has followying files:
- `PROGRAM_MODE_MODEL.pkl`: The pickled file containing the performance model for the program. Each program has 10 different modes (i.e., entropy, CoV, entropy and CoV, etc.) and 5 different model names (i.e., linear regression, random forest, etc.).

- `PROGRAM_MODE_MODEL_errors.json`: The json file containing the errors of the performance model for the program. The errors are calculated using the mean absolute error (MAE), root mean squared error (RMSE), and R-squared.

- `PROGRAM_MODE_experiment_data.pkl`: The pickled file containing the experiment data of PyCaret for the program. We use this data to save the experiment data for the performance model, which can be used to reproduce the model.