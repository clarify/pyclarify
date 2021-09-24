from pydantic import BaseModel, constr, validate_arguments
from pydantic.fields import Optional
from typing import List, Union, Dict
from datetime import datetime, timedelta
import logging
from enum import Enum

# constrained string defined by the API
InputID = constr(regex=r"^[a-z0-9_-]{1,40}$")
LabelsKey = constr(regex=r"^[A-Za-z0-9-_/]{1,40}$")
AnnotationKey = constr(regex=r"^[A-Za-z0-9-_/]{1,40}$")
NumericalValuesType = List[Union[float, int, None]]


class DataFrame(BaseModel):
    times: List[datetime] = None
    series: Dict[InputID, NumericalValuesType] = None


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


class TypeSignal(str, Enum):
    numeric = "numeric"
    enum = "enum"


class SourceTypeSignal(str, Enum):
    measurement = "measurement"
    aggregation = "aggregation"
    prediction = "prediction"


class Signal(BaseModel):
    name: str
    type: TypeSignal = TypeSignal.numeric
    description: str = ""
    labels: Dict[LabelsKey, List[str]] = {}
    annotations: Dict[AnnotationKey, str] = {}
    engUnit: str = ""
    enumValues: Dict[str, str] = {}
    sourceType: SourceTypeSignal = SourceTypeSignal.measurement
    sampleInterval: Optional[timedelta] = None
    gapDetection: Optional[timedelta] = None
