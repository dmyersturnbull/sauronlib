# Sauronlib

[![Version status](https://img.shields.io/pypi/status/sauronlib)](https://pypi.org/project/sauronlib/)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/sauronlib)](https://pypi.org/project/sauronlib/)
[![Docker](https://img.shields.io/docker/v/dmyersturnbull/sauronlib?color=green&label=DockerHub)](https://hub.docker.com/repository/docker/dmyersturnbull/sauronlib)
[![GitHub release (latest SemVer including pre-releases)](https://img.shields.io/github/v/release/dmyersturnbull/sauronlib?include_prereleases&label=GitHub)](https://github.com/dmyersturnbull/sauronlib/releases)
[![Latest version on PyPi](https://badge.fury.io/py/sauronlib.svg)](https://pypi.org/project/sauronlib/)
[![Documentation status](https://readthedocs.org/projects/sauronlib/badge/?version=latest&style=flat-square)](https://sauronlib.readthedocs.io/en/stable/)
[![Build & test](https://github.com/dmyersturnbull/sauronlib/workflows/Build%20&%20test/badge.svg)](https://github.com/dmyersturnbull/sauronlib/actions)
[![Azure DevOps builds](https://img.shields.io/azure-devops/build/dmyersturnbull/<<key>>/<<defid>>?label=Azure)](https://dev.azure.com/dmyersturnbull/sauronlib/_build?definitionId=1&_a=summary)
[![Maintainability](https://api.codeclimate.com/v1/badges/<<apikey>>/maintainability)](https://codeclimate.com/github/dmyersturnbull/sauronlib/maintainability)
[![Coverage](https://coveralls.io/repos/github/dmyersturnbull/sauronlib/badge.svg?branch=master)](https://coveralls.io/github/dmyersturnbull/sauronlib?branch=master)


Sauronlib is a high-level Python API to control hardware and software for scientific experiments that rely on Arduinos or computer-connected hardware.
It's used in [SauronX](https://github.com/dmyersturnbull/sauronx) to capture data for zebrafish experiments that consist of a series of scheduled events.

Out of the box, it works with [Firmata](https://www.arduino.cc/en/reference/firmata), [PointGrey cameras](https://www.flir.com/iis/machine-vision/), MATLAB's [Image Acquisition Toolbox](https://www.mathworks.com/products/image-acquisition.html), and computer-driven audio input and output on Linux, Windows, and Mac OS.
You can add support for any hardware with a custom wrapper.

It knows about hardware configuration and data organization, and runs an experiment consisting of scheduled and triggered events while capturing sensor data.
It conceptually seperates hardware from experiments.

⚠ Sauronlib is not finished. It's a redesigned subset of SauronX (which is fully functional).

[See the docs](https://sauronlib.readthedocs.io/en/stable/) for more information.


[New issues](https://github.com/dmyersturnbull/sauronlib/issues) and pull requests are welcome.
Please refer to the [contributing guide](https://github.com/dmyersturnbull/sauronlib/blob/master/CONTRIBUTING.md).
Generated with [Tyrannosaurus](https://github.com/dmyersturnbull/tyrannosaurus).
