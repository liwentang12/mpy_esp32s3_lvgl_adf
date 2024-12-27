# We (ab)use MicroPython's submodule system to include our dependencies in the sync
string(CONCAT GIT_SUBMODULES "${GIT_SUBMODULES} " ztron/micropython_adf/mod)

# Inject the driver as a user module
list(APPEND USER_C_MODULES
    ../../../ztron/adf/micropython_adf/mod/micropython.cmake
)
