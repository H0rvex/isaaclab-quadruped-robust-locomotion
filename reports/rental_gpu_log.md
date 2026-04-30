# Rental GPU Log

Record every rented GPU session that produces install evidence, training evidence, evaluation data, or videos.

## Session Template

```text
Date:
Provider:
Instance type:
GPU:
VRAM:
CPU:
RAM:
Disk:
OS:
NVIDIA driver:
CUDA:
Python:
PyTorch:
Isaac Sim:
Isaac Lab:
RSL-RL:
Project commit:
IsaacLab commit:
Commands run:
Artifacts produced:
Issues:
Cost/time notes:
```

## Notes

Run Isaac Lab smoke tests before long training jobs. If installation or task launch fails, preserve the error and environment details before deleting the machine.
