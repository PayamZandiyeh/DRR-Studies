# StereoFlouroscopyRegistration

## Software Guidelines
We are going to follow the [ITK Style](https://itk.org/Wiki/ITK/Git/Develop) for software
development. Those rules roughly manifest themselves as such:

1) Do not push to master
2) All work is done on a seperate branch: `git checkout -b my-topic`
3) Merge on GitHub after at least one review
4) Follow standard prefixes for commits:
	- BUG: Fix for runtime crash or incorrect result
	- COMP: Compiler error or warning fix
	- DOC: Documentation change
	- ENH: New functionality
	- PERF: Performance improvement
	- STYLE: No logic impact (indentation, comments)
	- WIP: Work In Progress not ready for merge

## Setup Local Python Environment
To setup your local Python environment, do the following.

1) [Install Anaconda](https://www.anaconda.com/download)
2) Open a terminal and move to this directory
3) Install conda dependancies: `conda env create --file environment.yml`
4) Activate you new found environment: `conda activate drr`
5) Install the package locally: `pip install -e .`
6) If you are on mac, install one additional dependancy: `conda install python.app`

Note: You will need to activate the `reg` environment for each terminal you use.
