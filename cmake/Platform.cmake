message(STATUS "CMAKE_SOURCE_DIR: ${CMAKE_SOURCE_DIR}")
if(${CMAKE_SOURCE_DIR} MATCHES " +")
	set(STRIPPED_PATH "")
	STRING(REGEX REPLACE  " +" "_" STRIPPED_PATH "${CMAKE_SOURCE_DIR}")

	message(STATUS
		"Current path: ${CMAKE_SOURCE_DIR}\n"
		"Suggested path: ${STRIPPED_PATH}\n"
		"Your path contains spaces, this is not recommended.")
endif()

# Enhanced cross-platform detection and optimization
message(STATUS "=== Cross-Platform Build Configuration ===")

# Detect target platform and architecture
if(CMAKE_SIZEOF_VOID_P EQUAL 8)
    message(STATUS "CMAKE_SIZEOF_VOID_P == 8: 64-bit build")
    set(platform_suffix "64")
    set(lib_dir lib64)
    add_compile_definitions(ENV64BIT)
elseif(CMAKE_SIZEOF_VOID_P EQUAL 4)
    message(STATUS "CMAKE_SIZEOF_VOID_P == 4: 32-bit build")
    if(WIN32)
        message(FATAL_ERROR "32-bit Windows builds are not supported")
    endif()
    add_compile_definitions(ENV32BIT)
endif()

# Detect CPU architecture for platform-specific optimizations
if(CMAKE_SYSTEM_PROCESSOR MATCHES "^(x86_64|AMD64|amd64)$")
    set(TARGET_ARCH "x86_64")
    message(STATUS "Target Architecture: x86_64")
elseif(CMAKE_SYSTEM_PROCESSOR MATCHES "^(arm64|aarch64|ARM64)$")
    set(TARGET_ARCH "arm64")
    message(STATUS "Target Architecture: ARM64")
    # Enable ARM64 specific optimizations
    if(CMAKE_CXX_COMPILER_ID MATCHES "GNU|Clang")
        add_compile_options(-mcpu=native)
    endif()
elseif(CMAKE_SYSTEM_PROCESSOR MATCHES "^(arm|ARM)$")
    set(TARGET_ARCH "arm")
    message(STATUS "Target Architecture: ARM32")
    if(CMAKE_CXX_COMPILER_ID MATCHES "GNU|Clang")
        add_compile_options(-mcpu=cortex-a72)
    endif()
else()
    set(TARGET_ARCH "unknown")
    message(WARNING "Unknown target architecture: ${CMAKE_SYSTEM_PROCESSOR}")
endif()

# Platform-specific optimizations
if(WIN32)
    message(STATUS "Platform: Windows")
    set(CMAKE_FIND_USE_SYSTEM_ENVIRONMENT_PATH OFF)
    add_compile_definitions(XI_PLATFORM_WINDOWS)
    
    # Windows-specific optimizations
    if(MSVC)
        # Enhanced Windows optimizations
        if(CMAKE_BUILD_TYPE STREQUAL "Release")
            add_compile_options(/favor:INTEL64)
            if(TARGET_ARCH STREQUAL "x86_64")
                add_compile_options(/arch:AVX2)
            endif()
        endif()
    endif()
    
elseif(APPLE)
    message(STATUS "Platform: macOS")
    add_compile_definitions(XI_PLATFORM_MACOS)
    
    # macOS-specific optimizations
    if(TARGET_ARCH STREQUAL "arm64")
        message(STATUS "Optimizing for Apple Silicon (ARM64)")
        add_compile_options(-mcpu=apple-m1)
    elseif(TARGET_ARCH STREQUAL "x86_64")
        message(STATUS "Optimizing for Intel macOS")
        add_compile_options(-march=core2 -mtune=intel)
    endif()
    
    # macOS version detection
    execute_process(
        COMMAND sw_vers -productVersion
        OUTPUT_VARIABLE MACOS_VERSION
        OUTPUT_STRIP_TRAILING_WHITESPACE
    )
    message(STATUS "macOS Version: ${MACOS_VERSION}")
    
    # Set minimum macOS deployment target
    if(NOT CMAKE_OSX_DEPLOYMENT_TARGET)
        set(CMAKE_OSX_DEPLOYMENT_TARGET "10.15" CACHE STRING "Minimum macOS deployment target")
    endif()
    message(STATUS "macOS Deployment Target: ${CMAKE_OSX_DEPLOYMENT_TARGET}")
    
