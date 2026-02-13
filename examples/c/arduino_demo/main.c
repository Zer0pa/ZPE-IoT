#include <stdio.h>
#include <stdint.h>
#include "../../../c/zpe_iot.h"

int main(void) {
    double samples[256];
    for (int i = 0; i < 256; ++i) {
        samples[i] = (double)i * 0.01;
    }

    zpe_iot_config_t cfg = zpe_iot_preset_vibration();
    uint8_t packed[2048];
    int32_t n = zpe_iot_encode(samples, 256, &cfg, packed, sizeof(packed));
    if (n < 0) {
        printf("encode failed: %d\n", (int)n);
        return 1;
    }

    double out[256];
    int32_t m = zpe_iot_decode(packed, (size_t)n, out, 256);
    printf("packed=%d decoded=%d\n", (int)n, (int)m);
    return 0;
}
