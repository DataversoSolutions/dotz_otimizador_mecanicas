from typing import List
from promo_scheduling.entities.entity import Promotion
from promo_scheduling.services.partner_service import PartnerService
from promo_scheduling.services.mechanic_service import MechanicService
from promo_scheduling.services.database import PDatabaseAdapter


class PromotionService:
    def __init__(self, promotions: List[Promotion]) -> None:
        self.promotions = promotions

    @classmethod
    def load_from_input(
        cls,
        input_data,
        partner_service: PartnerService,
        mechanics_service: MechanicService,
        database_adapter: PDatabaseAdapter,
    ) -> "PromotionService":
        possible_promotions = input_data["mecanicas_elegiveis"]
        listed_partners = []
        promotions = []
        if possible_promotions:
            for promotion in possible_promotions:
                partner_name = promotion["parceiro"]
                listed_partners.append(partner_name)
                for mechanic_name in promotion["mecanicas"]:
                    partner = partner_service.get_partner_by_name(partner_name)
                    mechanic = mechanics_service.get_mechanic_by_name(mechanic_name)
                    promotion = Promotion(partner, mechanic, database_adapter)
                    promotions.append(promotion)
        for partner in partner_service.partners:
            if partner.name in listed_partners:
                continue
            for mechanic in mechanics_service.mechanics:
                promotion = Promotion(partner, mechanic, database_adapter)
                promotions.append(promotion)
        return cls(promotions)
