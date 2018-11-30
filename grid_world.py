#### INFORMASJON #### 
# Forfatter: Simon Strandvold og Hans Petter Leines

# Beskrivelse:
# Denne koden generer miljøet som er lesbart
# for q_learning.py koden.

# Importerte biblioteker
import numpy as np
from webcamcapture import output
from labyrinter import mazes

#### HYPERPARAMETERE ####

# Gevinster
GOAL_REWARD = 5
RED_REWARD = -10
BLUE_REWARD = RED_REWARD/2
STEP_COST = -1

# Startposisjonen
START_STATE = (0,0)

# Størrelse på manuelt miljø og antall hinder ønsket
GRID_HEIGHT = 33
GRID_WIDTH = 33
NUM_OBSTACLES = GRID_HEIGHT

# Initsialiserer tilfeldig eller manuelt miljø
RANDOM_REWARDS = False
MAZE = mazes(1)

# Miljø fra kamera eller egendefinert
CAMERA = False

## GLOBALE VARIABLER ##
PREV_REWARDS = {}

#### KLASSE SOM INNEHOLDER MILJØET ####
class Grid:
    def __init__(self, height, width, start):
        self.height = height
        self.width = width
        self.i = start[0]
        self.j = start[1]

    # Setter gevinster og lovlige handlinger
    def set(self, rewards, actions):
        self.rewards = rewards
        self.actions = actions

    # Setter tilstanden
    def set_state(self, s):
        self.i = s[0]
        self.j = s[1]

    # Returnerer nåværende tilstand
    def current_state(self):
        return(self.i, self.j)

    # Beveger beslutningstakeren i miljøet
    def move(self, action):
        # Sjekker om det er en lovlig handling
        if action in self.actions[(self.i, self.j)]:
            if action == 'U':
                self.i -= 1
            elif action == 'D':
                self.i += 1
            elif action == 'L':
                self.j -= 1
            elif action == 'R':
                self.j += 1
        # Returnerer gevinst for neste tilstand
        return self.rewards.get((self.i, self.j), 0)

    # Sjekker om episoden er ferdig
    def game_over(self):
        # True om beslutningstakeren er i mål
        return self.rewards[self.i, self.j] == GOAL_REWARD

    # 
    def all_states(self):
        # possibly buggy but simple way to get all states
        # either a position that has possible next actions
        # or a position that yields a reward
        return set(self.actions.keys()) | set(self.rewards.keys())


## MILJØ MED KAMPERA SOM SENSOR ##

def camera_grid():
    global PREV_REWARDS
    camera_output = output()
    g = make_grid(4,6)
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

# Henter ut gevinster fra sensor
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

# Returnerer beslutningstakerens posisjon fra sensor
def get_startstate(grid):
    startstate = ()
    for i in range(grid.shape[0]):
        for j in range(grid.shape[1]):
            if (grid[i][j] == 4):
                startstate = (i, j)
    return startstate


#### KONSTRUKSJON AV MILJØ ####

# Konstruerer miljø som en dict
def make_grid(y, x, num_obstacles = 0):
    g = Grid(y, x, (0,0))
    rewards = {}

    # Legger til mulige handlinger i hver tilstand
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

    # Legger til steg-gevinst i hver tilstand
    for i in range(x):
        for j in range(y):
            rewards[(j,i)] = STEP_COST

    # Leser og tolker labyrinter hentet fra filen labyrinter.py
    if not RANDOM_REWARDS:
        labyrint = MAZE
        k = 0
        l = 0
        for i in labyrint:
            for j in i:
                if j==0: rewards[(l,k)] = RED_REWARD
                if j==5: rewards[(l,k)] = GOAL_REWARD
                k= k+1
            k = 0
            l = l+1
    
    # Lager tilfeldige hindringer i miljøet
    else:
        for _ in range(num_obstacles):
            rewards[(np.random.randint(0,y-1),np.random.randint(0,x-1))] = RED_REWARD 
        for _ in range(num_obstacles):
            rewards[(np.random.randint(0,y-1),np.random.randint(0,x-1))] = BLUE_REWARD 
        rewards[(y-1,x-1)] = GOAL_REWARD
        rewards[START_STATE] = STEP_COST

    # Setter handlinger og gevinster i klassen Grid
    g.set(rewards, actions)

    # Returnerer et element av klassen Grid
    return g

#### MANUELT MILJØ ####
def manual_grid():
    # Lager grid [y,x] stor 
    g = make_grid(GRID_HEIGHT,GRID_WIDTH,NUM_OBSTACLES)
    # Sier at den skal trene hver gang
    train = True
    # Setter startposisjon
    s = START_STATE
    g.set_state(s)
    # Returnerer element av klassen grid og variablen train
    return g, train

# Funksjonen hentet opp i q_learning.py som inneholder
# hele miljøet i objektet grid
def grid_world():
    if CAMERA: return camera_grid()
    else: return manual_grid()

#### PRINT FUNKSJONER ####
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