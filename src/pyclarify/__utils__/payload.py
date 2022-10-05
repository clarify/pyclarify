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
from pyclarify.fields.constraints import ApiMethod
from pyclarify.views.generics import Request

def unpack_params(request: Request):
  API_LIMIT = user_limit = skip = user_gte = user_lt = rollup = None
  query = request.params.query
  user_limit = query.limit
  skip = query.skip

  if request.method == ApiMethod.select_items:
    API_LIMIT = 1000

  if request.method == ApiMethod.select_signals:
    API_LIMIT = 1000

  if request.method == ApiMethod.data_frame:
    API_LIMIT = 50
    data = request.params.data
    times = data.filter["times"]
    user_gte = times.pop("$gte", None)
    user_lt = times.pop("$lt", None)
    rollup = data.rollup
  
  return API_LIMIT, user_limit, skip, user_gte, user_lt, rollup
