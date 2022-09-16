from promo_scheduling.entities.entity import SystemSettings


def get_system_settings(input_data):
    system_config_data = input_data['configuracoes_do_sistema']
    return SystemSettings(min_duration=system_config_data['mecanicas']['dias_duracao_minima'])
