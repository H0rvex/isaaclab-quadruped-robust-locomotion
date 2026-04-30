# Domain Randomization Plan

## Goal

Improve robustness by training policies under controlled variation in contact, dynamics, sensing, and disturbances.

## Randomization Axes

- Ground friction.
- Base mass or payload.
- Actuator strength scaling.
- Joint damping or stiffness where supported cleanly.
- Observation noise.
- External pushes.

## Training Levels

### None

Use nominal simulator parameters. This is the baseline for measuring whether randomization helps or hurts.

### Moderate

Use bounded randomization ranges intended to preserve learnability while exposing the policy to common deployment variation.

### Strong

Use wider ranges for stress testing. Treat instability or degraded reward as a useful result, not as a reason to hide the run.

## Reporting

For each randomization level, report nominal evaluation and randomized evaluation. Include failure cases when stronger randomization causes stumbling, falls, or poor command tracking.
