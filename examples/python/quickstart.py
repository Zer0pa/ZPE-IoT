"""ZPE-IoT Quick Start — compress sensor data in 10 lines."""

import numpy as np
import zpe_iot

# Simulate vibration sensor data (1 second at 1000 Hz)
t = np.linspace(0, 1, 1000)
signal = np.sin(2 * np.pi * 50 * t) + 0.3 * np.sin(2 * np.pi * 120 * t)

# Compress
compressed = zpe_iot.encode(signal, preset="vibration")
print(f"Compression ratio: {compressed.compression_ratio:.1f}x")
print(f"Original: {signal.nbytes} bytes → Compressed: {compressed.packed_size} bytes")

# Decompress
restored = zpe_iot.decode(compressed)
nrmse = zpe_iot.compute_nrmse(signal, restored)
print(f"Reconstruction error (NRMSE): {nrmse:.2%}")
