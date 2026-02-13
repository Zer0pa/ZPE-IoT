pub const DIRECTION_DELTAS: [f64; 8] = [
    0.0,   // flat
    1.0,   // rise gentle
    2.0,   // rise moderate
    4.0,   // rise steep
    8.0,   // rise extreme
    -8.0,  // fall extreme
    -2.0,  // fall moderate
    -1.0,  // fall gentle
];

pub trait Quantiser {
    fn quantise(&self, delta: f64, threshold: f64) -> u8;
}

#[derive(Clone, Copy, Debug)]
pub struct DefaultQuantiser {
    pub bands: [f64; 3],
}

impl Default for DefaultQuantiser {
    fn default() -> Self {
        Self {
            bands: [1.0, 4.0, 16.0],
        }
    }
}

impl Quantiser for DefaultQuantiser {
    fn quantise(&self, delta: f64, threshold: f64) -> u8 {
        let abs_delta = delta.abs();
        if abs_delta < threshold {
            return 0;
        }

        // Preset bands are stored as [1,4,16]-style factors; expand to true boundaries
        // for [1x..4x), [4x..16x), [16x..64x), [64x+).
        let gentle = self.bands[0].max(1.0) * 4.0;
        let moderate = self.bands[1].max(gentle) * 4.0;
        let steep = self.bands[2].max(self.bands[1]).max(gentle) * 4.0;

        if delta > 0.0 {
            if abs_delta < gentle * threshold {
                1
            } else if abs_delta < moderate * threshold {
                2
            } else if abs_delta < steep * threshold {
                3
            } else {
                4
            }
        } else if abs_delta < gentle * threshold {
            7
        } else if abs_delta < steep * threshold {
            6
        } else {
            5
        }
    }
}

#[inline]
pub fn direction_sign(direction: u8) -> f64 {
    match direction {
        1..=4 => 1.0,
        5..=7 => -1.0,
        _ => 0.0,
    }
}

#[cfg(test)]
mod tests {
    use super::{DefaultQuantiser, Quantiser};

    #[test]
    fn quantiser_covers_all_codes() {
        let q = DefaultQuantiser::default();
        assert_eq!(q.quantise(0.0, 1.0), 0);
        assert_eq!(q.quantise(0.5, 1.0), 0);
        assert_eq!(q.quantise(1.1, 1.0), 1);
        assert_eq!(q.quantise(5.0, 1.0), 2);
        assert_eq!(q.quantise(20.0, 1.0), 3);
        assert_eq!(q.quantise(80.0, 1.0), 4);
        assert_eq!(q.quantise(-0.9, 1.0), 0);
        assert_eq!(q.quantise(-1.01, 1.0), 7);
        assert_eq!(q.quantise(-8.0, 1.0), 6);
        assert_eq!(q.quantise(-80.0, 1.0), 5);
    }

    #[test]
    fn boundaries_are_deterministic() {
        let q = DefaultQuantiser::default();
        // exact boundaries fall into the higher band by design (< comparison)
        assert_eq!(q.quantise(1.0, 1.0), 1);
        assert_eq!(q.quantise(4.0, 1.0), 2);
        assert_eq!(q.quantise(16.0, 1.0), 3);
        assert_eq!(q.quantise(64.0, 1.0), 4);
        assert_eq!(q.quantise(-1.0, 1.0), 7);
        assert_eq!(q.quantise(-4.0, 1.0), 6);
        assert_eq!(q.quantise(-64.0, 1.0), 5);
    }
}
