class RewardCalculator:
    def __init__(self, vehicle_reward=2.0, ped_reward=3.0, blocked_penalty=-1.0,
                 crossing_penalty=-2.0, turn_over_penalty=-2.0):
        self.vehicle_reward = vehicle_reward
        self.ped_reward = ped_reward
        self.blocked_penalty = blocked_penalty
        self.crossing_penalty = crossing_penalty
        self.turn_over_penalty = turn_over_penalty

    def vehicle_crossed(self, count):
        return count * self.vehicle_reward

    def pedestrian_served(self):
        return self.ped_reward

    def vehicle_blocked_by_pedestrian(self):
        return self.blocked_penalty

    def other_pedestrians_blocked(self, count):
        return count * self.crossing_penalty

    def right_turn_penalty(self):
        return self.turn_over_penalty
