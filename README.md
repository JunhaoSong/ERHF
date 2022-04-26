# ERHF
Eqt-REAL-Hypoinverse-Flow (ERHF) to detect and locate earthquakes

This flow follows the structure of ESPRH (https://github.com/MrXiaoXiao/ESPRH)

uses some perl/python scripts from LOC-FLOW (https://github.com/Dal-mzhang/LOC-FLOW)

and provide the same example data as seisloc (https://pypi.org/project/seisloc/0.0.8/)

### Download dependencies
EQTransformer: git clone https://github.com/smousavi05/EQTransformer

REAL: git clone https://github.com/Dal-mzhang/REAL

Hypoinverse: https://www.usgs.gov/software/hypoinverse-earthquake-location

Please compile REAL and Hypoinverse source scripts and get two executable files (hyp1.40 and REAL)

### Install necessary python packages in a new environmnt
```Bash
conda create -n ERHF python=3.7
conda activate ERHF
git clone https://github.com/JunhaoSong/ERHF
cd ERHF
sh installation.sh
```

### Edit configuration.yaml, prepare velocity model, hypoinverse command file
```Bash
python step01_run_Eqt_detection.py
python step02_run_REAL_association.py
python step03_run_Hypoinv_absloc.py
```
