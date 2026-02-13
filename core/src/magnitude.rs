pub const LOG_BASE: f64 = 1.091_928;
pub const LOG_MAG_TABLE_SIZE: usize = 64;
pub const LOG_MAG_TABLE: [u16; LOG_MAG_TABLE_SIZE] = [
    1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 2, 3, 3, 3, 3, 4, 4, 4, 5, 5, 6, 6, 7, 8, 8, 9, 10, 11, 12,
    13, 14, 15, 17, 18, 20, 22, 24, 26, 28, 31, 34, 37, 40, 44, 48, 52, 57, 62, 68, 74, 81, 89,
    97, 106, 115, 126, 138, 150, 164, 179, 196, 214, 233, 255,
];

#[inline]
pub fn magnitude_value(index: u8) -> f64 {
    LOG_MAG_TABLE[index as usize] as f64
}

pub fn find_magnitude(abs_delta: f64, step: f64) -> u8 {
    if abs_delta <= 0.0 || step <= 0.0 {
        return 0;
    }
    let target = abs_delta / step;

    let mut best_idx = 0usize;
    let mut min_err = (LOG_MAG_TABLE[0] as f64 - target).abs();
    let mut i = 1usize;
    while i < LOG_MAG_TABLE_SIZE {
        let err = (LOG_MAG_TABLE[i] as f64 - target).abs();
        if err < min_err {
            min_err = err;
            best_idx = i;
        }
        i += 1;
    }
    best_idx as u8
}

#[cfg(test)]
mod tests {
    use super::{find_magnitude, LOG_MAG_TABLE, LOG_MAG_TABLE_SIZE};

    #[test]
    fn table_matches_formula() {
        let mut i = 0usize;
        while i < LOG_MAG_TABLE_SIZE {
            let expected = (1.091_928_f64.powi(i as i32)).round() as u16;
            assert_eq!(LOG_MAG_TABLE[i], expected, "index={i}");
            i += 1;
        }
    }

    #[test]
    fn find_magnitude_stable() {
        assert_eq!(find_magnitude(0.0, 0.01), 0);
        assert!(find_magnitude(1.0, 0.01) > 0);
    }
}
