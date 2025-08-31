find_library(BINUTILS_LIBRARY
    NAMES
        libbfd bfd libbfd-2.42-system
    PATHS
        /usr/lib/x86_64-linux-gnu/
        /usr/lib/
        /usr/local/lib/
        /opt/lib/)

include(FindPackageHandleStandardArgs)
find_package_handle_standard_args(Binutils DEFAULT_MSG BINUTILS_LIBRARY)

message(STATUS "Binutils_FOUND: ${BINUTILS_FOUND}")
message(STATUS "Binutils_LIBRARY: ${BINUTILS_LIBRARY}")

