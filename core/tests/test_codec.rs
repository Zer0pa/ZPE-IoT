use zpe_iot::{decode_into, encode, Config, Mode, Preset};

fn nrmse(a: &[f64], b: &[f64]) -> f64 {
    let n = a.len().min(b.len());
    if n == 0 {
        return 0.0;
    }
    let mut mse = 0.0;
    let mut min_v = f64::INFINITY;
    let mut max_v = f64::NEG_INFINITY;
    for i in 0..n {
        let d = a[i] - b[i];
        mse += d * d;
        min_v = min_v.min(a[i]);
        max_v = max_v.max(a[i]);
    }
    mse /= n as f64;
    let range = (max_v - min_v).max(1e-9);
    mse.sqrt() / range
}

#[test]
fn deterministic_encoding() {
    let mut x = [0.0f64; 256];
    for i in 0..256 {
        x[i] = ((i as f64) * 0.03).sin() + 0.1 * ((i as f64) * 0.33).cos();
    }

    let cfg = Preset::Vibration.config();
    let a = encode::<1024>(&x, &cfg).unwrap();
    let b = encode::<1024>(&x, &cfg).unwrap();
    assert_eq!(a.rle_tokens.as_slice(), b.rle_tokens.as_slice());
}

#[test]
fn balanced_roundtrip_quality() {
    let mut x = [0.0f64; 512];
    for i in 0..512 {
        x[i] = ((i as f64) * 0.02).sin() + 0.2 * ((i as f64) * 0.08).sin();
    }
    let mut cfg = Config { ..Preset::Accelerometer.config() };
    cfg.mode = Mode::Balanced;

    let enc = encode::<2048>(&x, &cfg).unwrap();
    let mut out = [0.0f64; 512];
    let n = decode_into(&enc, &mut out).unwrap();
    assert_eq!(n, x.len());
    assert!(nrmse(&x, &out) < 0.2);
}
