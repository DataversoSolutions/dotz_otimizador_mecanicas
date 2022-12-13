from dataclasses import dataclass
from typing import List
from promo_scheduling.services.database import PDatabaseAdapter
from ortools.sat.python import cp_model
from promo_scheduling.utils.weights_func import (
    get_week_weight,
    get_weekday_weight,
    get_duration_weight,
)


@dataclass
class SystemSettings:
    starting_week_day: int = 0
    min_duration: int = 3


@dataclass
class Mechanic:
    name: str
    availability: int


@dataclass
class Partner:
    name: str
    availability: int
    mechanics: list[Mechanic]


@dataclass
class Promotion:
    partner: Partner
    mechanic: Mechanic
    database_adapter: PDatabaseAdapter

    def get_productivity_ref(self):
        return self.database_adapter.productivity_base(
            self.partner.name, self.mechanic.name
        )


class Schedule:
    # 2d matrix
    #     duration
    # [[0, 0 ,0 ,0 ,0], <- if set, start at day 0
    #  [0, 0 ,0 ,0 ,0], <- if set, start at day 1
    #  [1, 1 ,0 ,0 ,0], <- if set, start at day 2
    #  [0, 0 ,0 ,0 ,0], <- if set, start at day 3
    #  [0, 0 ,0 ,0 ,0]] <- if set, start at day 4
    # this example means a duration of 2 days, starting at day 2
    schedule_array: List[List[cp_model.IntVar]]

    def __init__(self, name, model: cp_model.CpModel, num_days, promo_lenght):
        self.promo_lenght = promo_lenght
        self.num_days = num_days
        self.schedule_array = [
            [model.NewBoolVar(f"{name}_[{i},{j}]") for i in range(promo_lenght)]
            for j in range(num_days)
        ]

    def get_duration_array_at_day(self, day):
        return self.schedule_array[day]

    def get_day_flags_var(self):
        # return the first flag of the duration array
        return [duration[0] for duration in self.schedule_array]


@dataclass
class Assignment:
    id: str
    is_active: cp_model.IntVar
    not_is_active: cp_model.IntVar
    start: cp_model.IntVar
    end: cp_model.IntVar
    duration: cp_model.IntVar
    interval: cp_model.IntervalVar
    schedule: Schedule
    promotion: Promotion

    def __post_init__(self):
        self.prod_ref = self.promotion.get_productivity_ref()

    def get_productivity_at(self, zero_day_week_day, start_day, num_days_since_start):
        productivity = round(
            self.prod_ref
            * get_week_weight(start_day, num_days_since_start)
            * get_weekday_weight(zero_day_week_day, start_day, num_days_since_start)
            * get_duration_weight(num_days_since_start)
        )
        # print(
        #     f"{self.id}: {zero_day_week_day=} {start_day=} {num_days_since_start=} {productivity=}"
        # )
        return productivity

    def productivity(self, zero_day_week_day):
        ret = 0
        for starting_day, duration_array in enumerate(self.schedule.schedule_array):
            coefs = []
            for num_days in range(len(duration_array)):
                productivity = self.get_productivity_at(
                    zero_day_week_day=zero_day_week_day,
                    start_day=starting_day,
                    num_days_since_start=num_days,
                )
                coefs.append(productivity)
            ret += cp_model.LinearExpr.WeightedSum(duration_array, coefs)
        return ret
