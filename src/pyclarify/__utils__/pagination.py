from datetime import timedelta, datetime
from . import convert


class GetDates:
    def __init__(self, dates):
        self.dates = dates
        self.api_limit = (
            960  # limit in hours, the window can not be longer than 960 hours
        )
        self.count = 0

    def __iter__(self):
        self.not_before = convert.str_to_datetime(self.dates[0])
        self.before = convert.str_to_datetime(self.dates[1])
        self.hours = self.get_hours(self.not_before, self.before)
        return self

    def __next__(self):
        if self.hours > self.api_limit:
            self.new_not_before = self.not_before
            self.new_before = self.new_not_before + timedelta(
                seconds=self.api_limit * 3600
            )
            if self.new_before + timedelta(seconds=1) < convert.str_to_datetime(
                self.dates[1]
            ):
                self.not_before = self.new_before + timedelta(seconds=1)
                self.before = convert.str_to_datetime(self.dates[1])
                self.hours = self.get_hours(self.new_not_before, self.before)
                return self.new_not_before, self.new_before
            else:
                self.hours = self.get_hours(self.not_before, self.before)
                self.count += 1
                return self.not_before, self.before

        elif (self.hours <= self.api_limit) and self.count == 0:
            self.count += 1
            self.hours = self.get_hours(self.not_before, self.before)
            return self.not_before, self.before

        else:
            raise StopIteration

    def get_hours(self, not_before, before):
        dt = before - not_before
        return dt.days * 24 + dt.seconds / 3600


class GetItems:
    def __init__(self, limit, number_of_items, skip):
        self.number_of_items = number_of_items
        self.limit = limit
        self.skip = skip
        self.count_iter = -1
        self.count_remainder = 0

    def __iter__(self):
        self.current_items = self.number_of_items
        return self

    def __next__(self):
        if self.current_items > self.limit:
            self.current_items -= self.limit
            self.count_iter += 1

            if self.count_iter > 0:
                self.skip += self.limit

            return self.limit, self.skip

        elif self.current_items <= self.limit and self.count_remainder == 0:
            self.count_remainder += 1
            if self.count_iter > 0:
                self.skip += self.limit
            return self.current_items, self.skip

        else:
            raise StopIteration
