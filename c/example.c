#include <stdio.h>
#include <stdint.h>
#include "zpe_iot.h"

int main(void) {
    double samples[16];
    for (int i = 0; i < 16; ++i) samples[i] = i * 0.1;

    zpe_iot_config_t cfg = zpe_iot_preset_generic();
    uint8_t out[512];
    int32_t packed = zpe_iot_encode(samples, 16, &cfg, out, sizeof(out));
    printf("packed=%d\n", (int)packed);
    return 0;
}
