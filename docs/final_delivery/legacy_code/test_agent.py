from environment.intersection_env import IntersectionEnv
from agents.q_learning_agent import QLearningAgent
from agents.dqn_agent import DQNAgent
import numpy as np
import argparse
import pygame
import time
import csv
import matplotlib.pyplot as plt

WIDTH, HEIGHT = 900, 600
INTERSECTION_SIZE = 120
WHITE = (255, 255, 255)
GRAY = (120, 120, 120)
GREEN = (60, 220, 60)
RED = (220, 60, 60)
BLACK = (20, 20, 20)
BLUE = (40, 90, 255)
PED_COLOR = (255, 120, 120)
BG_COLOR = (230, 235, 240)

def split_state(full_state, agent_id, total_agents=2):
    size = len(full_state) // total_agents
    return full_state[agent_id * size:(agent_id + 1) * size]

def draw_street_network(screen):
    road_color = (40, 40, 40)
    road_width = INTERSECTION_SIZE

    pygame.draw.rect(screen, road_color,
                     (WIDTH // 2 - road_width // 2, HEIGHT // 2 - 200 + INTERSECTION_SIZE,
                      road_width, 300))
    pygame.draw.rect(screen, road_color,
                     (WIDTH // 2 - road_width // 2, 0,
                      road_width, HEIGHT // 2 - 200))
    pygame.draw.rect(screen, road_color,
                     (WIDTH // 2 - road_width // 2, HEIGHT // 2 + 100 + INTERSECTION_SIZE,
                      road_width, HEIGHT // 2 - 100 - INTERSECTION_SIZE))
    pygame.draw.rect(screen, road_color,
                     (0, HEIGHT // 2 - 200 + INTERSECTION_SIZE // 2 - road_width // 2,
                      WIDTH, road_width))
    pygame.draw.rect(screen, road_color,
                     (0, HEIGHT // 2 + 100 + INTERSECTION_SIZE // 2 - road_width // 2,
                      WIDTH, road_width))

def draw_intersection(screen, font, font_big, x, y, phase, label, queues, ped_requests, ped_cross_timer, vehicle_cross_timer):
    pygame.draw.rect(screen, GRAY, (x, y, INTERSECTION_SIZE, INTERSECTION_SIZE), border_radius=12)
    label_surface = font.render(label, True, WHITE)
    screen.blit(label_surface, (x + 5, y + 5))
    ns_color = GREEN if phase == 0 else RED
    ew_color = GREEN if phase == 1 else RED
    pygame.draw.circle(screen, ns_color, (x + INTERSECTION_SIZE // 2 - 50, y - 15), 8)
    pygame.draw.circle(screen, ns_color, (x + INTERSECTION_SIZE // 2 + 50, y + INTERSECTION_SIZE + 15), 8)
    pygame.draw.circle(screen, ew_color, (x + INTERSECTION_SIZE + 15, y + INTERSECTION_SIZE // 2 - 50), 8)
    pygame.draw.circle(screen, ew_color, (x - 15, y + INTERSECTION_SIZE // 2 + 50), 8)
    cross_color = WHITE
    line_width = 2
    step = 8
    length = INTERSECTION_SIZE
    for i in range(0, length, step * 2):
        pygame.draw.line(screen, cross_color, (x + i, y - 10), (x + i + step, y - 10), line_width)
        pygame.draw.line(screen, cross_color, (x + i, y + INTERSECTION_SIZE + 10),
                         (x + i + step, y + INTERSECTION_SIZE + 10), line_width)
    for i in range(0, length, step * 2):
        pygame.draw.line(screen, cross_color, (x - 10, y + i), (x - 10, y + i + step), line_width)
        pygame.draw.line(screen, cross_color, (x + INTERSECTION_SIZE + 10, y + i),
                         (x + INTERSECTION_SIZE + 10, y + i + step), line_width)
    for d in range(4):
        for q in range(queues[d]):
            if d == 0:
                px = x + INTERSECTION_SIZE // 2 - 16
                py = y - 28 - q * 16
            elif d == 1:
                px = x + INTERSECTION_SIZE + 12 + q * 16
                py = y + INTERSECTION_SIZE // 2 - 16
            elif d == 2:
                px = x + INTERSECTION_SIZE // 2 + 16
                py = y + INTERSECTION_SIZE + 12 + q * 16
            else:
                px = x - 28 - q * 16
                py = y + INTERSECTION_SIZE // 2 + 16
            pygame.draw.rect(screen, BLUE, (px, py, 12, 12), border_radius=3)
    for d in range(4):
        if vehicle_cross_timer[d] > 0:
            total_time = 2
            t = vehicle_cross_timer[d]
            progress = 1 - (t / total_time)
            if d == 0:
                start_x = x + INTERSECTION_SIZE // 2 - 6
                start_y = y - 28
                end_x = x + INTERSECTION_SIZE // 2 - 6
                end_y = y + INTERSECTION_SIZE // 2 - 6
            elif d == 1:
                start_x = x + INTERSECTION_SIZE + 12
                start_y = y + INTERSECTION_SIZE // 2 - 6
                end_x = x + INTERSECTION_SIZE // 2 - 6
                end_y = y + INTERSECTION_SIZE // 2 - 6
            elif d == 2:
                start_x = x + INTERSECTION_SIZE // 2 - 6
                start_y = y + INTERSECTION_SIZE + 12
                end_x = x + INTERSECTION_SIZE // 2 - 6
                end_y = y + INTERSECTION_SIZE // 2 - 6
            else:
                start_x = x - 28
                start_y = y + INTERSECTION_SIZE // 2 - 6
                end_x = x + INTERSECTION_SIZE // 2 - 6
                end_y = y + INTERSECTION_SIZE // 2 - 6
            cx = int(start_x + (end_x - start_x) * progress)
            cy = int(start_y + (end_y - start_y) * progress)
            pygame.draw.rect(screen, (0, 180, 255), (cx, cy, 14, 14), border_radius=4)
    for d in range(4):
        if ped_requests[d]:
            if d == 0:
                px, py = x + INTERSECTION_SIZE // 2, y - 30
            elif d == 1:
                px, py = x + INTERSECTION_SIZE + 30, y + INTERSECTION_SIZE // 2
            elif d == 2:
                px, py = x + INTERSECTION_SIZE // 2, y + INTERSECTION_SIZE + 30
            else:
                px, py = x - 30, y + INTERSECTION_SIZE // 2
            pygame.draw.circle(screen, PED_COLOR, (px, py), 8)
    for d in range(4):
        if ped_cross_timer[d] > 0:
            if d == 0:
                px, py = x + INTERSECTION_SIZE // 2, y + 10
            elif d == 1:
                px, py = x + INTERSECTION_SIZE - 10, y + INTERSECTION_SIZE // 2
            elif d == 2:
                px, py = x + INTERSECTION_SIZE // 2, y + INTERSECTION_SIZE - 10
            else:
                px, py = x + 10, y + INTERSECTION_SIZE // 2
            pygame.draw.circle(screen, PED_COLOR, (px, py), 10, 2)

def test_agent(agent_type="q", episodes=10, step_delay=0.2):
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Traffic Simulation Test")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 20)
    font_big = pygame.font.SysFont(None, 28)

    env = IntersectionEnv()
    state_size = len(split_state(env.reset(), 0))
    action_size = 4

    if agent_type == "q":
        agentA = QLearningAgent(state_size, action_size)
        agentB = QLearningAgent(state_size, action_size)
        agentA.load("models/agentA_q.pkl")
        agentB.load("models/agentB_q.pkl")
    else:
        agentA = DQNAgent(state_size, action_size)
        agentB = DQNAgent(state_size, action_size)
        agentA.load("models/agentA_dqn.pth")
        agentB.load("models/agentB_dqn.pth")

    total_rewards = []
    running = True
    rewards = []
    vehicles_crossed = []
    pedestrians_served = []
    avg_ped_wait = []

    for ep in range(episodes):
        state = env.reset()
        done = False
        ep_reward = 0
        while not done and running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    break

            screen.fill(BG_COLOR)
            draw_street_network(screen)

            xA, yA = WIDTH // 2 - INTERSECTION_SIZE // 2, HEIGHT // 2 + 100
            xB, yB = WIDTH // 2 - INTERSECTION_SIZE // 2, HEIGHT // 2 - 200

            phaseA = np.argmax(env.signals[0])
            phaseB = np.argmax(env.signals[1])

            draw_intersection(
                screen, font, font_big,
                xA, yA,
                phaseA, "A",
                env.queues[0], env.ped_requests[0], env.ped_timers[0], env.signal_timer[0]
            )
            draw_intersection(
                screen, font, font_big,
                xB, yB,
                phaseB, "B",
                env.queues[1], env.ped_requests[1], env.ped_timers[1], env.signal_timer[1]
            )

            ped_served, ped_avg_wait = env.get_pedestrian_metrics()
            veh_crossed = np.sum(env.get_vehicle_metrics())
            txt1 = font_big.render(f"Pedestrians served: {ped_served} | Avg wait: {ped_avg_wait:.2f}", True, BLACK)
            txt2 = font_big.render(f"Vehicles crossed: {veh_crossed}", True, BLACK)
            txt3 = font_big.render(f"Episode {ep+1}/{episodes}", True, BLACK)
            screen.blit(txt1, (30, 20))
            screen.blit(txt2, (30, 50))
            screen.blit(txt3, (30, 80))

            pygame.display.flip()

            stateA = split_state(state, 0)
            stateB = split_state(state, 1)
            actionA = agentA.get_action(stateA)
            actionB = agentB.get_action(stateB)
            actions = [actionA, actionB]
            state, reward, done, _ = env.step(actions)
            ep_reward += reward

            time.sleep(step_delay)
            clock.tick(60)
        if not running:
            break
        total_rewards.append(ep_reward)
        rewards.append(ep_reward)
        vehicles_crossed.append(np.sum(env.get_vehicle_metrics()))
        ped_served, ped_wait = env.get_pedestrian_metrics()
        pedestrians_served.append(ped_served)
        avg_ped_wait.append(ped_wait)
        print(f"Ep {ep+1}: reward={ep_reward}, vehicles={vehicles_crossed[-1]}, peds={pedestrians_served[-1]}, wait={avg_ped_wait[-1]}")
    pygame.quit()
    print(f"Average test reward: {np.mean(total_rewards):.2f}")

    with open("test_metrics.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Episode", "Reward", "VehiclesCrossed", "PedestriansServed", "AvgPedWait"])
        for i in range(episodes):
            writer.writerow([i+1, rewards[i], vehicles_crossed[i], pedestrians_served[i], avg_ped_wait[i]])

    plt.plot(rewards, label="Reward")
    plt.plot(vehicles_crossed, label="Vehicles Crossed")
    plt.plot(pedestrians_served, label="Pedestrians Served")
    plt.plot(avg_ped_wait, label="Avg Pedestrian Wait")
    plt.xlabel("Episode")
    plt.legend()
    plt.title("Test Metrics per Episode")
    plt.show()

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--agent", choices=["q", "dqn"], required=True)
    parser.add_argument("--episodes", type=int, default=10)
    parser.add_argument("--speed", type=float, default=0.2, help="Delay between steps (seconds)")
    args = parser.parse_args()
    test_agent(agent_type=args.agent, episodes=args.episodes, step_delay=args.speed)