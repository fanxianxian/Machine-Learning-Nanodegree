import random
from environment import Agent, Environment
from planner import RoutePlanner
from simulator import Simulator
import csv

class LearningAgent(Agent):
    """An agent that learns to drive in the smartcab world."""

    def __init__(self, env):
        super(LearningAgent, self).__init__(env)  # sets self.env = env, state = None, next_waypoint = None, and a default color
        self.color = 'red'  # override color
        self.planner = RoutePlanner(self.env, self)  # simple route planner to get next_waypoint
        # TODO: Initialize any additional variables here
        self.reward = 0
        self.alpha = [ i * 0.1 for i in range(1,10)]
        self.gama  = [ i * 0.1 for i in range(1,10)]
        self.Q_Learning = {}
        self.record = []
        self.succ = ''
        self.epsilon = random.randint(0,5) * 0.1
        self.equal = False
        self.move_times = 1
        self.cur_state = None
        self.next_state = None
    def reset(self, destination=None):
        self.planner.route_to(destination)
        # TODO: Prepare for a new trip; reset any variables here, if required
        self.reward = 0
        self.move_times += 1
        self.epsilon = random.randint(0,5) * 0.1 / (self.move_times)

    def update(self, t):
        # Gather inputs
        self.next_waypoint = self.planner.next_waypoint()  # from route planner, also displayed by simulator
        inputs = self.env.sense(self)
        deadline = self.env.get_deadline(self)

        # TODO: Update state
        #self.state = (item[1] for item in inputs.items())
        self.state = (inputs['light'], inputs['oncoming'], inputs['left'], inputs['right'], self.next_waypoint)
        self.cur_state = self.state[:]
        # TODO: Select action according to your policy
        # Init Q_learning and get the max possible action
        # action = random.choice(self.env.valid_actions)
        action = self.get_action(self.state, random.random() > self.epsilon)
 
        # action = self.get_action(self.state, True)
        # Execute action and get reward
        reward = self.env.act(self, action)
        self.reward += reward
       
        # TODO: Learn policy based on state, action, reward
        inputs = self.env.sense(self)
        self.next_state = (inputs['light'], inputs['oncoming'], inputs['left'], inputs['right'], self.next_waypoint)
        max_q = self.get_max_q(self.next_state)
        # self.Q_Learning[self.state][action] = (1 - self.alpha[3]) * self.Q_Learning[self.state][action] + self.alpha[3] * (reward + self.gama[3] * max_q)
        self.Q_Learning[self.state][action] = (1 - self.alpha[0]) * self.Q_Learning[self.state][action] + self.alpha[0] * (reward + self.gama[0] * max_q)

        if self.env.done and deadline >= 0:
            self.succ = 'succ'
            self.record.append([deadline, inputs, action, reward, self.succ])
        
        print "LearningAgent.update(): deadline = {}, inputs = {}, action = {}, reward = {}".format(deadline, inputs, action, reward)  # [debug]

    def get_action(self, state, flag):

        cur_value = None
        cur_action = None
        random_action = random.choice([action for action in self.env.valid_actions])
         
        if not flag or self.init_state(state):
            return random_action

        for item in self.Q_Learning[state].items():
                if item[1] > cur_value:
                    cur_value = item[1]
                    cur_action = item[0]

        return cur_action

    def get_max_q(self, state):

        self.init_state(state)
        return max(self.Q_Learning[state].values())
           
    def init_state(self, state):

        if state not in self.Q_Learning:
             self.Q_Learning[state] = {valid_action:1 for valid_action in self.env.valid_actions}
             return True
        return False
      
def run():
    """Run the agent for a finite number of trials."""

    # Set up environment and agent
    e = Environment()  # create environment (also adds some dummy traffic)
    a = e.create_agent(LearningAgent)  # create agent
    e.set_primary_agent(a, enforce_deadline=True)  # specify agent to track
    # NOTE: You can set enforce_deadline=False while debugging to allow longer trials

    # Now simulate it
    sim = Simulator(e, update_delay=0.5, display=True)  # create simulator (uses pygame when display=True, if available)
    # NOTE: To speed up simulation, reduce update_delay and/or set display=False

    sim.run(n_trials=100)  # run for a specified number of trials
    # NOTE: To quit midway, press Esc or close pygame window, or hit Ctrl+C on the command-line

if __name__ == '__main__':
    run()
