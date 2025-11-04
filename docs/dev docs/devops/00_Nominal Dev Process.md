---
domain: software
parent: yggdrasill
---

## Daily work
**Local test**
If no changes to dockerfile, main-github-actions.sh, or new python packages:
		- then no need to rebuild container:
	If dockerfile has changed, need to rebuild container:
		- [[00a_container rebuild]]
	If new python package has been added, need to regenerate environment.yml AND recreate the container
		- [[Recreate environment.yml]]
		- [[00a_container rebuild]]

To deploy the app locally (on dev port 8502) run *main-github-actions.sh*
## Nominal merge process
- Make your changes
- Test locally:
	- From repo root, run: *./main_github_actions.sh*
		- This will deploy (locally) to port 8502. See [[03_port assignments]]
	- When you think it's working.
- Create a new branch
- Commit to the new branch
- Push
	- This will deploy to a branch location. See [[03_port assignments]]
	- Check the branch.
- Merge latest master into your branch. 
- Commit master -> this should redeploy to the branch location
- Open up the PR to master -> this should make a dedicated PR build (on a different port)
- Review the PR build.
- Accept the merge -> this should deploy to prod.
- Check prod (i.e. port 8501) is good.


```mermaid
flowchart TD
    A[Make your changes]
    B[Test locally. See main_github_actions.sh]
    C[Create a new branch]
	D[Commit to the new branch]
    B1[Deployed to port 8502]
    B2{Human-review on port 8502}

    E[Push branch to git remote]
    F[Merge latest master into branch]
    E1[E1-Deployed to branch-specific port. See 03_port assignments]
    G[Commit merge from master]
    G1[Triggers redeploy to branch location]
    H[Open PR to master]
    H1[Triggers PR build on dedicated port]
    I[Review PR build]
    J[Accept merge to master]
    K[Deployed to prod on port 8501]
    L[Check prod deployment]

	%% Flow
    A --> B
	B --> |manual run of main_github_actions.sh| B1 --> B2
	B --> C --> D --> |git push|E
	E -.->|github-actions| E1
    E --> F --> G --> G1 --> H --> H1 --> I --> J --> K --> L
    
```













