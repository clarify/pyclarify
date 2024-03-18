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

## [0.6.4] - 2024-09-16

### Added

- Added group parameter in experimental client.

## [0.6.3] - 2024-03-12

### Fixed

- Fixed json decoding bug in in Pydantic where special characters where not serialized correctly. More specifically two byte characters would be read as 1 byte, resulting in incorrect content length.

## [0.6.2] - 2024-03-12

### Fixed

- Fixed json decoding bug in JSONRPC client where execution would crash on non 200-range response.

## [0.6.1] - 2024-03-04

### Added

- Experimental folder with experimental features. Experimental features might be added to stable or removed.

## [0.6.0] - 2024-02-27

### Changed

- Bumping pydantic version from 1.10 to 2.6.0.
- Removed specific versioning of other dependencies.

### Security

- Python 3.7 reached upstream end-of-life on June 27th, 2023, and no longer receives security or bug fixes. Removing Python 3.7 from build order.

### Removed

- typing_extensions support is removed, due to Python 3.7 no longer being supported.

## [0.5.0] - 2023-10-10

### Added

- New Evaluate endpoint. A data method for aggregating time-series data and perform evaluate formula expressions. Along with support classes for validation.

  ```python
  from pyclarify import ItemAggregation, Calculation

  item1 = ItemAggregation(
      id="cbpmaq6rpn52969vfl00",
      aggregation="max",
      alias="i1"
  )

  item2 = ItemAggregation(
      id="cbpmaq6rpn52969vfl0g",
      aggregation="avg",
      alias="i2"
  )

  items = [
      item1, item2
  ]


  step1 = Calculation(
      formula="i1 * i2",
      alias="c1"
  )

  step2 = Calculation(
      formula="gapfill(i1) / c1",
      alias="c2"
  )

  calculations = [step1, step2]

  r = client.evaluate(
      items=items,
      calculations=calculations,
      gte="2023-10-01T00:00:00Z",
      lt="2023-10-23T00:00:00Z",
      include=["items"],
      rollup="PT10M"
  )

  >>> r.result.data.to_pandas()
  ...                                   c1        c2   i1        i2
  ... 2023-10-20 10:20:00+00:00  21.333333  0.281250  6.0  3.555556
  ... 2023-10-20 10:30:00+00:00  42.428571  0.212121  9.0  4.714286
  ... 2023-10-20 10:40:00+00:00  36.363636  0.220000  8.0  4.545455
  ```

### Changed

- API version changed from 1.1beta2 to 1.1.
- Changes to internal models to comply with new models in the API.
- Added `origin`, `timeZone`, and `firstDayOfWeek` parameters to `pyclarify.Client.data_frame` method, allowing higher control of rollup options.

### Fixed

- Typo in CONTRIBUTION.md.

## [0.4.5] - 2023-08-09

### Fixed

- Still experienced issues. Forced SDK to use pydantic.V1.

## [0.4.4] - 2023-08-09

### Fixed

- Fixed deprecated `Pydantic` dependency to the `pydantic.fields.Optional` resource. Changed all occurances to `typing.Optional`.

## [0.4.3] - 2023-02-20

### Added

- Added possibility to directly insert pd.DataFrame, pd.Series and dictionaries into Clarify. NB! Infers timestamp column and only supports when there only exists one timestamp column.
- Added possibility to directly insert dictionaries to `pyclarify.client.data_frame`, `pyclarify.client.select_signals`, and `pyclarify.client.select_items`.
- Added default timezone for general timestamp such as `datetime.today()`. This also applies to timestamps without explicit timezone.

### Fixed

- Fixed bug where the response was not JSON encoded causing error initialization to fail. Added more tests to check for such issues.
- Fixed bug where Filter did not allow dictionary without comparison as an input argument for the filter.
- Fixed included list containing multiple instances of same object.

## [0.4.2] - 2022-12-16

### Fixed

- Integration parameter in `SignalSelectView` is now optional, as it would break on some occations.
- More descriptive warning message when using `None` or `[None]` in `query.Filters`.

## [0.4.1] - 2022-10-11

### Added

- All select queries (`client.select_items`, `client.select_signals`) now supports a `None` limit to do an exhaustive query for all resources.
- Sanity checks for initializing `pyclarify.Client` with more descriptive errors.

## [0.4.0] - 2022-07-12

Changing to JSON:API format!

### Added

- `fields` folder containing all fields used internally.
- `views` folder containing all models for communicating with the API.
- `jsonrpc` folder containing all network functionality for the `ClarifyClient`.
- `pyclarify.query.filter.DataFilter` for filtering on DataFrames.
- `pyclarify.client.Client.data_frame()` for selecting DataFrames.

### Changed

- `pyclarify.client.ClarifyClient` renamed to `pyclarify.client.Client`
- Moved `ResourceQuery` and `DataQuery` models to `pyclarify.query.query`.
- Moved `Comparison` and `Operators` to `pyclarify.fields.query`.
- Moved `DataFrame` and all sub methods to `pyclarify.views.dataframe`.
- `merge`, `to_pandas` and `from_pandas` methods are now class methods on the `pyclarify.views.DataFrame` class.

  ```python
  from pyclarify import DataFrame

  series = {"signal_1" : [1, 2]}
  times = ["2021-11-01T21:50:06Z",  "2021-11-02T21:50:06Z"]
  df = DataFrame(series=series, times=times)

  panda_df = df.to_pandas()

  new_df = DataFrame.from_pandas(panda_df)

  merged = DataFrame.merge([df, new_df])
  ```

