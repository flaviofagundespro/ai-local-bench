# Project Framing

Date: 2026-06-06
Status: Draft

## Project Name

AI Local Bench

Repository slug:

```text
ai-local-bench
```

## One-Line Description

Reproducible cross-platform benchmarks for local AI inference on consumer hardware.

## Core Positioning

AI Local Bench is hardware-vendor neutral, but its first maintainer-validated target is consumer AMD hardware.

This matters because AMD local AI support can vary widely across operating systems, drivers, and backend technologies. The project should make those differences visible without becoming AMD-only.

## First Validation Hardware

Maintainer validation starts with:

- CPU: AMD Ryzen 9 7900X
- GPU: AMD Radeon RX 6750 XT 12GB
- RAM: 32GB DDR5
- Storage: NVMe SSD

## Initial Audience

- Local AI users comparing backends on their own machines
- Developers choosing between Windows and Linux for inference
- AMD users looking for practical benchmark evidence
- NVIDIA, Intel, Apple Silicon, and CPU-only users who want to submit comparable results

## Initial Product Boundary

Version `v0.1` should be a CLI benchmark suite.

It should not include:

- UI
- hosted leaderboard
- online account system
- automatic model downloads without explicit user action
- broad benchmark claims without recorded environment metadata

## Initial Technical Direction

- Language: Python
- Interface: CLI
- Platforms: Windows and Linux
- Output formats: JSONL, CSV, Markdown
- First runners: `llama.cpp`, `Ollama`, `ComfyUI`
- First benchmark families: text generation and image generation

## Documentation Principle

Documentation must separate:

- planned
- implemented
- experimental
- maintainer validated
- community reported

The project should avoid claiming support for hardware or backends that were not actually tested.
