# How to build ZMQ Libs:
# libzmq.lib, libzmq-d.lib, libzmq_64.lib, libzmq-d_64.lib, etc.
#
# git clone --branch v4.3.4 --depth 1 https://github.com/zeromq/libzmq.git
#
# mkdir libzmq\build32
# cmake -DCMAKE_BUILD_TYPE=Release -A Win32 -S libzmq -B "libzmq\build32" -DBUILD_TESTS=NO -DZMQ_BUILD_TESTS=NO -DENABLE_CURVE=NO -DWITH_TLS=NO
# cmake --build libzmq\build32 --config Debug
# cmake --build libzmq\build32 --config Release
#
# mkdir libzmq\build64
# cmake -DCMAKE_BUILD_TYPE=Release -A x64 -S libzmq -B "libzmq\build64" -DBUILD_TESTS=NO -DZMQ_BUILD_TESTS=NO -DENABLE_CURVE=NO -DWITH_TLS=NO
# cmake --build libzmq\build64 --config Debug
# cmake --build libzmq\build64 --config Release
#
# Libs and Dlls can be found in libzmq\build64\bin\<build_type> and libzmq\build64\lib\<build_type> etc.
#
# Copy and rename dlls:
# "C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Auxiliary\Build\vcvars32.bat"
# python ..\..\..\tools\rename_dll.py .\libzmq-v143-mt-4_3_4.dll libzmq.dll x86
# python ..\..\..\tools\rename_dll.py .\libzmq-v143-mt-gd-4_3_4.dll libzmq-d.dll x86
#
# "C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Auxiliary\Build\vcvars64.bat"
# python ..\..\..\tools\rename_dll.py .\libzmq-v143-mt-4_3_4.dll libzmq_64.dll x64
# python ..\..\..\tools\rename_dll.py .\libzmq-v143-mt-gd-4_3_4.dll libzmq-d_64.dll x64
#
# Also, if you're updating the libs, you should update cppzmq (zmq.hpp and zmq_addon.hpp)
# https://github.com/zeromq/cppzmq
#
# TEST AND MAKE SURE THAT EVERYTHING STILL WORKS!

find_library(ZeroMQ_LIBRARY 
    NAMES 
        "zmq${lib_debug}" "zmq${lib_debug}_64" "libzmq${lib_debug}" "libzmq${lib_debug}_64" "zmq" "libzmq" "zmq5" "libzmq5"
    PATHS
        ${PROJECT_SOURCE_DIR}/ext/zmq/${libpath}
        /usr/lib/x86_64-linux-gnu/
        /usr/lib/
        /usr/local/lib/
        /opt/lib/)

# If not found in standard locations, try versioned libraries
if(NOT ZeroMQ_LIBRARY)
    find_library(ZeroMQ_LIBRARY 
        NAMES 
            "libzmq.so.5" "libzmq.so.4" "libzmq.so.3"
        PATHS
            /usr/lib/x86_64-linux-gnu/
            /usr/lib/
            /usr/local/lib/
            /opt/lib/)
endif()

# For system installations, check both internal and system paths
find_path(ZeroMQ_INCLUDE_DIR
    NAMES zmq.h
    PATHS
        ${PROJECT_SOURCE_DIR}/ext/zmq/include/zmq/
        ${PROJECT_SOURCE_DIR}/ext/zmq/include/
        /usr/include/
        /usr/local/include/
        /opt/include/)

# If we found zmq.h in a zmq/ subdirectory, we need the parent for #include <zmq.hpp>
if(ZeroMQ_INCLUDE_DIR MATCHES "zmq$")
    get_filename_component(ZeroMQ_INCLUDE_DIR "${ZeroMQ_INCLUDE_DIR}/.." ABSOLUTE)
endif()

include(FindPackageHandleStandardArgs)
find_package_handle_standard_args(ZeroMQ DEFAULT_MSG ZeroMQ_LIBRARY ZeroMQ_INCLUDE_DIR)

message(STATUS "ZeroMQ_FOUND: ${ZeroMQ_FOUND}")
message(STATUS "ZeroMQ_LIBRARY: ${ZeroMQ_LIBRARY}")
message(STATUS "ZeroMQ_INCLUDE_DIR: ${ZeroMQ_INCLUDE_DIR}")

if (${ZeroMQ_FOUND})
    link_libraries(${ZeroMQ_LIBRARY})
    include_directories(SYSTEM ${ZeroMQ_INCLUDE_DIR})
    # Also include the zmq subdirectory for direct access to zmq/* headers
    include_directories(SYSTEM ${ZeroMQ_INCLUDE_DIR}/zmq)
endif()
