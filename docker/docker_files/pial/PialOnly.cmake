# Focused build for the pinned FreeSurfer source. No surface algorithm changes.
# Installed as the source tree's top-level CMakeLists.txt by Dockerfile.
cmake_minimum_required(VERSION 3.16)
project(purple_pial LANGUAGES C CXX Fortran)
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)
set(CMAKE_POSITION_INDEPENDENT_CODE ON)
set(CMAKE_INCLUDE_CURRENT_DIR ON)
set(CMAKE_BUILD_TYPE Release CACHE STRING "Build type")
set(FS_VERSION "purple-80ec14cb-custom-focal")
set(BUILD_STAMP "purple-pial-80ec14cb-ubuntu20")
set(TIFF_SYSLIBS ON)
set(FIPS_SUPPORT OFF)
set(BUILD_SCRIBBLE OFF)
set(BUILD_DCM2NIIXFSLIB ON CACHE BOOL "Build dcm2niix wrapper")
set(ZLIB_IMPLEMENTATION Miniz CACHE STRING "dcm2niix compression implementation")
include(cmake/functions.cmake)
include(TestBigEndian)
host_os()
test_big_endian(IS_BIG_ENDIAN)
if(IS_BIG_ENDIAN)
  set(BYTEORDER 4321)
else()
  set(BYTEORDER 1234)
endif()
add_compile_definitions(Linux HAVE_ZLIB ITK_USE_SYSTEM_ZLIB)
find_package(ZLIB REQUIRED)
find_package(OpenMP REQUIRED)
find_package(ITK 4.13 REQUIRED COMPONENTS ITKVNL)
if(NOT ITKVNL_LIBRARIES)
  message(FATAL_ERROR "ITK did not export ITKVNL_LIBRARIES")
endif()
set(OMP_CXX_LIBRARIES OpenMP::OpenMP_CXX)
add_compile_definitions(HAVE_OPENMP)
set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} ${OpenMP_C_FLAGS}")
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} ${OpenMP_CXX_FLAGS} -ffunction-sections -fdata-sections")
set(CMAKE_Fortran_FLAGS "${CMAKE_Fortran_FLAGS} ${OpenMP_Fortran_FLAGS} -fno-builtin")
set(CMAKE_EXE_LINKER_FLAGS "${CMAKE_EXE_LINKER_FLAGS} -Wl,--gc-sections")
set(FS_INCLUDE_DIRS
  ${CMAKE_SOURCE_DIR}/include ${CMAKE_BINARY_DIR}/include
  ${CMAKE_SOURCE_DIR}/packages/minc ${CMAKE_SOURCE_DIR}/packages/netcdf
  ${CMAKE_SOURCE_DIR}/packages/nifti)
include_directories(${FS_INCLUDE_DIRS} ${ITK_INCLUDE_DIRS} ${ZLIB_INCLUDE_DIRS})
enable_testing()
# Only the bundled libraries required by the original utils target.
# Keep upstream CMake rules and the full utils source list unchanged.
foreach(pkg jpeg expat xml2 minc dicom dcm2niix cephes netcdf nrrdio nifti gifti)
  add_subdirectory(packages/${pkg})
endforeach()
add_subdirectory(utils)
add_executable(mris_place_surface mris_make_surfaces/mris_place_surface.cpp)
# Same xxd help generation as FreeSurfer's add_help(), with explicit paths.
set(HELP_XML "${CMAKE_SOURCE_DIR}/mris_make_surfaces/mris_place_surface.help.xml")
set(HELP_HEADER "${CMAKE_BINARY_DIR}/mris_place_surface.help.xml.h")
add_custom_command(OUTPUT "${HELP_HEADER}"
  COMMAND xxd -i mris_place_surface.help.xml "${HELP_HEADER}"
  WORKING_DIRECTORY "${CMAKE_SOURCE_DIR}/mris_make_surfaces"
  DEPENDS "${HELP_XML}" VERBATIM)
target_sources(mris_place_surface PRIVATE "${HELP_HEADER}")
target_include_directories(mris_place_surface PRIVATE
  "${CMAKE_BINARY_DIR}" "${CMAKE_SOURCE_DIR}/resurf/Code")
target_link_libraries(mris_place_surface utils)
