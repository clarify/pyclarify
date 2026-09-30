# Copyright 2023 Searis AS

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


import inspect

from typing_extensions import deprecated as _deprecated

string_types = (type(b""), type(""))


def deprecated(reason):
    """
    Decorator which marks a function or class as deprecated: using it emits a DeprecationWarning,
    and type checkers and IDEs flag it (PEP 702). Use as ``@deprecated`` or ``@deprecated("reason")``.

    Parameters
    ----------
    reason : str or function or class
        Why it is deprecated, or the function or class itself.

    Returns
    -------
    The decorated function or class, or a decorator when given a reason.
    """

    def kind(obj):
        return "class" if inspect.isclass(obj) else "function"

    if isinstance(reason, string_types):
        reason = reason.decode() if isinstance(reason, bytes) else reason

        def decorator(obj):
            return _deprecated(f"Call to deprecated {kind(obj)} {obj.__name__} ({reason}).")(obj)

        return decorator

    elif inspect.isclass(reason) or inspect.isfunction(reason):
        return _deprecated(f"Call to deprecated {kind(reason)} {reason.__name__}.")(reason)

    else:
        raise TypeError(repr(type(reason)))

