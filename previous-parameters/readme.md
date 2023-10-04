# Previous Parameters
**Description:** This folder contains the randomly sampled inputs for each program that were used for the analysis tracing. Since we used **2,500** random inputs during the analysis tracing, in this folder, we have **333** randomly sampled inputs for each program (confidence level is 95% and margine of error is 5%).

This is the formula to calculate the number of samples needed for a given population:

$n = Math.ceil(\frac{\frac{{Z^2 \cdot \text{{std}} \cdot (1 - \text{{std}})}}{{E^2}}}{{1 + \frac{{Z^2 \cdot \text{{std}} \cdot (1 - \text{{std}})}}{{E^2 \cdot N}}}})$

Where:
- $n$ is the required sample size.
- $Z$ is the critical value corresponding to the desired confidence level ($C$). In our case, $C = 95\%$ and $Z = 1.96$.
- $std$ is the estimated population proportion. In our case, $std = 0.5$.
- $E$ is the margin of error. In our case, $E = 0.05$.
- $N$ is the population size. In our case, $N = 2500$.

## How we sampled the inputs?
We used the following script to sample the inputs:
```python
import random
import pymongo
...
# Initializing the connection to the database
...
documents = list(db["PROGRAM_NAME_analysis"].find())
all_parameters = [document['parameters'] for document in documents]
sampled_parameters = random.sample(all_parameters, 333)
```