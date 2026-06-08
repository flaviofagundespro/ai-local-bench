# STORY-015 - AMD Text Backend Comparison Battery

Status: Complete

## Context

The project already has a credible Windows AMD text baseline using `llama.cpp + Vulkan`. The next documentation step is to define a stronger cross-environment comparison battery that can later be executed on the same workstation.

## Scope

Add reusable `llama.cpp` text suites for latency, throughput, and longer-context behavior, plus a dedicated comparison-plan document for future AMD backend validation.

## Deliverables

- reusable text suite for short-response latency
- reusable text suite for sustained throughput
- reusable text suite for longer-context processing
- documented comparison plan for Windows and Linux AMD text runs
- concrete suite templates for Windows Vulkan and Ubuntu ROCm execution
- operational runbook for maintainer execution

## Acceptance Criteria

- New suites follow the existing JSON suite structure.
- New suites are conservative and runner-specific.
- Comparison guidance explains the difference between backend-only and full-stack claims.
- Documentation remains suitable for a public GitHub repository.

## Test Notes

This story defines benchmark inputs and comparison guidance. It does not execute the real model during automated validation.

## Documentation Updates

- Add a dedicated AMD text backend comparison plan under `docs/validation/`.
- Add reusable text suites under `benchmarks/text/`.
- Add concrete `qwen2.5` comparison suite templates for Windows and Ubuntu.
- Add a maintainer runbook for the future execution pass.
