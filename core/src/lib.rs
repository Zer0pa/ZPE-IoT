#![cfg_attr(feature = "embedded", no_std)]

pub mod adaptive;
pub mod bitpack;
pub mod codec;
pub mod ffi;
pub mod magnitude;
pub mod presets;
pub mod quantise;
pub mod rle;

pub use bitpack::{pack, unpack};
pub use codec::{decode_into, encode, Config, EncodedStream, Mode};
pub use presets::Preset;

#[cfg(all(feature = "embedded", not(test)))]
#[panic_handler]
fn panic(_info: &core::panic::PanicInfo) -> ! {
    loop {}
}
