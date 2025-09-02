# Set a default build type if none was specified
if(NOT CMAKE_BUILD_TYPE)
  message(STATUS "Setting build type to 'RelWithDebInfo' as none was specified.")
  set(CMAKE_BUILD_TYPE
      "RelWithDebInfo"
      CACHE STRING "Choose the type of build." FORCE)
  # Set the possible values of build type for cmake-gui, ccmake
  set_property(
    CACHE CMAKE_BUILD_TYPE
    PROPERTY STRINGS
             "Debug"
             "Release"
             "MinSizeRel"
             "RelWithDebInfo")
endif()

option(ENABLE_IPO "Enable Interprocedural Optimization, aka Link Time Optimization (LTO)" ON)
set(CMAKE_INTERPROCEDURAL_OPTIMIZATION OFF)
if(ENABLE_IPO AND NOT CMAKE_BUILD_TYPE STREQUAL Debug)
  include(CheckIPOSupported)
  check_ipo_supported(
    RESULT
    result
    OUTPUT
    output)
  if(result)
    set(CMAKE_INTERPROCEDURAL_OPTIMIZATION ON)
  else()
    message(STATUS "IPO is not supported: ${output}")
  endif()
endif()
message(STATUS "CMAKE_INTERPROCEDURAL_OPTIMIZATION: ${CMAKE_INTERPROCEDURAL_OPTIMIZATION} (this implies /GL or -flto)")

# Snippet from GLM: https://github.com/g-truc/glm (MIT)
# NOTE: fast-math was on by default before the CMake build refactoring!
option(ENABLE_FAST_MATH "Enable fast math optimizations" ON)

# Disable fast math on macOS with Clang to avoid fmt library infinity issues
if(APPLE AND CMAKE_CXX_COMPILER_ID MATCHES "Clang")
    set(ENABLE_FAST_MATH OFF CACHE BOOL "Disabled on macOS Clang due to fmt library compatibility" FORCE)
    message(STATUS "ENABLE_FAST_MATH disabled on macOS with Clang to avoid fmt library issues")
endif()

if(ENABLE_FAST_MATH)
    message(STATUS "ENABLE_FAST_MATH: ON")
    if((CMAKE_CXX_COMPILER_ID MATCHES "Clang") OR (CMAKE_CXX_COMPILER_ID MATCHES "GNU"))
        add_compile_options(-ffast-math)
        # Additional floating point optimizations for non-MSVC compilers
        if(XI_TARGET_ARCH STREQUAL "x86_64")
            add_compile_options(-mfpmath=sse -msse2)
        endif()
    elseif(CMAKE_CXX_COMPILER_ID MATCHES "MSVC")
        add_compile_options(/fp:fast)
    endif()
else()
    message(STATUS "ENABLE_FAST_MATH: OFF")
    if(CMAKE_CXX_COMPILER_ID MATCHES "MSVC")
        add_compile_options(/fp:precise)
    endif()
endif()

# Cross-platform optimization settings
option(ENABLE_NATIVE_OPTIMIZATIONS "Enable native CPU optimizations" OFF)
if(ENABLE_NATIVE_OPTIMIZATIONS)
    message(STATUS "ENABLE_NATIVE_OPTIMIZATIONS: ON")
    if((CMAKE_CXX_COMPILER_ID MATCHES "Clang") OR (CMAKE_CXX_COMPILER_ID MATCHES "GNU"))
        if(XI_TARGET_ARCH STREQUAL "x86_64")
            add_compile_options(-march=native -mtune=native)
        elseif(XI_TARGET_ARCH STREQUAL "arm64")
            add_compile_options(-mcpu=native)
        endif()
    endif()
else()
    message(STATUS "ENABLE_NATIVE_OPTIMIZATIONS: OFF")
endif()

if(MSVC)
    list(APPEND FLAGS_AND_DEFINES
        -D_CONSOLE
        -D_MBCS
        -DNOMINMAX
        -D_CRT_SECURE_NO_WARNINGS
        -D_CRT_NONSTDC_NO_DEPRECATE
        # TODO: This is being overwritten by /Ob0
        # /Ob2 # Inline Function Expansion
        /Oy- # Frame-Pointer Omission
        /MP # Build with Multiple Processes
        /bigobj # Allow bigger .obj files, which we have from mainly the sol templating
        /utf-8 # Treat source files as UTF-8. This is needed because of certain symbols inside fmtlib's code. u-second, etc.
    )

    # Platform-specific MSVC optimizations
    if(XI_TARGET_ARCH STREQUAL "x86_64")
        list(APPEND FLAGS_AND_DEFINES /favor:INTEL64)
    endif()

    if(CMAKE_BUILD_TYPE STREQUAL Debug)
        # /EDITANDCONTINUE isn't supported, it messes with Tracy
        set(CMAKE_EXE_LINKER_FLAGS "${CMAKE_EXE_LINKER_FLAGS} /INCREMENTAL /SAFESEH:NO")
        list(APPEND FLAGS_AND_DEFINES
            /Zi # The /Zi option produces a separate PDB file that contains all the symbolic debugging information for use with the debugger.
            /GR # Enable RTTI
        )
    else()
        set(CMAKE_EXE_LINKER_FLAGS "${CMAKE_EXE_LINKER_FLAGS} /INCREMENTAL:NO /LTCG /OPT:REF /OPT:ICF")
        list(APPEND FLAGS_AND_DEFINES
            /Oi # Generate Intrinsic Functions
            /GL # Whole Program Optimization
            /Gy # Enable Function Level Linking
            /TP # C++ Source Files
        )
        
        # Additional release optimizations for x86_64
        if(XI_TARGET_ARCH STREQUAL "x86_64")
            list(APPEND FLAGS_AND_DEFINES /arch:AVX2)
        endif()
    endif()

    link_libraries(WS2_32 dbghelp Shlwapi)
