from promo_scheduling.services.system_settings import get_system_settings
from promo_scheduling.services.promotion_service import PromotionService
from promo_scheduling.services.partner_service import PartnerService
from promo_scheduling.services.mechanic_service import MechanicService
from promo_scheduling.solver.solver import MechanicPartnerAssignmentSolver


def promo_scheduling(input_data):
    print(input_data)
    system_settings = get_system_settings(input_data)
    partner_service = PartnerService.load_from_input(input_data)
    mechanic_service = MechanicService.load_from_input(input_data)
    promo_service = PromotionService.load_from_input(
        input_data=input_data,
        partner_service=partner_service,
        mechanics_service=mechanic_service

    )
    solver = MechanicPartnerAssignmentSolver(
        possible_promotions=promo_service.promotions,
        partners=partner_service.partners,
        mechanics=mechanic_service.mechanics,
        system_settings=system_settings
    )
    solver.run()
    solution = solver.get_solution()
    return solution
