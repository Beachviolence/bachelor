import numpy as np
from webcamcapture import output
from labyrinter import mazes

# hyper parameters
GOAL_REWARD = 5
RED_REWARD = -30
BLUE_REWARD = RED_REWARD/2
STEP_COST = -1
START_STATE = (0,0)

RANDOM_REWARDS = False
MAZE = mazes(1)

# global variables
PREV_REWARDS = {}

# grid environment
class Grid:
    def __init__(self, height, width, start):
        self.height = height
        self.width = width
        self.i = start[0]
        self.j = start[1]

    def set(self, rewards, actions):
        # rewards should be a dict of: (i, j): r (row, col): reward
        # actions should be a dict of: (i, j): A (row, col): list of possible actions
        self.rewards = rewards
        self.actions = actions

    def set_state(self, s):
        self.i = s[0]
        self.j = s[1]

    def current_state(self):
        return(self.i, self.j)

    def move(self, action):
        # check if legal move first
        if action in self.actions[(self.i, self.j)]:
            if action == 'U':
                self.i -= 1
            elif action == 'D':
                self.i += 1
            elif action == 'L':
                self.j -= 1
            elif action == 'R':
                self.j += 1
        # return a reward (if any)
        return self.rewards.get((self.i, self.j), 0)

    def game_over(self):
        # returns true if game is over, else false
        # true if we are in a state where the reward is the goal reward
        return self.rewards[self.i, self.j] == GOAL_REWARD

    def all_states(self):
        # possibly buggy but simple way to get all states
        # either a position that has possible next actions
        # or a position that yields a reward
        return set(self.actions.keys()) | set(self.rewards.keys())

# extracting rewards and current state
def get_rewards(grid, goal_reward = GOAL_REWARD, red_reward = RED_REWARD, blue_reward = BLUE_REWARD, step_cost = STEP_COST):
    rewards = {}
    for i in range(grid.shape[0]):
        for j in range(grid.shape[1]):
            if (grid[i][j] == 1):
                rewards.update({(i, j): red_reward})
            elif (grid[i][j] == 2):
                rewards.update({(i, j): goal_reward})
            elif (grid[i][j] == 3):
                rewards.update({(i, j): blue_reward})
            else:
                rewards.update({(i, j): step_cost})
    return rewards

def get_startstate(grid):
    startstate = ()
    for i in range(grid.shape[0]):
        for j in range(grid.shape[1]):
            if (grid[i][j] == 4):
                startstate = (i, j)
    return startstate


# grid worlds
def debug_grid():
    g = Grid(4, 6, (0, 0))
    rewards = {(0, 5): 1, (1,5): -1}
    actions = {
        (0, 0): ('D', 'R'),
        (0, 1): ('D', 'R', 'L'),
        (0, 2): ('D', 'R', 'L'),
        (0, 3): ('D', 'R', 'L'),
        (0, 4): ('D', 'R', 'L'),
        (0, 5): ('D', 'L'),
        (1, 0): ('U', 'D', 'R'),
        (1, 1): ('U', 'D', 'R', 'L'),
        (1, 2): ('U', 'D', 'R', 'L'),
        (1, 3): ('U', 'D', 'R', 'L'),
        (1, 4): ('U', 'D', 'R', 'L'),
        (1, 5): ('U', 'D', 'L'),
        (2, 0): ('U', 'D', 'R'),
        (2, 1): ('U', 'D', 'R', 'L'),
        (2, 2): ('U', 'D', 'R', 'L'),
        (2, 3): ('U', 'D', 'R', 'L'),
        (2, 4): ('U', 'D', 'R', 'L'),
        (2, 5): ('U', 'D', 'L'),
        (3, 0): ('U', 'R'),
        (3, 1): ('U', 'R', 'L'),
        (3, 2): ('U', 'R', 'L'),
        (3, 3): ('U', 'R', 'L'),
        (3, 4): ('U', 'R', 'L'),
        (3, 5): ('U', 'L')
    }
    g.set(rewards, actions)
    return g

