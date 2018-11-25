import numpy as np
import matplotlib.pyplot as plt
import time
from grid_world import standard_grid, print_values, print_policy, manual_grid

# hyper parameters
GAMMA = 0.9
ALPHA = 0.1

# global  variables
ALL_POSSIBLE_ACTIONS = ('U', 'D', 'L', 'R')
DEBUG = True
MANUAL = False
GRID_Y = 6
GRID_X = 6
PREV_POLICY = {}
PREV_STATE = ()
NUM_EPISODES = 5000

def max_dict(d):
  # returns the argmax (key) and max (value) from a dictionary
  # put this into a function since we are using it so often
  max_key = None
  max_val = float('-inf')
  for k, v in d.items():
    if v > max_val:
      max_val = v
      max_key = k
  return max_key, max_val

def random_action(a, eps=0.1):
  # we'll use epsilon-soft to ensure all states are visited
  # what happens if you don't do this? i.e. eps=0
  p = np.random.random()
  if p < (1 - eps):
    return a
  else:
    return np.random.choice(ALL_POSSIBLE_ACTIONS)

def run(first):
  if MANUAL:
    grid, learn = manual_grid(GRID_Y, GRID_X)
  else:
    grid, learn = standard_grid()
  if learn:
    return q_learn(grid, first)
  else:
    return PREV_POLICY, grid.current_state()


def q_learn(grid, first):
  
  start_state = grid.current_state()

  # no policy initialization, we will derive our policy from most recent Q

  # initialize Q(s,a) if first run
  if first:
    Q = {}
    states = grid.all_states()
    for s in states:
      Q[s] = {}
      for a in ALL_POSSIBLE_ACTIONS:
        Q[s][a] = 0
  else:
    Q = prev_Q

  # let's also keep track of how many times Q[s] has been updated
  update_counts = {}
  update_counts_sa = {}
  for s in states:
    update_counts_sa[s] = {}
    for a in ALL_POSSIBLE_ACTIONS:
      update_counts_sa[s][a] = 1.0

  # repeat until convergence
  t = 1.0
  deltas = []
  
  for it in range(NUM_EPISODES):
    if it % 100 == 0:
      t += 1e-2
    if it % 2000 == 0:
      if DEBUG:
        print("it:", it)

    # instead of 'generating' an epsiode, we will PLAY
    # an episode within this loop
    s = start_state # actual start state
    grid.set_state(s)
    
    # the first (s, r) tuple is the state we start in and 0
    # (since we don't get a reward) for simply starting the game
    # the last (s, r) tuple is the terminal state and the final reward
    # the value for the terminal state is by definition 0, so we don't
    # care about updating it.
    a, _ = max_dict(Q[s])
    biggest_change = 0
    while not grid.game_over():
      a = random_action(a, eps=0.5/t) # epsilon-greedy
      # random action also works, but slower since you can bump into walls
      # a = np.random.choice(ALL_POSSIBLE_ACTIONS)
      r = grid.move(a)
      s2 = grid.current_state()

      # adaptive learning rate
      alpha = ALPHA / update_counts_sa[s][a]
      update_counts_sa[s][a] += 0.005

      # we will update Q(s,a) AS we experience the episode
      old_qsa = Q[s][a]
      # the difference between SARSA and Q-Learning is with Q-Learning
      # we will use this max[a']{ Q(s',a')} in our update
      # even if we do not end up taking this action in the next step
      a2, max_q_s2a2 = max_dict(Q[s2])
      Q[s][a] = Q[s][a] + alpha*(r + GAMMA*max_q_s2a2 - Q[s][a])
      biggest_change = max(biggest_change, np.abs(old_qsa - Q[s][a]))

      # we would like to know how often Q(s) has been updated too
      update_counts[s] = update_counts.get(s,0) + 1

      # next state becomes current state
      s = s2
      a = a2
     
    deltas.append(biggest_change)

  # determine the policy from Q*
  # find V* from Q*
  policy = {}
  V = {}
  for s in grid.actions.keys():
    a, max_q = max_dict(Q[s])
    policy[s] = a
    V[s] = max_q
  global PREV_POLICY
  PREV_POLICY = policy

  if DEBUG:
    plt.plot(deltas)
    plt.show()

    # print start state
    print("start state: ")
    print(s)

    # print rewards
    print("rewards:")
    print_values(grid.rewards, grid)

    # what's the proportion of time we spend updating each part of Q?
    print("update counts:")
    total = np.sum(list(update_counts.values()))
    for k, v in update_counts.items():
      update_counts[k] = float(v) / total
    print_values(update_counts, grid)

    rew = np.zeros((GRID_Y, GRID_X))
    for i in range (GRID_X):
      for j in range(GRID_Y):
        rew[i,j] = grid.rewards.get((i,j), 0)
    val = np.zeros((GRID_Y, GRID_X))
    for i in range (GRID_X):
      for j in range(GRID_Y):
        val[i,j] = V.get((i,j), 0)
    
    plt.imshow(val)
    plt.colorbar()
    plt.show()
    plt.imshow(rew)
    plt.colorbar()
    plt.show()
    print("values:")
    print_values(V, grid)
    print("policy:")
    print_policy(policy, grid)

    prev_Q = Q

  return policy, start_state

if __name__ == "__main__":
  while True:
    i = 0
    if i>0: first = False
    else: first = True
    input("Trykk enter")
    t0 = time.time()
    policy, s = run(first)
    action = policy.get(s)
    print("recommended action:")
    print(action)
    t1 = time.time()
    print("time elapsed:")
    print(t1-t0)