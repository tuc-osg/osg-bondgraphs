from __future__ import annotations
from typing import Callable
import sympy as sp

from .bond import *
from .equation import *


class Element():
    # WARN: Constitutive equations are always of the form eq(.) = 0

    def __init__(
        self,
        identifier: str,
        constitutive_equation: Callable|None = None,
        initial_value: float|None = None,
    ):
        self.__constitutive_equation: Callable|None = constitutive_equation
        self.__initial_value: float|None = initial_value
        self.__identifier: str = identifier
        self.__in_bonds: list[Bond] = []
        self.__out_bonds: list[Bond] = []

    def add_in_bond(self, bond: Bond):
        if self.__identifier != bond.get_end():
            raise Exception("Bond " + str(bond) + " does not contain element " + self.__identifier)
        if bond in self.__in_bonds:
            raise Exception("Bond " + str(bond) + " already in element" + self.__identifier)
        self.__in_bonds.append(bond)

    def add_out_bond(self, bond: Bond):
        if self.__identifier != bond.get_start():
            raise Exception("Bond " + str(bond) + " does not contain element " + self.__identifier)
        if bond in self.__in_bonds:
            raise Exception("Bond " + str(bond) + " already in element" + self.__identifier)
        self.__out_bonds.append(bond)

    def get_in_bonds(self) -> list[Bond]:
        return self.__in_bonds

    def get_out_bonds(self) -> list[Bond]:
        return self.__out_bonds

    def get_bonds(self) -> list[Bond]:
        return self.__in_bonds + self.__out_bonds

    def check_bonds(self):
        if self.is_oneport():
            if len(self.get_in_bonds()) + len(self.get_out_bonds()) != 1:
                raise Exception(
                    "Wrong number of in- and outgoing power bonds for " + self.get_identifier()
                )
        if self.is_twoport():
            if len(self.get_in_bonds()) + len(self.get_out_bonds()) != 2:
                raise Exception(
                    "Wrong number of in- and outgoing power bonds for " + self.get_identifier()
                )
        if self.is_junction():
            if len(self.get_in_bonds()) + len(self.get_out_bonds()) < 2:
                raise Exception(
                    "Wrong number of in- and outgoing power bonds for " + self.get_identifier()
                )

    def is_junction(self):
        return self.is_common_effort_junction() or self.is_common_flow_junction()

    def is_storage(self):
        return self.is_inertance() or self.is_capacitance()

    def is_source(self):
        return self.is_effort_source() or self.is_flow_source()

    def is_sensor(self):
        return self.is_effort_sensor() or self.is_flow_sensor()

    def is_controller(self):
        return self.is_effort_controller() or self.is_flow_controller()

    def is_oneport(self) -> bool:
        return type(self) in [
            Capacitance,
            Inertance,
            Resistance,
            EffortSource,
            FlowSource,
            EffortSensor,
            FlowSensor,
            EffortController,
            FlowController,
        ]

    def is_twoport(self) -> bool:
        return type(self) in [Transformer, Gyrator]

    def is_resistance(self):
        return isinstance(self, Resistance)

    def is_capacitance(self):
        return isinstance(self, Capacitance)

    def is_inertance(self):
        return isinstance(self, Inertance)

    def is_effort_source(self):
        return isinstance(self, EffortSource)

    def is_flow_source(self):
        return isinstance(self, FlowSource)

    def is_effort_sensor(self):
        return isinstance(self, EffortSensor)

    def is_flow_sensor(self):
        return isinstance(self, FlowSensor)

    def is_effort_controller(self):
        return isinstance(self, EffortController)

    def is_flow_controller(self):
        return isinstance(self, FlowController)

    def is_common_effort_junction(self):
        return isinstance(self, CommonEffortJunction)

    def is_common_flow_junction(self):
        return isinstance(self, CommonFlowJunction)

    def is_transformer(self):
        return isinstance(self, Transformer)

    def is_gyrator(self):
        return isinstance(self, Gyrator)

    def get_initial_value(self) -> float|None:
        return self.__initial_value

    def get_identifier(self) -> str:
        return self.__identifier

    def get_constitutive_equation(self) -> Callable|None:
        return self.__constitutive_equation

    def get_vars(
        self,
        var_type: str,
        time_var: sp.Symbol,
        as_funcs: bool = False
    ) -> list[sp.Function]:
        vars: list[sp.Function] = []
        for b in self.get_bonds():
            match var_type:
                case "effort":
                    if as_funcs:
                        vars.append(b.get_effort())
                    else:
                        vars.append(b.get_effort(time_var))
                case "flow":
                    if as_funcs:
                        vars.append(b.get_flow())
                    else:
                        vars.append(b.get_flow(time_var))
                case "displacement":
                    if self.is_capacitance():
                        if as_funcs:
                            vars.append(b.get_displacement())
                        else:
                            vars.append(b.get_displacement(time_var))
                case "momentum":
                    if self.is_inertance():
                        if as_funcs:
                            vars.append(b.get_momentum())
                        else:
                            vars.append(b.get_momentum(time_var))
                case "power":
                    if as_funcs:
                        vars.extend([
                            b.get_effort(),
                            b.get_flow(),
                        ])
                    else:
                        vars.extend([
                            b.get_effort(time_var),
                            b.get_flow(time_var),
                        ])
                case "energy":
                    if self.is_inertance():
                        if as_funcs:
                            vars.extend([
                                b.get_momentum()
                            ])
                        else:
                            vars.extend([
                                b.get_momentum(time_var)
                            ])
                    elif self.is_capacitance():
                        if as_funcs:
                            vars.extend([
                                b.get_displacement()
                            ])
                        else:
                            vars.extend([
                                b.get_displacement(time_var)
                            ])
                case "all":
                    if as_funcs:
                        vars.append(b.get_effort())
                        vars.append(b.get_flow())
                        if self.is_capacitance():
                            vars.append(b.get_displacement())
                        if self.is_inertance():
                            vars.append(b.get_momentum())
                    else:
                        vars.append(b.get_effort(time_var))
                        vars.append(b.get_flow(time_var))
                        if self.is_capacitance():
                            vars.append(b.get_displacement(time_var))
                        if self.is_inertance():
                            vars.append(b.get_momentum(time_var))
                case _:
                    raise Exception("Unknown variable type " + var_type + ".")
        return vars

    def is_effort_input(self, bond: Bond) -> bool:
        caus_edge: tuple[str,str]|None = bond.get_effort_causality_direction()
        if caus_edge == None:
            raise Exception("No causality relevant for", self.get_identifier())
        end: str = caus_edge[1]
        return end == self.get_identifier()

    def is_flow_input(self, bond: Bond) -> bool:
        return not self.is_effort_input(bond)

    def is_constitutive_equation_solvable_for(self, var_type: str, time_var: sp.Symbol) -> bool:
        if not self.is_resistance():
            raise Exception("Checking invertibility not implemented for non-resistance.", self.get_identifier())
        eq: Callable|None = self.get_constitutive_equation()
        if eq == None:
            raise Exception("Constitutive equation should not be none for", self.get_identifier())
        bonds: list[Bond] = self.get_bonds()
        if len(bonds) != 1:
            raise Exception("Wrong number of connected bonds for", self.get_identifier())
        bond: Bond = bonds[0]
        effort: sp.Function = bond.get_effort(time_var)
        flow: sp.Function = bond.get_flow(time_var)
        res_effort = sp.solve(eq(effort, flow), effort)
        res_flow = sp.solve(eq(effort, flow), flow)
        if var_type == "effort":
            return len(res_effort) > 0
        elif var_type == "flow":
            return len(res_flow) > 0
        else:
            raise Exception("Checking solvability not implemented for var type", var_type)

    def is_constitutive_equation_invertible(self, time_var: sp.Symbol) -> bool:
        if not self.is_resistance():
            raise Exception("Checking invertibility not implemented for", self.get_identifier())
        is_eff: bool = self.is_constitutive_equation_solvable_for("effort", time_var)
        is_flow: bool = self.is_constitutive_equation_solvable_for("flow", time_var)
        return is_eff and is_flow

    def __get_oneport_equations(self, elements: dict[str,Element], time_var: sp.Symbol, tau: sp.Symbol) -> list:
        eq: Callable|None = self.get_constitutive_equation()
        # if eq == None:
        #     raise Exception("Constitutive equation should not be None for " + self.get_identifier())
        bond: Bond = self.get_bonds()[0]
        effort_in: bool = self.is_effort_input(bond)
        flow_in: bool = self.is_flow_input(bond)
        effort: sp.Function = bond.get_effort(time_var)
        flow: sp.Function = bond.get_flow(time_var)
        displacement: sp.Function = bond.get_displacement(time_var)
        momentum: sp.Function = bond.get_momentum(time_var)
        init_val: float|None = self.get_initial_value()
        equations: list = []
        # INFO: C : q(t) = phi_C(e(t)), d/dt q = f(t)
        if self.is_capacitance():
            if init_val == None:
                raise Exception("Initial value should not be none for", self.get_identifier())
            disp_func = bond.get_displacement()
            if effort_in:
                sols = sp.solve(eq(effort, displacement), displacement)
                expr = sols[0]
                if isinstance(expr, Callable):
                    res = expr(effort)
                else:
                    res = expr
                equations.extend([
                    BondgraphEquation(sp.Equality(res, displacement)),
                    BondgraphEquation(
                        sp.Equality(sp.diff(displacement), flow),
                        initial_values = { disp_func(0): init_val },
                    ),
                ])
            elif flow_in:
                flow_func: sp.Function = bond.get_flow()
                sols = sp.solve(eq(effort, displacement), effort)
                expr = sols[0]
                if isinstance(expr, Callable):
                    res = expr(displacement)
                else:
                    res = expr
                equations.extend([
                    BondgraphEquation(sp.Equality(res, effort)),
                    BondgraphEquation(
                        sp.Equality(
                            sp.integrate(flow_func(tau), (tau, 0, time_var)) + init_val,
                            displacement
                        ),
                        initial_values = { disp_func(0): init_val }
                    ),
                ])
        # INFO: I : p(t) = phi_I(f(t)), d/dt p = e(t)
        elif self.is_inertance():
            if init_val == None:
                raise Exception("Initial value should not be none for", self.get_identifier())
            mom_func: sp.Function = bond.get_momentum()
            if effort_in:
                effort_func: sp.Function = bond.get_effort()
                sols: list = sp.solve(eq(flow, momentum), flow)
                expr = sols[0]
                if isinstance(expr, Callable):
                    res = expr(momentum)
                else:
                    res = expr
                equations.extend([
                    BondgraphEquation(sp.Equality(res, flow)),
                    BondgraphEquation(
                        sp.Equality(
                            sp.integrate(effort_func(tau), (tau, 0, time_var)) + init_val,
                            momentum
                        ),
                        initial_values = { mom_func(0): init_val }
                    ),
                ])
            elif flow_in:
                sols: list = sp.solve(eq(flow, momentum), momentum)
                if len(sols) > 0:
                    expr = sols[0]
                else:
                    expr = momentum
                if isinstance(expr, Callable):
                    res = expr(flow)
                else:
                    res = expr
                equations.extend([
                    BondgraphEquation(sp.Equality(res, momentum)),
                    BondgraphEquation(
                        sp.Equality(sp.diff(momentum), effort),
                        initial_values = { mom_func(0): init_val }
                    ),
                ])
        # INFO: R : e(t) = phi_R(f(t))
        elif self.is_resistance():
            if effort_in:
                expr = sp.solve(eq(effort, flow), flow)[0]
                if isinstance(expr, Callable):
                    res = expr(effort)
                else:
                    res = expr
                equations.extend([
                    BondgraphEquation(sp.Equality(res, flow)),
                ])
            elif flow_in:
                expr = sp.solve(eq(effort, flow), effort)[0]
                if isinstance(expr, Callable):
                    res = expr(flow)
                else:
                    res = expr
                equations.extend([
                    BondgraphEquation(sp.Equality(res, effort)),
                ])
        # INFO: Se : e(t) = h(t)
        elif self.is_effort_source():
            equations.extend([
                BondgraphEquation(sp.Equality(eq(time_var), effort)),
            ])
        # INFO: Sf : f(t) = g(t)
        elif self.is_flow_source():
            equations.extend([
                BondgraphEquation(sp.Equality(eq(time_var), flow)),
            ])
        # INFO: De : f(t) = 0
        elif self.is_effort_sensor():
            equations.extend([
                BondgraphEquation(sp.Equality(0, flow)),
            ])
        # INFO: Df : e(t) = 0
        elif self.is_flow_sensor():
            equations.extend([
                BondgraphEquation(sp.Equality(0, effort)),
            ])
        # INFO: Ge : e(t) = f(y,t)
        elif self.is_effort_controller():
            measurements: dict[str,sp.Function] = {}
            for ekey in filter(lambda e: elements[e].is_effort_sensor(), elements):
                measurements[ekey] = elements[ekey].get_vars("effort", time_var)[0]
            for ekey in filter(lambda e: elements[e].is_flow_sensor(), elements):
                measurements[ekey] = elements[ekey].get_vars("flow", time_var)[0]
            effort_func: sp.Function = self.get_vars("effort", time_var, as_funcs=True)[0]
            equations.extend([
                BondgraphEquation(
                    sp.Equality(eq(time_var, measurements), effort),
                ),
            ])
        # INFO: Gf : f(t) = f(y,t)
        elif self.is_flow_controller():
            measurements: dict[str,sp.Function] = {}
            for ekey in filter(lambda e: elements[e].is_effort_sensor(), elements):
                measurements[ekey] = elements[ekey].get_vars("effort", time_var)[0]
            for ekey in filter(lambda e: elements[e].is_flow_sensor(), elements):
                measurements[ekey] = elements[ekey].get_vars("flow", time_var)[0]
            flow_func: sp.Function = self.get_vars("flow", time_var, as_funcs=True)[0]
            equations.extend([
                BondgraphEquation(
                    sp.Equality(eq(time_var, measurements), flow),
                ),
            ])
        else:
            raise Exception("Element", self.get_identifier(), "is not a oneport.")
        return equations

    def __get_twoport_equations(self, time_var: sp.Symbol) -> list:
        eq: Callable|None = self.get_constitutive_equation()
        if eq == None:
            raise Exception("Constitutive equation should not be None for " + self.get_identifier())
        a_bond: Bond = self.get_bonds()[0]
        b_bond: Bond = self.get_bonds()[1]
        a_effort_in: bool = self.is_effort_input(a_bond)
        b_effort_in: bool = self.is_effort_input(b_bond)
        if a_effort_in and b_effort_in:
            raise Exception("Causality for transformer", self.get_identifier(), "not fitting")
        if a_effort_in:
            in_effort = a_bond.get_effort(time_var)
            out_flow = a_bond.get_flow(time_var)
            in_flow = b_bond.get_flow(time_var)
            out_effort = b_bond.get_effort(time_var)
        elif b_effort_in:
            in_effort = a_bond.get_effort(time_var)
            out_flow = a_bond.get_flow(time_var)
            in_flow = b_bond.get_flow(time_var)
            out_effort = b_bond.get_effort(time_var)
        else:
            raise Exception("Causality for transformer", self.get_identifier(), "not fitting")
        equations: list = []
        # INFO: TF : e_out - phi_TF(e_in(t)) = 0, f_in - phi_TF(f_out)
        if self.is_transformer():
            eff_expr = sp.solve(eq(in_effort, out_effort), out_effort)[0]
            if isinstance(eff_expr, Callable):
                eff_res = eff_expr(in_effort)
            else:
                eff_res = eff_expr
            flow_expr = sp.solve(eq(in_flow, out_flow), out_flow)[0]
            if isinstance(flow_expr, Callable):
                flow_res = flow_expr(in_flow)
            else:
                flow_res = flow_expr
            equations.extend([
                BondgraphEquation(sp.Equality(out_effort, eff_res)),
                BondgraphEquation(sp.Equality(out_flow, flow_res)),
            ])
        # INFO: GY : e_in(t) = phi_GY(f_out(t)), e_out(t) = phy_GY(f_in(t))
        elif self.is_gyrator():
            eff_expr = sp.solve(eq(in_effort, out_flow), out_flow)[0]
            if isinstance(eff_expr, Callable):
                eff_res = eff_expr(in_effort)
            else:
                eff_res = eff_expr
            flow_expr = sp.solve(eq(out_effort, in_flow), out_effort)[0]
            if isinstance(flow_expr, Callable):
                flow_res = flow_expr(in_flow)
            else:
                flow_res = flow_expr
            equations.extend([
                BondgraphEquation(sp.Equality(out_flow, eff_res)),
                BondgraphEquation(sp.Equality(out_effort, flow_res)),
            ])
        else:
            raise Exception("Element", self.get_identifier(), "is not a twoport.")
        return equations

    def __get_junction_equations(self, time_var: sp.Symbol) -> list:
        eq: Callable|None = self.get_constitutive_equation()
        if eq != None:
            raise Exception("Constitutive equation should be None for " + self.get_identifier())
        in_efforts: list[sp.Function] = [b.get_effort(time_var) for b in self.get_in_bonds()]
        in_flows: list[sp.Function] = [b.get_flow(time_var) for b in self.get_in_bonds()]
        out_efforts: list[sp.Function] = [b.get_effort(time_var) for b in self.get_out_bonds()]
        out_flows: list[sp.Function] = [b.get_flow(time_var) for b in self.get_out_bonds()]
        equations: list = []
        # INFO: 0: e_i = e_j, sum(f_in) = sum(f_out)
        if self.is_common_effort_junction():
            equations.extend([
                BondgraphEquation(sp.Equality(sum(in_flows), sum(out_flows))),
            ])
            junction_efforts: list[sp.Function] = in_efforts + out_efforts
            first_effort: sp.Function = junction_efforts[0]
            for e in junction_efforts[1:]:
                equations.extend([
                    BondgraphEquation(sp.Equality(first_effort, e))
                ])
        # INFO: 1: f_i = f_j, sum(e_in) = sum(e_out)
        elif self.is_common_flow_junction():
            equations.extend([
                BondgraphEquation(sp.Equality(sum(in_efforts), sum(out_efforts))),
            ])
            junction_flows: list[sp.Function] = in_flows + out_flows
            first_flow: sp.Function = junction_flows[0]
            for f in junction_flows[1:]:
                equations.extend([
                    BondgraphEquation(sp.Equality(first_flow, f)),
                ])
        else:
            raise Exception("Element", self.get_identifier(), "is not a junction.")
        return equations

    def get_equations(self, elements: dict[str,Element], time_var: sp.Symbol, tau: sp.Symbol) -> list:
        if self.is_oneport():
            return self.__get_oneport_equations(elements, time_var, tau)
        elif self.is_twoport():
            return self.__get_twoport_equations(time_var)
        elif self.is_junction():
            return self.__get_junction_equations(time_var)
        else:
            raise Exception("Unknown element type for", self.get_identifier())


