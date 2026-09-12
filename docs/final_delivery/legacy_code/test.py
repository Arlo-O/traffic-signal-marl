import argparse
import time
from environment.intersection_env import IntersectionEnv
from agents.q_learning_agent import QLearningAgent
from agents.dqn_agent import DQNAgent
from Code.pygame_renderer import Renderer  # we’ll build this next
import numpy as np

def split_state(full_state, agent_id, total_agents=2):
    size = len(full_state) // total_agents
    return full_state[agent_id * size:(agent_id + 1) * size]

def run_test(agent_type="q", episodes=5, render_delay=0.5):
    env = IntersectionEnv()
    state_size = len(split_state(env.reset(), 0))
    action_size = 4

    # --- Load trained agents ---
    if agent_type == "q":
        agentA = QLearningAgent(state_size, action_size)
        agentB = QLearningAgent(state_size, action_size)
        agentA.load("models/agentA.pth")
        agentB.load("models/agentB.pth")
    else:
        agentA = DQNAgent(state_size, action_size)
        agentB = DQNAgent(state_size, action_size)
        agentA.load("models/agentA.pth")
        agentB.load("models/agentB.pth")

    # --- Initialize renderer ---
    renderer = Renderer()

    for ep in range(episodes):
        print(f"\n[Test] Episode {ep+1}")
        state = env.reset()
        done = False
        total_reward = 0

        for step in range(200):
            stateA = split_state(state, 0)
            stateB = split_state(state, 1)

            actionA = agentA.get_action(stateA, training=False)
            actionB = agentB.get_action(stateB, training=False)

            state, reward, done, _ = env.step([actionA, actionB])
            total_reward += reward

            renderer.render(env)  # Show current state
            time.sleep(render_delay)

        print(f"[Test] Ep {ep+1} total reward: {total_reward:.2f}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--agent", choices=["q", "dqn"], required=True)
    parser.add_argument("--episodes", type=int, default=5)
    args = parser.parse_args()

    run_test(agent_type=args.agent, episodes=args.episodes)

