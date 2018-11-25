import numpy as np
num_obstacles = 2
step_cost = -0.1

def debug_grid(y, x):
    #g = Grid(y, x, (0,0))
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
            rewards[(j,i)] = step_cost

    #Adds goal and obstacle rewards
    rewards[(x-1,y-1)] = 1
    for _ in range(num_obstacles):
        rewards[(np.random.randint(0,y-1),np.random.randint(0,x-1))] = -100

    g.set(rewards, actions)
    return g

    print(actions)
    print(rewards)

debug_grid(3,3)
