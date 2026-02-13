#ifndef ZPE_IOT_H
#define ZPE_IOT_H
#include <stdint.h>
#include <stddef.h>

typedef struct {
  uint8_t mode;
  double threshold;
  double step;
  double bands0;
  double bands1;
  double bands2;
  uint8_t adaptive;
  double thr_min;
  double thr_max;
  double alpha;
  double k;
  uint8_t preset_id;
} zpe_iot_config_t;

int32_t zpe_iot_encode(const double* samples, size_t n_samples,
                       const zpe_iot_config_t* config,
                       uint8_t* out_bytes, size_t out_capacity);
int32_t zpe_iot_decode(const uint8_t* packed, size_t packed_len,
                       double* out_samples, size_t out_capacity);
float zpe_iot_compression_ratio(size_t packed_size, size_t sample_count);

zpe_iot_config_t zpe_iot_preset_temperature(void);
zpe_iot_config_t zpe_iot_preset_vibration(void);
zpe_iot_config_t zpe_iot_preset_accelerometer(void);
zpe_iot_config_t zpe_iot_preset_pressure(void);
zpe_iot_config_t zpe_iot_preset_gps_track(void);
zpe_iot_config_t zpe_iot_preset_voltage(void);
zpe_iot_config_t zpe_iot_preset_current(void);
zpe_iot_config_t zpe_iot_preset_flow(void);
zpe_iot_config_t zpe_iot_preset_generic(void);

#endif
