# Trace Data
**Description:** This folder contains the trace data collected for each program. For each program we have:
- **vanilla**: Only the baseline information about the program's execution time for each input. It doesn't involve any tracing.
- **analysis**: The trace data which has been captured with full tracing enabled. It consist of 2,500 executions (i.e., for each input).
- **optimized**: The trace data after applying the pruning algorithms. There are 333 executions (i.e., for each input) for each pruning method (i.e., entropy, cv, etc.).
- **regression**: Same as optimized, the collected trace data for each input and each pruning method. However, a performance regression was injected for each input.

## Structure of the Trace Data
Each trace data is stored in a ```JSON``` file. The structure of the records is as follows:
```json
{
    "build": {
        "type": "The build type of the program (e.g., entropy, cv, etc.)",
        "range": "Indicating the target function in regression injection (e.g., low-0, low-1, ..., medium-2, ..., high-4, etc.)"
    },
    "stats": {
        "cpu_utilization": [
            "core-0 -> The CPU utilization of core 0",
            "core-1 -> The CPU utilization of core 1",
            ...
        ]
    },
    "times": {
        "vanilla": "The execution time of the program without any tracing",
        "full": "The execution time of the program with tracing",
    },
    "sizes": {
        "full": "The size of the trace data regarding storage usage (in kilobytes)",
    },
    "parameters": {
        "": "The input parameters of the program for that specific execution",
    },
    "functions": {
        "function_name": {
            "self": "Total self execution time of the function",
            "self_min": "Minimum self execution time of the function",
            "self_max": "Maximum self execution time of the function",
            "calls": "Total number of calls to the function"
        },
        ...
    }
}
```