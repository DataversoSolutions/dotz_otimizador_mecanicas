from promo_scheduling.entities.entity import SystemSettings


def get_system_settings(input_data):
    system_config_data = input_data["configuracoes_do_sistema"]
    return SystemSettings(
        min_duration=system_config_data["mecanicas"]["dias_duracao_minima"],
        starting_week_day=system_config_data["mecanicas"]["dia_da_semana_inicial"],
        max_daily_promotions = system_config_data["mecanicas"]["maximo_promocoes_no_mesmo_dia"]
    )
