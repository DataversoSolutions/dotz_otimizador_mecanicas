from typing import List
from promo_scheduling.entities.entity import Partner
from promo_scheduling.entities.entity import Mechanic


class PartnerService:
    def __init__(self, partners: List[Partner]) -> None:
        self.partners = partners
        self.partners_map = self.create_partners_map(self.partners)

    def create_partners_map(self, partners: List[Partner]):
        return {partner.name: partner for partner in partners}

    def get_partner_by_name(self, name):
        return self.partners_map[name]

    @classmethod
    def load_from_input(cls, input_data) -> "PartnerService":
        partners_input = input_data["parceiros"]
        partners = []
        for partner_input in partners_input:
            mechanics_input = partner_input["mecanicas"]
            mechanics = []
            for mechanic_input in mechanics_input:
                mechanic = Mechanic(
                    name=mechanic_input["id"],
                    availability=mechanic_input["dias_disponiveis"],
                )
                mechanics.append(mechanic)
            partner = Partner(
                name=partner_input["id"],
                availability=partner_input["dias_possiveis"],
                mechanics=mechanics,
            )
            partners.append(partner)
        return cls(partners)
