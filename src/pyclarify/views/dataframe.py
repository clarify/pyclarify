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

from itertools import compress
from datetime import datetime
from pydantic import BaseModel, Extra, validator
from pydantic.fields import Optional
from typing import ForwardRef, List, Dict
from pyclarify.__utils__.auxiliary import local_import
from pyclarify.__utils__.time import is_datetime
from pyclarify.fields.constraints import (
    InputID,
    ResourceID,
    IntegrationID,
    NumericalValuesType,
)
from pyclarify.query.query import ResourceQuery, DataQuery


DataFrame = ForwardRef("DataFrame")


class DataFrame(BaseModel):
    """
    DataFrame structure maps to data structure used in the API for saving time series.
    Supports merging with other Clarify DataFrame objects and can convert to and from Pandas.DataFrame.

    Parameters
    ----------
        series: Dict[InputID, List[Union[None, float, int]]]
            Map of inputid to Array of data points to insert by Input ID.
            The length of each array must match that of the times array.
            To omit a value for a given timestamp in times, use the value null.

        times:  List of timestamps
            Either as a python datetime or as YYYY-MM-DD[T]HH:MM[:SS[.ffffff]][Z or [±]HH[:]MM]]] to insert.
    Example
    -------
        >>> from pyclarify import DataFrame
        >>> data = DataFrame(
        ...     series={"INPUT_ID_1": [1, 2], "INPUT_ID_2": [3, 4]},
        ...     times=["2021-11-01T21:50:06Z",  "2021-11-02T21:50:06Z"]
        ... )

    """

    times: List[datetime] = None
    series: Dict[InputID, NumericalValuesType] = None

    @validator("series", allow_reuse=True)
    def convert_numpy_to_native(cls, v):
        if isinstance(v, Dict):
            for key, value in v.items():
                v[key] = [None if x != x else x for x in value]
        return v

    def to_pandas(self):
        """Convert the instance into a pandas DataFrame.

        Returns
        -------
            pandas.DataFrame: The pandas DataFrame representing this instance.

        Example
        -------

            >>> from pyclarify import DataFrame
            >>> data = DataFrame(
            ...     series={"INPUT_ID_1": [1, 2], "INPUT_ID_2": [3, 4]},
            ...     times=["2021-11-01T21:50:06Z",  "2021-11-02T21:50:06Z"]
            ... )
            >>> data.to_pandas()
            ...                            INPUT_ID_1  INPUT_ID_2
            ... 2021-11-01 21:50:06+00:00         1.0         3.0
            ... 2021-11-02 21:50:06+00:00         2.0         4.0


        """
        pd = local_import("pandas")

        df = pd.DataFrame(self.series)
        df.index = self.times
        return df

    @classmethod
    def from_dict(cls, data, time_col=None):
        keys = list(data.keys())
        if time_col:
            times = data[time_col]
            time_keys = [time_col]
        else:
            import warnings
            warnings.warn("No obvious time index! Attempting to select based on data.", stacklevel=2)
            possible_indexes = [is_datetime(data[k][0]) for k in keys]
            if sum(possible_indexes) == 0:
                raise ValueError("No time variable in the data. Can not convert.")
            time_keys = list(compress(keys, possible_indexes))
            if sum(possible_indexes) > 1:
                raise ValueError(f"Unambiguous time index! {time_keys} could be index. Use `time_col` variable or set time to index.")
            times=data[time_keys[0]]
            warnings.warn(f'Choosing "{time_keys[0]}" as time axis.', stacklevel=2)
        try:
            return DataFrame(times=times, series={key: data[key] for key in keys if key not in time_keys})
        except:
            raise ValueError("Could not parse dictionary")

    @classmethod
    def from_pandas(cls, df, time_col=None):
        """Convert a pandas DataFrame into a Clarify DataFrame.
        
        Parameters
        ----------
        df: pandas.DataFrame
            The pandas.DataFrame object to cast to pyclarify.DataFrame.

        time_col: str, default None
            A string denoting the column containing the time axis. If no string is given it is assumed to be the index of the DataFrame.

        Returns
        -------
            pyclarify.DataFrame: The Clarify DataFrame representing this instance.

        Example
        -------
                
            >>> from pyclarify import DataFrame
            >>> import pandas as pd
            >>> df = pd.DataFrame(data={"INPUT_ID_1": [1, 2], "INPUT_ID_2": [3, 4]})
            >>> df.index = ["2021-11-01T21:50:06Z",  "2021-11-02T21:50:06Z"]
            >>> DataFrame.from_pandas(df)
            ... DataFrame(
            ...     times=[
            ...         datetime.datetime(2021, 11, 1, 21, 50, 6, tzinfo=datetime.timezone.utc), 
            ...         datetime.datetime(2021, 11, 2, 21, 50, 6, tzinfo=datetime.timezone.utc)], 
            ...     series={
            ...         'INPUT_ID_1': [1.0, 2.0], 
            ...         'INPUT_ID_2': [3.0, 4.0]
            ...     }
            ... )

            With specific time column.
            
            >>> from pyclarify import DataFrame
            >>> import pandas as pd
            >>> df = pd.DataFrame(data={
            ...     "INPUT_ID_1": [1, 2], 
            ...     "INPUT_ID_2": [3, 4],
            ...     "timestamps": ["2021-11-01T21:50:06Z",  "2021-11-02T21:50:06Z"]
            ...})
            >>> DataFrame.from_pandas(df, time_col="timestamps")
            ... DataFrame(
            ...     times=[
            ...         datetime.datetime(2021, 11, 1, 21, 50, 6, tzinfo=datetime.timezone.utc), 
            ...         datetime.datetime(2021, 11, 2, 21, 50, 6, tzinfo=datetime.timezone.utc)], 
            ...     series={
            ...         'INPUT_ID_1': [1.0, 2.0], 
            ...         'INPUT_ID_2': [3.0, 4.0]
            ...     }
            ... )

        """

        pd = local_import("pandas")
        if isinstance(df, pd.DataFrame):
            series = df.to_dict(orient="list")
        if isinstance(df, pd.Series):
            if df.name is not None:
                series =  {df.name : list(df.values)}
            else:
                raise ValueError("The series you are converting does not have a name.")

        if time_col:
            times = df[time_col].values
            series.pop(time_col)
        else:
            if is_datetime(df.index.values[0]):
                times = df.index.values
            else:
                import warnings
                warnings.warn("No obvious time index! Attempting to select based on data.", stacklevel=2)
                possible_indexes = [is_datetime(c) for c in df.values[0]]
                if sum(possible_indexes) == 0:
                    raise ValueError("No time variable in the data. Can not convert.")
                col = df.columns[possible_indexes]
                if sum(possible_indexes) > 1:
                    raise ValueError(f"Unambiguous time index! {list(df.columns[possible_indexes])} could be index. Use `time_col` variable or set time to index.")
                else:
                    times = df[col[0]].values
                    series.pop(col[0])
                warnings.warn(f'Choosing "{col[0]}" as time axis.', stacklevel=2)
        return cls(times=list(times), series=series)

    @classmethod
    def merge(cls, data_frames) -> "DataFrame":
        """
        Method for merging 2 or more Clarify Data Frames. Mapping overlapping
        signal names to single series. Concatenates timestamps of all data frames.
        Inserts none value to series not containing entry at a given timestamp.

        Parameters
        ----------
        data_frames : List[DataFrame]
            A Clarify DataFrame or a list of Clarify Data_Frames

        Returns
        -------
        DataFrame : DataFrame
            Merged data frame of all input data frames and self

        Example
        -------

            Merging two data frames.

            >>> df1 = DataFrame(
            ...     series={"INPUT_ID_1": [1, 2], "INPUT_ID_2": [3, 4]},
            ...     times=["2021-11-01T21:50:06Z",  "2021-11-02T21:50:06Z"]
            ... )
            >>> df2 = DataFrame(
            ...     series={"INPUT_ID_1": [5, 6], "INPUT_ID_3": [7, 8]},
            ...     times=["2021-11-01T21:50:06Z",  "2021-11-03T21:50:06Z"]
            ... )
            >>> merged_df = DataFrame.merge([df1, df2])
            >>> merged_df.to_pandas()
            ...                            INPUT_ID_2  INPUT_ID_1  INPUT_ID_3
            ... 2021-11-01 21:50:06+00:00         3.0         5.0         7.0
            ... 2021-11-02 21:50:06+00:00         4.0         2.0         NaN
            ... 2021-11-03 21:50:06+00:00         NaN         6.0         8.0

        Warning
        -----

            Notice from the example above that when time series have overlapping timestamps the last data frame overwrites the first. 

            >>> df1 = DataFrame(
            ...     series={"INPUT_ID_1": [1, 2]},
            ...     times=["2021-11-01T21:50:06Z",  "2021-11-02T21:50:06Z"]
            ... )
            >>> df2 = DataFrame(
            ...     series={"INPUT_ID_1": [5, 6]},
            ...     times=["2021-11-01T21:50:06Z",  "2021-11-03T21:50:06Z"]
            ... )
            >>> DataFrame.merge([df1, df2])
            ...                             INPUT_ID_1
            ... 2021-11-01 21:50:06+00:00         5.0   <--
            ... 2021-11-02 21:50:06+00:00         2.0
            ... 2021-11-03 21:50:06+00:00         6.0
            >>> DataFrame.merge([df2, df1])
            ...                             INPUT_ID_1
            ... 2021-11-01 21:50:06+00:00         1.0   <--
            ... 2021-11-02 21:50:06+00:00         2.0
            ... 2021-11-03 21:50:06+00:00         6.0
        """

        if not isinstance(data_frames, List):
            raise ValueError(
                "The input data frames needs to be a list containing at least one Clarify DataFrame"
            )

        for df in data_frames:
            if not isinstance(df, cls):
                raise ValueError(
                    f"Expected Clarify Data_Frames in list but got {df.__class__()}"
                )
        signals = [key for df in data_frames for key in df.series.keys()]
        signals = list(set(signals))

        cdf_dict = {}
        for cdf in data_frames:
            for signal, values in list(cdf.series.items()):
                for value, time in zip(values, cdf.times):
                    cdf_dict.setdefault(time, []).append((signal, value))

        times = sorted(list(cdf_dict.keys()))

        # make sure not to reference pointers
        signal_values = [[None] * len(times) for i in range(len(signals))]

        for i, time in enumerate(times):
            for value in cdf_dict[time]:
                signal_values[signals.index(value[0])][i] = value[1]

        series = {}
        for signal, values in zip(signals, signal_values):
            series[signal] = values

        return cls(times=times, series=series)

    def __add__(self, other):
        try:
            data = DataFrame.merge([self, other])
            return data
        except TypeError as e:
            raise TypeError(source=self, other=other) from e


DataFrame.update_forward_refs()


class InsertParams(BaseModel):
    """
    :meta private:
    """
    integration: IntegrationID
    data: DataFrame


class CreateSummary(BaseModel, extra=Extra.forbid):
    """
    :meta private:
    """
    id: ResourceID
    created: bool


class InsertResponse(BaseModel, extra=Extra.forbid):
    """
    :meta private:
    """
    signalsByInput: Dict[InputID, CreateSummary]


class DataFrameParams(BaseModel):
    """
    :meta private:
    """
    query: Optional[ResourceQuery] = {}
    data: Optional[DataQuery] = {}
    include: Optional[List[str]] = []
    groupIncludedByType: bool = True
