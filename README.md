# 🚦 Traffic Signal MARL — Autonomous Cybernetic Traffic Control

> Sistema multi-agente de control de semáforos basado en aprendizaje por refuerzo (Q-learning y DQN), aplicado a un corredor de dos intersecciones consecutivas. El proyecto combina principios de cibernética (control por retroalimentación) con RL para que cada semáforo aprenda a coordinar el flujo vehicular y peatonal de forma descentralizada.

**Estado:** 🚧 En refactor activo — ver [Roadmap](#-roadmap) para el progreso por fase.

---

## Índice
- [Resumen del problema](#resumen-del-problema)
- [Demo](#demo)
- [Resultados clave](#resultados-clave)
- [Arquitectura](#arquitectura)
- [Stack técnico](#stack-técnico)
- [Estructura del repositorio](#estructura-del-repositorio)
- [Cómo ejecutarlo](#cómo-ejecutarlo)
- [Roadmap](#-roadmap)
- [Historia del proyecto](#historia-del-proyecto)
- [Documentación](#documentación)
- [Autores](#autores)
- [Licencia](#licencia)

---

## Resumen del problema

Dos intersecciones consecutivas, cada una controlada por un agente independiente, deben aprender a minimizar el tiempo de espera de vehículos y peatones sin coordinación centralizada. El flujo de salida de la primera intersección alimenta directamente la cola de la segunda, por lo que la decisión de un agente afecta las condiciones del otro — esto es lo que hace al problema genuinamente multi-agente y no dos problemas de control independientes.

El sistema se modela formalmente como un MDP por agente (estado, acción, recompensa, transición) y se entrena con dos enfoques comparables entre sí: **Q-learning tabular** y **Deep Q-Network (DQN)**, evaluados contra un **baseline de ciclo fijo** bajo las mismas condiciones de tráfico.

## Demo

<!-- TODO (Fase 2.4): GIF de la simulación con agentes entrenados, corriendo en un escenario fuera de entrenamiento (hora pico / baja demanda). -->
*Pendiente — se agrega al cierre de la Fase 2.4 (simulador fuera de entrenamiento).*

## Resultados clave

<!-- TODO (Fase 2.2): tabla comparativa Q-learning vs DQN vs baseline, misma semilla de tráfico. -->
| Política | Espera acumulada | Throughput | Cambios de fase |
|---|---|---|---|
| Q-learning | *pendiente* | *pendiente* | *pendiente* |
| DQN | *pendiente* | *pendiente* | *pendiente* |
| Baseline (ciclo fijo) | *pendiente* | *pendiente* | *pendiente* |

## Arquitectura

<!-- TODO (Fase 2.3): diagrama C4 en docs/architecture/. -->
El sistema separa un **modelo de dominio** (objetos que representan vehículos, peatones, semáforos e intersecciones) de un **adaptador Gymnasium** delgado que expone ese dominio como entorno de RL estándar. Esto permite reutilizar exactamente la misma lógica de simulación tanto para entrenar los agentes como para correr demos fuera de entrenamiento con distintos escenarios de tráfico.

Detalle completo de decisiones de diseño en [`docs/architecture/`](docs/architecture/) (Architecture Decision Records).

## Stack técnico

- **Python 3.11**, [Gymnasium](https://gymnasium.farama.org/) para la interfaz de entorno de RL
- Q-learning tabular y DQN implementados desde cero (PyTorch)
- `pytest` para tests del dominio de simulación
- GitHub Actions para CI (lint + tests en cada push)
- Renderizado de la simulación vía Pygame / interfaz web (Canvas)

## Estructura del repositorio

```
traffic-signal-marl/
├── docs/
│   ├── workshops/           # Desarrollo iterativo original (cibernética, modelado dinámico, código v1)
│   ├── architecture/        # ADRs y diagramas C4
│   └── final_delivery/      # Reporte técnico, paper, póster y slides del curso original
├── src/traffic_rl/
│   ├── domain/               # Vehicle, Pedestrian, Intersection, Corridor
│   ├── envs/                 # Adaptador gymnasium.Env
│   ├── agents/                # Q-learning, DQN
│   ├── controllers/           # Estrategias intercambiables (RL / ciclo fijo)
│   ├── training/
│   ├── evaluation/
│   └── simulation/            # Simulador fuera de entrenamiento
├── configs/                   # Escenarios parametrizables (YAML)
├── tests/
├── results/                   # Métricas versionadas por release
└── models/                    # Pesos entrenados
```

## Cómo ejecutarlo

<!-- TODO: completar cuando exista pyproject.toml y entry points reales (Fase 2.1) -->
```bash
git clone https://github.com/<usuario>/traffic-signal-marl.git
cd traffic-signal-marl
pip install -e ".[dev]"

# Entrenar
python -m traffic_rl.training.train --config configs/normal.yaml

# Evaluar contra baseline
python -m traffic_rl.evaluation.evaluate --config configs/normal.yaml

# Correr demo fuera de entrenamiento
python -m traffic_rl.simulation.demo --config configs/rush_hour.yaml
```

## 🗺 Roadmap

- [x] `v0.1-legacy` — Importación del desarrollo original (workshops + entrega final del curso)
- [ ] **2.0** — Diseño de dominio (clases, secuencia, parametrización)
- [ ] **2.1** `v0.2.1` — Entorno Gymnasium + agentes corregidos + tests
- [ ] **2.2** `v0.3` — Baseline, configs, evaluación reproducible
- [ ] **2.3** `v0.4` — Arquitectura documentada (C4 + ADRs)
- [ ] **2.4** `v0.5` — Simulador fuera de entrenamiento + evaluación de generalización
- [ ] Actualización del Final Delivery (reporte, paper, póster, slides)
- [ ] **3** `v0.6` — Respuesta a vehículos de emergencia
- [ ] **4** `v1.0` — Coordinación multi-agente (green wave)

Seguimiento detallado en [Issues](../../issues) y [Milestones](../../milestones).

## Historia del proyecto

Este proyecto nació en el curso *Systems Sciences Foundations* (Universidad Distrital Francisco José de Caldas, 2025-I) como una exploración de sistemas cibernéticos aplicados a control de tráfico. Los repositorios originales, con el desarrollo por workshops y la entrega final del curso, están preservados como referencia:

- [`SCF_project`](https://github.com/<usuario>/SCF_project) — desarrollo iterativo por workshops
- [`FinalDelivery-Project-FCS`](https://github.com/<usuario>/FinalDelivery-Project-FCS) — entrega final (reporte, paper, póster, slides)

Este repositorio parte de ese trabajo y lo refactoriza con una arquitectura orientada a objetos, evaluación experimental rigurosa y documentación de decisiones de diseño — llevándolo de un proyecto de curso a un sistema con estándares de ingeniería de software y ML aplicados en producción.

## Documentación

- [`docs/workshops/`](docs/workshops/) — proceso de diseño original (blackbox, feedback loops, modelado dinámico)
- [`docs/architecture/`](docs/architecture/) — ADRs y diagramas de arquitectura
- [`docs/final_delivery/`](docs/final_delivery/) — reporte técnico, paper, póster, slides

## Autores

- **Juan Santiago Ramos Ome**
- **Arlo Nicolás Ocampo Gallego**
- Asesor original: Carlos Andrés Sierra Virguez

## Licencia

GNU GPL v3.0 — ver [`LICENSE`](LICENSE).
