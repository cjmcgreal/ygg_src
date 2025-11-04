---
domain: software
parent: yggdrasill
type: procedure
---

From the directory where the docker file lives (usually root of yggdrasill repo):
```bash docker build --no-cache -t [container_name] . ```

as an example:
```bash docker build --no-cache -t yggdrasill:local-dev . ```