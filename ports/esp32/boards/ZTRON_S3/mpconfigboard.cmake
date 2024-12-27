set(IDF_TARGET esp32s3)

set(SDKCONFIG_DEFAULTS
    boards/sdkconfig.base
    boards/sdkconfig.usb
    boards/sdkconfig.ble
    boards/sdkconfig.240mhz
    boards/sdkconfig.spiram_oct
    boards/ZTRON_S3/sdkconfig.board
)
#    boards/sdkconfig.spiram_sx
#    boards/ZTRON_S3/sdkconfig.partition


set(MICROPY_FROZEN_MANIFEST ${MICROPY_BOARD_DIR}/manifest.py)

include (${MICROPY_BOARD_DIR}/../ZTRON_S3/zc_lvgl.cmake)

#include (${MICROPY_BOARD_DIR}/../ZTRON_S3/zc_nvs.cmake)
#include (${MICROPY_BOARD_DIR}/../ZTRON_S3/zc_application.cmake)
