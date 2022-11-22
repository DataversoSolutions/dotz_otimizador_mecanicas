from typing import List
from promo_scheduling.entities.entity import Mechanic


class MechanicService:
    def __init__(self, mechanics: List[Mechanic]) -> None:
        self.mechanics = mechanics
        self.mechanics_map = self.create_mechanics_map(self.mechanics)

    def create_mechanics_map(self, mechanics: List[Mechanic]):
        return {mechanic.name: mechanic for mechanic in mechanics}

    def get_mechanic_by_name(self, name):
        return self.mechanics_map[name]

    @classmethod
    def load_from_input(cls, input_data) -> "MechanicService":
        mechanics_input = input_data["mecanicas"]
        mechanics = []
        for partner_input in mechanics_input:
            partner = Mechanic(
                name=partner_input["id"], availability=partner_input["dias_disponiveis"]
            )
            mechanics.append(partner)
        return cls(mechanics)
