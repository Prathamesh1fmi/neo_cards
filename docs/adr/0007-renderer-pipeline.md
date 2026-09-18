# ADR 0007: Renderer Pipeline

## Context
If we store JSON, we need a way to convert it to HTML for the `WebView` preview and studying interfaces.

## Decision
We will implement a multi-stage Renderer Pipeline in Rust.
`JSON Document -> Markdown Renderer -> Math Renderer (KaTeX/MathJax) -> Media Renderer -> HTML Renderer -> Template Engine (Handlebars) -> Final Preview HTML`.

## Consequences
- **Positive**: Highly modular. If we switch math libraries or add syntax highlighting, we only update one pipeline stage. Security is enforced by a final sanitization step.
- **Negative**: Rendering a card requires multiple AST passes in Rust.