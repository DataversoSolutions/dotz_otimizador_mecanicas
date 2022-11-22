import configparser


class ConfigParser:
    weekdays = [
        "sunday",
        "monday",
        "tuesday",
        "wednesday",
        "thursday",
        "friday",
        "saturday",
    ]
    weeks = ["week1", "week2", "week3", "week4"]

    duration_days = ["D1", "D2", "D3", "D4", "D5", "D6", "D7", "D8", "ELSE"]

    def __init__(self, config_file_path):
        self.config = configparser.ConfigParser()
        self.config.read(config_file_path)

    @property
    def weekday_weights(self):
        weekday_weights = self.config["weekday_weights"]
        return [weekday_weights.getfloat(weekday) for weekday in self.weekdays]

    @property
    def week_weights(self):
        week_weights = self.config["week_weights"]
        return [week_weights.getfloat(week) for week in self.weeks]

    @property
    def duration_weights(self):
        durations = self.config["duration_weights"]
        return [durations.getfloat(day) for day in self.duration_days]

    @property
    def database_project(self):
        return self.config["database"]["PROJECT"]

    @property
    def database_dataset(self):
        return self.config["database"]["DATASET_ID"]

    @property
    def database_table(self):
        return self.config["database"]["TABLE_ID"]
