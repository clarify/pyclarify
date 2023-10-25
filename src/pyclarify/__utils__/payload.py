"""
Copyright 2023 Searis AS

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
  #TODO: CLEAN UP THE MESS
  API_LIMIT = user_limit = skip = user_gte = user_lt = rollup = series= None
  query = getattr(request.params, "query") if hasattr(request.params, "query") else None
  user_limit = getattr(query, "limit") if hasattr(query, "limit") else None
  skip = getattr(query, "skip") if hasattr(query, "skip") else 0

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

  if request.method == ApiMethod.evaluate:
    API_LIMIT = 50
    data = request.params.data
    times = data.filter["times"]
    user_gte = times.pop("$gte", None)
    user_lt = times.pop("$lt", None)
    series = data.filter["series"]["$in"] if "series" in data.filter.keys() else None
    rollup = data.rollup
    user_limit = len(request.params.items)



  return API_LIMIT, user_limit, skip, user_gte, user_lt, rollup, series
