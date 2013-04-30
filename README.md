rs13ps1
=======

Problem Set 1 for class Recognition System


For this problem set we will revisit reinforcement learning. Your goal
will be to train a simulated mouse robot to navigate a maze. To do so
you'll build a collection of progressively more sophisticated
actions. You will then compare random choice of actions with actions
chosen by a reinforcement learner.

You will be provided a maze specified by UTF-8 text. In the text below
Unicode code points are indicated in parentheses. Maze walls are
indicated by "█" (U+2588). Free space is indicated by " "
(U+0020). The robot's starting point is indicated by "S" (U+0053) and
the goal is indicated by "G" (U+0047).

The robot is a very simple system that responds to the following
primitive actions:

- TurnLeft: results in the robot turning left by 90 degrees

- TurnRight: results in the robot turning right by 90 degrees

- MoveAhead: either returns a new location or a bump signal indicating
it has collided with a wall.

- LookAhead: shows the state of the next two locations the robot is
facing.

The robot exists in a 2D grid. The first step of the simulation
will be to replace "S" with a symbol indicating the robot is
pointing towards the top of the maze "↑" (U+2191). If the robot
is facing toward the top and TurnLeft is called then the robot's
symbol becomes replaced with "←" (U+2190). Another call of
TurnLeft would result in a leftward facing robot to turn to the
bottom "↓" (U+2193). Two more calls of TurnLeft would cause the
robot to face right in the maze "→" (U+2192) and then to face
toward the top again "↑" (U+2191). So the TurnLeft and TurnRight
commands change the robot's orientation.

MoveAhead causes the robot to update its (X,Y) position. Exactly how
depends on the robot's orientation. If the robot is at Cartesian
coordinates (6,3) pointing upward on the map toward a free space and
MoveAhead is called the robot's location becomes (6,4). Vertical
coordinates in this example are upward increasing. This causes the
previous location to return to " " (U+0020) and the new location to be
set to "↑" (U+2191) and this location is returned. If the robot is at
Cartesian coordinates (26,15) and its orientation is "←" but the
location (25,15) is filled with a wall "█" then MoveAhead should
return a bump signal ("B","U"). If the robot is at any location and
the square it is facing is the goal, then MoveAhead will return the
goal signal ("G","G") and the simulation should end.

LookAhead returns a tuple with the state of the next two locations the
robot is oriented toward. So if the robot is facing two empty spaces
LookAhead would return (" "," "). If the robot is facing a wall and
about to bump into it, LookAhead would return ("█","█"). If the robot
is one free space away from a block, LookAhead returns (" ","█"). If
the goal is ahead of the robot and a wall is after that LookAhead
returns ("G","█"). Note that the robot does not have full information
but can only see locally. This means that it can't employ optimal
search strategies but must explore using local information.

Problem 1) 

Starting from the specification above, implement a robot simulator
using whatever language you chose. You may work together with
classmates on your simulator implementation. Test mazes can be
downloaded from:

http://www.k2.t.u-tokyo.ac.jp/members/carson/rs13/maze.zip

Your simulator should be able to print the maze after a sequence of
actions. It should also be capable of computing how far the robot is
from the goal in Manhattan distance. How many lines of code is your
simulator?

Problem 2)

You can subsume the primitive actions (TurnLeft, TurnRight, MoveAhead,
and LookAhead) with more complex actions. For instance:

- RandomlyReorient: rotates the robot to a random orientation. It
should draw a random number from a discrete uniform distribution
ranging from 0 to 3. It should then make this random number of
successive calls to either MoveLeft or MoveRight.

Implement this action and a new action of your own design.

Problem 3)

Make a controller which uses RandomlyReorient and MoveAhead to
randomly navigate test mazes. Using maze-9-9.txt, run 100 trials of
the randomly walking controller and plot how many actions were
required to reach the goal for each trial. What is the mean number of
steps to reach the goal for the trials? Run a few trials and estimate
how many steps are required for RandomlyReorient to reach the goal of
maze-61-21.txt.

Problem 4)

Implement a new controller using reinforcement learning. You may use
whatever reinforcement learning algorithm you'd like but Q-learning
and SARSA are two of the most-popular candidates. The algorithm can
use any primitive or subsumption actions you have implemented (so long
as they don't do illegal things like tunnel through the maze
walls). Reward your robot when it takes a step, strongly punish the
robot when it bumps into a wall, and provide the robot a large reward
when it reaches the goal.

Run 100 trails of the reinforcement learning robot and plot how many
primitive actions were required to reach the goal of each
trial. Compare the performance of the reinforcement learning system
with the randomly walking controller. You may do so by plotting the
number of actions taken to reach the goal for both the reinforcement
learning controller and the random controller.
