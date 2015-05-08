# GLAER
###### _OpenGL API Entrypoint Retriever_

GLAER is a C wrapper for the OpenGL API that loads entrypoints at runtime. Source files are generated inside a CMake project with a Python script that parses the OpenGL XML documentation. The script inlines documentation in the generated header if a supported IDE (currently only Visual Studio) is detected.

This is currently _alpha_ software; it has only just reached the point where things actually work.

## OpenGL XML Documentation

The API specification './api/gl.xml' will be downloaded if it is not present. The documentation is not critical to operation, and as such will not be downloaded if it does not exist. GLAER does however come with both the API specification and documentation already present. To update the API specification and documentation, import the Python module `glapi` and call `glapi.update_api()` and `glapi.update_docs()` respectively, then reload the module.

## Python

The scripts currently run under (and the CMake project looks for) Python 2.7.

The package [Beautiful Soup 4](http://www.crummy.com/software/BeautifulSoup/) is required and is included in GLAER for convenience. However, Beautiful Soup requires [lxml](http://lxml.de/installation.html) in order to parse XML. This can be installed with `pip install [--user] lxml`. On Windows, you may need to specify a version number if there is no pre-built package for the latest version, e.g `pip install lxml==3.4.1`.

## Test Project

The directory `/test` contains a CMake project (using [GLFW](http://www.glfw.org/)) that does some basic drawing with OpenGL in order to test that entrypoints are being loaded correctly. It can also serve as an example of how to add GLAER as a CMake sub-project.
