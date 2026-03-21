use crate::codec::{Config, Mode};

#[derive(Clone, Copy, Debug)]
pub enum Preset {
    Temperature,
    Vibration,
    Accelerometer,
    Pressure,
    GpsTrack,
    Voltage,
    Current,
    Flow,
    Generic,
}

impl Preset {
    pub fn id(&self) -> u8 {
        match self {
            Preset::Temperature => 0,
            Preset::Vibration => 1,
            Preset::Accelerometer => 2,
            Preset::Pressure => 3,
            Preset::GpsTrack => 4,
            Preset::Voltage => 5,
            Preset::Current => 6,
            Preset::Flow => 7,
            Preset::Generic => 8,
        }
    }

    pub fn name(&self) -> &'static str {
        match self {
            Preset::Temperature => "temperature",
            Preset::Vibration => "vibration",
            Preset::Accelerometer => "accelerometer",
            Preset::Pressure => "pressure",
            Preset::GpsTrack => "gps_track",
            Preset::Voltage => "voltage",
            Preset::Current => "current",
            Preset::Flow => "flow",
            Preset::Generic => "generic",
        }
    }

    pub fn config(&self) -> Config {
        let mut cfg = Config {
            preset_id: self.id(),
            ..Config::default()
        };

        match self {
            Preset::Temperature => {
                cfg.mode = Mode::Balanced;
                cfg.threshold = 0.05;
                cfg.step = 0.0;
                cfg.bands = [1.0, 2.0, 4.0];
            }
            Preset::Vibration => {
                cfg.mode = Mode::Balanced;
                cfg.threshold = 0.02;
                cfg.step = 0.01;
                cfg.bands = [1.0, 4.0, 16.0];
            }
            Preset::Accelerometer => {
                cfg.mode = Mode::Balanced;
                cfg.threshold = 0.03;
                cfg.step = 0.01;
                cfg.bands = [1.0, 4.0, 16.0];
            }
            Preset::Pressure => {
                cfg.mode = Mode::Balanced;
                cfg.threshold = 0.01;
                cfg.step = 0.1;
                cfg.bands = [1.0, 2.0, 8.0];
            }
            Preset::GpsTrack => {
                cfg.mode = Mode::Balanced;
                cfg.threshold = 0.001;
                cfg.step = 0.0;
                cfg.bands = [1.0, 4.0, 16.0];
            }
            Preset::Voltage => {
                cfg.mode = Mode::Balanced;
                cfg.threshold = 0.02;
                cfg.step = 0.01;
                cfg.bands = [1.0, 4.0, 16.0];
            }
            Preset::Current => {
                cfg.mode = Mode::Balanced;
                cfg.threshold = 0.02;
                cfg.step = 0.01;
                cfg.bands = [1.0, 4.0, 16.0];
            }
            Preset::Flow => {
                cfg.mode = Mode::Balanced;
                cfg.threshold = 0.05;
                cfg.step = 0.0;
                cfg.bands = [1.0, 2.0, 8.0];
            }
            Preset::Generic => {
                cfg.mode = Mode::Balanced;
                cfg.threshold = 0.05;
                cfg.step = 0.0;
                cfg.bands = [1.0, 4.0, 16.0];
            }
        }

        cfg
    }

    pub fn from_name(name: &str) -> Option<Self> {
        if name.eq_ignore_ascii_case("temperature") {
            Some(Self::Temperature)
        } else if name.eq_ignore_ascii_case("vibration") {
            Some(Self::Vibration)
        } else if name.eq_ignore_ascii_case("accelerometer") {
            Some(Self::Accelerometer)
        } else if name.eq_ignore_ascii_case("pressure") {
            Some(Self::Pressure)
        } else if name.eq_ignore_ascii_case("gps_track") || name.eq_ignore_ascii_case("gps") {
            Some(Self::GpsTrack)
        } else if name.eq_ignore_ascii_case("voltage") {
            Some(Self::Voltage)
        } else if name.eq_ignore_ascii_case("current") {
            Some(Self::Current)
        } else if name.eq_ignore_ascii_case("flow") {
            Some(Self::Flow)
        } else if name.eq_ignore_ascii_case("generic") {
            Some(Self::Generic)
        } else {
            None
        }
    }
}

#[cfg(test)]
mod tests {
    use super::Preset;
    use crate::codec::Mode;

    #[test]
    fn ratified_temperature_preset_matches_canonical_values() {
        let cfg = Preset::Temperature.config();
        assert_eq!(cfg.mode, Mode::Balanced);
        assert_eq!(cfg.threshold, 0.05);
        assert_eq!(cfg.step, 0.0);
        assert_eq!(cfg.bands, [1.0, 2.0, 4.0]);
    }

    #[test]
    fn ratified_gps_preset_matches_canonical_values() {
        let cfg = Preset::GpsTrack.config();
        assert_eq!(cfg.mode, Mode::Balanced);
        assert_eq!(cfg.threshold, 0.001);
        assert_eq!(cfg.step, 0.0);
        assert_eq!(cfg.bands, [1.0, 4.0, 16.0]);
    }

    #[test]
    fn ratified_flow_preset_matches_canonical_values() {
        let cfg = Preset::Flow.config();
        assert_eq!(cfg.mode, Mode::Balanced);
        assert_eq!(cfg.threshold, 0.05);
        assert_eq!(cfg.step, 0.0);
        assert_eq!(cfg.bands, [1.0, 2.0, 8.0]);
    }
}
