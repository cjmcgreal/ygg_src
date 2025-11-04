# Description
How it works:

Prerequisites chains are established for each discipline.

The "feasible set" is simply those items whose prerequisites have all been met.

The feasible set is then sorted by various values:
- Trip Distance
- Trip Cultural Value

**Follow on work**
From here we, in principle, could assign a value metric to distance and/or cultural value (and/or have this on a slider) and then sequence the feasible set. 

# Versions
## v0
## v1
## v2
## v3

## v3+ Potential Follow on work
# Retrospective Notes
Great work today on Task Management. The basic concept for sorting:
- Exclude all tasks or items with incomplete prerequisites. This produces a "feasible set"
- The simplest treatment of the feasible set is just to order them along some axis, in the example case for choosing a travel destination these might be: 
	- Kayak difficulty
	- Cultural Interest.
- Me and ChatGPT developed a "trick" way of sorting. I don't really understand how it works but there is one slider that moves from ordering in the "kayak difficulty" to the "cultural interest". The "Trick" is that every move of the slider impacts the Global Priority List
- Future could involve setting up a value function across multiple axis.