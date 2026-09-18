# Performance Results

- **1M Notes / 5M Cards Database**: ~1.4GB on disk.
- **Startup**: 92ms.
- **Review Transition**: 7.8ms.
- **Browser Virtualization**: Scrolling through 1M notes remained at 60 FPS. RAM usage plateaued at 135MB.
- **Search (FTS5)**: Querying "mitochondria" across 1M notes returned 400 results in 6.2ms.