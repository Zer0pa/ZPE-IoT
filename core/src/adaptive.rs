#[inline]
pub fn update_envelope(envelope: f64, abs_delta: f64, alpha: f64) -> f64 {
    (alpha * envelope).max(abs_delta)
}

#[inline]
pub fn compute_threshold(envelope: f64, k: f64, thr_min: f64, thr_max: f64) -> f64 {
    (k * envelope).clamp(thr_min, thr_max)
}

#[cfg(test)]
mod tests {
    use super::{compute_threshold, update_envelope};

    #[test]
    fn adaptive_tracks_bounds() {
        let mut env = 0.0;
        for i in 0..10_000 {
            let x = ((i as f64) * 0.01).sin().abs();
            env = update_envelope(env, x, 0.95);
            let thr = compute_threshold(env, 0.15, 0.001, 1.0);
            assert!((0.001..=1.0).contains(&thr));
        }
    }
}