elseif(UNIX)
    message(STATUS "Platform: Linux/Unix")
    add_compile_definitions(XI_PLATFORM_LINUX)
    
    # Linux distribution detection
    if(EXISTS "/etc/os-release")
        file(READ "/etc/os-release" OS_RELEASE)
        if(OS_RELEASE MATCHES "ID=([a-zA-Z0-9_-]+)")
            set(LINUX_DISTRO ${CMAKE_MATCH_1})
            message(STATUS "Linux Distribution: ${LINUX_DISTRO}")
        endif()
    endif()
    
    # Linux-specific optimizations
    if(CMAKE_CXX_COMPILER_ID MATCHES "GNU|Clang")
        if(TARGET_ARCH STREQUAL "x86_64")
            add_compile_options(-march=x86-64-v2 -mtune=generic)
        endif()
        
        # Enable position independent code for better security
        set(CMAKE_POSITION_INDEPENDENT_CODE ON)
    endif()
    
    # Docker environment detection
    if(EXISTS "/.dockerenv")
        message(STATUS "Build Environment: Docker Container")
        add_compile_definitions(XI_BUILD_DOCKER)
    endif()
endif()

# Compiler-specific cross-platform optimizations
if(CMAKE_CXX_COMPILER_ID STREQUAL "GNU")
    message(STATUS "Compiler: GCC ${CMAKE_CXX_COMPILER_VERSION}")
    # GCC-specific optimizations
    if(CMAKE_BUILD_TYPE STREQUAL "Release")
        add_compile_options(-O3 -DNDEBUG)
        if(TARGET_ARCH STREQUAL "x86_64")
            add_compile_options(-msse4.2 -mpopcnt)
        endif()
    endif()
    
elseif(CMAKE_CXX_COMPILER_ID MATCHES "Clang")
    message(STATUS "Compiler: Clang ${CMAKE_CXX_COMPILER_VERSION}")
    # Clang-specific optimizations
    if(CMAKE_BUILD_TYPE STREQUAL "Release")
        add_compile_options(-O3 -DNDEBUG)
        if(TARGET_ARCH STREQUAL "x86_64")
            add_compile_options(-msse4.2 -mpopcnt)
        endif()
    endif()
    
elseif(CMAKE_CXX_COMPILER_ID STREQUAL "MSVC")
    message(STATUS "Compiler: MSVC ${CMAKE_CXX_COMPILER_VERSION}")
    # MSVC optimizations handled in StandardProjectSettings.cmake
endif()

# Cross-compilation support
if(CMAKE_CROSSCOMPILING)
    message(STATUS "Cross-compilation detected")
    message(STATUS "Host System: ${CMAKE_HOST_SYSTEM_NAME}")
    message(STATUS "Target System: ${CMAKE_SYSTEM_NAME}")
    add_compile_definitions(XI_CROSS_COMPILING)
endif()

if(CMAKE_CONFIGURATION_TYPES STREQUAL Debug)
    set(lib_debug "-d")
else()
    set(lib_debug "")
endif()

set(libpath "lib${platform_suffix}")

message(STATUS "Target Architecture: ${TARGET_ARCH}")
message(STATUS "Library Path: ${libpath}")
message(STATUS "==========================================")

# Set platform-specific variables for use in other CMake files
set(XI_TARGET_ARCH ${TARGET_ARCH} CACHE STRING "Target architecture")
set(XI_PLATFORM_SUFFIX ${platform_suffix} CACHE STRING "Platform suffix")
