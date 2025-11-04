---
parent: product 1
status: new
type: surface
---

# Fundamentals
**All notes in the same folder as this note**
```dataview
LIST WHERE contains(file.folder, this.file.folder)
```
**Product Component List**
```dataview
list
where contains(file.path, "my fourth project - note linking")
	and parent = [[product 1]] 
	and type = "component"
```
**User story feature queue**
```dataview
list
where contains(file.path, "my fourth project - note linking")
	and user_story = [[user story 1]] 
	and type = "feature"
sort sequence asc
```
**Component feature queue**
Component 1
```dataview
list
where contains(file.path, "my fourth project - note linking")
	and parent = [[component 1]] 
	and type = "feature"
sort sequence asc
```
Component 2
```dataview
list
where contains(file.path, "my fourth project - note linking")
	and parent = [[component 2]] 
	and type = "feature"
sort sequence asc
```
**Feature task queue**
Feature 1
```dataview
list
where contains(file.path, "my fourth project - note linking")
	and parent = [[feature 1]] 
	and type = "task"
sort sequence asc
```
**Skill queue**
Skill = Python
```dataview
list
where contains(file.path, "my fourth project - note linking")
	and skill = "python"
sort skill_sequence asc
```
# Combinations
**Feature skill queue**
Feature 1, python tasks
```dataview
list
where contains(file.path, "my fourth project - note linking")
	and parent = [[feature 1]] 
	and skill = "python"
sort skill_sequence asc
```