# ZPE-IoT Novelty Card

**Product:** ZPE-IoT  
**Domain:** Bounded-lossy encoding of constrained IoT sensor streams and adjacent deterministic sensor telemetry  
**What we sell:** Smaller deterministic sensor packets with replay-stable decode for edge and industrial telemetry pipelines

## Novel contributions

1. **Compass-8 sensor delta codebook** — ZPE-IoT maps sensor deltas into an eight-direction amplitude lattice, then reconstructs from the same deterministic directional surface. The implementation couples fixed directional deltas, preset-controlled band expansion, and adaptive thresholding for bounded-lossy replay rather than a generic lossless delta codec. Code: [`python/zpe_iot/codec.py#L31-L40`](../../../python/zpe_iot/codec.py#L31-L40), [`python/zpe_iot/codec.py#L122-L152`](../../../python/zpe_iot/codec.py#L122-L152), [`core/src/quantise.rs#L1-L66`](../../../core/src/quantise.rs#L1-L66). Nearest prior art (if known): Gorilla-style delta encoding and other time-series delta/RLE codecs. What is genuinely new here: the product's directional amplitude lattice and preset-tuned threshold boundaries are used as the canonical bounded-lossy representation for sensor deltas, not as a thin wrapper around a standard lossless stream.
2. **Deterministic packet contract over directional tokens** — Encoded streams are reduced to `(direction, magnitude, run)` tokens, then packed into a fixed packet format with compact and zero-special payload modes before CRC validation at decode. Code: [`python/zpe_iot/codec.py#L190-L259`](../../../python/zpe_iot/codec.py#L190-L259), [`python/zpe_iot/codec.py#L462-L692`](../../../python/zpe_iot/codec.py#L462-L692), [`core/src/codec.rs#L141-L199`](../../../core/src/codec.rs#L141-L199). Nearest prior art (if known): fixed-header binary codecs with RLE and CRC guards. What is genuinely new here: the packet contract is specific to the directional token lattice above and is validated as decode-deterministic under the repo's destructive-test surface, rather than acting as a generic transport envelope.

## Standard techniques used (explicit, not novel)

- Delta coding
- Run-length encoding
- CRC16-CCITT packet guards
- Fixed-width binary headers
- PyO3 / Python native bindings
- zlib-backed experimental wrappers (`WI-1`, `ZH-1`)

## Compass-8 / 8-primitive architecture

YES — the core sensor codec uses an eight-direction delta lattice and deterministic direction quantiser. Code: [`python/zpe_iot/codec.py#L31-L40`](../../../python/zpe_iot/codec.py#L31-L40), [`python/zpe_iot/codec.py#L122-L145`](../../../python/zpe_iot/codec.py#L122-L145), [`core/src/quantise.rs#L1-L66`](../../../core/src/quantise.rs#L1-L66).

## Open novelty questions for the license agent

- Should the preset matrix in [`python/zpe_iot/presets.py#L19-L83`](../../../python/zpe_iot/presets.py#L19-L83) be treated as protectable novelty, or as product tuning around the core directional codec?
- Should the `python/zpe_iot/chemosense/` surface remain inside the ZPE-IoT novelty schedule, or be carved out if it later becomes its own product line?
