project (GLTEST CXX)
cmake_minimum_required (VERSION 2.8.8)

# OpenGL
find_package(OpenGL)

# GLFW
add_subdirectory("${PROJECT_SOURCE_DIR}/ext/glfw-3.0.3" "${PROJECT_BINARY_DIR}/ext/glfw")
include_directories("${PROJECT_SOURCE_DIR}/ext/glfw-3.0.3/include")

# GLAER
add_subdirectory(".." "${PROJECT_BINARY_DIR}/ext/glaer")
include_directories("${GLAER_BINARY_DIR}/src/include")

if(MSVC)
	# Force to always compile with W4
	if(CMAKE_CXX_FLAGS MATCHES "/W[0-4]")
		string(REGEX REPLACE "/W[0-4]" "/W4" CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS}")
	else()
		set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} /W4")
	endif()
elseif(CMAKE_COMPILER_IS_GNUCXX)
	# Update if necessary
	set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -Wall -Wextra -pedantic -std=c++1y -g")
endif()




set(gltest_src "src/main.cpp")
set(gltest_hdr)

add_executable(gltest ${gltest_hdr} ${gltest_src})

target_link_libraries(gltest glfw ${GLFW_LIBRARIES} glaer ${GLAER_LIBRARIES})







