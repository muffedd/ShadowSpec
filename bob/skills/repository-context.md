# Bob skill: repository context

## Purpose

Give every Bob role the same full-repository context so handoffs do not lose
callers, tests, side effects, or security constraints.

## Use when

Starting a session, changing roles, reviewing a new diff, or exporting
evidence.

## Procedure

- Read `AGENTS.md`, the design, plan, package metadata, current status/diff,
  relevant source, fixtures, tests, and existing evidence.
- Record the revision/source hash when available and identify files actually
  inspected.
- Distinguish observed facts, static-analysis inferences, and unknowns.
- Refresh the packet after implementation; do not carry stale assumptions.

## Guardrails

Never substitute a selected snippet for repository context. Do not expose
secrets, environment variables, private source, or absolute host paths in a
packet.

