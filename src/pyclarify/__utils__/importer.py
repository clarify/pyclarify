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

import csv
from pyclarify import ClarifyClient, SignalInfo, DataFrame
from typing import Union, IO, Callable, Any, Dict, List, DefaultDict, Tuple
from collections import defaultdict


def __is_float__(element: Any) -> bool:
    try:
        float(element)
        return True
    except ValueError:
        return False


def __default_numerical__(value):
    return float(value.replace(" ", ""))


def __identity__(value):
    return value


def __clean_name__(name):
    return name.lower().replace(" ", "_").replace("-", "_").replace("/", "_")


def __read_all__(reader, transforms: Dict[int, Callable], time_index: int):
    res = defaultdict(list)
    times = []
    key_index = dict()
    enum_colums_index = dict()
    for row in reader:
        list_keys = list(row.keys())

        for idx, key in enumerate(list_keys):
            if idx == time_index:
                transform_function = __identity__
            else:
                if __is_float__(row[key]):
                    transform_function = __default_numerical__
                else:
                    ## treat as an enum, which default behavior is to convert the string into an int index
                    if idx not in enum_colums_index:
                        enum_colums_index[idx] = dict()
                    if row[key] not in enum_colums_index[idx]:
                        enum_colums_index[idx][row[key]] = len(enum_colums_index[idx])
                    transform_function = lambda x: enum_colums_index[idx][row[key]]

            if idx in transforms:
                transform_function = transforms[idx]

            old_value = row[key]

            row[key] = transform_function(old_value)
        for idx, key in enumerate(list_keys):
            if idx != time_index:
                key_index[idx] = key
                res[key].append(row[key])
        times.append(row[list_keys[time_index]])
    return res, times, key_index, enum_colums_index


class CsvImporter:
    """
    Reads a CSV file and import the data in the file to Clarify. The CSV file is expected to have
    a column with the timestamps, and other columns with timeseries data compatible with Clarify (floats, int or enum).

    Parameters
    ----------
    source: str/IO file
        str with path to a file, or an IO file

    """

    def __init__(self, source: Union[IO, str]):
        self.source = source
        self.data = None
        self.times = None
        self.time_index = 0
        self.cols_index = dict()
        self.enum_cols_index = dict()

    def read_csv(
        self,
        delimiter: str = ",",
        time_index_column: int = 0,
        time_converter: Callable = None,
        values_converter: Dict[int, Callable] = None,
        *args,
        **kwds
    ):
        """
        Reads the CSV file defined in self.source, using the parameters that defines the delimiters (default=","),
        the column index that is stored the timestamp data (default 0), a function to convert the timestamp data (default None),
        and list of functions to convert the other columns (default None). The method accepts other arguments general accepted
        by `csv.DictReader` https://docs.python.org/3/library/csv.html#csv.DictReader and passes them to
        the underlying DictReader object.

        Parameters
        ----------
        delimiter: str
            The delimiter used to separate columns in the CSV file.
        time_index_column: int
            The index of the column that contains the timestamp data.
        time_converter: function
            A function that converts the timestamp data to a datetime object.
        values_converter: Dict of functions
            A Dict of functions that converts the other columns to the custom data type.
            Indexed by the column index number in the original CSV (starting from 0)
        args:
            Other arguments that are passed to the underlying DictReader object.
        kwds:   dict
            Other keyword arguments that are passed to the underlying DictReader object.
        """
        reader = None
        converters = dict()
        self.time_index = time_index_column
        if values_converter is not None:
            converters = values_converter
        if time_converter is not None:
            time_converter_dict = {time_index_column: time_converter}
            if converters is None:
                converters = time_converter_dict
            else:
                converters.update(time_converter_dict)

        if isinstance(self.source, str):
            with open(self.source, newline="") as csvfile:
                reader = csv.DictReader(
                    csvfile, *args, delimiter=delimiter, skipinitialspace=True, **kwds
                )
                (
                    self.data,
                    self.times,
                    self.cols_index,
                    self.enum_cols_index,
                ) = __read_all__(reader, converters, time_index_column)
        if isinstance(self.source, IO):
            reader = csv.DictReader(
                csvfile, *args, delimiter=delimiter, skipinitialspace=True, **kwds
            )
            self.data, self.times, self.cols_index, self.enum_cols_index = __read_all__(
                reader, converters, time_index_column
            )

    def insert_csv_data(
        self, client: ClarifyClient, labels_dict: Dict[int, Dict[str, Any]] = None
    ):
        """
        Inserts the data read from the CSV file into Clarify using a ClarifyClient object, and custom_labels (default None).
        Should be called after reading the data using read_csv.

        Parameters
        ----------
        client: ClarifyClient
            The ClarifyClient object that is used to insert the data.
        labels_dict: dict
            A dictionary with the custom labels that are added as metadata indexed by the column index on the CSV file
            (each column being a different signal)
        """
        signals = []
        input_ids = []
        insert_data = {}
        return_default = {"msg": "No data added"}
        if self.data is not None:
            for idx in self.cols_index:
                key = self.cols_index[idx]
                info = SignalInfo(name=key)

                if labels_dict is not None:
                    info.labels = labels_dict[idx]
                if idx in self.enum_cols_index:
                    info.type = "enum"
                    info.enumValues = {
                        int_repr: string_repr
                        for string_repr, int_repr in self.enum_cols_index[idx].items()
                    }
                input_id = __clean_name__(key)
                input_ids.append(input_id)
                signals.append(info)
                insert_data[input_id] = self.data[key]

            return_save = client.save_signals(input_ids, signals, create_only=False)
            new_df = DataFrame(times=self.times, series=insert_data)
            return_insert = client.insert(new_df)
            return return_save, return_insert
        else:
            return_default = {
                "msg": "No data added. No data read. Call read_csv first."
            }
        return return_default
