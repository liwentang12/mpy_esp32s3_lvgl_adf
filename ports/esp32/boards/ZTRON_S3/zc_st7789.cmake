# We (ab)use MicroPython's submodule system to include our dependencies in the sync
string(CONCAT GIT_SUBMODULES "${GIT_SUBMODULES} " ztron/st7789_mpy)

# Inject the driver as a user module
list(APPEND USER_C_MODULES
    ../../../ztron/st7789_mpy/st7789/micropython.cmake
)
