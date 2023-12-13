# Fatball

Fatball learns to survive by regulating his temperature and hunger. Fatball is trained on human and self play data - it uses the data points from human attempts at regulation of basic variables of survival (temperature and metabolism). Based on the successfull data points (surviving and obtaining 5 pieces of food) Fatball learns to self-regulate. 

Fatball is made for two different motives 
1) To familiarise ourselves with basic machine learning methods beginning with most well known ones : decision trees to eventually move on to deep and unsupervised learning
2) To lay down the foundation for building simulation based animats - beginning with basic survival
Fatball allows us to develop skill sets in both domains 


## Setup

- Clone the repo
- Install `pygame`, `sklearn`, `numpy`
- Run the program

## Rules

- The ball always start in the center at the beginning of each turn.
- 5 Foods (green dots) will be scattered randomly across the screen.
- The ball can do two operations - wait or go to the nearest food.
- There are two gauges at the top of the screen which shows - temperature and hunger, respectively
- If the ball stays still, the temperature and food will go down.
- If the ball moves, the temperature will rise and the food will go down at a higher rate than when stationary.
- If the temperature drops below 0, or goes over the limit, its game over.
- If the food drops below 0, the its game over.
- There is no limit to food gathering.

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
