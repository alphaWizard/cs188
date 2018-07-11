# valueIterationAgents.py
# -----------------------
# Licensing Information:  You are free to use or extend these projects for
# educational purposes provided that (1) you do not distribute or publish
# solutions, (2) you retain this notice, and (3) you provide clear
# attribution to UC Berkeley, including a link to http://ai.berkeley.edu.
# 
# Attribution Information: The Pacman AI projects were developed at UC Berkeley.
# The core projects and autograders were primarily created by John DeNero
# (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# Student side autograding was added by Brad Miller, Nick Hay, and
# Pieter Abbeel (pabbeel@cs.berkeley.edu).


# valueIterationAgents.py
# -----------------------
# Licensing Information:  You are free to use or extend these projects for
# educational purposes provided that (1) you do not distribute or publish
# solutions, (2) you retain this notice, and (3) you provide clear
# attribution to UC Berkeley, including a link to http://ai.berkeley.edu.
# 
# Attribution Information: The Pacman AI projects were developed at UC Berkeley.
# The core projects and autograders were primarily created by John DeNero
# (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# Student side autograding was added by Brad Miller, Nick Hay, and
# Pieter Abbeel (pabbeel@cs.berkeley.edu).


import mdp, util

from learningAgents import ValueEstimationAgent
import collections

class ValueIterationAgent(ValueEstimationAgent):
    """
        * Please read learningAgents.py before reading this.*

        A ValueIterationAgent takes a Markov decision process
        (see mdp.py) on initialization and runs value iteration
        for a given number of iterations using the supplied
        discount factor.
    """
    def __init__(self, mdp, discount = 0.9, iterations = 100):
        """
          Your value iteration agent should take an mdp on
          construction, run the indicated number of iterations
          and then act according to the resulting policy.

          Some useful mdp methods you will use:
              mdp.getStates()
              mdp.getPossibleActions(state)
              mdp.getTransitionStatesAndProbs(state, action)
              mdp.getReward(state, action, nextState)
              mdp.isTerminal(state)
        """
        self.mdp = mdp
        self.discount = discount
        self.iterations = iterations
        self.values = util.Counter() # A Counter is a dict with default 0
        self.runValueIteration()

    def runValueIteration(self):
        for i in range(self.iterations):
            dictionary = util.Counter()
            for state in self.mdp.getStates():
                if self.mdp.isTerminal(state):
                    continue
                maxVal = - float('inf')
                for action in self.mdp.getPossibleActions(state):
                    totalValue = self.computeQValueFromValues(state, action)
                    if totalValue > maxVal:
                        maxVal = totalValue
                        # intialize everyhting to 0 if it's not in self.values for Vk(s')
                        #set self.values at the end
                dictionary[state] = maxVal
            self.values = dictionary

    def getValue(self, state):
        """
          Return the value of the state (computed in __init__).
        """
        return self.values[state]


    def computeQValueFromValues(self, state, action):
        """
          Compute the Q-value of action in state from the
          value function stored in self.values.
        """
        totalValue = 0
        for transition, probability in self.mdp.getTransitionStatesAndProbs(state, action):
            reward = self.mdp.getReward(state, action, transition)
            totalValue += probability * (reward + (self.discount * self.getValue(transition)))
        return totalValue
        # page 6 Q-learnnig. compute q* with given v*

    def computeActionFromValues(self, state):
        """
          The policy is the best action in the given state
          according to the values currently stored in self.values.

          You may break ties any way you see fit.  Note that if
          there are no legal actions, which is the case at the
          terminal state, you should return None.
        """
        maxAction = None
        maxValue = - float ('inf')
        for action in self.mdp.getPossibleActions(state):
            qvalue = self.computeQValueFromValues(state, action)
            if qvalue > maxValue:
                maxValue = qvalue
                maxAction = action
        return maxAction

    def getPolicy(self, state):
        return self.computeActionFromValues(state)

    def getAction(self, state):
        "Returns the policy at the state (no exploration)."
        return self.computeActionFromValues(state)

    def getQValue(self, state, action):
        return self.computeQValueFromValues(state, action)

class AsynchronousValueIterationAgent(ValueIterationAgent):
    """
        * Please read learningAgents.py before reading this.*

        An AsynchronousValueIterationAgent takes a Markov decision process
        (see mdp.py) on initialization and runs cyclic value iteration
        for a given number of iterations using the supplied
        discount factor.
    """
    def __init__(self, mdp, discount = 0.9, iterations = 1000):
        """
          Your cyclic value iteration agent should take an mdp on
          construction, run the indicated number of iterations,
          and then act according to the resulting policy. Each iteration
          updates the value of only one state, which cycles through
          the states list. If the chosen state is terminal, nothing
          happens in that iteration.

          Some useful mdp methods you will use:
              mdp.getStates()
              mdp.getPossibleActions(state)
              mdp.getTransitionStatesAndProbs(state, action)
              mdp.getReward(state)
              mdp.isTerminal(state)
        """
        ValueIterationAgent.__init__(self, mdp, discount, iterations)

    def runValueIteration(self):
        states = self.mdp.getStates()
        for i in range(self.iterations):
            dictionary = self.values.copy()
            # print dictionary
            state = states[i % len(states)]
            # print state
            if state == self.mdp.isTerminal(state):
                continue
            maxValue = - float('inf')
            possibleActions = self.mdp.getPossibleActions(state)
            for action in possibleActions:
                totalValue = self.computeQValueFromValues(state, action)
                if totalValue > maxValue:
                    maxValue = totalValue
                    dictionary[state] = maxValue
            self.values = dictionary

class PrioritizedSweepingValueIterationAgent(AsynchronousValueIterationAgent):
    """
        * Please read learningAgents.py before reading this.*

        A PrioritizedSweepingValueIterationAgent takes a Markov decision process
        (see mdp.py) on initialization and runs prioritized sweeping value iteration
        for a given number of iterations using the supplied parameters.
    """
    def __init__(self, mdp, discount = 0.9, iterations = 100, theta = 1e-5):
        """
          Your prioritized sweeping value iteration agent should take an mdp on
          construction, run the indicated number of iterations,
          and then act according to the resulting policy.
        """
        self.theta = theta
        ValueIterationAgent.__init__(self, mdp, discount, iterations)
    
    # def getMaxQval(state):
    #     return max(self.getQValue(s, action) for a in self.mdp.getPossibleActions(s))

    def runValueIteration(self):
        # compute predecessors for all states
        PQ = util.PriorityQueue()
        predecessors = set()
        states = self.mdp.getStates()
        for state in states:
            numActionsForState = len(self.mdp.getPossibleActions(state))
            if numActionsForState > 0:
                predecessors.add(state)
        
        for s in states:
            # for all non terminal states
            if not self.mdp.isTerminal(s):
                sVal = self.values[s]
                
                #calculate highest q value from all possible actions from s
                maxQ = - float('inf')
                maxAction = None
                for action in self.mdp.getPossibleActions(s):
                    computedQ = self.mdp.computeQValueFromValues(s, action)
                    if computedQ > maxQ:
                        computedQ = maxQ
                        maxAction = action
                diff = abs(sVal - maxQ)
                # prioritize states with higher error
                PQ.push(s, -diff)
        for i in range(self.iterations):
            if PQ.isEmpty():
                break
            s = PQ.pop()
            if not self.mdp.isTerminal(s):
                # Update s's value (if it is not a terminal state) in self.values.
                maxQval = getMaxQval(s)
                self.values[s] = maxQval
        return

