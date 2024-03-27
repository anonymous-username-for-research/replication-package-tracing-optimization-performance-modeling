# Program Inputs
**Description:** This folder contains the input files for the program. Below is a description of each directory (i.e., each program).

## Programs
### 631.deepsjeng_s
This program requires the following inputs to be executed:
- **chess position:** A chess position in FEN (Forsyth-Edwards Notation) format. The FEN format is described [here](https://en.wikipedia.org/wiki/Forsyth%E2%80%93Edwards_Notation).
- **depth**: The depth of the search tree. This is an integer value.

### 638.imagick_s
This program requires a set of CLI arguments to be executed. The arguments are described [here](https://imagemagick.org/script/command-line-options.php). Also, it requires an input image to perform the operations on. Some sample images are provided in the program's directory.

### 657.xz_s
This program requires an input file to be executed. The input file is a compressed file (i.e., a .xz file). In order to generate the input files (i.e., before compressing them), we created a Python script that generates random files with different types (e.g., text, image, audio, etc.). You may check the ```file_input_generator.py``` script in the ```657.xz_s``` directory.

### freqmine
This program requires a dataset to be executed. The dataset is a text file that contains a list of transactions. To generate the dataset, we created a Python script that generates random transactions. You may check the ```transaction_generator.py``` script in the ```freqmine``` directory.

### SU2 (CFD)
This program requires a configuration file (i.e., ```input.SU2_CFG.cfg```) in order to be executed.  Also, it requires an input file (i.e., a mesh file) to perform the operations on (i.e., ```mesh_NACA0012_inv.su2```).