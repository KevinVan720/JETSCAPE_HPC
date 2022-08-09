This repo contains python scripts that submits multiple jobs of JETSCAPE on a HPC. Specifically, this repo is for heavy flavor study using the branch:
https://github.com/JETSCAPE/JETSCAPE-COMP/tree/ReleaseAApaper_for_HD_HF_photon. 

### WSU

The WSU folder contains scripts that were tested on the WSU grid that uses the slurm job scheduler. It is for exploring JETSCAPE with different settings once at a time. You need to put the JETSCAPE folder, the user xml file and the sub_to_run.py file under the same folder. Then type "python3 sub_to_run.py" will submit the jobs that has different pThat bins. 

The sub_to_hadronize.py will submit jobs that takes final partons generated from the previous step and hadronize them with the settings you assign. 

### NERSC_Bayesian

This folder is used for running JETSCAPE simulations with different settings on NERSC. NERSC also uses the slurm scheduler but some details are different. Also NERSC does not allow you to submit many small jobs. So we will instead use whats called task farmer. 

The steps are the following:
1. Download the JETSCAPE repo to the same folder. Get all the external data tables.
2. Run design_jetscape.py to generate the design points.
3. Run get_jetscape.py to copy JETSCAPE and user xml files to the design point folders.
4. Run copy_and_generate.py to generate the job scripts for each design point.
5. Run generate_tasks.py to generate the final submission scripts.

I choose to generate 5 submission scripts, each contains hundreds of JETSCAPE jobs. Then you need to manually submit these 5 scripts.
Hadronization is not explored at the moment, as they are found to be not affecting the R_AA's too much. In the future, when we look at more observables, we should use different hadronization settings.

