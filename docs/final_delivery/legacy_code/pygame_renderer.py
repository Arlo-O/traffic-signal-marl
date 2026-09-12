import pygame
import random

# Constants
WIDTH, HEIGHT = 800, 600
FPS = 60
INTERSECTION_SIZE = 120
VEHICLE_SIZE = (20, 10)
PED_SIZE = 8

# Colors
GRAY = (50, 50, 50)
WHITE = (255, 255, 255)
RED = (200, 0, 0)
GREEN = (0, 200, 0)
BLUE = (50, 50, 255)
YELLOW = (255, 255, 0)

# Phases
NS_GREEN, NS_YELLOW, EW_GREEN, EW_YELLOW = 0, 1, 2, 3

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Dynamic Yellow Phase Traffic")
clock = pygame.time.Clock()

# Entities
vehicles = []
pedestrians = []

# Crossing trackers
crossing_vehicles_A = []
crossing_pedestrians_A = []
crossing_vehicles_B = []
crossing_pedestrians_B = []

class Vehicle:
    def __init__(self, x, y, dx, dy, inter_id=None):
        self.x, self.y = x, y
        self.dx, self.dy = dx, dy
        self.inter_id = inter_id
        self.entered = False  # Nuevo
        self.color = (0, 100, 255)

    def update(self, phase):
        if not self.entered:
            if self._can_enter(phase):
                self.entered = self._is_in_intersection_area()
                self.x += self.dx * 2
                self.y += self.dy * 2
        else:
            self.x += self.dx * 2
            self.y += self.dy * 2

    def _can_enter(self, phase):
        # Fase 0: NS verde, Fase 1: EW verde
        if self.dx != 0:  # E-W
            return phase == 1
        elif self.dy != 0:  # N-S
            return phase == 0
        return False

    def _is_in_intersection_area(self):
        if self.inter_id == "A":
            cx, cy = WIDTH // 2, HEIGHT // 2 + 160
        else:
            cx, cy = WIDTH // 2, HEIGHT // 2 - 140
        return abs(self.x - cx) < INTERSECTION_SIZE // 2 and abs(self.y - cy) < INTERSECTION_SIZE // 2

    def draw(self, surface):
        rect = pygame.Rect(int(self.x), int(self.y), *VEHICLE_SIZE)
        pygame.draw.rect(surface, self.color, rect)

class Pedestrian:
    def __init__(self, x, y, dx, dy, inter_id, direction):
        self.x, self.y = x, y
        self.dx, self.dy = dx, dy
        self.inter_id = inter_id
        self.direction = direction
        self.crossing = True
        self.color = (255, 255, 0)

    def update(self, phase):
        if self.crossing and self.can_cross(phase):
            if self.inter_id == "A" and self not in crossing_pedestrians_A:
                crossing_pedestrians_A.append(self)
            if self.inter_id == "B" and self not in crossing_pedestrians_B:
                crossing_pedestrians_B.append(self)

            self.x += self.dx * 1.2
            self.y += self.dy * 1.2

            if self._crossed():
                self.crossing = False
                if self in crossing_pedestrians_A:
                    crossing_pedestrians_A.remove(self)
                if self in crossing_pedestrians_B:
                    crossing_pedestrians_B.remove(self)

    def can_cross(self, phase):
        return (self.direction in ['N', 'S'] and phase == NS_GREEN) or \
               (self.direction in ['E', 'W'] and phase == EW_GREEN)

    def _crossed(self):
        return not (0 <= self.x <= WIDTH and 0 <= self.y <= HEIGHT)

    def draw(self, surface):
        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), PED_SIZE)
