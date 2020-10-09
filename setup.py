#!/usr/bin/env python

import os
import re

from setuptools import Extension, find_packages, setup

with open("README.rst") as readme_file:
    readme = readme_file.read()

with open("HISTORY.rst") as history_file:
    history = history_file.read()

requirements = ["pandas>=0.20,<2", "htimeseries>=3,<4"]

setup_requirements = ["cython>=0.29,<0.30"]

test_requirements = []


def use_cython():
    base_dir = os.path.dirname(os.path.realpath(__file__))

    calculation_pyx = os.path.join(base_dir, "rocc", "calculation.pyx")
    calculation_pyx_exists = os.path.exists(calculation_pyx)
    calculation_c = os.path.join(base_dir, "rocc", "calculation.c")
    calculation_c_exists = os.path.exists(calculation_c)

    if (not calculation_pyx_exists) and (not calculation_c_exists):
        raise Exception(f"Neither {calculation_pyx} nor {calculation_c} exists")

    return (not calculation_c_exists) or (
        calculation_pyx_exists
        and os.path.getmtime(calculation_pyx) > os.path.getmtime(calculation_c)
    )


if use_cython():
    import numpy
    from Cython.Build import cythonize

    # The way we do the below is because of a Cython bug or maybe documentation error.
    # See https://github.com/cython/cython/issues/1480#issuecomment-401875701
    ext_modules = cythonize(
        Extension(
            "rocc.calculation",
            sources=["rocc/calculation.pyx"],
            include_dirs=[numpy.get_include()],
        )
    )
else:
    import numpy

    ext_modules = [
        Extension(
            "rocc.calculation",
            ["rocc/calculation.c"],
            include_dirs=[numpy.get_include()],
        ),
    ]


def get_version():
    scriptdir = os.path.dirname(os.path.abspath(__file__))
    init_py_path = os.path.join(scriptdir, "rocc", "__init__.py")
    with open(init_py_path) as f:
        return re.search(r'^__version__ = "(.*?)"$', f.read(), re.MULTILINE).group(1)


setup(
    ext_modules=ext_modules,
    name="rocc",
    author="Antonis Christofides",
    author_email="antonis@antonischristofides.com",
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Natural Language :: English",
        "Programming Language :: Python :: 3.7",
    ],
    description="Rate-of-change check of time series",
    install_requires=requirements,
    license="GNU General Public License v3",
    long_description=readme + "\n\n" + history,
    long_description_content_type="text/x-rst",
    include_package_data=True,
    packages=find_packages(include=["rocc"]),
    setup_requires=setup_requirements,
    test_suite="tests",
    tests_require=test_requirements,
    url="https://github.com/openmeteo/rocc",
    version=get_version(),
    zip_safe=False,
)
