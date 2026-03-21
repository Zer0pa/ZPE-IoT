# Dataset Provenance

DS-01..DS-10 and DS-12 are sourced from real public datasets (E1).
DS-11 is explicitly blocked because the named no-login Telemanom source is no longer directly accessible.
Raw artifacts are downloaded into `validation/datasets/raw/DS-XX/` during operator runs and transformed into standard `data.npz` files. The committed repo keeps the normalized `data.npz` surfaces and manifest truth, not the downloaded raw archives.

Manifest policy:
- `validation/datasets/manifest.json` records provenance class, source URL, license, retrieval timestamp, and SHA256 hashes.
- For READY datasets, provenance is considered valid only when `verify_provenance.py` succeeds.
- If an upstream dataset becomes unavailable, mark `status=BLOCKED` explicitly rather than silently promoting PASS claims.

Credential policy:
- `HF_TOKEN`: optional for public Hugging Face pulls; required for private/gated assets.
- `GH_TOKEN`: optional for low-volume public fetch; required/recommended for API-heavy or private GitHub access.
- Kaggle auth: `KAGGLE_API_TOKEN` supported, with legacy compatibility via `KAGGLE_USERNAME` + `KAGGLE_KEY`.
- Current READY sources are public-first and run tokenless by default; auth failures emit explicit remediation hints.
