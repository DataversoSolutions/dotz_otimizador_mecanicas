from typing import Dict, List
from ortools.sat.python import cp_model
import json

from promo_scheduling.entities.entity import (
    Assignment,
    Schedule,
    Partner,
    Promotion,
    SystemSettings,
)
from promo_scheduling.services.logging import logger
from promo_scheduling.settings import WEEKDAY_INDEX


class MechanicPartnerAssignmentSolver:
    def __init__(
        self,
        possible_promotions: List[Promotion],
        partners: List[Partner],
        system_settings: SystemSettings,
    ) -> None:
        self.possible_promotions = possible_promotions
        self.partners = partners
        self.system_settings = system_settings
        self.model = cp_model.CpModel()
        self.solver = cp_model.CpSolver()
        logger.debug(f"{self.solver.parameters}")
        self.all_assignments: Dict[str, Assignment] = {}
        self.zero_day_week_day = WEEKDAY_INDEX[system_settings.starting_week_day]

    def create_promo_interval_var(self, relation_id, availability_horizon):
        start_var = self.model.NewIntVar(0, availability_horizon, "start_" + relation_id)
        end_var = self.model.NewIntVar(0, availability_horizon, "end_" + relation_id)
        duration_var = self.model.NewIntVar(
            0, availability_horizon, "duration_" + relation_id
        )
        interval_var = self.model.NewIntervalVar(
            start_var, duration_var, end_var, "interval_" + relation_id
        )
        return start_var, end_var, duration_var, interval_var

    def create_promo_active_flag_var(self, relation_id, duration_var):
        is_active = self.model.NewBoolVar(relation_id + "_is_active")
        not_is_active = self.model.NewBoolVar(relation_id + "_not_is_active")
        # model can either be active or not
        self.model.Add(is_active + not_is_active == 1)
        # if not active, duration should be zero, this is a workaround to force the activation vars
        self.model.Add(duration_var == 0).OnlyEnforceIf(not_is_active)
        self.model.Add(duration_var > 0).OnlyEnforceIf(is_active)
        return is_active, not_is_active

    def create_variables(self) -> None:
        availability_horizon = max(
            promotion.partner.availability for promotion in self.possible_promotions
        )
        for promotion in self.possible_promotions:
            partner = promotion.partner
            mechanic = promotion.mechanic
            partner_availability = partner.availability
            relation_id = f"{partner.name}_{mechanic.name}"

            (
                start_var,
                end_var,
                duration_var,
                interval_var,
            ) = self.create_promo_interval_var(
                relation_id=relation_id, availability_horizon=availability_horizon
            )

            is_active, not_is_active = self.create_promo_active_flag_var(
                relation_id=relation_id, duration_var=duration_var
            )

            schedule = Schedule(
                name=relation_id,
                model=self.model,
                num_days=partner_availability,
                promo_lenght=mechanic.availability,
            )

            self.all_assignments[relation_id] = Assignment(
                id=relation_id,
                is_active=is_active,
                not_is_active=not_is_active,
                start=start_var,
                end=end_var,
                duration=duration_var,
                interval=interval_var,
                schedule=schedule,
                promotion=promotion,
            )

    def add_constraint_partner_max_availability(self) -> None:
        for partner in self.partners:
            # the sum of all mechanics of the partner must be equal or lower than the partner availability
            self.model.Add(
                sum(
                    self.all_assignments[
                        f"{partner.name}_{mechanic.name}"
                    ].duration
                    for mechanic in partner.mechanics
                )
                <= partner.availability
            )

    def add_constraint_min_duration(self) -> None:
        for assignment in self.all_assignments.values():
            # if the mechanic is active, we constraint its duration to be higher or equal the minimum duration
            self.model.Add(
                assignment.interval.SizeExpr() >= self.system_settings.min_duration
            ).OnlyEnforceIf(assignment.is_active)

    def add_schedule_constraint(self) -> None:
        for assignment in self.all_assignments.values():
            schedule = assignment.schedule
            schedule_days = schedule.num_days
            schedule_promo_duration = schedule.promo_lenght
            start_var = assignment.start
            duration_var = assignment.duration
            day_flags = schedule.get_day_flags_var()
            # only one day active
            self.model.AddAtMostOne(day_flags)
            for day in range(schedule_days):
                duration_array = schedule.get_duration_array_at_day(day)
                # enforce the day_flags[start_var] == 1
                self.model.AddMapDomain(var=start_var, bool_var_array=day_flags)

                # only one day active
                self.model.AddAtMostOne(day_flags)
                # enforce duration if day is active
                self.model.Add(sum(duration_array) == duration_var + 1).OnlyEnforceIf(
                    day_flags[day]
                )
                # enforce the duration array is a vector with all ones in the beginning
                for pos in range(schedule_promo_duration - 1):
                    self.model.Add(duration_array[pos] >= duration_array[pos + 1])

    def add_constraint_no_overlapping_promotion_on_partner(self):
        for partner in self.partners:
            # the partner cant have more than one promotion running at any time
            # so, the interval variables must not overlap
            self.model.AddNoOverlap(
                self.all_assignments[f"{partner.name}_{mechanic.name}"].interval
                for mechanic in partner.mechanics
            )

    def add_constraint_promotion_end_before_availability_end(self):
        # we cant end a promotion after the partner availability
        for possible_assignment in self.all_assignments.values():
            self.model.Add(
                possible_assignment.end
                <= possible_assignment.promotion.partner.availability
            )

    def add_constraint_daily_promotions(self):
        promotions_intervals = []
        promotions_demands = []
        for assignment in self.all_assignments.values():
            promotions_intervals.append(assignment.interval)
            promotions_demands.append(1)
        self.model.AddCumulative(promotions_intervals, promotions_demands, self.system_settings.max_daily_promotions)

    def create_objective_function(self) -> None:
        self.model.Maximize(
            # we maximize the productivity (clients) of all promotions
            sum(
                assignment.productivity(self.zero_day_week_day)
                for assignment in self.all_assignments.values()
            )
        )

    def has_solution_found(self) -> bool:
        # status_map = {
        #     cp_model.UNKNOWN: 'UNKNOWN',
        #     cp_model.MODEL_INVALID: 'MODEL_INVALID',
        #     cp_model.FEASIBLE: 'FEASIBLE',
        #     cp_model.INFEASIBLE: 'INFEASIBLE',
        #     cp_model.OPTIMAL: 'OPTIMAL'
        # }
        # TODO: add this to log
        # logger.debug(status_map[self.status])
        return self.status == cp_model.OPTIMAL or self.status == cp_model.FEASIBLE

    def run(self) -> None:
        self.create_variables()
        self.add_schedule_constraint()
        self.add_constraint_partner_max_availability()
        self.add_constraint_no_overlapping_promotion_on_partner()
        self.add_constraint_min_duration()
        # self.add_constraint_promotion_end_before_availability_end()
        self.add_constraint_daily_promotions()
        self.create_objective_function()
        self.status = self.solver.Solve(self.model)

    def get_solution_json(self) -> str:
        solution = {}
        if not self.has_solution_found():
            solution["status"] = "Solution not found"
            return json.dumps(solution)
        promotion_assignments = []
        for promotion in self.possible_promotions:
            promotion_assignment = {}
            partner = promotion.partner
            mechanic = promotion.mechanic
            assignment = self.all_assignments[f"{partner.name}_{mechanic.name}"]
            start_var = self.solver.Value(assignment.start) - 1
            end_var = self.solver.Value(assignment.end) - 1
            productivity = self.solver.Value(assignment.productivity(self.zero_day_week_day))
            if productivity == 0:
                continue
            promotion_assignment["partner"] = promotion.partner.name
            promotion_assignment["mechanic"] = promotion.mechanic.name
            promotion_assignment["start"] = start_var
            promotion_assignment["end"] = end_var
            promotion_assignment["productivity"] = productivity
            promotion_assignments.append(promotion_assignment)
        solution["status"] = "Solution found"
        solution["total_clients"] = self.solver.ObjectiveValue()
        solution["promotion_assignments"] = promotion_assignments
        return solution

    def get_solution_str(self) -> str:
        result = []
        if self.has_solution_found():
            result.append("Solution:")

            output = []
            for promotion in self.possible_promotions:
                partner = promotion.partner
                mechanic = promotion.mechanic
                assignment = self.all_assignments[f"{partner.name}_{mechanic.name}"]
                start_var = self.solver.Value(assignment.start) - 1
                end_var = self.solver.Value(assignment.end) - 1
                duration_var = self.solver.Value(assignment.duration)
                productivity = self.solver.Value(
                    assignment.productivity(self.zero_day_week_day)
                )
                # if productivity == 0:
                #     continue

                schedule_matrix = [
                    [
                        self.solver.Value(duration_array[i])
                        for i in range(len(duration_array))
                    ]
                    for duration_array in assignment.schedule.schedule_array
                ]
                is_active = self.solver.Value(assignment.is_active)
                not_is_active = self.solver.Value(assignment.not_is_active)
                logger.debug(
                    f"{assignment.id} is active={is_active} / not is active={not_is_active}"
                )
                for line in schedule_matrix:
                    logger.debug(line)
                output.append(
                    f"Parceiro {promotion.partner.name} "
                    f"com promoção {promotion.mechanic.name} "
                    f"iniciando em {start_var} e "
                    f"terminando em {end_var} "
                    f"com duração de {duration_var} "
                    f"com resultando em {productivity} clientes"
                )

            result.append(f"Optimal result: {self.solver.ObjectiveValue()} clientes")
            result.append("\n".join(output))
        else:
            result.append("No solution found.")
        return "\n".join(result)

    def print_solution(self) -> None:
        result = self.get_solution_str()
        logger.debug(result)

    def print_statistics(self) -> None:
        logger.debug("\nStatistics")
        logger.debug("  - conflicts: %i" % self.solver.NumConflicts())
        logger.debug("  - branches : %i" % self.solver.NumBranches())
        logger.debug("  - wall time: %f s" % self.solver.WallTime())

    def export_model(self, filename) -> None:
        self.model.ExportToFile(filename)
