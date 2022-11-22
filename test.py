import requests

data = {
    "configuracoes_do_sistema": {"mecanicas": {"dias_duracao_minima": 3}},
    "mecanicas": [
        {"id": "DZ_2", "dias_disponiveis": 28},
        {"id": "DZ_4", "dias_disponiveis": 4},
        {"id": "DZ_8", "dias_disponiveis": 3},
    ],
    "parceiros": [
        {"id": "AMAZON", "dias_possiveis": 7},
        {"id": "Magazine Luiza.com", "dias_possiveis": 7},
        {"id": "Americanas.com", "dias_possiveis": 7},
        {"id": "Submarino", "dias_possiveis": 7},
    ],
    "mecanicas_elegiveis": None,
}

response = requests.post("http://localhost:5000/v1/promo_scheduling", json=data)
print_msg = response.content.decode("unicode-escape")
print(print_msg)
