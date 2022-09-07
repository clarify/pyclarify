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

from datetime import datetime
from pydantic import BaseModel, Extra, validator
from pydantic.fields import Optional
from typing import ForwardRef, List, Dict
from pyclarify.__utils__.auxiliary import local_import
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
            if time_col:
                times = df[time_col].values
            else:
                times = df.index.values
            return cls(times=list(times), series=series)
        else:
            raise ValueError("Did not recognise input as Pandas DataFrame")

    @classmethod
    def merge(cls, dataframes) -> "DataFrame":
        """
        Method for merging 2 or more Clarify Data Frames. Mapping overlapping
        signal names to single series. Concatenates timestamps of all data frames.
        Inserts none value to series not containing entry at a given timestamp.

        Parameters
        ----------
        dataframes : List[DataFrame]
            A Clarify DataFrame or a list of Clarify DataFrames

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

        if not isinstance(dataframes, List):
            raise ValueError(
                "Input dataframes needs to be a list containing atleast one Clarify DataFrame"
            )

        for df in dataframes:
            if not isinstance(df, cls):
                raise ValueError(
                    f"Expected Clarify DataFrames in list but got {df.__class__()}"
                )
        signals = [key for df in dataframes for key in df.series.keys()]
        signals = list(set(signals))

        cdf_dict = {}
        for cdf in dataframes:
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
