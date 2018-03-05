cmake_minimum_required(VERSION 3.5)

project(LineProfile)

#-----------------------------------------------------------------------------
# Extension meta-information
set(EXTENSION_HOMEPAGE "http://slicer.org/slicerWiki/index.php/Documentation/Nightly/Extensions/LineProfile")
set(EXTENSION_CATEGORY "Quantification")
set(EXTENSION_CONTRIBUTORS "Andras Lasso (PerkLab)")
set(EXTENSION_DESCRIPTION "Compute intensity profile along a line")
set(EXTENSION_ICONURL "http://www.example.com/Slicer/Extensions/LineProfile.png")
set(EXTENSION_SCREENSHOTURLS "http://www.example.com/Slicer/Extensions/LineProfile/Screenshots/1.png")
set(EXTENSION_DEPENDS "SegmentEditorExtraEffects") # Specified as a space separated string, a list or 'NA' if any

#-----------------------------------------------------------------------------
# Extension dependencies
find_package(Slicer REQUIRED)
include(${Slicer_USE_FILE})

#-----------------------------------------------------------------------------
# Extension modules
add_subdirectory(LineProfile)
## NEXT_MODULE

#-----------------------------------------------------------------------------
include(${Slicer_EXTENSION_GENERATE_CONFIG})
include(${Slicer_EXTENSION_CPACK})
