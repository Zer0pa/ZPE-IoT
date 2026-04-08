from __future__ import annotations

import subprocess
import sys
from pathlib import Path
import venv


REPO_ROOT = Path(__file__).resolve().parents[2]
PYTHON_DIR = REPO_ROOT / "python"


def _venv_python(venv_dir: Path) -> Path:
    if sys.platform == "win32":
        return venv_dir / "Scripts" / "python.exe"
    return venv_dir / "bin" / "python"


def test_clean_install_from_built_wheel(tmp_path: Path) -> None:
    dist_dir = tmp_path / "dist"
    subprocess.run(
        [sys.executable, "-m", "build", "--wheel", "--outdir", str(dist_dir)],
        cwd=PYTHON_DIR,
        check=True,
    )
    wheel = next(dist_dir.glob("zpe_iot-*.whl"))

    venv_dir = tmp_path / "clean-venv"
    venv.EnvBuilder(with_pip=True).create(venv_dir)
    clean_python = _venv_python(venv_dir)

    subprocess.run([str(clean_python), "-m", "pip", "install", str(wheel)], check=True)
    smoke = subprocess.run(
        [
            str(clean_python),
            "-c",
            (
                "import numpy as np; "
                "import zpe_iot; "
                "packet = zpe_iot.encode(np.array([1.0, 1.1, 1.2, 1.3]), preset='generic').to_bytes(); "
                "print(len(packet))"
            ),
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    assert smoke.stdout.strip().isdigit()
