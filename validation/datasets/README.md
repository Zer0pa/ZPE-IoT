# Dataset Provenance

DS-01..DS-08 are now sourced from real public datasets (E1).
Raw artifacts are stored under `validation/datasets/raw/DS-XX/` and transformed into standard `data.npz` files.

Manifest policy:
- `validation/datasets/manifest.json` records provenance class, source URL, license, retrieval timestamp, and SHA256 hashes.
- For DS-01..DS-08, provenance is considered valid only when `verify_provenance.py` succeeds.
- If an upstream dataset becomes unavailable, mark `status=BLOCKED` explicitly rather than silently promoting PASS claims.

Credential policy:
- `HF_TOKEN`: optional for public Hugging Face pulls; required for private/gated assets.
- `GH_TOKEN`: optional for low-volume public fetch; required/recommended for API-heavy or private GitHub access.
- Kaggle auth: `KAGGLE_API_TOKEN` supported, with legacy compatibility via `KAGGLE_USERNAME` + `KAGGLE_KEY`.
- Current DS-01..DS-08 sources are public-first and run tokenless by default; auth failures emit explicit remediation hints.

Chemosense addendum:
- Public modality proxies are materialized under `validation/datasets/raw/chemosense/`.
- `validation/datasets/manifest_chemosense.json` records `provenance_class`, `evidence_class`, source/license metadata, and raw/transform hashes for `CS-01..CS-03`.
- Validate chemosense provenance with:
  `python validation/datasets/verify_chemosense_provenance.py --min-class E1`
