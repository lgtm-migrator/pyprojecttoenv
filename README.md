# pyprojecttoenv
Create yaml environments from pyproject.toml file

## Overview
Dependencies and optional dependencies can be installed from a pyproject.toml file using pip, but installing these dependencies is not straight-forward using conda. *pyprojecttoenv* makes this easy, by providing a command line tool to automatically create environment yaml files from your pyproject.toml.

This can be incorporated into your CI routines so that you can just manage your dependencies in pyproject.toml, but easily use conda in your CI routines.
