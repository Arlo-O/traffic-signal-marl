# 1. Registrar decisiones de arquitectura con ADRs

## Estado
Aceptado

## Contexto
Necesitamos un historial de por que se tomaron ciertas decisiones de diseño
(ej. por que Q-learning tabular ademas de DQN, por que no SUMO en el loop de
entrenamiento), para que el repo sea legible por un revisor externo sin
tener que preguntar.

## Decision
Usar el formato ADR (Architecture Decision Record) en
`docs/architecture/decisions/`, un archivo markdown numerado por decision.

## Consecuencias
Cada decision de diseño relevante debe documentarse aqui antes o justo
despues de implementarla.
