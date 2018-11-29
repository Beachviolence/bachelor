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
MANUAL = True
GRID_Y = 33
GRID_X = 33
PREV_POLICY = {}
PREV_STATE = ()
PREV_Q = {}
NUM_EPISODES = 18.66 * GRID_X*GRID_Y + 5932.01


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

def run(epoch):
  if MANUAL:
    grid, learn = manual_grid(GRID_Y, GRID_X)
  else:
    grid, learn = standard_grid()
  if learn:
    return q_learn(grid, epoch)
  else:
    return PREV_POLICY, grid.current_state()


def q_learn(grid, epoch):
  global PREV_Q
  #TIMER START
  t0 = time.time()

  #Imports start state
  start_state = grid.current_state()

  # no policy initialization, we will derive our policy from most recent Q

  # initialize Q(s,a) if first run
  if epoch == 0:
    Q = {}
    states = grid.all_states()
    for s in states:
      Q[s] = {}
      for a in ALL_POSSIBLE_ACTIONS:
        Q[s][a] = 0
  else:
    Q = PREV_Q
    states = grid.all_states() 

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
  sum_reward = []

  if epoch == 0: num_episodes = 80000
  else: num_episodes = NUM_EPISODES/(100)

  for it in range(int(num_episodes)):
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
    sum_episode_rewards = []

    while not grid.game_over():
      #a = random_action(a, eps=0.5/t) # epsilon-greedy with decaying epsilon
      a = random_action(a, eps=0.5) # epsilon-greedy
      # random action also works, but slower since you can bump into walls
      # a = np.random.choice(ALL_POSSIBLE_ACTIONS)
      r = grid.move(a)
      sum_episode_rewards.append(r)
      s2 = grid.current_state()

      # adaptive learning rate
      # alpha = ALPHA / update_counts_sa[s][a]
      alpha = ALPHA
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
    sum_reward.append(sum(sum_episode_rewards))
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

  #TIMER STOP
  t1 = time.time()
  print("Time elapsed: {}".format(t1-t0))

  if DEBUG:
    lowest_delta = min(deltas)
    print(lowest_delta)
    print(deltas.index(lowest_delta))
    plt.plot(deltas)
    plt.show()

    plt.plot(sum_reward)
    plt.show()

    # print rewards
    # print("rewards:")
    # print_values(grid.rewards, grid)

    # what's the proportion of time we spend updating each part of Q?
    # print("update counts:")
    # total = np.sum(list(update_counts.values()))
    # for k, v in update_counts.items():
    #   update_counts[k] = float(v) / total
    # print_values(update_counts, grid)

    # Prints environment with rewards
    rew = np.zeros((GRID_Y, GRID_X))
    for i in range (GRID_X):
      for j in range(GRID_Y):
        rew[i,j] = grid.rewards.get((i,j), 0)
    plt.imshow(rew)
    plt.colorbar()
    plt.show()

    # val = np.zeros((GRID_Y, GRID_X))
    # for i in range (GRID_X):
    #   for j in range(GRID_Y):
    #     val[i,j] = V.get((i,j), 0)
    # plt.imshow(val)
    # plt.colorbar()
    # plt.show()

    #Plots policy from start state
    route = rew
    pos_x, pos_y = start_state[0],start_state[1]
    while route[pos_y,pos_x] != 5:
      route[pos_y,pos_x] = 5
      if policy.get((pos_y,pos_x)) == 'U': 
        pos_y -= 1
      elif policy.get((pos_y,pos_x)) == 'D': 
        pos_y += 1
      elif policy.get((pos_y,pos_x)) == 'L': 
        pos_x -= 1
      elif policy.get((pos_y,pos_x)) == 'R': 
        pos_x += 1

    plt.imshow(route)
    plt.colorbar()
    plt.show()
    

    # Printfunksjoner
    # print("values:")
    # print_values(V, grid)
    # print("policy:")
    # print_policy(policy, grid)

  PREV_Q = Q

  return policy, start_state

if __name__ == "__main__":
  epoch = 0
  while True:
    input("Trykk enter")
    policy, s = run(epoch)
    action = policy.get(s)
    print("recommended action:")
    print(action)
    epoch += 1