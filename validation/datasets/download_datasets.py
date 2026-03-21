#!/usr/bin/env python3
"""Download/build DS-01..DS-12 and emit provenance-rich manifest metadata."""

from __future__ import annotations

import argparse
import csv
import gzip
import hashlib
import io
import json
import math
import shutil
import subprocess
import tempfile
import urllib.error
import urllib.request
import zipfile
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
DATASET_DIR = ROOT / "validation" / "datasets"
RAW_DIR = DATASET_DIR / "raw"

MIN_SAMPLES = 4096
MAX_SAMPLES = 200_000


def _iso_utc_from_mtime(path: Path) -> str:
    ts = datetime.fromtimestamp(path.stat().st_mtime, timezone.utc)
    return ts.isoformat().replace("+00:00", "Z")


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _download(url: str, dst: Path) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    req = urllib.request.Request(url, headers={"User-Agent": "zpe-iot-hardening/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=300) as resp, dst.open("wb") as out:
            shutil.copyfileobj(resp, out)
    except urllib.error.HTTPError as exc:
        if exc.code in {401, 403}:
            raise RuntimeError(
                "Source requires authentication. "
                "Use HF_TOKEN for gated Hugging Face, GH_TOKEN for GitHub API/private access, "
                "or Kaggle credentials (KAGGLE_API_TOKEN or KAGGLE_USERNAME+KAGGLE_KEY) for Kaggle pulls."
            ) from exc
        raise


def _normalise_samples(samples: np.ndarray, sample_rate_hz: float) -> tuple[np.ndarray, float, list[str]]:
    arr = np.asarray(samples, dtype=np.float64).reshape(-1)
    arr = arr[np.isfinite(arr)]
    if arr.size == 0:
        raise RuntimeError("No finite samples after extraction")

    notes: list[str] = []
    rate = float(sample_rate_hz)

    if arr.size > MAX_SAMPLES:
        step = int(math.ceil(arr.size / MAX_SAMPLES))
        arr = arr[::step][:MAX_SAMPLES]
        rate = rate / step
        notes.append(f"downsampled by factor {step} to cap runtime")

    if arr.size < MIN_SAMPLES:
        repeats = int(math.ceil(MIN_SAMPLES / arr.size))
        arr = np.tile(arr, repeats)[:MIN_SAMPLES]
        notes.append(f"cycled trace {repeats}x to satisfy minimum {MIN_SAMPLES} samples")

    return arr.astype(np.float64), rate, notes


def _save_dataset(ds_id: str, name: str, samples: np.ndarray, sample_rate_hz: float, provenance: str) -> Path:
    out_dir = DATASET_DIR / ds_id
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "data.npz"
    np.savez(
        out_path,
        samples=samples.astype(np.float64),
        sample_rate=np.array([sample_rate_hz], dtype=np.float64),
        name=np.array([name]),
        provenance=np.array([provenance]),
    )
    return out_path


def _extract_air_quality(raw_zip: Path) -> np.ndarray:
    with zipfile.ZipFile(raw_zip) as zf:
        csv_name = next(name for name in zf.namelist() if name.lower().endswith(".csv"))
        data = zf.read(csv_name).decode("latin1", errors="ignore")

    rows = csv.reader(io.StringIO(data), delimiter=";")
    header = next(rows)
    idx = header.index("PT08.S1(CO)")

    out = []
    for row in rows:
        if idx >= len(row):
            continue
        val = row[idx].strip()
        if not val or val == "-200":
            continue
        out.append(float(val.replace(",", ".")))
    return np.asarray(out, dtype=np.float64)


def _extract_phm_bearing(raw_csv: Path) -> np.ndarray:
    arr = np.loadtxt(raw_csv, delimiter=",", dtype=np.float64)
    if arr.ndim == 1:
        arr = arr.reshape(1, -1)
    if arr.shape[1] < 6:
        raise RuntimeError("Unexpected PHM CSV format")

    # Use resultant acceleration from the x/y channels.
    x = arr[:, 4]
    y = arr[:, 5]
    return np.sqrt((x * x) + (y * y))


def _extract_intel_lab(raw_gz: Path) -> np.ndarray:
    out = []
    with gzip.open(raw_gz, "rt", encoding="utf-8", errors="ignore") as f:
        for line in f:
            parts = line.strip().split()
            if len(parts) < 7:
                continue
            temp_c = float(parts[4])
            if -60.0 <= temp_c <= 80.0:
                out.append(temp_c)
    return np.asarray(out, dtype=np.float64)


def _extract_har(raw_outer_zip: Path) -> np.ndarray:
    return _extract_har_body_acc(raw_outer_zip, split="train")


def _extract_har_body_acc(raw_outer_zip: Path, split: str) -> np.ndarray:
    with zipfile.ZipFile(raw_outer_zip) as outer:
        inner_name = next(name for name in outer.namelist() if name.endswith(".zip"))
        inner_bytes = outer.read(inner_name)

    with zipfile.ZipFile(io.BytesIO(inner_bytes)) as inner:
        suffix = f"{split}/Inertial Signals/body_acc_x_{split}.txt"
        target = next(name for name in inner.namelist() if name.endswith(suffix))
        with inner.open(target) as f:
            values: list[float] = []
            for line in f:
                values.extend(float(tok) for tok in line.decode("utf-8", errors="ignore").strip().split())
    return np.asarray(values, dtype=np.float64)


def _extract_noaa_pressure(raw_csv: Path) -> np.ndarray:
    out = []
    with raw_csv.open("r", encoding="utf-8", errors="ignore", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            tmp = (row.get("TMP") or "").split(",")[0].strip()
            if tmp and tmp != "+9999" and tmp != "-9999":
                out.append(float(tmp) / 10.0)
    return np.asarray(out, dtype=np.float64)


def _extract_nab(raw_csv: Path) -> np.ndarray:
    out = []
    with raw_csv.open("r", encoding="utf-8", errors="ignore", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            val = row.get("value")
            if val is None:
                continue
            out.append(float(val))
    return np.asarray(out, dtype=np.float64)


def _haversine_m(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    r = 6371000.0
    p1 = math.radians(lat1)
    p2 = math.radians(lat2)
    dp = math.radians(lat2 - lat1)
    dl = math.radians(lon2 - lon1)
    a = (math.sin(dp / 2.0) ** 2) + math.cos(p1) * math.cos(p2) * (math.sin(dl / 2.0) ** 2)
    return 2.0 * r * math.atan2(math.sqrt(a), math.sqrt(max(1e-12, 1.0 - a)))


def _extract_gps(raw_zip: Path) -> np.ndarray:
    with tempfile.TemporaryDirectory() as td:
        tdir = Path(td)
        with zipfile.ZipFile(raw_zip) as zf:
            zf.extractall(tdir)

        rar_path = tdir / "GPS Trajectory.rar"
        if not rar_path.exists():
            raise RuntimeError("Missing GPS Trajectory.rar in archive")

        subprocess.run(["bsdtar", "-xf", str(rar_path), "-C", str(tdir)], check=True)
        points_path = tdir / "GPS Trajectory" / "go_track_trackspoints.csv"
        if not points_path.exists():
            raise RuntimeError("Missing go_track_trackspoints.csv after extraction")

        deltas: list[float] = []
        prev: dict[str, tuple[float, float]] = {}
        with points_path.open("r", encoding="utf-8", errors="ignore", newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                tid = str(row.get("track_id", ""))
                lat = float(row["latitude"])
                lon = float(row["longitude"])
                if tid in prev:
                    plat, plon = prev[tid]
                    dx = _haversine_m(plat, plon, plat, lon)
                    dy = _haversine_m(plat, plon, lat, plon)
                    if lon < plon:
                        dx = -dx
                    if lat < plat:
                        dy = -dy
                    deltas.extend([dx, dy])
                prev[tid] = (lat, lon)

    return np.asarray(deltas, dtype=np.float64)


def _extract_household_power(raw_zip: Path) -> np.ndarray:
    with zipfile.ZipFile(raw_zip) as zf:
        txt_name = next(name for name in zf.namelist() if name.lower().endswith(".txt"))
        with zf.open(txt_name) as f:
            raw = f.read().decode("utf-8", errors="ignore")

    rows = csv.reader(io.StringIO(raw), delimiter=";")
    header = next(rows)
    idx_voltage = header.index("Voltage")
    idx_current = header.index("Global_intensity")

    out = []
    for row in rows:
        if len(row) <= max(idx_voltage, idx_current):
            continue
        v = row[idx_voltage].strip()
        i = row[idx_current].strip()
        if v == "?" or i == "?":
            continue
        out.append(float(v))
    return np.asarray(out, dtype=np.float64)


def _extract_cwru_48k_drive_end(raw_mat: Path) -> np.ndarray:
    try:
        from scipy.io import loadmat
    except ImportError as exc:
        raise RuntimeError("scipy is required to parse the CWRU .mat source") from exc

    payload = loadmat(raw_mat)
    numeric_keys: list[tuple[str, np.ndarray]] = []
    for key, value in payload.items():
        if key.startswith("__"):
            continue
        if not isinstance(value, np.ndarray):
            continue
        if not np.issubdtype(value.dtype, np.number):
            continue
        arr = np.asarray(value, dtype=np.float64).reshape(-1)
        if arr.size:
            numeric_keys.append((key, arr))

    for key, arr in numeric_keys:
        if key.endswith("_DE_time") or "DE_time" in key:
            return arr

    if numeric_keys:
        return numeric_keys[0][1]
    raise RuntimeError(f"No numeric drive-end channel found in {raw_mat}")


def _extract_har_test(raw_outer_zip: Path) -> np.ndarray:
    return _extract_har_body_acc(raw_outer_zip, split="test")


def _extract_electricity_load(raw_zip: Path) -> np.ndarray:
    with zipfile.ZipFile(raw_zip) as zf:
        txt_name = next(name for name in zf.namelist() if name.lower().endswith(".txt"))
        with zf.open(txt_name) as f:
            wrapper = io.TextIOWrapper(f, encoding="utf-8", errors="ignore", newline="")
            rows = csv.reader(wrapper, delimiter=";")
            header = next(rows)
            if len(header) < 2:
                raise RuntimeError("Electricity dataset missing meter columns")
            out = []
            for row in rows:
                if len(row) < 2:
                    continue
                value = row[1].strip()
                if not value:
                    continue
                out.append(float(value.replace(",", ".")))
    return np.asarray(out, dtype=np.float64)


@dataclass(frozen=True)
class PublicDataset:
    ds_id: str
    name: str
    source_url: str
    license_name: str
    raw_filename: str
    sample_rate_hz: float
    extractor: Callable[[Path], np.ndarray]
    notes: str


PUBLIC_DATASETS = [
    PublicDataset(
        ds_id="DS-01",
        name="UCI AirQuality (CO channel)",
        source_url="https://archive.ics.uci.edu/ml/machine-learning-databases/00360/AirQualityUCI.zip",
        license_name="CC BY 4.0 (UCI repository terms)",
        raw_filename="AirQualityUCI.zip",
        sample_rate_hz=1.0 / 3600.0,
        extractor=_extract_air_quality,
        notes="Original DS-01 source; extracted PT08.S1(CO) channel and removed sentinel -200 rows.",
    ),
    PublicDataset(
        ds_id="DS-02",
        name="PHM 2012 Bearing Challenge (Learning_set/Bearing1_1)",
        source_url="https://raw.githubusercontent.com/wkzs111/phm-ieee-2012-data-challenge-dataset/master/Learning_set/Bearing1_1/acc_00001.csv",
        license_name="Citation-required academic use (PHM 2012 challenge terms)",
        raw_filename="acc_00001.csv",
        sample_rate_hz=25_600.0,
        extractor=_extract_phm_bearing,
        notes="Original FEMTO challenge endpoint is unavailable; using public mirror and resultant acceleration magnitude.",
    ),
    PublicDataset(
        ds_id="DS-03",
        name="MIT Intel Lab Data (temperature)",
        source_url="https://db.csail.mit.edu/labdata/data.txt.gz",
        license_name="Academic research dataset (Intel Lab Data page)",
        raw_filename="intel_lab_data.txt.gz",
        sample_rate_hz=1.0 / 31.0,
        extractor=_extract_intel_lab,
        notes="Original DS-03 source; extracted temperature column from mote stream.",
    ),
    PublicDataset(
        ds_id="DS-04",
        name="UCI HAR Smartphone Inertial Signals (body_acc_x)",
        source_url="https://archive.ics.uci.edu/static/public/240/human+activity+recognition+using+smartphones.zip",
        license_name="CC BY 4.0 (UCI repository terms)",
        raw_filename="uci_har_outer.zip",
        sample_rate_hz=50.0,
        extractor=_extract_har,
        notes="Original SHL endpoint is non-direct; using public UCI HAR inertial accelerometer channel.",
    ),
    PublicDataset(
        ds_id="DS-05",
        name="NOAA Global Hourly (station 01001099999)",
        source_url="https://www.ncei.noaa.gov/data/global-hourly/access/2022/01001099999.csv",
        license_name="U.S. Government work (public domain)",
        raw_filename="noaa_global_hourly_2022_01001099999.csv",
        sample_rate_hz=1.0 / 3600.0,
        extractor=_extract_noaa_pressure,
        notes="Original DS-05 source; extracted TMP numeric channel from NOAA hourly feed.",
    ),
    PublicDataset(
        ds_id="DS-06",
        name="Numenta NAB NYC Taxi",
        source_url="https://raw.githubusercontent.com/numenta/NAB/master/data/realKnownCause/nyc_taxi.csv",
        license_name="MIT",
        raw_filename="nab_nyc_taxi.csv",
        sample_rate_hz=1.0 / 1800.0,
        extractor=_extract_nab,
        notes="Original DS-06 source; extracted value column from realKnownCause/nyc_taxi.csv.",
    ),
    PublicDataset(
        ds_id="DS-07",
        name="UCI GPS Trajectories (go_track trackpoints)",
        source_url="https://archive.ics.uci.edu/static/public/354/gps+trajectories.zip",
        license_name="CC BY 4.0 (UCI repository terms)",
        raw_filename="gps_trajectories.zip",
        sample_rate_hz=0.2,
        extractor=_extract_gps,
        notes="Original Geolife URL returned 404; using public UCI GPS trajectories and signed per-axis meter deltas.",
    ),
    PublicDataset(
        ds_id="DS-08",
        name="UCI Household Power Consumption (Voltage channel)",
        source_url="https://archive.ics.uci.edu/ml/machine-learning-databases/00235/household_power_consumption.zip",
        license_name="CC BY 4.0 (UCI repository terms)",
        raw_filename="household_power_consumption.zip",
        sample_rate_hz=1.0 / 60.0,
        extractor=_extract_household_power,
        notes="Original DEBS 2012 sample links returned 404; substituted with public voltage telemetry from UCI household power data.",
    ),
    PublicDataset(
        ds_id="DS-09",
        name="CWRU Bearing Drive End 48kHz (109.mat)",
        source_url="https://engineering.case.edu/sites/default/files/109.mat",
        license_name="Public research dataset (Case Western Reserve University Bearing Data Center terms)",
        raw_filename="109.mat",
        sample_rate_hz=48_000.0,
        extractor=_extract_cwru_48k_drive_end,
        notes="Direct Case Western Reserve University Bearing Data Center 48kHz drive-end file.",
    ),
    PublicDataset(
        ds_id="DS-10",
        name="UCI HAR Smartphone Inertial Signals (body_acc_x test split)",
        source_url="https://archive.ics.uci.edu/static/public/240/human+activity+recognition+using+smartphones.zip",
        license_name="CC BY 4.0 (UCI repository terms)",
        raw_filename="uci_har_outer.zip",
        sample_rate_hz=50.0,
        extractor=_extract_har_test,
        notes="Extracted test split body_acc_x from the same public UCI HAR archive to avoid duplicating DS-04 train split.",
    ),
    PublicDataset(
        ds_id="DS-12",
        name="UCI Electricity Load Diagrams (MT_001)",
        source_url="https://archive.ics.uci.edu/static/public/321/electricityloaddiagrams20112014.zip",
        license_name="CC BY 4.0 (UCI repository terms)",
        raw_filename="electricityloaddiagrams20112014.zip",
        sample_rate_hz=1.0 / 900.0,
        extractor=_extract_electricity_load,
        notes="Extracted the first public smart-meter channel (MT_001) from the UCI electricity load archive.",
    ),
]

BLOCKED_DATASETS = {
    "DS-11": {
        "status": "BLOCKED",
        "name": "SMAP Telemetry (P-1)",
        "provenance_class": "real_public",
        "source_url": "https://raw.githubusercontent.com/khundman/telemanom/master/data/train/P-1.npy",
        "license": "Telemanom / NASA anomaly dataset (current upstream access now requires credentialed mirror)",
        "notes": (
            "Requested SMAP P-1 telemetry channel from the Telemanom corpus."
        ),
        "blocked_reason": (
            "2026-03-21 verification found the raw GitHub path returns 404, the historical S3 bundle returns 403, "
            "and the upstream telemanom README now directs users to a Kaggle download; the named no-login source is not currently viable."
        ),
    },
}


def _build_public_dataset(spec: PublicDataset, force: bool) -> tuple[dict, bool]:
    raw_path = RAW_DIR / spec.ds_id / spec.raw_filename
    downloaded = False
    if force or not raw_path.exists():
        _download(spec.source_url, raw_path)
        downloaded = True

    samples = spec.extractor(raw_path)
    samples, sample_rate_hz, resize_notes = _normalise_samples(samples, spec.sample_rate_hz)
    out_npz = _save_dataset(spec.ds_id, spec.name, samples, sample_rate_hz, provenance="real_public")

    note = spec.notes
    if resize_notes:
        note = note + " " + " ".join(resize_notes) + "."

    entry = {
        "status": "READY",
        "name": spec.name,
        "provenance_class": "real_public",
        "source_url": spec.source_url,
        "license": spec.license_name,
        "retrieval_date_utc": _iso_utc_from_mtime(raw_path),
        "raw_artifact": str(raw_path.relative_to(ROOT)),
        "raw_sha256": _sha256(raw_path),
        "transform_sha256": _sha256(out_npz),
        "notes": note,
    }
    return entry, downloaded


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--force",
        nargs="*",
        default=None,
        help="Regenerate selected dataset IDs (or all when provided without IDs).",
    )
    args = parser.parse_args()

    DATASET_DIR.mkdir(parents=True, exist_ok=True)
    RAW_DIR.mkdir(parents=True, exist_ok=True)

    force_all = args.force == []
    force_set = set(args.force or [])

    manifest: dict[str, dict] = {}

    for spec in PUBLIC_DATASETS:
        should_force = force_all or spec.ds_id in force_set
        entry, downloaded = _build_public_dataset(spec, force=should_force)
        manifest[spec.ds_id] = entry
        action = "DOWNLOADED" if downloaded else "REUSED"
        print(f"[{action}] {spec.ds_id} -> {spec.name}")

    for ds_id, info in BLOCKED_DATASETS.items():
        manifest[ds_id] = dict(info)
        print(f"[BLOCKED] {ds_id} -> {info['name']}")

    (DATASET_DIR / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")

    readme = DATASET_DIR / "README.md"
    readme.write_text(
        "# Dataset Provenance\n\n"
        "DS-01..DS-10 and DS-12 are sourced from real public datasets (E1).\n"
        "DS-11 is explicitly blocked because the named no-login Telemanom source is no longer directly accessible.\n"
        "Raw artifacts are stored under `validation/datasets/raw/DS-XX/` and transformed into standard `data.npz` files.\n\n"
        "Manifest policy:\n"
        "- `validation/datasets/manifest.json` records provenance class, source URL, license, retrieval timestamp, and SHA256 hashes.\n"
        "- For READY datasets, provenance is considered valid only when `verify_provenance.py` succeeds.\n"
        "- If an upstream dataset becomes unavailable, mark `status=BLOCKED` explicitly rather than silently promoting PASS claims.\n\n"
        "Credential policy:\n"
        "- `HF_TOKEN`: optional for public Hugging Face pulls; required for private/gated assets.\n"
        "- `GH_TOKEN`: optional for low-volume public fetch; required/recommended for API-heavy or private GitHub access.\n"
        "- Kaggle auth: `KAGGLE_API_TOKEN` supported, with legacy compatibility via `KAGGLE_USERNAME` + `KAGGLE_KEY`.\n"
        "- Current READY sources are public-first and run tokenless by default; auth failures emit explicit remediation hints.\n"
    )

    print("Dataset manifest written to validation/datasets/manifest.json")


if __name__ == "__main__":
    main()
