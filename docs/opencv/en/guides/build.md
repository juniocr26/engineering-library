# opencv — Out-of-tree configuration

Temporary reviewed partial model excerpt. Important contracts remain undocumented. Not approved for publication; source quotes and full review evidence are preserved separately.

Source revision: `5d0660acfed08650cafec4876b4792a369a20601`.

Editorial scope: only the first model sentence is retained; the rest of that paragraph was omitted during source review. This edited excerpt is separate from the frozen, scored original.

## 1

The implementation checks if the CMake source directory is the same as the binary directory, and if so, it displays an error message indicating that in-source builds are not allowed.

Source: `CMakeLists.txt:1`; SHA-256: `e932d829154adb2b67d2ead32c5165f6c3c378211860beb40345fc7960003bb3`.

    # ----------------------------------------------------------------------------
    #  Root CMake file for OpenCV
    #
    #    From the off-tree build directory, invoke:
    #      $ cmake <PATH_TO_OPENCV_ROOT>
    #
    # ----------------------------------------------------------------------------
    # Disable in-source builds to prevent source tree corruption.
    if(" ${CMAKE_SOURCE_DIR}" STREQUAL " ${CMAKE_BINARY_DIR}")
      message(FATAL_ERROR "
    FATAL: In-source builds are not allowed.
           You should create a separate directory for build files.
    ")
    endif()
    
    include(cmake/OpenCVMinDepVersions.cmake)
    
    cmake_minimum_required(VERSION "${MIN_VER_CMAKE}" FATAL_ERROR)
    


