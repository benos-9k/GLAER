
# require new behaviour of: CMP0054
cmake_minimum_required(VERSION 3.1)

project(GLAER C CXX)

option(BUILD_SHARED_LIBS "Build shared libraries" OFF)

# output directories
# necessary for building shared libs so they all go in the same place and can then be loaded
# however, the current value takes effect when a target is created, so overriding as a subproject would be bad
# therefore, we only set the output directories if we are the top-level project
if("${CMAKE_SOURCE_DIR}" STREQUAL "${PROJECT_SOURCE_DIR}")
	message(STATUS "GLAER: setting CMake output directories to '${CMAKE_BINARY_DIR}/bin'")
	set(CMAKE_RUNTIME_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/bin")
	set(CMAKE_ARCHIVE_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/bin")
	set(CMAKE_LIBRARY_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/bin")
endif()

# enable IDE project folders
set_property(GLOBAL PROPERTY USE_FOLDERS ON)

# OpenGL is required
find_package(OpenGL REQUIRED)

# python2 is required to generate GLAER source files
# TODO python3: support or error
find_package(PythonInterp 2.7 REQUIRED)

# generator; allow user to override
if(MSVC_IDE)
	set(GLAER_GENERATOR "Visual Studio" CACHE STRING "GLAER generator")
else()
	set(GLAER_GENERATOR "Default" CACHE STRING "GLAER generator")
endif()

# ensure output directories exist
file(MAKE_DIRECTORY "${PROJECT_BINARY_DIR}/src/include/GLAER")

# output files
set(GLAER_HEADER "${PROJECT_BINARY_DIR}/src/include/GLAER/glaer.h")
set(GLAER_SOURCE "${PROJECT_BINARY_DIR}/src/glaer.c")

# if GLAER hasn't been (completely) generated previously
if((NOT EXISTS "${GLAER_HEADER}") OR (NOT EXISTS "${GLAER_SOURCE}"))
	# generate GLAER now, at cmake time, to improve the IDE experience on first run
	# GLAER will (probably) be re-generated on first build
	message(STATUS "Generating GLAER...")
	execute_process(COMMAND
		"${PYTHON_EXECUTABLE}" "${PROJECT_SOURCE_DIR}/makeglaer.py"
		"-oh" "${GLAER_HEADER}"
		"-oc" "${GLAER_SOURCE}"
		"-g" "${GLAER_GENERATOR}"
	)
endif()

# generate GLAER output files
add_custom_command(
	OUTPUT
		"${GLAER_HEADER}"
		"${GLAER_SOURCE}"
	DEPENDS
		"${PROJECT_SOURCE_DIR}/makeglaer.py"
		"${PROJECT_SOURCE_DIR}/glapi/__init__.py"
		"${PROJECT_SOURCE_DIR}/glapi/api/gl.xml"
		"${PROJECT_SOURCE_DIR}/glapi/docs/man2.zip"
		"${PROJECT_SOURCE_DIR}/glapi/docs/man3.zip"
		"${PROJECT_SOURCE_DIR}/glapi/docs/man4.zip"
		"${PROJECT_SOURCE_DIR}/common/glaer.h"
		"${PROJECT_SOURCE_DIR}/common/glaer.c"
	COMMAND
		"${PYTHON_EXECUTABLE}" "${PROJECT_SOURCE_DIR}/makeglaer.py"
		"-oh" "${GLAER_HEADER}"
		"-oc" "${GLAER_SOURCE}"
		"-g" "${GLAER_GENERATOR}"
	VERBATIM
)

# GLAER lib target
add_library(
	glaer
	"${GLAER_HEADER}"
	"${GLAER_SOURCE}"
)

set_property(TARGET glaer PROPERTY FOLDER "GLAER")

# add generated header to include path usage requirements
target_include_directories(glaer PUBLIC "${PROJECT_BINARY_DIR}/src/include")

# library usage requirements
target_link_libraries(glaer PRIVATE ${OPENGL_LIBRARIES})

# if GLAER is being statically linked into a DLL, this needs to be on
# set_target_properties(glaer PROPERTIES POSITION_INDEPENDENT_CODE ON)

# system-specific library usage requirements
if(WIN32)
	# dynamic loading (pretty sure you can't _not_ link kernel32 anyway)
	target_link_libraries(glaer PRIVATE kernel32)
elseif(UNIX)
	# dynamic loading
	target_link_libraries(glaer PRIVATE ${CMAKE_DL_LIBS})
endif()

# shared vs. static
set_target_properties(glaer PROPERTIES DEFINE_SYMBOL "GLAER_EXPORTS")
if(BUILD_SHARED_LIBS)
	target_compile_definitions(glaer PUBLIC GLAER_SHARED)
endif()

# test project
if (EXISTS "${PROJECT_SOURCE_DIR}/test")
	add_subdirectory(test)
endif()









