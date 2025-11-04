---
parent: product 1
status: new
type: documentation
---

**Fields**
Sequence - where is this note in the queue of notes *of the same type*.
- e.g. if this note is *type = task* then the *sequence* field refers to the task queue.

**Types**
Product -> something a *user* interacts with

Component -> something a *developer* interacts with
- should be opaque to the user, i.e. this is a dev architecture object.
- User Stories should tie to a product, not a component.
- If it looks like a user story needs to tie to a component, should consider promoting that component to a product.
- e.g. python class, or package, or file

User Story -> a child of a *product*. Functionality a user wants/needs

Feature -> a child of a *component*. A change that needs to be made to a component

Skill -> a property of a developer.