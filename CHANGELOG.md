# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

The changelog for SDK version 0.x.x can be found here.

Changes are grouped as follows

- `Added` for new features.
- `Changed` for changes in existing functionality.
- `Deprecated` for soon-to-be removed features.
- `Removed` for now removed features.
- `Fixed` for any bug fixes.
- `Security` in case of vulnerabilities.

# [0.2.0] - 2021-11-22

## Added

- Added methods to APIClient for the Admin API.
- Restructured the Pydantic models into Request and Response types.

# [0.2.1] - 2021-11-23

## Added

- Copyright
- `pyclarify.models.response.Response` encapsulating all response types.

# [0.2.2] - 2021-11-23

## Fixed

- Fix import dependency for python version 3.7.

# [0.3.0] - 2022-02-04

## Added

- Iterators for sending multiple JSONRPC requests, constrained by API limits.
- `pyclarify.client.ClarifyClient` containing all methods supported by `APIClient`, but written in a pythonic manner.
- `pyclarify.data.DataFrame` now has `to_pandas()` and `from_pandas()` methods.
- `pyclarify.data.Item` class supporting `visible` attribute.
-

## Fix

- Docstrings on several methods in `pyclarify.client.py`.

## Changed

- `pyclarify.models.requests.PublishSignalsParams` changed type attribute from `SignalInfo` to `Item`.

# [0.3.1] - 2022-04-01

## Fixed

- Update versioning of API to 1.1beta1 (All prior versions of SDK will not work due API version 1.1 introducing non backwards compatible changes).

# [0.3.2] - 2022-04-01

## Fixed

- Hotfix bug in version header.

# [0.3.3] - 2022-04-26

## Changed

- Renamed file `convert.py` to `time.py`.
- Refactored `pagination.GetDates` and changed name to `pagination.TimeIterator`.
- Refactored `pagination.GetItems` and changed name to `pagination.ItemIterator`.
- Minor changes to names in `time.py` to be more precise.
- Refactored `@iterator` wrapper to use said iterators.
- `pyclarify.client.make_request()` now uses iterator and is only method for sending requests.
- Extended `models.response.Response` to handle add operation.
- Refactored return on all methods in `client.ClarifyClient` and `client.APIClient`.

## Removed

- `pyclarify.__utils__.convert.str_to_datetime()`
- `pyclarify.client.pretty_response()`
- `pyclarify.client.iterate_bool()`
- `pyclarify.client.send_simple()`
- `pyclarify.client.send_iter()`

## Added

- RFC3339 to time delta function in time.py.
- `__add__()` functionality to SelectItemsResponse model and GenericResponse model.
- Filter model to create filters and combining them.
  Filter is based on MongoDB filters and works as described in [the docs](https://docs.clarify.io/api/1.1beta1/methods/filter-syntax).

  Usage:

  ```python
  from pyclarify import filter

  f1 = filter.Filter(fields={"name": filter.NotEqual(value="Lufttemperatur")})
  f2 = filter.Filter(fields={"labels.unit-type": filter.NotIn(value=["Fl??te", "Merde 5"])})

  f1.to_query()
  >>> {'name': {'$ne': 'Lufttemperatur'}}

  f3 = f1 & f2
  f3.to_query()
  >>> {
  >>>     '$and': [
  >>>         {'name': {'$ne': 'Lufttemperatur'}},
  >>>         {'labels.unit-type': {'$nin': ['Fl??te', 'Merde 5']}}
  >>>     ]
  >>>}
  ```

  Complete list of operators:

  - Equal
  - NotEqual
  - Regex
  - In
  - NotIn
  - LessThan
  - GreaterThan
  - GreaterThanOrEqual

- Exception class for `FilterError` and `TypeError` both located in `__utils__.exceptions`.

## Fixed

- Validator on `models.data.DataFrame` now converts `numpy.nan` to native python `none` .
- `annotations` field on `models.data.SignalInfo` is now optional.

# [0.3.4] - 2022-04-27

## Added

- `pyclarify.client.ClarifyClient.select_items()` using `query.Filter` model.
- `pyclarify.client.ClarifyClient.select_signals_filter()` using `query.Filter` model. NB! Will be renamed `pyclarify.client.ClarifyClient.select_signals()` in the future and replace current `select_signals()` method.
- Deprication warning module in `pyclarify.__utils__.warnings`

## Changed

- Replaced custom time parse methods with `pydantic.datetime_parse` methods.
- ContentHash is constrained as plain string and not SHA1.

## Deprecated

- `pyclarify.client.ClarifyClient.select_items_metadata()`
- `pyclarify.client.ClarifyClient.select_items_data()`
- `pyclarify.client.ClarifyClient.select_signals()`
- `pyclarify.client.APIClient`

# [0.3.5] - 2022-05-13

## Fixed

- Adding `insert` method to `pyclarify.client.ClarifyClient`
