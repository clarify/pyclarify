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
from typing import ForwardRef, List, Dict, Union
from pyclarify.__utils__.auxiliary import local_import
from pyclarify.fields.constraints import InputID, ResourceID, IntegrationID, NumericalValuesType, ResourceMetadata
from pyclarify.query.query import ResourceQuery, DataQuery

DataFrame = ForwardRef("DataFrame")


class DataFrame(BaseModel):  # <- Views
    times: List[datetime] = None
    series: Dict[InputID, NumericalValuesType] = None

    @validator("series", allow_reuse=True)
    def convert_numpy_to_native(cls, v):
        if isinstance(v, Dict):
            for key, value in v.items():
                v[key] = [None if x != x else x for x in value]
        return v

    # @validator("times", allow_reuse=True)
    # def remove_timezone_information(cls, v):
    #     return [time.replace(tzinfo=None) for time in v]

    def to_pandas(self):
        """Convert the instance into a pandas DataFrame.

        Returns:
            pandas.DataFrame: The pandas DataFrame representing this instance.
        """
        pd = local_import("pandas")

        df = pd.DataFrame(self.series)
        df.index = self.times
        return df

    @classmethod
    def from_pandas(cls, df, time_col=None):
        """Convert a pandas DataFrame into a Clarify DataFrame.

        Returns:
            pyclarify.DataFrame: The Clarify DataFrame representing this instance.
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
    def merge(cls, dataframes) -> 'DataFrame':
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
        """

        if not isinstance(dataframes, List):
            raise ValueError("Input dataframes needs to be a list containing atleast one Clarify DataFrame")

        for df in dataframes:
            if not isinstance(df, cls):
                raise ValueError(f"Expected Clarify DataFrames in list but got {df.__class__()}")
        signals = [key for df in dataframes for key in df.series.keys()]
        signals = list(set(signals))

        cdf_dict = {}
        for cdf in dataframes:
            for signal, values in list(cdf.series.items()):
                for value, time in zip(values, cdf.times):
                    cdf_dict.setdefault(time, []).append((signal, value))

        times = sorted(list(cdf_dict.keys()))

        # make sure not to refrence pointers
        signal_values = [[None] * len(times) for i in range(len(signals))]

        for i, time in enumerate(times):
            for value in cdf_dict[time]:
                signal_values[signals.index(value[0])][i] = value[1]

        series = {}
        for signal, values in zip(signals, signal_values):
            series[signal] = values

        return cls(times=times, series=series)


DataFrame.update_forward_refs()


class InsertParams(BaseModel):
    integration: IntegrationID
    data: DataFrame


class InsertSummary(BaseModel, extra=Extra.forbid):
    id: ResourceID
    created: bool


class InsertResponse(BaseModel, extra=Extra.forbid):
    signalsByInput: Dict[InputID, InsertSummary]


class SelectDataFrameParams(BaseModel):
    query: Optional[ResourceQuery] = {}
    data: Optional[DataQuery] = {}
    include: Optional[List[str]] = []
    groupIncludedByType: Optional[bool] = False

class SelectDataFrameResponse(BaseModel, extra=Extra.forbid):
    meta: Dict = {}
    data: DataFrame
    included: Optional[Union[Dict, List]]
