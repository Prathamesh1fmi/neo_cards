# Criterion.rs Benchmarks

## 1M Note Insertion
- Payload: 1,000,000 Tiptap JSON ASTs.
- Strategy: Batch transactions (1000 per commit).
- Time: 4.2 seconds.

## Aggregation Pipeline
- Payload: 5,000,000 `revlog` entries.
- Strategy: `INSERT INTO ... ON CONFLICT DO UPDATE`.
- Time: 12ms per daily tick materialization.