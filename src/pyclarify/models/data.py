"""
Copyright 2021 Clarify

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

from pydantic import BaseModel, constr, validate_arguments, Extra
from pydantic.fields import Optional
from typing import List, Union, Dict
from typing_extensions import Literal
from datetime import datetime, timedelta
import logging
from enum import Enum
from pyclarify.__utils__.convert import timedelta_isoformat, time_to_string
from pyclarify.__utils__.auxiliary import local_import

# constrained string defined by the API
InputID = constr(regex=r"^[a-z0-9_-]{1,40}$")
ResourceID = constr(regex=r"^[a-v0-9]{20}$")
LabelsKey = constr(regex=r"^[A-Za-z0-9-_/]{1,40}$")
AnnotationKey = constr(regex=r"^[A-Za-z0-9-_/]{1,40}$")
NumericalValuesType = List[Union[float, int, None]]
SHA1Hash = constr(regex=r"^[0-9a-f]{5,40}$")


class DataFrame(BaseModel):
    times: List[datetime] = None
    series: Dict[InputID, NumericalValuesType] = None

    def to_pandas(self):
        """Convert the instance into a pandas DataFrame.

        Returns:
            pandas.DataFrame: The pandas DataFrame representing this instance.
        """

        pd = local_import("pandas")

        df = pd.DataFrame(self.series)
        df.index = self.times
        return df


@validate_arguments
def from_pandas(df, time_col=None):
    """Convert a pandas DataFrame into a Clarify DataFrame.

    Returns:
        pandas.DataFrame: The pandas DataFrame representing this instance.
    """
    pd = local_import("pandas")
    if isinstance(df, pd.DataFrame):
        series = df.to_dict(orient="list")
        if time_col:
            times = df[time_col].values.tolist()
        else:
            times = df.index.values.tolist()
        return DataFrame(times=times, series=series)
    else:
        return False


@validate_arguments
def merge(dataframes: List[DataFrame]):
    """
    Method for merging 2 or more Clarify Data Frames. Mapping overlapping
    signal names to single series. Concatenates timestamps of all data frames.
    Inserts none value to series not containing entry at a given timestamp.

    Parameters
    ----------
    dataframes : List[DataFrame]
       List of Clarify Data Frames

    Returns
    -------
    DataFrame : DataFrame
        Merged data frame of all input data frames
    """
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

    return DataFrame(times=times, series=series)


class DataQuery(BaseModel, extra=Extra.forbid):
    include: bool = False
    notBefore: Optional[datetime]
    before: Optional[datetime]
    rollup: Union[timedelta, Literal["window"]] = None


class ResourceQuery(BaseModel, extra=Extra.forbid):
    include: bool = False
    filter: dict  # TODO: ResourceFilter (https://docs.clarify.io/v1.1/reference/filtering)
    limit: int = (
        0  # select_items: max=50, default=10 | select_signal: max=1000, default=50
    )
    skip: int = 0


class GenericSummary(BaseModel, extra=Extra.forbid):
    id: ResourceID
    created: bool


class InsertSummary(GenericSummary, extra=Extra.forbid):
    pass


class SaveSummary(GenericSummary, extra=Extra.forbid):
    updated: bool


class TypeSignal(str, Enum):
    numeric = "numeric"
    enum = "enum"


class SourceTypeSignal(str, Enum):
    measurement = "measurement"
    aggregation = "aggregation"
    prediction = "prediction"


class SignalInfo(BaseModel):
    name: str
    type: TypeSignal = TypeSignal.numeric
    description: str = ""
    labels: Dict[LabelsKey, List[str]] = {}
    annotations: Dict[AnnotationKey, str] = {}
    engUnit: str = ""
    enumValues: Dict[str, str] = {}
    sourceType: SourceTypeSignal = SourceTypeSignal.measurement
    sampleInterval: timedelta = None
    gapDetection: timedelta = None

    class Config:
        json_encoders = {
            timedelta: timedelta_isoformat,
            datetime: time_to_string
            }
        extra = Extra.forbid


class ResourceMetadata(BaseModel):
    contentHash: SHA1Hash
    updatedAt: datetime
    createdAt: datetime


class Signal(SignalInfo):
    item: Union[ResourceID, None]
    inputId: InputID
    meta: ResourceMetadata


class Item(SignalInfo):
    visible: bool = False
