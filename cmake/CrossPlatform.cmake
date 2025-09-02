# Cross-Platform Build Configuration for FFXI Server
# This file contains platform-specific build instructions and optimizations

cmake_minimum_required(VERSION 3.20)

# Platform-specific build configurations
include(Platform)

# Platform-specific optimization functions
function(apply_platform_optimizations target)
    message(STATUS "Applying platform optimizations for ${target}")
    
    # Windows-specific optimizations
    if(WIN32)
        target_compile_definitions(${target} PRIVATE 
            XI_PLATFORM_WINDOWS=1
            NOMINMAX
            _CRT_SECURE_NO_WARNINGS
        )
        
        if(MSVC)
            target_compile_options(${target} PRIVATE
                /W4        # High warning level
                /MP        # Multi-processor compilation
                /bigobj    # Large object files
                /utf-8     # UTF-8 source files
            )
            
            # Release-specific optimizations
            if(CMAKE_BUILD_TYPE STREQUAL "Release")
                target_compile_options(${target} PRIVATE
                    /O2        # Maximize speed
                    /Oi        # Enable intrinsic functions
                    /GL        # Whole program optimization
                    /Gy        # Function-level linking
                )
                
                if(XI_TARGET_ARCH STREQUAL "x86_64")
                    target_compile_options(${target} PRIVATE
                        /favor:INTEL64
                        /arch:AVX2
                    )
                endif()
                
                target_link_options(${target} PRIVATE
                    /LTCG      # Link-time code generation
                    /OPT:REF   # Remove unreferenced functions
                    /OPT:ICF   # Identical COMDAT folding
                )
            endif()
            
            # Debug-specific settings
            if(CMAKE_BUILD_TYPE STREQUAL "Debug")
                target_compile_options(${target} PRIVATE
                    /Zi        # Debug information
                    /Od        # Disable optimizations
                )
                target_link_options(${target} PRIVATE
                    /INCREMENTAL
                )
            endif()
        endif()
        
        # Windows system libraries
        target_link_libraries(${target} PRIVATE
            ws2_32
            dbghelp
            shlwapi
        )
    endif()
    
    # macOS-specific optimizations
    if(APPLE)
        target_compile_definitions(${target} PRIVATE XI_PLATFORM_MACOS=1)
        
        # macOS deployment target
        if(NOT CMAKE_OSX_DEPLOYMENT_TARGET)
            set_target_properties(${target} PROPERTIES
                OSX_DEPLOYMENT_TARGET "10.15"
            )
        endif()
        
        # Apple Silicon optimizations
        if(XI_TARGET_ARCH STREQUAL "arm64")
            target_compile_options(${target} PRIVATE
                -mcpu=apple-m1
                -mtune=apple-m1
            )
        endif()
        
        # Intel macOS optimizations
        if(XI_TARGET_ARCH STREQUAL "x86_64")
            target_compile_options(${target} PRIVATE
                -march=core2
                -mtune=intel
            )
        endif()
        
        # macOS frameworks
        find_library(CORE_FOUNDATION CoreFoundation)
        find_library(CORE_SERVICES CoreServices)
        if(CORE_FOUNDATION AND CORE_SERVICES)
            target_link_libraries(${target} PRIVATE
                ${CORE_FOUNDATION}
                ${CORE_SERVICES}
            )
        endif()
    endif()
    
    # Linux-specific optimizations
    if(CMAKE_SYSTEM_NAME STREQUAL "Linux")
        target_compile_definitions(${target} PRIVATE XI_PLATFORM_LINUX=1)
        
        # Position-independent code for security
        set_target_properties(${target} PROPERTIES
            POSITION_INDEPENDENT_CODE ON
        )
        
        # x86_64 optimizations
        if(XI_TARGET_ARCH STREQUAL "x86_64")
            target_compile_options(${target} PRIVATE
                -march=x86-64-v2
                -mtune=generic
                -msse4.2
                -mpopcnt
            )
        endif()
        
        # ARM64 optimizations
        if(XI_TARGET_ARCH STREQUAL "arm64")
            target_compile_options(${target} PRIVATE
                -mcpu=cortex-a72
                -mtune=cortex-a72
            )
        endif()
        
        # Linux system libraries
        target_link_libraries(${target} PRIVATE
            dl
            pthread
        )
        
        # Link-time optimization for release builds
        if(CMAKE_BUILD_TYPE STREQUAL "Release")
            if(CMAKE_CXX_COMPILER_ID MATCHES "GNU|Clang")
                target_compile_options(${target} PRIVATE -flto)
                target_link_options(${target} PRIVATE -flto)
            endif()
        endif()
    endif()
    
    # Compiler-specific optimizations
    if(CMAKE_CXX_COMPILER_ID STREQUAL "GNU")
        # GCC-specific flags
        target_compile_options(${target} PRIVATE
            -Wall
            -Wextra
            -Wpedantic
        )
        
        if(CMAKE_BUILD_TYPE STREQUAL "Release")
            target_compile_options(${target} PRIVATE
                -O3
                -DNDEBUG
                -fomit-frame-pointer
            )
        endif()
        
    elseif(CMAKE_CXX_COMPILER_ID MATCHES "Clang")
        # Clang-specific flags
        target_compile_options(${target} PRIVATE
            -Wall
            -Wextra
            -Wpedantic
        )
        
        if(CMAKE_BUILD_TYPE STREQUAL "Release")
            target_compile_options(${target} PRIVATE
                -O3
                -DNDEBUG
            )
        endif()
    endif()
    
    # Docker environment optimizations
    if(DEFINED ENV{XI_BUILD_DOCKER} OR EXISTS "/.dockerenv")
        target_compile_definitions(${target} PRIVATE XI_BUILD_DOCKER=1)
        message(STATUS "Applied Docker-specific optimizations for ${target}")
    endif()
    
    message(STATUS "Platform optimizations applied for ${target}")
