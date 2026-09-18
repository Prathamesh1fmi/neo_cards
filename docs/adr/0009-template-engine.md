# ADR 0009: Template Engine Boundaries

## Context
Handlebars was originally used to render the entire card preview directly from HTML fields.

## Decision
Handlebars will strictly be restricted to replacing Field Placeholders (`{{Front}}`). It will operate *after* the Renderer Pipeline has converted the JSON AST fields into secure HTML strings. Handlebars will not parse blocks or inline elements.

## Consequences
- **Positive**: Security boundary is clear. Template engine logic remains simple.
- **Negative**: Users cannot use Handlebars logic *inside* their notes, only inside the Card Templates.