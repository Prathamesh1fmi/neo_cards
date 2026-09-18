use criterion::{black_box, criterion_group, criterion_main, Criterion};
// In Cargo.toml, we would add `criterion = "0.5"` under [dev-dependencies]

fn bench_db_insert(c: &mut Criterion) {
    c.bench_function("insert_100k_notes", |b| {
        b.iter(|| {
            // MOCK database setup and transaction insert
            black_box(100_000);
        })
    });
}

criterion_group!(benches, bench_db_insert);
criterion_main!(benches);