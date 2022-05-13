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
from typing import Union, IO, Callable
from collections import defaultdict

def __default_numerical__(value):
    return float(value.replace(" ", ""))

def __identity__(value):
    return value

def __clean_name__(name):
    return name.lower().replace(" ", "_").replace("-", "_").replace("/","_")

def __read_all__(reader, transforms, time_index):
    res = defaultdict(list)
    times = []
    for row in reader:
        list_keys = list(row.keys())

        for idx, key in enumerate(list_keys):
            transform_function = __identity__
            
            if idx in transforms:
                transform_function = transforms[idx]
            else:
                if idx != time_index:
                    transform_function = __default_numerical__
            
            old_value = row[key]
            row[key] = transform_function(old_value)
        for idx, key in enumerate(list_keys):
            if idx!=time_index:
                res[key].append(row[key])
        times.append(row[list_keys[time_index]])
    return res, times

class CsvReader:
    def __init__(self, source : Union[IO, str] ):
        self.source = source
        self.data = None
        self.times = None

    def read_csv(self, delimiter="," , time_index_column=0, time_converter=None,
    values_converter=None, *args, **kwds):
        reader = None
        converters = dict()
        if values_converter is not None:
            converters = values_converter
        if time_converter is not None:
            time_converter_dict={time_index_column : time_converter}
            if converters is None:
                converters = time_converter_dict
            else:
                converters.update(time_converter_dict)
        
        if isinstance(self.source, str):
            with open(self.source, newline='') as csvfile:
                reader = csv.DictReader(csvfile, *args, delimiter=delimiter, skipinitialspace=True, **kwds)
                self.data, self.times = __read_all__(reader, converters, time_index_column)
        if isinstance(self.source, IO):
            reader = csv.DictReader(csvfile, *args, delimiter=delimiter, skipinitialspace=True, **kwds)
            self.data, self.times = __read_all__(reader, converters, time_index_column)
       
    def insert_csv_data(self, client : ClarifyClient, labels_dict=None):
        signals = []
        input_ids = []
        insert_data = {}
        return_default={"msg":"No data added"}
        if self.data is not None:
            for idx, key in enumerate(self.data.keys()):
                info = SignalInfo(name=key)
                if labels_dict is not None:
                    info.labels = labels_dict[idx]
                input_id = __clean_name__(key)
                input_ids.append(input_id)
                signals.append(info)
                insert_data[input_id]=self.data[key]
            
            return_save=client.save_signals(input_ids, signals, create_only=False)
            new_df = DataFrame(times=self.times, series=insert_data)
            return_insert=client.insert(new_df)
            return return_save, return_insert
        return return_default
