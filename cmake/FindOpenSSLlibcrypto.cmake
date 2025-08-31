find_library(OpenSSLlibcrypto_LIBRARY
    NAMES
        crypto crypto_64 libcrypto libcrypto_64
    PATHS
        ${PROJECT_SOURCE_DIR}/ext/openssl/${libpath}
        /usr/lib/x86_64-linux-gnu/
        /usr/lib/
        /usr/local/lib/
        /usr/local/opt/openssl/lib/		 # OSX brew install location
        /opt/lib/)

# For system installations, check both internal and system paths
find_path(OpenSSLlibcrypto_INCLUDE_DIR
    NAMES openssl/crypto.h
    PATHS
        ${PROJECT_SOURCE_DIR}/ext/openssl/include/
        /usr/include/
        /usr/local/include/
        /usr/local/opt/openssl/include/
        /opt/include/)

include(FindPackageHandleStandardArgs)
find_package_handle_standard_args(OpenSSLlibcrypto DEFAULT_MSG OpenSSLlibcrypto_LIBRARY OpenSSLlibcrypto_INCLUDE_DIR)

message(STATUS "OpenSSLlibcrypto_FOUND: ${OpenSSLlibcrypto_FOUND}")
message(STATUS "OpenSSLlibcrypto_LIBRARY: ${OpenSSLlibcrypto_LIBRARY}")
message(STATUS "OpenSSLlibcrypto_INCLUDE_DIR: ${OpenSSLlibcrypto_INCLUDE_DIR}")

# TODO: Don't do this globally
if (${OpenSSLlibcrypto_FOUND})
    link_libraries(${OpenSSLlibcrypto_LIBRARY})
    include_directories(SYSTEM ${OpenSSLlibcrypto_INCLUDE_DIR})
    include_directories(SYSTEM ${OpenSSLlibcrypto_INCLUDE_DIR}/../)
endif()