class Capacitance(Element):
    def __init__(self, identifier: str, constitutive_equation: Callable, initial_value: float):
        super().__init__(
            identifier,
            constitutive_equation=constitutive_equation,
            initial_value=initial_value
        )

class Inertance(Element):
    def __init__(self, identifier: str, constitutive_equation: Callable, initial_value: float):
        super().__init__(
            identifier,
            constitutive_equation=constitutive_equation,
            initial_value=initial_value
        )

class Resistance(Element):
    def __init__(self, identifier: str, constitutive_equation: Callable):
        super().__init__(
            identifier,
            constitutive_equation=constitutive_equation,
            initial_value=None
        )

class EffortSource(Element):
    def __init__(self, identifier: str, constitutive_equation: Callable):
        super().__init__(
            identifier,
            constitutive_equation=constitutive_equation,
            initial_value=None
        )

class FlowSource(Element):
    def __init__(self, identifier: str, constitutive_equation: Callable):
        super().__init__(
            identifier,
            constitutive_equation=constitutive_equation,
            initial_value=None
        )

class EffortSensor(Element):
    def __init__(self, identifier: str):
        super().__init__(
            identifier,
            constitutive_equation=None,
            initial_value=None
        )

class FlowSensor(Element):
    def __init__(self, identifier: str):
        super().__init__(
            identifier,
            constitutive_equation=None,
            initial_value=None
        )

