
# GLFW (if not already available)
if(NOT TARGET glfw)
	add_subdirectory("${CMAKE_CURRENT_SOURCE_DIR}/ext/glfw-3.0.3")
endif()

# Compile options
if("${CMAKE_CXX_COMPILER_ID}" STREQUAL "MSVC")
	add_compile_options(/W4)
elseif("${CMAKE_CXX_COMPILER_ID}" STREQUAL "GNU")
	add_compile_options(-std=c++1y -Wall -Wextra -pedantic)
elseif("${CMAKE_CXX_COMPILER_ID}" MATCHES "^(Apple)?Clang$")
	add_compile_options(-std=c++1y -Wall -Wextra -pedantic)
endif()

# test exe target
add_executable(glaer_test "src/main.cpp")

set_property(TARGET glaer_test PROPERTY FOLDER "GLAER")

# ensure GLFW is linked properly
target_include_directories(glaer_test PRIVATE "${GLFW_SOURCE_DIR}/include")
target_link_libraries(glaer_test glfw ${GLFW_LIBRARIES} glaer)







