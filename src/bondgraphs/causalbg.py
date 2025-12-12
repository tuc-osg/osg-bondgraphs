from __future__ import annotations
from .element import *
from .bond import *

class CausalBondgraph():

    def get_elements(self) -> dict[str,Element]:
        raise NotImplementedError

    def get_bonds(self) -> list[Bond]:
        raise NotImplementedError

    def get_time_var(self) -> sp.Symbol:
        raise NotImplementedError

    def __propagate_causalities(self) -> bool:
        change: bool = False
        elements: dict[str,Element] = self.get_elements()

        # Effort junctions
        for ekey in filter(lambda e: isinstance(elements[e], CommonEffortJunction), elements):
            element: Element = elements[ekey]
            for bond in element.get_bonds():
                eff_caus_dir: tuple[str,str]|None = bond.get_effort_causality_direction()
                if eff_caus_dir and eff_caus_dir[1] == ekey:
                    for other_bond in filter(lambda b: b != bond, element.get_bonds()):
                        other_eff_caus_dir: tuple[str,str]|None = other_bond.get_effort_causality_direction()
                        if other_eff_caus_dir == None:
                            other_bond.set_effort_causality_direction_from(ekey)
                            change = True
                        elif other_eff_caus_dir[0] == ekey:
                            pass
                        else:
                            raise Exception("Causal conflict during propagation", str(other_bond))

        # Flow junctions
        for ekey in filter(lambda e: isinstance(elements[e], CommonFlowJunction), elements):
            element: Element = elements[ekey]
            for bond in element.get_bonds():
                flow_caus_dir: tuple[str,str]|None = bond.get_flow_causality_direction()
                if flow_caus_dir and flow_caus_dir[1] == ekey:
                    for other_bond in filter(lambda b: b != bond, element.get_bonds()):
                        other_flow_caus_dir: tuple[str,str]|None = other_bond.get_flow_causality_direction()
                        if other_flow_caus_dir == None:
                            other_bond.set_flow_causality_direction_from(ekey)
                            change = True
                        elif other_flow_caus_dir[0] == ekey:
                            pass
                        else:
                            raise Exception("Causal conflict during propagation", str(other_bond))

        # Transformers
        for ekey in filter(lambda e: isinstance(elements[e], Transformer), elements):
            element: Element = elements[ekey]
            for bond in element.get_bonds():
                effort_caus_dir: tuple[str,str]|None = bond.get_effort_causality_direction()
                if effort_caus_dir and effort_caus_dir[1] == ekey:
                    for other_bond in filter(lambda b: b != bond, element.get_bonds()):
                        other_effort_caus_dir: tuple[str,str]|None = other_bond.get_effort_causality_direction()
                        if other_effort_caus_dir == None:
                            other_bond.set_effort_causality_direction_from(ekey)
                            change = True
                        elif other_effort_caus_dir[0] == ekey:
                            pass
                        else:
                            raise Exception("Causal conflict during propagation", str(other_bond))
                elif effort_caus_dir and effort_caus_dir[0] == ekey:
                    for other_bond in filter(lambda b: b != bond, element.get_bonds()):
                        other_effort_caus_dir: tuple[str,str]|None = other_bond.get_effort_causality_direction()
                        if other_effort_caus_dir == None:
                            other_bond.set_effort_causality_direction_towards(ekey)
                            change = True
                        elif other_effort_caus_dir[1] == ekey:
                            pass
                        else:
                            raise Exception("Causal conflict during propagation", str(other_bond))

        # Gyrators
        for ekey in filter(lambda e: isinstance(elements[e], Gyrator), elements):
            element: Element = elements[ekey]
            for bond in element.get_bonds():
                effort_caus_dir: tuple[str,str]|None = bond.get_effort_causality_direction()
                if effort_caus_dir and effort_caus_dir[1] == ekey:
                    for other_bond in filter(lambda b: b != bond, element.get_bonds()):
                        other_effort_caus_dir: tuple[str,str]|None = other_bond.get_effort_causality_direction()
                        if other_effort_caus_dir == None:
                            other_bond.set_effort_causality_direction_towards(ekey)
                            change = True
                        elif other_effort_caus_dir[1] == ekey:
                            pass
                        else:
                            raise Exception("Causal conflict during propagation", str(other_bond))
                elif effort_caus_dir and effort_caus_dir[0] == ekey:
                    for other_bond in filter(lambda b: b != bond, element.get_bonds()):
                        other_effort_caus_dir: tuple[str,str]|None = other_bond.get_effort_causality_direction()
                        if other_effort_caus_dir == None:
                            other_bond.set_effort_causality_direction_from(ekey)
                            change = True
                        elif other_effort_caus_dir[0] == ekey:
                            pass
                        else:
                            raise Exception("Causal conflict during propagation", str(other_bond))

        return change

    def _assign_causalities(self):
        # Bond causality: is effort or is flow external one at power port?
        # Causal stroke is at the end of the bond where the flow is computed in adjacent element
        # Causal stroke indicates "direction of effort signal" (side with stroke means that effort is input at that element, flow is output)

        # Rules for assigning causality (according to Sequential Causality Assignment Procedure):

        # If flow source: output is flow
        # If effort source: output is effort

        # If 0-junction: only one effort allowed as input, others are output
        # If 1-junction: only one flow allowed as input, others are output

        # If transformer: only one effort can be input (the other must be output) -- role of efforts determines inverse input-output relationship for flows
        # If gyrator: both efforts must be either inputs or outputs

        # Prefer integral causality (so jumps can be represented), i.e.:
        #   If capacity: effort is output, flow is input
        #   If inertia: effort is input, flow is output
        # Otherwise derivative causality, i.e.:
        #   If capacity: effort is input, flow is output
        #   If inertia: flow is input, effort is output

        # If resistor: no rules

        # Propagation based on observing causality rules at element ports

        # 1) For each source in elements:
        #   1.1) Assign causality to corresponding power port of source
        elements: dict[str,Element] = self.get_elements()
        for ekey in filter(lambda e: isinstance(elements[e], EffortSource), elements):
            element: Element = elements[ekey]
            for bond in element.get_bonds():
                bond.set_effort_causality_direction_from(ekey)

        for ekey in filter(lambda e: isinstance(elements[e], FlowSource), elements):
            element: Element = elements[ekey]
            for bond in element.get_bonds():
                bond.set_flow_causality_direction_from(ekey)

        for ekey in filter(lambda e: isinstance(elements[e], EffortSensor), elements):
            element: Element = elements[ekey]
            for bond in element.get_bonds():
                bond.set_flow_causality_direction_from(ekey)

        for ekey in filter(lambda e: isinstance(elements[e], FlowSensor), elements):
            element: Element = elements[ekey]
            for bond in element.get_bonds():
                bond.set_effort_causality_direction_from(ekey)

        for ekey in filter(lambda e: isinstance(elements[e], EffortController), elements):
            element: Element = elements[ekey]
            for bond in element.get_bonds():
                bond.set_effort_causality_direction_from(ekey)

        for ekey in filter(lambda e: isinstance(elements[e], FlowController), elements):
            element: Element = elements[ekey]
            for bond in element.get_bonds():
                bond.set_flow_causality_direction_from(ekey)

        #   1.2) Propagate information through bond graph
        #   1.3) If causal conflict: check model assumptions

        # Continue as long as there are changes and no conflicts
        while self.__propagate_causalities():
            pass

        # 2) For each resistor port without unique inverse:
        #   2.1) Assign correct causality
        #   2.2) Propagate information through bond graph
        for ekey in filter(lambda e: isinstance(elements[e], Resistance), elements):
            element: Element = elements[ekey]
            for bond in element.get_bonds():
                if not element.is_constitutive_equation_invertible(self.get_time_var()):
                    if element.is_constitutive_equation_solvable_for("effort", self.get_time_var()):
                        bond.set_effort_causality_direction_from(ekey)
                    elif element.is_constitutive_equation_solvable_for("flow", self.get_time_var()):
                        bond.set_flow_causality_direction_from(ekey)
                    else:
                        raise Exception("Equation for", ekey, "not solvable at all.")

        # Continue as long as there are changes and no conflicts
        while self.__propagate_causalities():
            pass

        # 3) For each energy store without assigned causality:
        #   3.1) Assign preferred integral causality to port of energy store
        #   3.2) Propagate information (may lead to derivative causality at other energy stores and entails causality assignment at resistor ports)
        for ekey in filter(lambda e: isinstance(elements[e], Capacitance), elements):
            element: Element = elements[ekey]
            for bond in element.get_bonds():
                if not bond.is_causality_set():
                    bond.set_flow_causality_direction_towards(ekey)
                    # Continue as long as there are changes and no conflicts
                    while self.__propagate_causalities():
                        pass

        for ekey in filter(lambda e: isinstance(elements[e], Inertance), elements):
            element: Element = elements[ekey]
            for bond in element.get_bonds():
                if not bond.is_causality_set():
                    bond.set_effort_causality_direction_towards(ekey)
                    # Continue as long as there are changes and no conflicts
                    while self.__propagate_causalities():
                        pass

        # 4) For each resistors and internal bonds without causality: (If this is needed, there are algebraic loops)
        #   4.1) Assign causality randomly
        #   4.2) Propagate
        for bond in self.get_bonds():
            if not bond.is_causality_set():
                print("WARNING: BOND", bond, "HAS NOT BEEN ASSIGNED YET, THERE ARE ALGEBRAIC LOOPS.")
                end: str = bond.get_end()
                bond.set_effort_causality_direction_towards(end)
                while self.__propagate_causalities():
                    pass

