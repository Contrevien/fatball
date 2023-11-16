# Fatball

A pygame based snake game like implementation, where a ball chases after food and tries to survive.
A personal project to study Decision trees, even though it is not the best model for these kinds of project.

## Setup

- Clone the repo
- Install `pygame`, `sklearn`, `numpy`
- Run the program

## Rules

- The ball always start in the center at the beginning of each turn.
- 5 Foods (green dots) will be scattered randomly across the screen.
- The ball can do two operations - wait or go to the closest food.
- There are two gauges on top of the screen to denote - temperature and food, respectively.
- If the ball stays still, the temperature and food will go down.
- If the ball moves, the temperature will rise and the food will go down at a higher rate than when stationary.
- If the temperature drops below 0, or goes over the limit, the game get's over.
- If the food drops below 0, the game get's over.
- Gathering tons of food is possible.

## Modes

The game has two modes:

- Manual play
- Machine play

#### Manual play

When the game starts, it will ask to select mode.
Pressing `S` will select the Manual mode.

In manual mode, you have to decide when to wait and when to start moving to get the food.
Pressing `E` will make the ball move to get the **closest** food from it's current location.

Maintaining the balance between food and temperature is the way to win.

#### Machine play

When the game starts, it will ask to select mode.
Pressing `M` will select the Manual mode.

The model is trained enough to know the conditions of the game.
Tweaking the code will break the model since it is not dynamic.
