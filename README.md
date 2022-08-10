This repo contains python scripts that submits multiple jobs of JETSCAPE on a HPC. Specifically, this repo is for heavy flavor study using the branch:
https://github.com/JETSCAPE/JETSCAPE-COMP/tree/ReleaseAApaper_for_HD_HF_photon. This branch is is based on JETSCAPE 3.1, has the virtuality dependent qhat implementation, and some custom modifications. These modifications include custom event header in the final hadron files that include hydro information for that event (so we can analyze anisotropic flow), modifications to the ColorlessHadronization module so it can read in custom Pythia hadronization settings from the user xml file, and a custom energy loss module that reads in final parton list and feed it directly into hadronization. 

These custom modifications has not been merged into the main branch for the following reasons:
1. The custom event header is not necessary. You can read in the hydro information directly from the hydro files.
2. The modifications to the ColorlessHadronization module and the custom energy loss module are there so we can run different hadronization modes with the same final parton file without running the entire event multiple times. I don't think others in JETSCAPE have this kind of need now, and they may come up with a more integrated solution when they do. Please ask in the collaboration if you decide to merge this feature.

### WSU

The WSU folder contains scripts that were tested on the WSU grid that uses the slurm job scheduler. It is for exploring JETSCAPE with different settings once at a time. You need to put the JETSCAPE folder, the user xml file and the sub_to_run.py script under the same folder. Then type "python3 sub_to_run.py" will submit the jobs with different pThat bins. 

The sub_to_hadronize.py will submit jobs that takes final partons generated from the previous step and hadronize them with the hadronization settings you assign. 

We divide the simulation into two parts so we can study the effects of different hadronization and (maybe) hadronic rescattering modules. 


### NERSC_Bayesian

This folder is used for running JETSCAPE simulations with different parameters (for Bayesian parameter inference purpose) on NERSC. NERSC also uses the slurm scheduler but some details are different. Also NERSC does not allow you to submit many small jobs. So we will instead use whats called task farmer. 

The steps are the following:
1. Download the JETSCAPE repo to the same folder. Get all the external data tables.
2. Run design_jetscape.py to generate the design points.
3. Run get_jetscape.py to copy JETSCAPE and user xml files to all the design point folders.
4. Run copy_and_generate.py to generate the job bash scripts for each design point.
5. Run generate_tasks.py to generate the final submission scripts.

I choose to generate 5 submission scripts, each contains hundreds of JETSCAPE jobs. Then you need to manually submit these 5 scripts.
Hadronization is not explored at the moment, as they are found to be not affecting the R_AA's too much. In the future, when we look at more observables, we may need to use different hadronization settings.

