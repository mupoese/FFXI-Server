find_library(OpenSSLlibssl_LIBRARY
    NAMES
        ssl ssl_64 libssl libssl_64
    PATHS
        ${PROJECT_SOURCE_DIR}/ext/openssl/${libpath}
        /usr/lib/x86_64-linux-gnu/
        /usr/lib/
        /usr/local/lib/
        /usr/local/opt/openssl/lib/ # OSX brew install location
        /opt/lib/)

# For system installations, check both internal and system paths
find_path(OpenSSLlibssl_INCLUDE_DIR
    NAMES openssl/ssl.h
    PATHS
        ${PROJECT_SOURCE_DIR}/ext/openssl/include/
        /usr/include/
        /usr/local/include/
        /usr/local/opt/openssl/include/
        /opt/include/)

include(FindPackageHandleStandardArgs)
find_package_handle_standard_args(OpenSSLlibssl DEFAULT_MSG OpenSSLlibssl_LIBRARY OpenSSLlibssl_INCLUDE_DIR)

message(STATUS "OpenSSLlibssl_FOUND: ${OpenSSLlibssl_FOUND}")
message(STATUS "OpenSSLlibssl_LIBRARY: ${OpenSSLlibssl_LIBRARY}")
message(STATUS "OpenSSLlibssl_INCLUDE_DIR: ${OpenSSLlibssl_INCLUDE_DIR}")

# TODO: Don't do this globally
if (${OpenSSLlibssl_FOUND})
    link_libraries(${OpenSSLlibssl_LIBRARY})
    include_directories(SYSTEM ${OpenSSLlibssl_INCLUDE_DIR})
    include_directories(SYSTEM ${OpenSSLlibssl_INCLUDE_DIR}/../)
endif()