endif()

# Unix/Linux specific optimizations
if(UNIX)
    link_libraries(dl)
    
    # Linux-specific optimizations
    if(CMAKE_SYSTEM_NAME STREQUAL "Linux")
        # Enable position independent code for better security
        set(CMAKE_POSITION_INDEPENDENT_CODE ON)
        
        # Link-time optimizations for release builds
        if(CMAKE_BUILD_TYPE STREQUAL "Release" AND CMAKE_CXX_COMPILER_ID MATCHES "GNU|Clang")
            add_link_options(-flto)
        endif()
    endif()
    
    # macOS-specific optimizations
    if(APPLE)
        # macOS deployment target should be set in Platform.cmake
        if(XI_TARGET_ARCH STREQUAL "arm64")
            # Apple Silicon optimizations
            add_compile_options(-mcpu=apple-m1)
        endif()
        
        # Universal binary support (if needed)
        option(BUILD_UNIVERSAL_BINARY "Build universal binary for macOS" OFF)
        if(BUILD_UNIVERSAL_BINARY)
            set(CMAKE_OSX_ARCHITECTURES "arm64;x86_64")
            message(STATUS "Building universal binary for macOS")
        endif()
    endif()
endif()

if("${CMAKE_CXX_COMPILER_ID}" STREQUAL "GNU")
    if (CMAKE_CXX_COMPILER_VERSION VERSION_LESS 9.0)
        message(FATAL_ERROR
                "GCC version must be at least 9.0! Detected: ${CMAKE_CXX_COMPILER_VERSION}")
    endif()
    
    # GCC-specific optimizations
    if(CMAKE_BUILD_TYPE STREQUAL "Release")
        add_compile_options(-O3)
        if(XI_TARGET_ARCH STREQUAL "x86_64")
            add_compile_options(-msse4.2 -mpopcnt)
        endif()
    endif()
endif()

# Clang-specific optimizations
if(CMAKE_CXX_COMPILER_ID MATCHES "Clang")
    if(CMAKE_BUILD_TYPE STREQUAL "Release")
        add_compile_options(-O3)
        if(XI_TARGET_ARCH STREQUAL "x86_64")
            add_compile_options(-msse4.2 -mpopcnt)
        endif()
    endif()
endif()

# TODO: These should be applied on a per-target level, not globally like this!
string(REPLACE ";" " " FLAGS_AND_DEFINES_STR "${FLAGS_AND_DEFINES}")
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} ${FLAGS_AND_DEFINES_STR}")

function(set_target_output_directory target)
    message(STATUS "Setting output directory for ${target} to ${CMAKE_SOURCE_DIR}")
    set_target_properties(${target} PROPERTIES
        VS_DEBUGGER_WORKING_DIRECTORY "${CMAKE_SOURCE_DIR}"
        RUNTIME_OUTPUT_DIRECTORY_DEBUG "${CMAKE_SOURCE_DIR}"
        RUNTIME_OUTPUT_DIRECTORY_RELEASE "${CMAKE_SOURCE_DIR}"
        RUNTIME_OUTPUT_DIRECTORY_RELWITHDEBINFO "${CMAKE_SOURCE_DIR}"
        RUNTIME_OUTPUT_DIRECTORY_MINSIZEREL "${CMAKE_SOURCE_DIR}"
    )
endfunction()

function(disable_lto target)
    target_compile_options(${target} PRIVATE -fno-lto)
    target_link_options(${target} PRIVATE -fno-lto)
endfunction()

# If we're on Unix and the system is 32-bit (void* is 4-bytes wide),
# then there's a good chance we're compiling for Raspberry Pi.
# Currently, CMake doesn't detect this properly and needs some help
# to link libatomic.
# Source: https://gitlab.kitware.com/cmake/cmake/-/issues/21174
#
# TODO: Use include(CheckCXXSourceCompiles) to make this check better.
if(UNIX AND CMAKE_SIZEOF_VOID_P EQUAL 4)
    set(CMAKE_CXX_LINK_FLAGS "${CMAKE_CXX_LINK_FLAGS} -latomic")
endif()
