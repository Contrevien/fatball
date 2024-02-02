import random
import json

class Learner(object):
    def __init__(self):
        # Learning parameters
        self.epsilon = 0.1
        self.lr = 0.7
        self.discount = .5

        # State/Action history
        self.qvalues = self.LoadQvalues()
        self.history = []

        # Action space
        self.actions = {
            0:'wait',
            1:'move',
        }

    def Reset(self):
        self.history = []

    def LoadQvalues(self, path="qvalues.json"):
        with open(path, "r") as f:
            qvalues = json.load(f)
        return qvalues

    def SaveQvalues(self, path="qvalues.json"):
        with open(path, "w") as f:
            json.dump(self.qvalues, f)
            
    def act(self, state, n_games):
        # Epsilon greedy
        rand = random.uniform(0,1)
        if rand < self.epsilon:
            action_key = random.choices(list(self.actions.keys()))[0]
            print(f"Taking random action - {self.actions[action_key]}")
        else:
            state_scores = self.qvalues[self._GetStateStr(state)]
            action_key = state_scores.index(max(state_scores))
            print(f"Predicted action - {self.actions[action_key]}")
        action_val = self.actions[action_key]
        
        # Remember the actions it took at each state
        self.history.append({
            'state': state,
            'action': action_key
            })
        return action_val
    
    def UpdateQValues(self, died):
        history = self.history[::-1]
        for i, h in enumerate(history[:-1]):
            if died: # Snake Died -> Negative reward
                sN = history[0]['state']
                aN = history[0]['action']
                state_str = self._GetStateStr(sN)
                reward = -2
                self.qvalues[state_str][aN] = (1-self.lr) * self.qvalues[state_str][aN] + self.lr * reward # Bellman equation - there is no future state since game is over
            else:
                s1 = h['state'] # current state
                s0 = history[i+1]['state'] # previous state
                a0 = history[i+1]['action'] # action taken at previous state
                
                reward = 0
                if s0[0] == 1 and a0 == 1: # decided to move when temperature was high
                    reward = -1
                    print(f"Reward for temperature: -1")
                if s0[0] == -1 and a0 == 0: # decided to wait when temperature was low
                    reward = -1
                    print(f"Reward for temperature: -1")
                if s1[1] >= s0[1]: # ball maintained the energy
                    reward = 1
                    # print(f"Reward for energy: +1")
                    
                state_str = self._GetStateStr(s0)
                new_state_str = self._GetStateStr(s1)
                self.qvalues[state_str][a0] = (1-self.lr) * (self.qvalues[state_str][a0]) + self.lr * (reward + self.discount*max(self.qvalues[new_state_str])) # Bellman equation

    def _GetStateStr(self, state):
        return str((state[0],state[1]))