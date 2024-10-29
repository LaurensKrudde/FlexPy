from src.fleetctrl.repositioning.RepositioningBase import RepositioningBase
from src.fleetctrl.planning.VehiclePlan import RoutingTargetPlanStop
from src.fleetctrl.FleetControlBase import FleetControlBase
from src.fleetctrl.planning.PlanRequest import PlanRequest
from src.misc.globals import *


TARGET_NODE = 4123  # Hellevoetsluis, Kickersbloem


class SimpleRepositioning(RepositioningBase):
    """ A very basic repositioning strategy. It simply repositions all vehicles to a fixed node. """
    def __init__(self, fleetctrl : FleetControlBase, operator_attributes: dict, dir_names: dict, solver: str = "Gurobi"):
        super().__init__(fleetctrl, operator_attributes, dir_names, solver=solver)
        self.min_reservation_buffer = operator_attributes.get(G_OP_REPO_RES_PUF, 3600)  # TODO  # minimum time for service before a vehicle has a reserved trip

    def determine_and_create_repositioning_plans(self, sim_time, lock=None):
        """ Whenever a vehicle is idle, it is repositioned to a fixed node.

        :param sim_time: current simulation time
        :param lock: indicates if vehplans should be locked
        :return: list[vid] of vehicles with changed plans
        """
        self.sim_time = sim_time
        if lock is None:
            lock = self.lock_repo_assignments
        
        vid_changed_plans = []
        for veh in self.fleetctrl.sim_vehicles:
            if len(self.fleetctrl.veh_plans[veh.vid].list_plan_stops) == 0 and veh.pos[0] != TARGET_NODE:
                target_node = TARGET_NODE
                ps = RoutingTargetPlanStop((target_node, None, None), locked=lock, planstop_state=G_PLANSTOP_STATES.REPO_TARGET)
                veh_plan = self.fleetctrl.veh_plans[veh.vid]
                veh_obj = self.fleetctrl.sim_vehicles[veh.vid]
                veh_plan.add_plan_stop(ps, veh_obj, sim_time, self.routing_engine)
                self.fleetctrl.assign_vehicle_plan(veh_obj, veh_plan, sim_time)
                if lock:
                    self.fleetctrl.lock_current_vehicle_plan(veh_obj.vid)
                vid_changed_plans.append(veh.vid)
                
        return vid_changed_plans
