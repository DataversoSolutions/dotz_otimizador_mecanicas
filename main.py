from promo_scheduling.services.system_settings import get_system_settings
from promo_scheduling.services.promotion_service import PromotionService
from promo_scheduling.services.partner_service import PartnerService
from promo_scheduling.solver.solver import MechanicPartnerAssignmentSolver
from promo_scheduling.services.database import BigqueryDatabaseAdapter
from promo_scheduling.settings import conf
import yaml


def main():
    with open("input.yaml", "r") as stream:
        input_data = yaml.safe_load(stream)
    print(input_data)
    database_adapter = BigqueryDatabaseAdapter(
        project=conf.database_project,
        dataset_id=conf.database_dataset,
        table_id=conf.database_table,
    )
    system_settings = get_system_settings(input_data)
    partner_service = PartnerService.load_from_input(input_data)
    promo_service = PromotionService.load_from_input(
        partner_service=partner_service,
        database_adapter=database_adapter,
    )

    solver = MechanicPartnerAssignmentSolver(
        possible_promotions=promo_service.promotions,
        partners=partner_service.partners,
        system_settings=system_settings,
    )
    solver.run()
    solver.print_solution()
    solver.print_statistics()
    solver.export_model("gitignore_model.txt")


if __name__ == "__main__":
    main()
