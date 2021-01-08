# Connect4-reinforced-learning
A simple example of Q-learning with connect4 based off of Jeremy Zhang's example using tic-tac-toe which can be found here: 

https://towardsdatascience.com/reinforcement-learning-implement-tictactoe-189582bea542

As a first attempt at reinforcment learning I chose a simple game (tic-tac-toe) and adjusted it to make it my own for a seperate game (connect4).

Version 2 introduced the following:

1. Checking if a winning move is available and playing it. (This greatly increasing learning efficiency with little cost).

2. An option to check 2 moves ahead for a winning move. This comes at great cost in time and was only used to begin with to save many "lose in 1" positions as possible to be avoided when normal learning commenced.

3. Adding values to the inverted board also i.e when a game is completed and values are given to all positions, they are also given to the flipped version of the board which should have the same value.
This roughly doubles the efficiency of the learning.

4. Now has the option to play like a regular engine that checks for potential win in 1 or 2s.

5. Checks for a winning move before the chance of playing a random move greatly increasing learning speed.
