"""
Copyright 2022 Searis AS

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


class ImportError(PyClarifyException):
    """PyClarify Import Error

    Raised if the user attempts to use functionality which requires an uninstalled package.
    Args:
        module (str): Name of the module which could not be imported
        message (str): The error message to output.
    """

    def __init__(self, module: str, message: str = None):
        self.module = module
        self.message = (
            message or "The functionality your are trying to use requires '{}' to be installed.".format(
                self.module
            )
        )

    def __str__(self):
        return self.message


class FilterError(PyClarifyException):
    """PyClarify Filter Error

    Raised if the user attempts to create Filter with operator that does not refelct the values.
    Args:
        field (str): Name of the field which produced the error
        values :
        message (str): The error message to output.
    """

    def __init__(self, field: str, desired_type, actual_values, message: str = None):
        self.field = field
        self.desired_type = desired_type
        self.actual_values = actual_values
        self.message = (
            message or "The operator '{}' does not allow values of type '{}'. You used '{}'.".format(
                self.field,
                self.desired_type,
                self.actual_values
            )
        )

    def __str__(self):
        return self.message

             
class TypeError(PyClarifyException):
    """PyClarify Type Error

    Raised if the user attempts to use functionality which combines the content of two Clarify Models.
    Args:
        module (str): Name of the module which could not be imported
        message (str): The error message to output.
    """

    def __init__(self, source, other, message: str = None):
        self.other = other
        self.source = source
        self.message = (
            message or "The objects you are trying to combine do not have the same type '{}' and '{}'.".format(
                type(self.other), type(self.source)
            )
        )

    def __str__(self):
        return self.message
