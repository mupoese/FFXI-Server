# Modern C++ Features and Enhancements for LandSandBoat
# Provides modern C++20 features and advanced compiler configurations

# Set minimum CMake version for modern features
cmake_minimum_required(VERSION 3.20)

# Modern C++20 features
function(enable_modern_cpp_features target)
    # Set C++20 standard
    target_compile_features(${target} PRIVATE cxx_std_20)
    
    # Enable modern C++20 features
    if(CMAKE_CXX_COMPILER_ID MATCHES "Clang|GNU")
        target_compile_options(${target} PRIVATE
            -fcoroutines
            -fmodules-ts
            -Wno-unknown-pragmas
        )
    elseif(CMAKE_CXX_COMPILER_ID STREQUAL "MSVC")
        target_compile_options(${target} PRIVATE
            /std:c++20
            /experimental:module
            /await
        )
    endif()
endfunction()

# Enhanced compiler warnings
function(enable_enhanced_warnings target)
    if(CMAKE_CXX_COMPILER_ID MATCHES "Clang|GNU")
        target_compile_options(${target} PRIVATE
            -Wall
            -Wextra
            -Wpedantic
            -Wshadow
            -Wnon-virtual-dtor
            -Wold-style-cast
            -Wcast-align
            -Wunused
            -Woverloaded-virtual
            -Wpedantic
            -Wconversion
            -Wsign-conversion
            -Wmisleading-indentation
            -Wduplicated-cond
            -Wduplicated-branches
            -Wlogical-op
            -Wnull-dereference
            -Wuseless-cast
            -Wdouble-promotion
            -Wformat=2
        )
        
        # Additional Clang-specific warnings
        if(CMAKE_CXX_COMPILER_ID STREQUAL "Clang")
            target_compile_options(${target} PRIVATE
                -Wlifetime
                -Wloop-analysis
                -Wthread-safety
            )
        endif()
    elseif(CMAKE_CXX_COMPILER_ID STREQUAL "MSVC")
        target_compile_options(${target} PRIVATE
            /W4
            /w14242 /w14254 /w14263 /w14265 /w14287 /we4289 /w14296 /w14311
            /w14545 /w14546 /w14547 /w14549 /w14555 /w14619 /w14640 /w14826
            /w14905 /w14906 /w14928
            /permissive-
        )
    endif()
endfunction()

# Static analysis integration
function(enable_static_analysis target)
    # Enable clang-tidy if available
    find_program(CLANG_TIDY_EXE NAMES "clang-tidy" DOC "Path to clang-tidy executable")
    if(CLANG_TIDY_EXE)
        set_target_properties(${target} PROPERTIES
            CXX_CLANG_TIDY "${CLANG_TIDY_EXE};-checks=-*,readability-*,performance-*,modernize-*,bugprone-*"
        )
    endif()
    
    # Enable cppcheck if available
    find_program(CPPCHECK_EXE NAMES "cppcheck" DOC "Path to cppcheck executable")
    if(CPPCHECK_EXE)
        set_target_properties(${target} PROPERTIES
            CXX_CPPCHECK "${CPPCHECK_EXE};--enable=warning,performance,portability;--inline-suppr"
        )
    endif()
    
    # Enable include-what-you-use if available
    find_program(IWYU_EXE NAMES "include-what-you-use" DOC "Path to include-what-you-use executable")
    if(IWYU_EXE)
        set_target_properties(${target} PROPERTIES
            CXX_INCLUDE_WHAT_YOU_USE ${IWYU_EXE}
        )
    endif()
endfunction()

# Memory safety features
function(enable_memory_safety target)
    if(CMAKE_CXX_COMPILER_ID MATCHES "Clang|GNU")
        target_compile_options(${target} PRIVATE
            -fstack-protector-strong
            -D_FORTIFY_SOURCE=2
        )
        
        # AddressSanitizer in Debug mode
        if(CMAKE_BUILD_TYPE STREQUAL "Debug")
            target_compile_options(${target} PRIVATE -fsanitize=address -fno-omit-frame-pointer)
            target_link_libraries(${target} PRIVATE -fsanitize=address)
        endif()
    endif()
endfunction()

# Link-time optimization
function(enable_lto target)
    include(CheckIPOSupported)
    check_ipo_supported(RESULT IPO_SUPPORTED OUTPUT IPO_ERROR)
    
    if(IPO_SUPPORTED AND CMAKE_BUILD_TYPE MATCHES "Release")
        set_target_properties(${target} PROPERTIES INTERPROCEDURAL_OPTIMIZATION TRUE)
        message(STATUS "Link-time optimization enabled for ${target}")
    elseif(NOT IPO_SUPPORTED)
        message(WARNING "Link-time optimization not supported: ${IPO_ERROR}")
    endif()
endfunction()

# Precompiled headers support
function(enable_precompiled_headers target)
    if(CMAKE_VERSION VERSION_GREATER_EQUAL "3.16")
        target_precompile_headers(${target} PRIVATE
            <algorithm>
            <array>
            <chrono>
            <cstdint>
            <cstring>
            <fstream>
            <functional>
            <iostream>
            <map>
            <memory>
            <mutex>
            <optional>
            <string>
            <string_view>
            <thread>
            <unordered_map>
            <vector>
        )
        message(STATUS "Precompiled headers enabled for ${target}")
    endif()
endfunction()

# Unity build support for faster compilation
function(enable_unity_build target)
    if(CMAKE_VERSION VERSION_GREATER_EQUAL "3.16")
        set_target_properties(${target} PROPERTIES
            UNITY_BUILD ON
            UNITY_BUILD_BATCH_SIZE 8
        )
        message(STATUS "Unity build enabled for ${target}")
    endif()
endfunction()

# Apply all modern features to a target
function(apply_modern_cpp_features target)
    enable_modern_cpp_features(${target})
    enable_enhanced_warnings(${target})
    enable_memory_safety(${target})
    
    # Optional features based on build type
    if(CMAKE_BUILD_TYPE MATCHES "Release")
        enable_lto(${target})
    endif()
    
    # Optional features based on CMake version
    if(CMAKE_VERSION VERSION_GREATER_EQUAL "3.16")
        enable_precompiled_headers(${target})
        
        # Enable unity build for faster compilation in CI
        if(DEFINED ENV{CI})
            enable_unity_build(${target})
        endif()
    endif()
    
    # Static analysis in Debug mode or when explicitly requested
    if(CMAKE_BUILD_TYPE STREQUAL "Debug" OR ENABLE_STATIC_ANALYSIS)
        enable_static_analysis(${target})
    endif()
endfunction()

# Export compile commands for language servers and static analysis tools
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)