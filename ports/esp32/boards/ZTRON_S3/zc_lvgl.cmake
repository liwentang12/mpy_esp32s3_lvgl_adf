# We (ab)use MicroPython's submodule system to include our dependencies in the sync
string(CONCAT GIT_SUBMODULES "${GIT_SUBMODULES} " ztron/lvgl_esp32_mpy)

# Inject the driver as a user module
list(APPEND USER_C_MODULES
    ../../../ztron/lvgl_esp32_mpy/micropython.cmake
)
