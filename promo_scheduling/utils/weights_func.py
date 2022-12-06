from promo_scheduling.settings import conf


def get_week_weight(start_day, num_days_since_start):
    week = (start_day + num_days_since_start) // 7
    weights = conf.week_weights
    # get the last value if its index is greater than the weights
    week = week if week < len(weights) else -1
    weight = conf.week_weights[week]
    return weight


def get_weekday_weight(zero_day_week_day, start_day):
    weekday = (zero_day_week_day + start_day) % 7
    weights = conf.weekday_weights
    return weights[weekday]


def get_duration_weight(num_days_since_start):
    weights = conf.duration_weights
    # get the last value if its index is greater than the weights
    duration = num_days_since_start if num_days_since_start < len(weights) else -1
    weight = weights[duration]
    return weight
