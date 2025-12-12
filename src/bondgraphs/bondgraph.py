from __future__ import annotations
from .element import *
from .bond import *
from .causalbg import CausalBondgraph
from .solver import Solver
from .viewer import BondgraphViewer


class DirectedBondgraph(BondgraphViewer, CausalBondgraph):
    """
    Directions of bonds determine what the positive flow of energy (power) is.
    Assume empty energy stores and energy flow from sources through junction structure into energy stores, dissipators and sinks.
    """

    def __init__(self, name: str, elements: list[Element] = [], bonds: list[tuple[str,str]] = []):
        self.__name: str = name
        self.__time_var: sp.Symbol = sp.Symbol("t", real=True, nonnegative=True)
        self.__tau: sp.Symbol = sp.Symbol("tau", real=True, nonnegative=True)
        self.__elements: dict[str, Element] = {}
        for e in elements:
            self.__add_element(e)
        self.__add_bonds(bonds)
        for ekey in self.__elements:
            self.__elements[ekey].check_bonds()
        self._assign_causalities()
        self.show_bond_causalities()
        self.show_bonds()
        self.show_elements()

    def __add_element(self, element: Element):
        identifier: str = element.get_identifier()
        if identifier in self.__elements:
            raise Exception(identifier + " already in elements of bond graph " + self.__name + ".")
        self.__elements[identifier] = element

    def __add_bonds(self, bonds: list[tuple[str,str]]):
        if len(bonds) != len(set(bonds)):
            raise Exception("Duplicate bonds defined.")
        for idx, (start_id, end_id) in enumerate(bonds):
            if start_id not in self.__elements:
                raise Exception(start_id + " not in elements of bond graph " + self.__name + ".")
            if end_id not in self.__elements:
                raise Exception(end_id + " not in elements of bond graph " + self.__name + ".")
            bond_obj: Bond = Bond(start_id, end_id, idx, self.__time_var)
            self.__elements[start_id].add_out_bond(bond_obj)
            self.__elements[end_id].add_in_bond(bond_obj)

    def get_name(self) -> str:
        return self.__name

    def get_node_ids(self) -> list[str]:
        return list(self.__elements.keys())

    def get_bonds(self) -> list[Bond]:
        bonds: list[Bond] = []
        for ekey in self.__elements:
            element: Element = self.__elements[ekey]
            bonds = bonds + element.get_in_bonds()
        return bonds

    def get_elements(self) -> dict[str,Element]:
        return self.__elements

    def get_time_var(self) -> sp.Symbol:
        return self.__time_var

    def get_tau(self) -> sp.Symbol:
        return self.__tau

    def get_vars(
        self,
        var_type: str = "all",
        element_id: str|None = None,
        as_funcs: bool = False
    ) -> list[sp.Function]:
        if element_id != None:
            return self.__elements[element_id].get_vars(var_type, self.__time_var, as_funcs)
        vars: list[sp.Function] = []
        for ekey in self.__elements:
            el_vars: list[sp.Function] = self.__elements[ekey].get_vars(
                var_type,
                self.__time_var,
                as_funcs
            )
            for ev in filter(lambda v: v not in vars, el_vars):
                vars.append(ev)
        return vars

    def show_elements(self):
        print("Elements:")
        for ekey in self.__elements:
            print(ekey, ":", self.__elements[ekey].get_vars("all", self.__time_var))
        print()

    def show_bonds(self):
        bonds: list[Bond] = self.get_bonds()
        print("Bondgraph " + self.get_name() + ":")
        for bond in bonds:
            print(bond)
        print()

    def show_bond_causalities(self):
        print("Causal edges:")
        for bond in self.get_bonds():
            eff_caus_dir: tuple[str,str]|None = bond.get_effort_causality_direction()
            if eff_caus_dir:
                print(bond.get_index(), ":", eff_caus_dir[0], eff_caus_dir[1])
        print()

    def simulate(
        self,
        start_time: float,
        step_number: int,
        step_size: float,
        variables: list[sp.Function],
        solution_nr: int,
    ) -> dict[str,list[float]]:
        time_var: sp.Symbol = self.get_time_var()
        solution: dict = self.get_solutions(log=True)[solution_nr]
        data_sets: dict[str,list[float]] = {}
        data_sets["t"] = []
        t: float = start_time
        for var in variables:
            data_sets[str(var)] = []
        for step in range(0, step_number):
            t = start_time + step * step_size
            data_sets["t"].append(t)
            for var in variables:
                data_sets[str(var)].append(
                    solution[var].subs(time_var, t).doit()
                )
        return data_sets

    def get_equations(self) -> list[BondgraphEquation]:
        equations: list[BondgraphEquation] = []
        for el_key in self.__elements:
            element: Element = self.__elements[el_key]
            el_equations: list[BondgraphEquation] = element.get_equations(
                self.__elements,
                self.__time_var,
                self.__tau
            )
            equations.extend(el_equations)
        return equations

    def get_solutions(self, log: bool = False) -> list[dict]:
        return Solver.get_solutions(
            self.get_equations(),
            self.get_vars(),
            self.get_vars(as_funcs=True),
            self.__time_var,
            self.__tau,
            log
        )


