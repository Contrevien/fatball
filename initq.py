import itertools
import json

dis = [0, 1, 2]
temps = [-1, 0,1]
energy = [0,1,2]

states = {}
for i in temps:
	for j in energy:
		for k in dis:
			states[str((i,j,k))] = [0,0]

with open("qvalues.json", "w") as f:
	json.dump(states, f)