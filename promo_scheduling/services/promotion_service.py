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
        partner_service: PartnerService,
        database_adapter: PDatabaseAdapter,
    ) -> "PromotionService":
        promotions = []

        for partner in partner_service.partners:
            for mechanic in partner.mechanics:
                promotion = Promotion(partner, mechanic, database_adapter)
                promotions.append(promotion)
        return cls(promotions)
