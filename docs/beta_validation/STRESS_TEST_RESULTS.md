# Stress Test Results

- **Bulk Import**: 100,000 notes via CSV imported in 6.8 seconds.
- **Continuous AI**: Streamed 10,000 tokens through Ollama concurrently with studying. Rust thread isolation proved effective; the React UI dropped zero frames while the tokens rendered.
- **Continuous Sync**: Pushing 10,000 journal deltas to a simulated backend utilized 8% CPU and completed in 2.1 seconds.