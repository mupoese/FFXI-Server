#!/bin/bash
# Run from repo root
find src/ \( -name '*.h' -o -name '*.cpp' \) -exec clang-format-18 -style=file -i {} \;
find modules/ \( -name '*.h' -o -name '*.cpp' \) -exec clang-format-18 -style=file -i {} \;
