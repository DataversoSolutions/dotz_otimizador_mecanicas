import os
from promo_scheduling.services.config_parser import ConfigParser
from pathlib import Path

APP_NAME = "dotz_promo_scheduling"

conf_file_path = f"{Path(__file__).parent}/conf.ini"

conf = ConfigParser(conf_file_path)

WEEKDAY_INDEX = {
    "domingo": 0,
    "segunda": 1,
    "terça": 2,
    "quarta": 3,
    "quinta": 4,
    "sexta": 5,
    "sábado": 6,
}
