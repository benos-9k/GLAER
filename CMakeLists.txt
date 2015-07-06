project(GLAER C CXX)
cmake_minimum_required(VERSION 3.0.0)

# enable IDE project folders
SET_PROPERTY(GLOBAL PROPERTY USE_FOLDERS ON)

# OpenGL is required
find_package(OpenGL REQUIRED)

# python2 is required to generate GLAER source files
find_package(PythonInterp 2.7 REQUIRED)

# generator; allow user to override
if(MSVC_IDE)
	set(GLAER_GENERATOR "Visual Studio" CACHE STRING "GLAER generator")
else()
	set(GLAER_GENERATOR "Default" CACHE STRING "GLAER generator")
endif()

# ensure output directories exist
file(MAKE_DIRECTORY "${PROJECT_BINARY_DIR}/src/include/GLAER")

# generate GLAER source files
add_custom_command(
	OUTPUT
		"${PROJECT_BINARY_DIR}/src/include/GLAER/glaer.h"
		"${PROJECT_BINARY_DIR}/src/glaer.c"
	DEPENDS
		"${PROJECT_SOURCE_DIR}/makeglaer.py"
		"${PROJECT_SOURCE_DIR}/glapi.py"
		"${PROJECT_SOURCE_DIR}/api/gl.xml"
		"${PROJECT_SOURCE_DIR}/common/glaer.h"
		"${PROJECT_SOURCE_DIR}/common/glaer.c"
	COMMAND
		${PYTHON_EXECUTABLE} "${PROJECT_SOURCE_DIR}/makeglaer.py"
		"-oh" "${PROJECT_BINARY_DIR}/src/include/GLAER/glaer.h"
		"-oc" "${PROJECT_BINARY_DIR}/src/glaer.c"
		"-g" ${GLAER_GENERATOR}
	VERBATIM
)

# GLAER lib target
add_library(
	glaer
	"${PROJECT_BINARY_DIR}/src/include/GLAER/glaer.h"
	"${PROJECT_BINARY_DIR}/src/glaer.c"
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
	# dynamic loading
	target_link_libraries(glaer PRIVATE kernel32)
elseif(APPLE)
	# dynamic loading ???
endif()

# shared library usage requirements
if(BUILD_SHARED_LIBS)
	# define macro for building DLL
	target_compile_definitions(glaer PRIVATE GLAER_BUILD_DLL)
	# define macro for importing DLL
	target_compile_definitions(glaer INTERFACE GLAER_DLL)
endif()

# test project
add_subdirectory(test)










