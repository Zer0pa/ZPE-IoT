# zpe-iot Python Package

`zpe-iot` provides deterministic sensor compression for IoT time-series.

## Install

```bash
python -m pip install -e ".[dev]"
```

Built wheels bundle the Rust native extension on supported targets. If the native
module is unavailable, the installed package falls back to the pure-Python codec.

## CLI

```bash
zpe-iot --help
zpe-iot compress input.csv --preset vibration --output out.zpk
zpe-iot info out.zpk
zpe-iot decompress out.zpk --output restored.csv
zpe-iot benchmark input.csv --compare zstd,lz4,zlib
zpe-iot chemosense-smoke --json
```

## API

```python
import numpy as np
import zpe_iot

samples = np.sin(np.linspace(0, 20, 1024))
stream = zpe_iot.encode(samples, preset="vibration")
packet = stream.to_bytes()
restored = zpe_iot.decode(packet)
```

## Chemosense API

```python
from zpe_iot.chemosense import smell, taste

smell_words = smell.encode_smell_strokes([smell.synthetic_sniff_stroke(smell.OdorCategory.FLORAL)])
taste_words = taste.pack_taste_zlayered([taste.zlayered_event_from_vector((7, 1, 1, 0, 3))], adaptive=True)
```
