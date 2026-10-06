# 10-Meter Band Moxon Antenna

This document explains the full-wave electromagnetic simulation of the 10-meter Moxon antenna using `Palace` (Parallel Large-scale Computational Electromagnetics), a finite-element-method (FEM) simulator. Palace has been developed by the Amazon Web Services (AWS) Center for Quantum Computing (https://awslabs.github.io/palace/stable/). It is an open-source software licensed under Apache-2.0 and may be used for both non-commercial and commercial applications.


## Full-wave Electromagnetic Simulations

The full-wave electromagnetic simulation of the Moxon antenna using `Palace` consists of two distinct steps: mesh generation and FEM simulation using the generated mesh. Python scripts are provided to simplify each task. The name and description of each script are given in the following table:

<table style="width: 600px;">
  <caption></caption>
  <thead>
    <tr style="background-color: white;">
      <th>Script Name</th>
      <th>Description</th>
    </tr>
  </thead>
  <tbody>
    <tr style="background-color: white;">
      <td>moxon_mesh.py</td>
      <td>Geometry and mesh generator for the Moxon antenna</td>
    </tr>
     <tr style="background-color: white;">
      <td>moxon_run.py</td>
      <td>Simulator launcher for the Moxon antenna</td>
    </tr>
    <tr style="background-color: white;">
      <td>mesh_info.py</td>
      <td>Mesh checker and attribute reader</td>
    </tr>
  </tbody>
</table>

The mesh-generation script is designed to read the antenna parameters from an Excel spreadsheet. To simulate a Moxon antenna, the user first enters the desired geometrical parameters into an Excel worksheet. As many parameter combinations as desired can be entered. Each combination is referenced by a unique index number in the spreadsheet. The antenna mesh can then be generated for a particular combination using its corresponding index number, after which the FEM simulation can be run using the generated mesh.

This approach provides flexibility for automation. For example, multiple geometric variations can be simulated overnight by first entering the parameter values into the spreadsheet, generating the mesh files, and then sweeping the corresponding indices in a Bash loop to run the simulator.

Installation and operating instructions are given below. These steps have been tested on AlmaLinux 9.8, although they should work on other Linux distributions with little or no modification.

---

## Installing Palace


### Step 1 – Install Spack

`Spack` is a package manager designed for scientific and high-performance-computing software (https://spack.io/). It simplifies the installation and management of scientific software and allows multiple versions of a package to be installed and selected as needed. Here, Spack is used to install the `Palace` simulator.

Installation of `Palace` requires certain system-level packages to be present. Therefore, first install the following packages with `root` privileges:

```bash
sudo dnf install git
sudo dnf install gcc gcc-c++ gcc-gfortran
sudo dnf install lbzip2
sudo dnf install bzip2
sudo dnf install patch
sudo dnf install unzip
```

Then, install and activate `Spack` as follows. Spack can be installed by a regular user, and doing so is recommended:

```bash
git clone -c feature.manyFiles=true https://github.com/spack/spack.git

source ~/spack/share/spack/setup-env.sh
```


### Step 2 – Install Palace

Once `Spack` is installed and activated, `Palace` and its required dependencies can be installed using the following command:

```bash
spack install palace
```

After installation, `Palace` should be loaded before use:

```bash
spack load palace
```

### Step 3 – Test the Installation

After loading `Palace`, run the following command to verify the installation:

```bash
palace --help
```

You should see the help output from the simulator. The next step is to download and run a simple test case:

```bash
mkdir -p ~/palace-test/mesh
cd ~/palace-test

curl -o mesh/spheres.msh https://raw.githubusercontent.com/awslabs/palace/refs/heads/main/examples/spheres/mesh/spheres.msh
curl -O https://raw.githubusercontent.com/awslabs/palace/refs/heads/main/examples/spheres/spheres.json

palace --dry-run spheres.json
```

If the dry-run does not report any errors, proceed with the full simulation:

```bash
palace -np 1 spheres.json
```

The simulation should start by displaying the `Palace` banner and other relevant information. The model consists of two conducting spheres with radii of 1 cm and 2 cm, separated by 5 cm in vacuum and surrounded by a distant grounded boundary. Palace computes the Maxwell capacitance matrix using a third-order finite-element solution.

Once the simulation is complete, inspect the `terminal-C.csv` file in the `postpro` directory. You should obtain capacitance values close to the following, together with the corresponding analytical values:

<table style="width: 600px;">
  <caption></caption>
  <thead>
    <tr style="background-color: white;">
      <th>Parameter</th>
      <th>Palace Simulation [pF]</th>
      <th>Analytical Value [pF]</th>
    </tr>
  </thead>
  <tbody>
    <tr style="background-color: white;">
      <td>C<sub>11</sub></td>
      <td>1.23745</td>
      <td>1.23052</td>
    </tr>
    <tr style="background-color: white;">
      <td>C<sub>22</sub></td>
      <td>2.47841</td>
      <td>2.43154</td>
    </tr>
    <tr style="background-color: white;">
      <td>C<sub>12</sub></td>
      <td>-0.4771</td>
      <td>-0.4946</td>
    </tr>
  </tbody>
</table>

---

## Running Palace


### Step 1 – Set Up a Python Virtual Environment

It is recommended to use a Python virtual environment for running the provided Python scripts. To create the environment, first ensure that Python 3.12 is installed on the operating system:

```bash
sudo dnf install python3.12
```

Then, proceed as follows from a terminal:

```bash
python3.12 -m venv ~/.palace01
source ~/.palace01/bin/activate
pip install --upgrade pip
pip install xlrd
pip install gmsh
```

### Step 2 – Activate the Python Virtual Environment

The environment is already active immediately after the creation step above. For subsequent simulation sessions, activate it again as follows:

```bash
source ~/.palace01/bin/activate
```


### Step 3 – Update the Moxon.xls File

Open the provided `Moxon.xls` template and enter the desired parameter combinations. The Moxon antenna parameters used by the script are shown in Fig. 1. You may enter as many combinations as desired. Be sure to assign a unique index number to each combination.

<figure>
  <img src="Moxon_model.svg" alt="Moxon_model">
  <figcaption>Figure 1: Aluminum-tube Moxon antenna model showing the simulation parameters.</figcaption>
</figure>

After entering the parameters, save the file.

### Step 4 – Generate the Antenna Model and Mesh

Generate the antenna geometry and mesh file using the following command:

```bash
./moxon_mesh.py 001
```

The script takes the index number of the desired parameter combination as a command-line argument. In the example above, the model and mesh are generated for index `001`. Once complete, the script creates a directory with the same name as the index and saves a mesh file (`.msh`) and a stereolithography file (`.stl`) in that directory. The `.msh` file is used by the Palace simulator. The `.stl` file can be opened with a CAD editor to inspect the generated model.

Note that the `.stl` file contains the mesh triangles, and the air volume surrounding the antenna may therefore obscure the antenna elements. To visualize the antenna elements, it may be necessary to explode the model into its mesh groups and make the surrounding air volume invisible in the CAD tool.

You may also verify the integrity of the generated mesh and read the embedded design attributes using the following script:

```bash
./mesh_info.py ./001/moxon.msh
```

The mesh-generation script embeds the parameter values used to generate the antenna model in the mesh file as design attributes. This is useful when the parameter values associated with a particular mesh file need to be identified later.

### Step 5 – Simulate the Antenna

Once the mesh is ready, generate the JSON configuration file that describes the model and simulation parameters using the provided template, and perform a dry-run:

```bash
source ~/spack/share/spack/setup-env.sh
spack load palace

./moxon_run.py 001 1 1
```

The first command-line argument is the index number. The second argument instructs the script to generate JSON configuration file, and the last argument instructs it to perform a dry-run to check the JSON file.

The JSON configuration file contains information required to describe the model, including material properties, frequency range, and desired output files. The script copies a template to create a local JSON configuration file in the simulation directory, which has the same name as the index. Simulation parameters may then be modified by directly editing this local file. For subsequent runs, set the second command-line argument to zero to avoid overwriting the modified local configuration file.

If the JSON configuration passes the dry-run, proceed with simulation using the following command:

```bash
./moxon_run.py 001 0 0
```

Because the JSON file has already been created and verified by the dry-run, the last two arguments are zero in this case. The simulation should start and proceed through the specified frequency sweep.

> [!NOTE]
> Using the mesh settings in the script, the simulation of the 10-meter Moxon antenna reaches a peak memory usage of approximately 22.7 GB. This should not be interpreted as the minimum memory required for the problem; further optimization of the mesh may reduce memory consumption while maintaining comparable simulation accuracy.
>

If many parameter combinations are to be simulated overnight, a Bash loop similar to the following can be used (assuming the corresponding mesh files are generated in advance):

```bash
for i in $(seq -w 001 010); do
    ./moxon_run.py "$i" 0 0
done
```
