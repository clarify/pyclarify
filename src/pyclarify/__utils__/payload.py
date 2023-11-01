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

from pyclarify.fields.constraints import ApiMethod
from pyclarify.views.generics import Request

def unpack_params(request: Request):
    #TODO: CLEAN UP THE MESS
    API_LIMIT = user_limit = skip = user_gte = user_lt = rollup = None

    # Resource Query
    query = getattr(request.params, "query") if hasattr(request.params, "query") else None
    user_limit = getattr(query, "limit") if hasattr(query, "limit") else None
    skip = getattr(query, "skip") if hasattr(query, "skip") else 0
    
    # Data Query
    data = getattr(request.params, "data") if hasattr(request.params, "data") else None
    if data:
        times = data.filter["times"]
        user_gte = times.pop("$gte", None)
        user_lt = times.pop("$lt", None)
        rollup = data.rollup

    if request.method == ApiMethod.select_items:
        API_LIMIT = 1000

    if request.method == ApiMethod.select_signals:
        API_LIMIT = 1000

    if request.method == ApiMethod.data_frame:
        API_LIMIT = 50        

    if request.method == ApiMethod.evaluate:
        API_LIMIT = 50



    return API_LIMIT, user_limit, skip, user_gte, user_lt, rollup