endfunction()

# Function to configure cross-platform dependencies
function(configure_platform_dependencies target)
    message(STATUS "Configuring platform-specific dependencies for ${target}")
    
    # Find platform-specific libraries
    if(WIN32)
        # Windows-specific dependency configuration
        find_package(Threads REQUIRED)
        target_link_libraries(${target} PRIVATE Threads::Threads)
        
    elseif(APPLE)
        # macOS-specific dependency configuration
        find_package(Threads REQUIRED)
        target_link_libraries(${target} PRIVATE Threads::Threads)
        
        # Homebrew library paths for macOS
        if(XI_TARGET_ARCH STREQUAL "arm64")
            list(APPEND CMAKE_PREFIX_PATH "/opt/homebrew")
        else()
            list(APPEND CMAKE_PREFIX_PATH "/usr/local")
        endif()
        
    elseif(UNIX)
        # Linux-specific dependency configuration
        find_package(Threads REQUIRED)
        target_link_libraries(${target} PRIVATE Threads::Threads)
        
        # Check for specific Linux distributions
        if(EXISTS "/etc/debian_version")
            # Debian/Ubuntu specific
            target_compile_definitions(${target} PRIVATE XI_DISTRO_DEBIAN=1)
        elseif(EXISTS "/etc/redhat-release")
            # RedHat/CentOS/Fedora specific
            target_compile_definitions(${target} PRIVATE XI_DISTRO_REDHAT=1)
        elseif(EXISTS "/etc/arch-release")
            # Arch Linux specific
            target_compile_definitions(${target} PRIVATE XI_DISTRO_ARCH=1)
        endif()
    endif()
    
    message(STATUS "Platform dependencies configured for ${target}")
endfunction()

# Function to set platform-specific output directories
function(set_platform_output_directory target)
    if(WIN32)
        # Windows executables in root directory
        set_target_properties(${target} PROPERTIES
            RUNTIME_OUTPUT_DIRECTORY "${CMAKE_SOURCE_DIR}"
            RUNTIME_OUTPUT_DIRECTORY_DEBUG "${CMAKE_SOURCE_DIR}"
            RUNTIME_OUTPUT_DIRECTORY_RELEASE "${CMAKE_SOURCE_DIR}"
        )
    else()
        # Unix-like systems
        set_target_properties(${target} PROPERTIES
            RUNTIME_OUTPUT_DIRECTORY "${CMAKE_SOURCE_DIR}/bin"
            RUNTIME_OUTPUT_DIRECTORY_DEBUG "${CMAKE_SOURCE_DIR}/bin"
            RUNTIME_OUTPUT_DIRECTORY_RELEASE "${CMAKE_SOURCE_DIR}/bin"
        )
        
        # Create bin directory if it doesn't exist
        file(MAKE_DIRECTORY "${CMAKE_SOURCE_DIR}/bin")
    endif()
endfunction()

# Function to apply all cross-platform configurations
function(configure_cross_platform_target target)
    apply_platform_optimizations(${target})
    configure_platform_dependencies(${target})
    set_platform_output_directory(${target})
    
    message(STATUS "Cross-platform configuration complete for ${target}")
endfunction()

# Export functions for use in other CMake files
set(CROSS_PLATFORM_CONFIGURED TRUE CACHE BOOL "Cross-platform configuration loaded")