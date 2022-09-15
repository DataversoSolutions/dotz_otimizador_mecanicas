from promo_scheduling.services import PromotionService, PartnerService, MechanicService, get_system_settings
from promo_scheduling.solver import MechanicPartnerAssignmentSolver
import yaml


def main():
    with open('input.yaml', 'r') as stream:
        input_data = yaml.safe_load(stream)
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
    solver.print_solution()
    solver.print_statistics()
    solver.export_model('gitignore_model.txt')


if __name__ == '__main__':
    main()
