"""
Copyright 2021 Clarify

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""


class PyClarifyException(Exception):
    pass


class PyClarifyImportError(PyClarifyException):
    """PyClarify Import Error

    Raised if the user attempts to use functionality which requires an uninstalled package.
    Args:
        module (str): Name of the module which could not be imported
        message (str): The error message to output.
    """

    def __init__(self, module: str, message: str = None):
        self.module = module
        self.message = (
            message
            or "The functionality your are trying to use requires '{}' to be installed.".format(
                self.module
            )
        )

    def __str__(self):
        return self.message
