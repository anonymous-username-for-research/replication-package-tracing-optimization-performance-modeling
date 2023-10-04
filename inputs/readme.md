# Program Inputs
**Description:** This folder contains the input files for the program. Below is a description of each directory (i.e., each program).

## Programs
### 631.deepsjeng_s
This program requires the following inputs to be executed:
- **chess position:** A chess position in FEN (Forsyth-Edwards Notation) format. The FEN format is described [here](https://en.wikipedia.org/wiki/Forsyth%E2%80%93Edwards_Notation).
- **depth**: The depth of the search tree. This is an integer value.

### 638.imagick_s
This program requires a set of CLI arguments to be executed. The arguments are described [here](https://imagemagick.org/script/command-line-options.php). Also, it requires an input image to perform the operations on. Some sample images are provided in the program's directory.

### freqmine
There is a sample input data for this program, which contains a number of transactions. Each transaction is a set of items. The items are separated by a space. The transactions are separated by a new line.
<br>
We generate new inputs (i.e., transactions) based on the structure of the sample file using the code provided in ```runner.parsec.freqmine.py```.

### SU2 (CFD)
This program requires a configuration file (i.e., ```input.SU2_CFG.cfg```) in order to be executed.  Also, it requires an input file (i.e., a mesh file) to perform the operations on (i.e., ```mesh_NACA0012_inv.su2```).