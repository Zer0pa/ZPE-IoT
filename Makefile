.PHONY: install test build wheel clean

install:
	cd python && python -m pip install -e ".[dev]"

test:
	cd core && cargo test
	cd python && python -m pytest tests/ -v

build:
	cd python && python -m maturin build --release

wheel:
	cd python && python -m maturin build --release --out dist/

clean:
	cd core && cargo clean
	rm -rf python/dist/ python/build/
