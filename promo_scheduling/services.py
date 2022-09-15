from typing import List
from promo_scheduling.entity import Partner, Mechanic, Promotion, SystemSettings


class PartnerService:
    def __init__(self, partners: List[Partner]) -> None:
        self.partners = partners
        self.partners_map = self.create_partners_map(self.partners)

    def create_partners_map(self, partners: List[Partner]):
        return {partner.name: partner for partner in partners}

    def get_partner_by_name(self, name):
        return self.partners_map[name]

    @classmethod
    def load_from_input(cls, input_data) -> 'PartnerService':
        partners_input = input_data['parceiros']
        partners = []
        for partner_input in partners_input:
            partner = Partner(
                name=partner_input['id'],
                availability=partner_input['dias_possiveis']
            )
            partners.append(partner)
        return cls(partners)


class MechanicService:
    def __init__(self, mechanics: List[Mechanic]) -> None:
        self.mechanics = mechanics
        self.mechanics_map = self.create_mechanics_map(self.mechanics)

    def create_mechanics_map(self, mechanics: List[Mechanic]):
        return {mechanic.name: mechanic for mechanic in mechanics}

    def get_mechanic_by_name(self, name):
        return self.mechanics_map[name]

    @classmethod
    def load_from_input(cls, input_data) -> 'MechanicService':
        mechanics_input = input_data['mecanicas']
        mechanics = []
        for partner_input in mechanics_input:
            partner = Partner(
                name=partner_input['id'],
                availability=partner_input['dias_disponiveis']
            )
            mechanics.append(partner)
        return cls(mechanics)


class PromotionService:
    def __init__(self, promotions: List[Promotion]) -> None:
        self.promotions = promotions

    @classmethod
    def load_from_input(
        cls,
        input_data,
        partner_service: PartnerService,
        mechanics_service: MechanicService
    ) -> 'PromotionService':
        possible_promotions = input_data['mecanicas_elegiveis']
        listed_partners = []
        promotions = []
        if possible_promotions:
            for promotion in possible_promotions:
                partner_name = promotion['parceiro']
                listed_partners.append(partner_name)
                for mechanic_name in promotion['mecanicas']:
                    partner = partner_service.get_partner_by_name(partner_name)
                    mechanic = mechanics_service.get_mechanic_by_name(mechanic_name)
                    promotion = Promotion(
                        partner, mechanic
                    )
                    promotions.append(promotion)
        for partner in partner_service.partners:
            if partner.name in listed_partners:
                continue
            for mechanic in mechanics_service.mechanics:
                promotion = Promotion(partner, mechanic)
                promotions.append(promotion)
        return cls(promotions)


def get_system_settings(input_data):
    system_config_data = input_data['configuracoes_do_sistema']
    return SystemSettings(min_duration=system_config_data['mecanicas']['dias_duracao_minima'])