class EffortController(Element):
    def __init__(self, identifier: str, constitutive_equation: Callable):
        super().__init__(
            identifier,
            constitutive_equation=constitutive_equation,
            initial_value=None
        )

class FlowController(Element):
    def __init__(self, identifier: str, constitutive_equation: Callable):
        super().__init__(
            identifier,
            constitutive_equation=constitutive_equation,
            initial_value=None
        )

class Transformer(Element):
    def __init__(self, identifier: str, constitutive_equation: Callable):
        super().__init__(
            identifier,
            constitutive_equation=constitutive_equation,
            initial_value=None
        )

class Gyrator(Element):
    def __init__(self, identifier: str, constitutive_equation: Callable):
        super().__init__(
            identifier,
            constitutive_equation=constitutive_equation,
            initial_value=None
        )

class CommonFlowJunction(Element):
    def is_active(self) -> bool:
        return self.__is_active

    def activate(self):
        if not self.__is_controlled:
            raise Exception("Trying to change active state of non-controlled junction" + self.__identifier)
        self.__is_active = True

    def deactivate(self):
        if not self.__is_controlled:
            raise Exception("Trying to change active state of non-controlled junction" + self.__identifier)
        self.__is_active = False

    def toggle(self):
        if not self.__is_controlled:
            raise Exception("Trying to change active state of non-controlled junction" + self.__identifier)
        self.__is_active = not self.__is_active

    def __init__(self, identifier: str, is_controlled=False):
        self.__is_controlled: bool = is_controlled
        self.__is_active: bool = True
        super().__init__(
            identifier,
            constitutive_equation=None,
            initial_value=None
        )

class CommonEffortJunction(Element):
    def is_active(self) -> bool:
        return self.__is_active

    def activate(self):
        if not self.__is_controlled:
            raise Exception("Trying to change active state of non-controlled junction" + self.__identifier)
        self.__is_active = True

    def deactivate(self):
        if not self.__is_controlled:
            raise Exception("Trying to change active state of non-controlled junction" + self.__identifier)
        self.__is_active = False

    def toggle(self):
        if not self.__is_controlled:
            raise Exception("Trying to change active state of non-controlled junction" + self.__identifier)
        self.__is_active = not self.__is_active

    def __init__(self, identifier: str, is_controlled=False):
        self.__is_controlled: bool = is_controlled
        self.__is_active: bool = True
        super().__init__(
            identifier,
            constitutive_equation=None,
            initial_value=None
        )
