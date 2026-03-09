# Falsification Results

- Generated: `2026-02-21T03:56:51.289695+00:00`

## F1 Low-variance/near-constant signals challenge
- Checked via DS-01..DS-08 comparator table with zpe/zlib/lz4/zstd/pcodec.
- Outcome: zpe still has non-win subsets; universal-win hypothesis falsified.

## F2 DT-09 mixed native/python asymmetry masking
- Checked via explicit split artifact and source inspection (no min masking).
- Outcome: masking hypothesis falsified.

## F3 RLE post-pass on adversarial alternating stream
- Adversarial gain pct: `0.000000`.
- Outcome: universal-RLE-gain hypothesis falsified.

## F4 Reproducibility rerun
- Full gate command set replayed with logged command transcript and strict replay campaign.
- Outcome: reproducibility challenge falsified (5/5 strict runs pass, determinism hash-consistent).

## F5 Payload economics with framing overhead
- Payload economics table includes transport payload bytes and relative reduction vs raw.
- Outcome: framing-ignored hypothesis falsified.
