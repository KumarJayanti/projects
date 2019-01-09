# Artificial Intelligence Nanodegree
## Introductory Project: Diagonal Sudoku Solver

# Question 1 (Naked Twins)
Q: How do we use constraint propagation to solve the naked twins problem?  
A: When there is a Naked Twin, it means that those two values are locked in two boxes of the unit. And so we can remove those two values as possibilities from their peers. Applying this constraint reduces the search space. By repeatedly applying naked twins constraint along with the regular elimination constraint the search space is further reduced.

# Question 2 (Diagonal Sudoku)
Q: How do we use constraint propagation to solve the diagonal sudoku problem?  
A: For diagonal boxes we add the elements on the same diagonal to the list of all peers of a given diagonal box. The list of peers is used during elimination step where : we go through all the boxes, and whenever there is a box with a value,  we eliminate that value from the values of all its peers. In terms of implementation we just add the two diagonals to unit_list and the code constructs the peers. 
Other Ideas tried to prune the search space:
 1. The search step would not pick a path down the tree if the next pick is going to cause a diagonal rule violation.
 2. Eliminating Naked Pairs, Triples and Quads
 3. Tried box/line reduction (http://www.sudokuwiki.org/Sudoku_X_Strategies) with not much imporvements in time taken for the 2 grids i am testing with 

### Install

This project requires **Python 3**.

We recommend students install [Anaconda](https://www.continuum.io/downloads), a pre-packaged Python distribution that contains all of the necessary libraries and software for this project. 
Please try using the environment we provided in the Anaconda lesson of the Nanodegree.

##### Optional: Pygame

Optionally, you can also install pygame if you want to see your visualization. If you've followed our instructions for setting up our conda environment, you should be all set.

If not, please see how to download pygame [here](http://www.pygame.org/download.shtml).

### Code

* `solution.py` - You'll fill this in as part of your solution.
* `solution_test.py` - Do not modify this. You can test your solution by running `python solution_test.py`.
* `PySudoku.py` - Do not modify this. This is code for visualizing your solution.
* `visualize.py` - Do not modify this. This is code for visualizing your solution.

### Visualizing

To visualize your solution, please only assign values to the values_dict using the ```assign_values``` function provided in solution.py

### Submission
Before submitting your solution to a reviewer, you are required to submit your project to Udacity's Project Assistant, which will provide some initial feedback.  

The setup is simple.  If you have not installed the client tool already, then you may do so with the command `pip install udacity-pa`.  

To submit your code to the project assistant, run `udacity submit` from within the top-level directory of this project.  You will be prompted for a username and password.  If you login using google or facebook, visit [this link](https://project-assistant.udacity.com/auth_tokens/jwt_login for alternate login instructions.

This process will create a zipfile in your top-level directory named sudoku-<id>.zip.  This is the file that you should submit to the Udacity reviews system.