def draw_intersection(x, y, phase, label):
    pygame.draw.rect(screen, GRAY, (x, y, INTERSECTION_SIZE, INTERSECTION_SIZE))
    font = pygame.font.SysFont(None, 20)
    screen.blit(font.render(label, True, WHITE), (x + 5, y + 5))

    ns_color = GREEN if phase == NS_GREEN else YELLOW if phase == NS_YELLOW else RED
    ew_color = GREEN if phase == EW_GREEN else YELLOW if phase == EW_YELLOW else RED

    pygame.draw.circle(screen, ns_color, (x + INTERSECTION_SIZE // 2 - 50, y - 15), 6)
    pygame.draw.circle(screen, ns_color, (x + INTERSECTION_SIZE // 2 + 50, y + INTERSECTION_SIZE + 15), 6)
    pygame.draw.circle(screen, ew_color, (x + INTERSECTION_SIZE + 15, y + INTERSECTION_SIZE // 2 - 50), 6)
    pygame.draw.circle(screen, ew_color, (x - 15, y + INTERSECTION_SIZE // 2 + 50), 6)

def draw_vehicles():
    for v in vehicles:
        phase = phase_A if v.inter_id == "A" else phase_B
        v.update(phase)
        v.draw(screen)

def draw_pedestrians():
    for p in pedestrians:
        phase = phase_A if p.inter_id == "A" else phase_B
        p.update(phase)
        p.draw(screen)
    pedestrians[:] = [p for p in pedestrians if p.crossing]

def spawn_vehicle():
    inter_id = random.choice(["A", "B"])
    entry = random.choice(["N", "E", "W", "S"]) if inter_id == "B" else random.choice(["N", "E", "W"])
    y_base = HEIGHT // 2 + 160 if inter_id == "A" else HEIGHT // 2 - 140

    if entry == "N": x, y, dx, dy = WIDTH // 2 - 10, -20, 0, 1
    elif entry == "E": x, y, dx, dy = WIDTH + 20, y_base + 10, -1, 0
    elif entry == "W": x, y, dx, dy = -20, y_base - 10, 1, 0
    elif entry == "S": x, y, dx, dy = WIDTH // 2 + 10, HEIGHT + 20, 0, -1

    vehicles.append(Vehicle(x, y, dx, dy, inter_id))

def spawn_pedestrian():
    inter_id = random.choice(["A", "B"])
    direction = random.choice(["N", "S", "E", "W"])
    cx, cy = WIDTH // 2, HEIGHT // 2 + 160 if inter_id == "A" else HEIGHT // 2 - 140
    offset = INTERSECTION_SIZE // 2 + 15

    if direction == "E": x, y, dx, dy = cx - offset - 50, cy - offset, 1, 0
    elif direction == "W": x, y, dx, dy = cx + offset + 50, cy + offset, -1, 0
    elif direction == "N": x, y, dx, dy = cx - offset, cy - offset - 50, 0, 1
    elif direction == "S": x, y, dx, dy = cx + offset, cy + offset + 50, 0, -1

    pedestrians.append(Pedestrian(x, y, dx, dy, inter_id, direction))

def draw_street_network():
    road_color = (40, 40, 40)
    road_width = INTERSECTION_SIZE
    pygame.draw.rect(screen, road_color, (WIDTH // 2 - road_width // 2, 0, road_width, HEIGHT))
    pygame.draw.rect(screen, road_color, (0, HEIGHT // 2 - 200 + INTERSECTION_SIZE // 2 - road_width // 2, WIDTH, road_width))
    pygame.draw.rect(screen, road_color, (0, HEIGHT // 2 + 100 + INTERSECTION_SIZE // 2 - road_width // 2, WIDTH, road_width))

# Initial state
phase_A, phase_B = NS_GREEN, NS_GREEN
yellow_A, yellow_B = False, False
frame_count = 0
PHASE_DURATION = 300  # only for green (yellow is dynamic)

running = True
while running:
    clock.tick(FPS)
    screen.fill((20, 20, 20))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Switch logic A
    if phase_A in [NS_GREEN, EW_GREEN] and frame_count >= PHASE_DURATION:
        if phase_A == NS_GREEN and not crossing_vehicles_A and not crossing_pedestrians_A:
            phase_A = NS_YELLOW
        elif phase_A == EW_GREEN and not crossing_vehicles_A and not crossing_pedestrians_A:
            phase_A = EW_YELLOW
    elif phase_A == NS_YELLOW and not crossing_vehicles_A and not crossing_pedestrians_A:
        phase_A = EW_GREEN
        frame_count = 0
    elif phase_A == EW_YELLOW and not crossing_vehicles_A and not crossing_pedestrians_A:
        phase_A = NS_GREEN
        frame_count = 0

    # Switch logic B (same as A)
    if phase_B in [NS_GREEN, EW_GREEN] and frame_count >= PHASE_DURATION:
        if phase_B == NS_GREEN and not crossing_vehicles_B and not crossing_pedestrians_B:
            phase_B = NS_YELLOW
        elif phase_B == EW_GREEN and not crossing_vehicles_B and not crossing_pedestrians_B:
            phase_B = EW_YELLOW
    elif phase_B == NS_YELLOW and not crossing_vehicles_B and not crossing_pedestrians_B:
        phase_B = EW_GREEN
        frame_count = 0
    elif phase_B == EW_YELLOW and not crossing_vehicles_B and not crossing_pedestrians_B:
        phase_B = NS_GREEN
        frame_count = 0

    draw_street_network()
    draw_intersection(WIDTH // 2 - INTERSECTION_SIZE // 2, HEIGHT // 2 + 100, phase_A, "A")
    draw_intersection(WIDTH // 2 - INTERSECTION_SIZE // 2, HEIGHT // 2 - 200, phase_B, "B")
    draw_vehicles()
    draw_pedestrians()

    if random.random() < 0.05:
        spawn_vehicle()
    if random.random() < 0.02:
        spawn_pedestrian()

    pygame.display.flip()
    frame_count += 1

pygame.quit()
