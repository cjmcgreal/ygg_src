---
type: runestone
parent: "[[exercise]]"
domain: "[[exercise]]"
---
**Links**
module [[exercise module]]
module version [[exercise module - v0p1]]

**Prompt** - Claude planning mode

Desired changes:
(1) Layout.
The main streamlit exercise tab should only have the "next recommended exercise".
All of the advanced configuration stuff should just be accessible from the "exercise" sidebar "pages".
The top, of the sidebar pages should have a "General" page at the top. This "general" page should have an exercise tab, that just has the workout of the day.

(2) Workout Template Definition - A "workout" is just a series of "muscle group @ intensity" definitions. The task of selection which actual exercises goes into the slot is separate. Once the exercise is selected, the follow-on operations, like calculating the set rep ranges and weights, warmup sets etc can be accomplished.

(3) Cycling through the workouts - Default behavior is just to cycle through the existing workouts "A", "B", "C", etc. Advanced option is to define the rotation of active/inactive workouts.

(4) the 'active' workout - this should be displayed on the main exercise tab on the "general" page. I want the option (i.e.a button) to export this to a markdown file. Both the streamlit and the markdown export should be formatted like the 'exercise template.md' Including the checkbox format for both the markdown and the streamlit file.

(5) I want a way to read in markdown files, once I have populated them by checking off the checkboxes. This could be a "load completed exercise" tab. This would load the exercise in, then log it into the database.