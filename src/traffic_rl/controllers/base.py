"""Controller: Strategy interface used by TrafficLightController to
decide actions. Implementations: RLPolicyController, FixedCycleController,
RandomController. All share the same interface so Corridor can swap
them without changes (used for baseline comparison and demos).

TODO (Fase 2.1/2.2).
"""
