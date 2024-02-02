import json

temps = [-1, 0, 1]
energy = range(-10, 30)

states = {}
for i in temps:
	for j in energy:
		states[str((i,j))] = [0,0]

with open("qvalues.json", "w") as f:
	json.dump(states, f)