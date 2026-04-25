use zpe_iot::codec::CodecError;
use zpe_iot::{decode_into, encode, Mode, Preset};

#[test]
fn encode_empty_input_rejects() {
    let cfg = Preset::Generic.config();
    let x: [f64; 0] = [];
    let err = encode::<16>(&x, &cfg).unwrap_err();
    assert_eq!(err, CodecError::EmptyInput);
}

#[test]
fn decode_into_truncates_to_output_capacity() {
    let mut x = [0.0_f64; 256];
    for (i, value) in x.iter_mut().enumerate() {
        *value = ((i as f64) * 0.04).sin();
    }

    let cfg = Preset::Vibration.config();
    let stream = encode::<1024>(&x, &cfg).unwrap();

    let mut short = [0.0_f64; 64];
    let n = decode_into(&stream, &mut short).unwrap();
    assert_eq!(n, short.len());
    assert!(short.iter().all(|v| v.is_finite()));
}

#[test]
fn fast_mode_roundtrip_is_finite() {
    let mut x = [0.0_f64; 512];
    for (i, value) in x.iter_mut().enumerate() {
        *value = ((i as f64) * 0.01).sin() + 0.25 * ((i as f64) * 0.07).cos();
    }

    let mut cfg = Preset::Generic.config();
    cfg.mode = Mode::Fast;
    let stream = encode::<2048>(&x, &cfg).unwrap();

    let mut out = [0.0_f64; 512];
    let n = decode_into(&stream, &mut out).unwrap();
    assert_eq!(n, x.len());
    assert!(out.iter().all(|v| v.is_finite()));
}
