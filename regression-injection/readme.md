# Regression Injection Tool
**Description:** This tool is designed to inject a code block (i.e., in this study, performance regression) to a particular point of the program (i.e., a specific function).

## Usage
In order to use this tool, you have to define a code block (e.g., a constant delay code block) to be injected to the program. You can check the ```code_blocks``` directory for more details. There are some sample code blocks in the aforementioned directory, but in the submitted research paper, we only used the *constant delay* code block. 

After defining the code block, you have to define the injection point. For this specific scenario (i.e., our research), we defined a list of target functions (i.e., ```target_functions.json```) to use as injection points. The structure of the the JSON file is as follows:
```json
{
    "program_name": {
        "cluster (i.e, low, medium, or high)": [
            {
                "function_name": "function_name",
                "calls": "number of calls to the function (this property does not have any effect on the injection tool, and it is just for better interpretation of the results)"
            },
            ...
        ],
        ...
    },
    ...
}
```

After defining the code block and the injection points, you can run the injection tool as follows:
```bash
python3 regression_inserter.py REGRESSION_TYPE PROGRAM_NAME PROGRA_SOURCE_DIRECTORY --range=RANGE --reset --no-build
```
where:
* ```REGRESSION_TYPE``` is the type of the regression to be injected (e.g., constant_delay, calculations, etc.)
* ```PROGRAM_NAME``` is the name of the program to be injected (e.g., 631.deepsjeng, 638.imagick_s, etc.)
* ```PROGRAM_SOURCE_DIRECTORY``` is the path to the source code of the program (e.g., %PATH/631.deepsjeng_s/src)
* ```--range=RANGE``` is the range of the injection points (e.g., low-0, low-1, ..., medium-2, etc.)
* ```--reset``` is an optional argument to reset the source code to the original version (i.e., without any injected code block)
* ```--no-build``` is an optional argument to skip the build process (i.e., if you have already built the program, you can use this argument to skip the build process). If you don't provide this argument, the tool will build the program after injecting the code block.

## Example
Consider we have mentioned that function ```main``` is a target function (i.e., low-0), and we want to inject a constant delay code block to it. This is the structure of the function before injection:

```cpp
// some code (e.g., #include, etc.)

int main() {
    // some code

    return 0;
}
```

We use the following command to inject the code block:

```bash
python3 regression_inserter.py constant_delay 631.deepsjeng_s %PATH/631.deepsjeng_s/src --range=low-0
```

Based on the code statments that we have mentioned in the ```code_blocks/constant_delay.cpp``` file, the tool will inject code block to the target function. The structure of the function after injection is as follows:

```cpp
#include <thread>
#include <chrono>
// some code (e.g., #include, etc.)

int main() {
    const auto start_time = std::chrono::high_resolution_clock::now();
    const auto duration_time = std::chrono::microseconds(5);

    do {
        std::this_thread::yield();
    } while (std::chrono::high_resolution_clock::now() - start_time < duration_time);

    // some code

    return 0;
}
```