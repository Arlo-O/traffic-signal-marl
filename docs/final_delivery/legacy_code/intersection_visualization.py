import pygame
import numpy as np
import sys
import time
from environment.intersection_env import IntersectionEnv
from agents.q_learning_agent import QLearningAgent
from agents.dqn_agent import DQNAgent

# --- Visual constants ---
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

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Traffic Simulation (Intersections A and B)")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 20)
font_big = pygame.font.SysFont(None, 28)

def split_state(full_state, agent_id, total_agents=2):
    size = len(full_state) // total_agents
    return full_state[agent_id * size:(agent_id + 1) * size]

def draw_street_network():
    road_color = (40, 40, 40)
    road_width = INTERSECTION_SIZE

    # Vertical road strip between A and B
    pygame.draw.rect(screen, road_color,
                     (WIDTH // 2 - road_width // 2, HEIGHT // 2 - 200 + INTERSECTION_SIZE,
                      road_width, 300))

    # North to top edge
    pygame.draw.rect(screen, road_color,
                     (WIDTH // 2 - road_width // 2, 0,
                      road_width, HEIGHT // 2 - 200))

    # South to bottom edge
    pygame.draw.rect(screen, road_color,
                     (WIDTH // 2 - road_width // 2, HEIGHT // 2 + 100 + INTERSECTION_SIZE,
                      road_width, HEIGHT // 2 - 100 - INTERSECTION_SIZE))

    # Horizontal roads (E-W)
    pygame.draw.rect(screen, road_color,
                     (0, HEIGHT // 2 - 200 + INTERSECTION_SIZE // 2 - road_width // 2,
                      WIDTH, road_width))  # B

    pygame.draw.rect(screen, road_color,
                     (0, HEIGHT // 2 + 100 + INTERSECTION_SIZE // 2 - road_width // 2,
                      WIDTH, road_width))  # A

def draw_intersection(x, y, phase, label, queues, ped_requests, ped_cross_timer, vehicle_cross_timer):
    # Base intersection square
    pygame.draw.rect(screen, GRAY, (x, y, INTERSECTION_SIZE, INTERSECTION_SIZE), border_radius=12)

    # Draw label
    label_surface = font.render(label, True, WHITE)
    screen.blit(label_surface, (x + 5, y + 5))

    # Traffic lights
    ns_color = GREEN if phase == 0 else RED
    ew_color = GREEN if phase == 1 else RED
    pygame.draw.circle(screen, ns_color, (x + INTERSECTION_SIZE // 2 - 50, y - 15), 8)
    pygame.draw.circle(screen, ns_color, (x + INTERSECTION_SIZE // 2 + 50, y + INTERSECTION_SIZE + 15), 8)
    pygame.draw.circle(screen, ew_color, (x + INTERSECTION_SIZE + 15, y + INTERSECTION_SIZE // 2 - 50), 8)
    pygame.draw.circle(screen, ew_color, (x - 15, y + INTERSECTION_SIZE // 2 + 50), 8)

    # Draw crosswalks
    cross_color = WHITE
    line_width = 2
    step = 8
    length = INTERSECTION_SIZE

    for i in range(0, length, step * 2):
        # Top
        pygame.draw.line(screen, cross_color, (x + i, y - 10), (x + i + step, y - 10), line_width)
        # Bottom
        pygame.draw.line(screen, cross_color, (x + i, y + INTERSECTION_SIZE + 10),
                         (x + i + step, y + INTERSECTION_SIZE + 10), line_width)
    for i in range(0, length, step * 2):
        # Left
        pygame.draw.line(screen, cross_color, (x - 10, y + i), (x - 10, y + i + step), line_width)
        # Right
        pygame.draw.line(screen, cross_color, (x + INTERSECTION_SIZE + 10, y + i),
                         (x + INTERSECTION_SIZE + 10, y + i + step), line_width)

    # Draw vehicles in queues (N=0, E=1, S=2, W=3)
    for d in range(4):
        for q in range(queues[d]):
            if d == 0:  # North
                px = x + INTERSECTION_SIZE // 2 - 16
                py = y - 28 - q * 16
            elif d == 1:  # East
                px = x + INTERSECTION_SIZE + 12 + q * 16
                py = y + INTERSECTION_SIZE // 2 - 16
            elif d == 2:  # South
                px = x + INTERSECTION_SIZE // 2 + 16
                py = y + INTERSECTION_SIZE + 12 + q * 16
            else:  # West
                px = x - 28 - q * 16
                py = y + INTERSECTION_SIZE // 2 + 16
            pygame.draw.rect(screen, BLUE, (px, py, 12, 12), border_radius=3)

    # Draw vehicles crossing (animated)
    for d in range(4):
        if vehicle_cross_timer[d] > 0:
            # Animation: move from entry to center based on timer
            total_time = 2  # vehicle_crossing_time from env
            t = vehicle_cross_timer[d]
            progress = 1 - (t / total_time)
            if d == 0:  # North to center
                start_x = x + INTERSECTION_SIZE // 2 - 6
                start_y = y - 28
                end_x = x + INTERSECTION_SIZE // 2 - 6
                end_y = y + INTERSECTION_SIZE // 2 - 6
            elif d == 1:  # East to center
                start_x = x + INTERSECTION_SIZE + 12
                start_y = y + INTERSECTION_SIZE // 2 - 6
                end_x = x + INTERSECTION_SIZE // 2 - 6
                end_y = y + INTERSECTION_SIZE // 2 - 6
            elif d == 2:  # South to center
                start_x = x + INTERSECTION_SIZE // 2 - 6
                start_y = y + INTERSECTION_SIZE + 12
                end_x = x + INTERSECTION_SIZE // 2 - 6
                end_y = y + INTERSECTION_SIZE // 2 - 6
            else:  # West to center
                start_x = x - 28
                start_y = y + INTERSECTION_SIZE // 2 - 6
                end_x = x + INTERSECTION_SIZE // 2 - 6
                end_y = y + INTERSECTION_SIZE // 2 - 6
            cx = int(start_x + (end_x - start_x) * progress)
            cy = int(start_y + (end_y - start_y) * progress)
            pygame.draw.rect(screen, (0, 180, 255), (cx, cy, 14, 14), border_radius=4)

    # Draw pedestrians waiting
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

    # Draw pedestrians crossing
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
def main():
    env = IntersectionEnv()
    state = env.reset()
    agent_type = "q"  # Cambia a "dqn" si quieres usar DQN

    state_size = len(split_state(state, 0))
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

    running = True
    step_delay = 1  # Puedes ajustar la velocidad

    while running:
        screen.fill(BG_COLOR)
        draw_street_network()

        # Intersection positions
        xA, yA = WIDTH // 2 - INTERSECTION_SIZE // 2, HEIGHT // 2 + 100
        xB, yB = WIDTH // 2 - INTERSECTION_SIZE // 2, HEIGHT // 2 - 200

        # Obtener la fase activa de cada intersección
        phaseA = np.argmax(env.signals[0])
        phaseB = np.argmax(env.signals[1])

        # Draw intersections
        draw_intersection(
            xA, yA,
            phaseA, "A",
            env.queues[0], env.ped_requests[0], env.ped_timers[0], env.signal_timer[0]
        )
        draw_intersection(
            xB, yB,
            phaseB, "B",
            env.queues[1], env.ped_requests[1], env.ped_timers[1], env.signal_timer[1]
        )

        # Draw metrics
        ped_served, ped_avg_wait = env.get_pedestrian_metrics()
        veh_crossed = np.sum(env.get_vehicle_metrics())
        txt1 = font_big.render(f"Pedestrians served: {ped_served} | Avg wait: {ped_avg_wait:.2f}", True, BLACK)
        txt2 = font_big.render(f"Vehicles crossed: {veh_crossed}", True, BLACK)
        screen.blit(txt1, (30, 20))
        screen.blit(txt2, (30, 50))

        pygame.display.flip()

        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Simple policy: alternate phases
        # actions = [(env.signal_phase[0]+1)%2, (env.signal_phase[1]+1)%2]
        stateA = split_state(state, 0)
        stateB = split_state(state, 1)
        actionA = agentA.get_action(stateA)
        actionB = agentB.get_action(stateB)
        actions = [actionA, actionB]
        state, reward, done, _ = env.step(actions)
        time.sleep(step_delay)
        clock.tick(60)
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()