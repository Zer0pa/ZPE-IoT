use heapless::Vec;

pub fn compress<const N: usize>(tokens: &[(u8, u8)]) -> Vec<(u8, u8, u16), N> {
    let mut result = Vec::new();
    if tokens.is_empty() {
        return result;
    }

    let mut curr_d = tokens[0].0;
    let mut curr_m = tokens[0].1;
    let mut curr_count = 1u16;

    for &(d, m) in &tokens[1..] {
        if d == curr_d && m == curr_m {
            if curr_count == u16::MAX {
                let _ = result.push((curr_d, curr_m, curr_count));
                curr_count = 1;
            } else {
                curr_count += 1;
            }
        } else {
            let _ = result.push((curr_d, curr_m, curr_count));
            curr_d = d;
            curr_m = m;
            curr_count = 1;
        }
    }
    let _ = result.push((curr_d, curr_m, curr_count));
    result
}

pub fn decompress(rle: &[(u8, u8, u16)], output: &mut [(u8, u8)]) -> usize {
    let mut out = 0usize;
    for &(d, m, count) in rle {
        let mut i = 0u16;
        while i < count {
            if out >= output.len() {
                return out;
            }
            output[out] = (d, m);
            out += 1;
            i += 1;
        }
    }
    out
}

#[cfg(test)]
mod tests {
    use super::{compress, decompress};

    #[test]
    fn rle_round_trip() {
        let input = [(1, 2), (1, 2), (3, 4), (3, 4), (3, 4), (0, 0)];
        let r = compress::<16>(&input);
        let mut out = [(0u8, 0u8); 16];
        let n = decompress(&r, &mut out);
        assert_eq!(&out[..n], &input);
    }
}