- `pyclarify.client.Client.select_items()` now responds with `JSON:API` format, and does not retrieve data frames.

  ```python
  client.select_items(
    filter = query.Filter(fields={"name": query.NotEqual(value="Air Temperature")}),
    skip = 0,
    limit = 10,
    sort = ["-id", "name"],
    total=True
  )
  ```

- `pyclarify.client.Client.select_signals()` replaced `pyclarify.client.ClarifyClient.select_signals_filter()`.
- `pyclarify.client.Client.select_signals()` now responds with `JSON:API` format.

  ```python
    client.select_signals(
      filter = Filter(fields={"name": filter.NotEqual(value="Air Temperature")}),
      limit = 10,
      skip = 0,
      sort = ["-id"],
      total= True,
      include = ["item"]
    )
  ```

- `GetToken` method renamed to `Authenticator`.
- `pyclarify.jsonrpc.pagination.ItemIterator` renamed to `SelectIterator` and now paginates `select_signals`, `select_items` and `data_frame` methods.
- Fix bug where timestamps was not timezone aware.
- Fix bug where pagination was not applied correctly.

### Removed

- `pyclarify.client.APIClient`
- `pyclarify.client.Client.get_token()`
- `pyclarify.client.Client.select_items_metadata()`
- `pyclarify.client.Client.select_items_data()`
- `pyclarify.client.Client.select_signals_filter()`

## [0.3.5] - 2022-05-13

### Fixed

- Adding `insert` method to `pyclarify.client.ClarifyClient`

## [0.3.4] - 2022-04-27

### Added

- `pyclarify.client.ClarifyClient.select_items()` using `query.Filter` model.
- `pyclarify.client.ClarifyClient.select_signals_filter()` using `query.Filter` model. NB! Will be renamed `pyclarify.client.ClarifyClient.select_signals()` in the future and replace current `select_signals()` method.
- Deprication warning module in `pyclarify.__utils__.warnings`

### Changed

- Replaced custom time parse methods with `pydantic.datetime_parse` methods.
- ContentHash is constrained as plain string and not SHA1.

### Deprecated

- `pyclarify.client.ClarifyClient.select_items_metadata()`
- `pyclarify.client.ClarifyClient.select_items_data()`
- `pyclarify.client.ClarifyClient.select_signals()`
- `pyclarify.client.APIClient`

## [0.3.3] - 2022-04-26

### Changed

- Renamed file `convert.py` to `time.py`.
- Refactored `pagination.GetDates` and changed name to `pagination.TimeIterator`.
- Refactored `pagination.GetItems` and changed name to `pagination.ItemIterator`.
- Minor changes to names in `time.py` to be more precise.
- Refactored `@iterator` wrapper to use said iterators.
- `pyclarify.client.make_request()` now uses iterator and is only method for sending requests.
- Extended `models.response.Response` to handle add operation.
- Refactored return on all methods in `client.ClarifyClient` and `client.APIClient`.

### Removed

- `pyclarify.__utils__.convert.str_to_datetime()`
- `pyclarify.client.pretty_response()`
- `pyclarify.client.iterate_bool()`
- `pyclarify.client.send_simple()`
- `pyclarify.client.send_iter()`

### Added

- RFC3339 to time delta function in time.py.
- `__add__()` functionality to SelectItemsResponse model and GenericResponse model.
- Filter model to create filters and combining them.
  Filter is based on MongoDB filters and works as described in [the docs](https://docs.clarify.io/api/1.1beta1/methods/filter-syntax).

  Usage:

  ```python
  from pyclarify import filter

  f1 = filter.Filter(fields={"name": filter.NotEqual(value="Lufttemperatur")})
  f2 = filter.Filter(fields={"labels.unit-type": filter.NotIn(value=["Flåte", "Merde 5"])})

  f1.to_query()
  >>> {'name': {'$ne': 'Lufttemperatur'}}

  f3 = f1 & f2
  f3.to_query()
  >>> {
  >>>     '$and': [
  >>>         {'name': {'$ne': 'Lufttemperatur'}},
  >>>         {'labels.unit-type': {'$nin': ['Flåte', 'Merde 5']}}
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

### Fixed

- Validator on `models.data.DataFrame` now converts `numpy.nan` to native python `none` .
- `annotations` field on `models.data.SignalInfo` is now optional.

## [0.3.2] - 2022-04-01

### Fixed

- Hotfix bug in version header.

## [0.3.1] - 2022-04-01

### Fixed

- Update versioning of API to 1.1beta1 (All prior versions of SDK will not work due API version 1.1 introducing non backwards compatible changes).

## [0.3.0] - 2022-02-04

### Added

- Iterators for sending multiple JSONRPC requests, constrained by API limits.
- `pyclarify.client.ClarifyClient` containing all methods supported by `APIClient`, but written in a pythonic manner.
- `pyclarify.data.DataFrame` now has `to_pandas()` and `from_pandas()` methods.
- `pyclarify.data.Item` class supporting `visible` attribute.
-

### Fix

- Docstrings on several methods in `pyclarify.client.py`.

### Changed

- `pyclarify.models.requests.PublishSignalsParams` changed type attribute from `SignalInfo` to `Item`.

## [0.2.2] - 2021-11-23

### Fixed

- Fix import dependency for python version 3.7.

## [0.2.1] - 2021-11-23

### Added

- Copyright
- `pyclarify.models.response.Response` encapsulating all response types.

## [0.2.0] - 2021-11-22

### Added

- Added methods to APIClient for the Admin API.
- Restructured the Pydantic models into Request and Response types.
