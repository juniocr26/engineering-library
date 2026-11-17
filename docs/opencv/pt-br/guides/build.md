# opencv — Configuração fora da árvore

Trecho parcial temporário do modelo, revisado. Contratos importantes continuam sem documentação. Sem aprovação de publicação; citações do código e evidências completas da revisão ficam preservadas separadamente.

Revisão de origem: `5d0660acfed08650cafec4876b4792a369a20601`.

Escopo editorial: somente a primeira frase do modelo foi mantida; o restante do parágrafo foi omitido na revisão do código. Este trecho editado é separado do original congelado e pontuado.

## 1

A implementação verifica se o diretório de fontes do CMake é o mesmo que o diretório de binários, e se for, exibe um erro indicando que os builds em fonte não são permitidos.

Fonte: `CMakeLists.txt:1`; SHA-256: `e932d829154adb2b67d2ead32c5165f6c3c378211860beb40345fc7960003bb3`.

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
    


