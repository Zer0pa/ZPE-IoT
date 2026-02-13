#![no_std]
#![no_main]

use cortex_m_rt::entry;
use zpe_iot::{encode, Preset};

#[entry]
fn main() -> ! {
    let mut samples = [0.0f64; 256];
    let mut i = 0usize;
    while i < samples.len() {
        samples[i] = (i as f64) * 0.001;
        i += 1;
    }

    let _encoded = encode::<1024>(&samples, &Preset::Accelerometer.config());

    loop {}
}
