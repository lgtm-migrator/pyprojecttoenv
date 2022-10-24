# -*- coding: utf-8 -*-
"""Create environment yaml files from pyproject.toml."""
import argparse
import os
from typing import Any, Dict, List, Sequence

import tomli
import yaml


# TODO: Add ability to specify dependency channels (to handle pip only deps)
# TODO: Investigate automatic renaming of dependencies like pypi-mapping at
# https://github.com/conda-incubator/conda-lock
# TODO: Switch to using get() to retrive from dicts
def create_parser() -> argparse.ArgumentParser:
    """Create command line parser.

    Returns
    -------
    parser : argparse.ArgumentParser
        The command line parser.
    """
    parser = argparse.ArgumentParser(
        description="Create environment.yaml files from pyproject.toml"
    )
    parser.add_argument(
        "--input_path",
        nargs="?",
        default=".",
        help="The path to the pyproject.toml file.",
    )
    parser.add_argument(
        "--output_path", nargs="?", default="./build_tools", help="The output path."
    )
    parser.add_argument(
        "--dep_type",
        nargs="?",
        const="all",
        default="all",
        help=(
            "Name of dependency to read from pyproject.toml. One of 'optional', 'all'."
        ),
    )
    return parser


def _load_dependencies(
    toml_project_dict: Dict[str, Any], dep_type: str = "dependencies"
) -> List[str]:
    """Load dependencies from the pyproject.toml files project table.

    Parameters
    ----------
    toml_project_dict : dict[str, Any]
        The dictionary that was loaded from the pyproject.toml's project table.
    dep_type : str
        The name of the dependency table to load. if `dep_type` does not equal
        "dependencies" then the dependency table will attempt to be loaded
        from the 'optional-dependencies' sub-table.

    Returns
    -------
    dependencies : list[str]
        The dependencies from the pyproject.toml file.

        - If ``dep_type='dependencies'`` then a list of the string dependencies
          is returned.
        - If ``dep_type!='dependencies'`` then a list of the string dependencies
          for the specified `dep_type` is returned from the 'optional-dependencies'
          sub-table.
    """
    if dep_type == "dependencies":
        dep_table = "dependencies"
    else:
        dep_table = "optional-dependencies"
    if dep_table not in toml_project_dict:
        raise ValueError(
            "pyproject.toml's project table does not include {dep_table} sub-table."
        )
    # Since the dependency sub-table exists try to load requested dependency
    if dep_type == "dependencies":
        dependencies = toml_project_dict[dep_type]
    else:
        sub_dep_table = toml_project_dict[dep_table]
        if dep_type not in sub_dep_table:
            raise ValueError("Something.")
        dependencies = sub_dep_table[dep_type]
    return dependencies


def _write_dependencies(
    deps: Dict[str, List[str]], output_path: str = ".", verbose: bool = False
) -> Dict[str, Sequence[str]]:
    """Write the dependencies from the pyproject.toml file to a environment yaml file.

    Parameters
    ----------
    deps : dict[str, list[str]]
        Mapping from string name of dependency table to the list of
        dependencies parsed from the pyproject.toml file.
    output_path : str, default="."
        The path to output the environment file to.
    verbose : bool, default=False
        Whether to print information about the depencency environment that was written.

    Returns
    -------
    dep_yaml : dict[str, list[str]]
        Mapping from the name of the dependency group to a list of string
        dependencies.
    """
    if not (output_path.endswith("\\") or output_path.endswith("/")):
        output_path = output_path + "/"
    if not os.path.exists(output_path):
        os.makedirs(output_path)

    if len(deps) == 0:
        raise ValueError("Empty dependency dictionary found.")

    dep_name = [*deps.keys()][0]
    dep_yaml = {"name": dep_name, "dependencies": deps[dep_name]}
    with open(output_path + f"{dep_name}.yaml", "w") as file:
        yaml.dump(dep_yaml, file)
    if verbose:
        print(
            f"Dependency environment created at {output_path + dep_name}.yaml "
            f"with data: {dep_yaml}."
        )
    return dep_yaml


def pyproject_toml_to_environment_file(
    input_path: str = ".",
    output_path: str = ".",
    dep_type: str = "dependencies",
    verbose: bool = True,
) -> None:
    """Parse pyproject.toml dependencies and write them to an environment yaml file.

    Output file name is ``dep_type.yml``.

    Parameters
    ----------
    input_path : str, default="."
        The path to read the pyproject.toml file from.
    output_path : str, default="."
        The path to output the environment file to.
    dep_type : str, default='dependencies'
        The name of the dependency table to read from the pyproject.toml file.
        If `dep_type` does not equal "dependencies" then the dependency table
        will attempt to be loaded from the 'optional-dependencies' sub-table.
    verbose : bool, default=False
        Whether to print information about the depencency environment that was written.

    Returns
    -------
    None :
        An environment yaml file is written, but no output is returned.
    """
    if not (output_path.endswith("\\") or output_path.endswith("/")):
        output_path = output_path + "/"

    if not (input_path.endswith("\\") or input_path.endswith("/")):
        input_path = input_path + "/"

    # Load the TOML file
    with open(input_path + "pyproject.toml", "rb") as f:
        toml_dict = tomli.load(f)

    # Verify it has the expected format
    if "project" not in toml_dict:
        raise ValueError("Expected pyproject.toml to include a project table.")

    project = toml_dict["project"]
    if not isinstance(project, dict):
        raise ValueError(
            "Expected pyproject.toml's project table to return dict, "
            f"but found {type(project)}."
        )

    if dep_type == "all":
        if "dependencies" in project:
            deps = _load_dependencies(project, dep_type="dependencies")
            dep_dict = {"dependencies": deps}
            _write_dependencies(dep_dict, output_path=output_path, verbose=verbose)
        if "optional-dependencies" in project:
            for optional_dep in project["optional-dependencies"].keys():
                deps = _load_dependencies(project, dep_type=optional_dep)
                dep_dict = {optional_dep: deps}
                _write_dependencies(dep_dict, output_path=output_path)
    else:
        deps = _load_dependencies(project, dep_type=dep_type)
        dep_dict = {dep_type: deps}
        _write_dependencies(dep_dict, output_path=output_path)
    return None


if __name__ == "__main__":
    parser = create_parser()
    args = vars(parser.parse_args())
    pyproject_toml_to_environment_file(**args)