def debug_negative_grid(step_cost = -0.1):
    g = debug_grid()
    g.rewards.update({
        (0, 0): step_cost,
        (0, 1): step_cost,
        (0, 2): step_cost,
        (0, 3): step_cost,
        (0, 4): step_cost,
        (1, 0): step_cost,
        (1, 1): step_cost,
        (1, 2): step_cost,
        (1, 3): step_cost,
        (1, 4): step_cost,
        (2, 0): step_cost,
        (2, 1): step_cost,
        (2, 2): step_cost,
        (2, 3): step_cost,
        (2, 4): step_cost,
        (2, 5): step_cost,
        (3, 0): step_cost,
        (3, 1): step_cost,
        (3, 2): step_cost,
        (3, 3): step_cost,
        (3, 4): step_cost,
        (3, 5): step_cost
    })
    return g

def standard_grid():
    global PREV_REWARDS
    camera_output = output()
    g = debug_grid()
    rewards = get_rewards(camera_output)
    if rewards == PREV_REWARDS:
        train = False
    else: 
        train = True
    PREV_REWARDS = rewards
    g.rewards.update(rewards)
    s = get_startstate(camera_output)
    g.set_state(s)
    return g, train

# print functions
def print_values(V, g):
    for i in range(g.height):
        print("-----------------------------------------------------------")
        for j in range(g.width):
            v = V.get((i,j), 0)
            if v >= 0:
                print("  %.2f  | " % v, end="")
            else:
                print(" %.2f  |" % v, end=" ") # '-' takes up an extra space
        print("")

def print_policy(P, g):
    for i in range(g.height):
        print("-----------------------------------")
        for j in range(g.width):
            a = P.get((i, j), ' ')
            print("  %s  |" % a, end="")
        print("")



##### MANUAL MODE ######
def make_grid(y, x, num_obstacles):
    g = Grid(y, x, (0,0))
    rewards = {}

    #Adds all possible actions in each state to a dict
    actions = {
        (0,0): ('D', 'R'),
        (y-1,x-1): ('U', 'L'),
        (0, x-1): ('D', 'L'),
        (y-1, 0): ('U', 'R')
    }
    for i in range(1, x-1):
        actions[(0,i)] = ('D', 'R', 'L')
        actions[(y-1,i)] = ('U', 'R', 'L')
    for j in range(1, y-1):
        actions[(j,0)] = ('U', 'D', 'R')
        actions[(j,x-1)] = ('U', 'D', 'L')
    for k in range(1,x-1):
        for l in range(1,y-1):
            actions[(l,k)] = ('U', 'D', 'R', 'L')

    #Adds step cost to every state
    for i in range(x):
        for j in range(y):
            rewards[(j,i)] = STEP_COST


    # 
    if not RANDOM_REWARDS:
        labyrint = MAZE
        k = 0
        l = 0
        for i in labyrint:
            for j in i:
                if j==0: rewards[(l,k)] = RED_REWARD
                if j==5: rewards[(l,l)] = GOAL_REWARD
                k= k+1
            k = 0
            l = l+1



    #Adds goal and random rewards
    else:
        for _ in range(num_obstacles):
            rewards[(np.random.randint(0,y-1),np.random.randint(0,x-1))] = RED_REWARD 
        for _ in range(num_obstacles):
            rewards[(np.random.randint(0,y-1),np.random.randint(0,x-1))] = BLUE_REWARD 
        rewards[(x-1,y-1)] = GOAL_REWARD
        rewards[START_STATE] = STEP_COST

    g.set(rewards, actions)
    return g

def manual_grid(y = 5, x = 5):
    global PREV_REWARDS
    #camera_output = output()
    g = make_grid(y,x,y)
    #rewards = get_rewards(camera_output)
    #if rewards == PREV_REWARDS:
    #    train = False
    #else: 
    #    train = True
    train = True
    #PREV_REWARDS = rewards
    #g.rewards.update(rewards)
    s = START_STATE
    g.set_state(s)
    return g, train