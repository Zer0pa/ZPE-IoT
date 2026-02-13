use zpe_iot::{encode, Preset};

#[test]
fn token_stability_snapshot() {
    let mut x = [0.0f64; 128];
    for i in 0..128 {
        x[i] = ((i as f64) * 0.11).sin();
    }

    let cfg = Preset::Generic.config();
    let enc = encode::<512>(&x, &cfg).unwrap();
    assert!(!enc.rle_tokens.is_empty());
}
