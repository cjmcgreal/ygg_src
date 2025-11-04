# Detailed debug process
## Frontend
[[00_frontend debug process index]]

### Run the streamlit app (and nothing else?)
```
**Note:** 
- This will not rebuild the "databases" i.e. the csv files.
- if you need to rebuild the conda environment, see below.
#### Clean conda rebuild (delete and recreate)
``` bash
conda env remove -n ygg -y
conda env create -n ygg -f Domains/Software/yggdrasill/_src/hlidskjalf/_src/environment.yml
```
#### Update conda without removing
```bash
conda env update -n ygg -f Domains/Software/yggdrasill/_src/hlidskjalf/_src/environment.yml --prune
```
#### Install Spyder (useful for local dev)
```bash
conda activate ygg
pip install spyder
```
**To run spyder** - after it's installed:
```bash
conda activate ygg
spyder
```
### Run the streamlit app from the start_app.sh command
**Note** - this *will* rebuild the csv files.
```bash
cd Domains/Software/yggdrasill/_src/hlidskjalf/_src
conda activate ygg
start_app.sh
```

### Run the streamlit app from the main-github-actions.sh script

### Run the streamlit app from a local docker container

Run the streamlit app via github actions

To start the github-actions-runner

## Docker cheat sheet
- Run the Yggdrasill docker file (locally) - See: ./run_dockerfile.sh
- list all running containers: docker ps -a
- stop a container: docker stop [container_id]
- remove a container: docker rm [container_name]

### rebuild a container
[[00a_container rebuild]]

## VSCode helpful hints
- Attach to a running container: F1 -> *Dev Containers - Attach to a running container*


Bash: 
     