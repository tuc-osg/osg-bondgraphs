from __future__ import annotations
import sympy as sp


class Bond():
    def __init__(self, start: str, end: str, index: int, time_var: sp.Symbol):
        self.__start: str = start
        self.__end: str = end
        self.__index: int = index
        self.__effort = sp.Function("e_{" + str(index) + "}", real=True)
        self.__flow = sp.Function("f_{" + str(index) + "}", real=True)
        self.__displacement = sp.Function("q_{" + str(index) + "}", real=True)
        self.__momentum = sp.Function("p_{" + str(index) + "}", real=True)
        self.__effort_causality_direction: tuple[str,str]|None = None
        self.__flow_causality_direction: tuple[str,str]|None = None

    def __str__(self):
        return str(self.__index) + ":(" + self.__start + "," + self.__end + ")"

    def is_causality_set(self) -> bool:
        return self.__effort_causality_direction != None and self.__flow_causality_direction != None

    def set_effort_causality_direction_towards(self, el_name: str):
        if self.__effort_causality_direction:
            if self.__effort_causality_direction[1] != el_name:
                raise Exception("Causal conflict: causality already set for bond", str(self))
        if self.__flow_causality_direction:
            if self.__flow_causality_direction[1] != el_name:
                raise Exception("Causal conflict: causality already set for bond", str(self))
        if self.__start == el_name:
            self.__effort_causality_direction = (self.__end, el_name)
            self.__flow_causality_direction = (el_name, self.__end)
        elif self.__end == el_name:
            self.__effort_causality_direction = (self.__start, el_name)
            self.__flow_causality_direction = (el_name, self.__start)
        else:
            raise Exception("Unknown element name in bond", self)

    def set_effort_causality_direction_from(self, el_name: str):
        if self.__effort_causality_direction:
            if self.__effort_causality_direction[0] != el_name:
                raise Exception("Causal conflict: effort causality already set for bond", str(self))
        if self.__flow_causality_direction:
            if self.__flow_causality_direction[0] != el_name:
                raise Exception("Causal conflict: flow causality already set for bond", str(self))
        if self.__start == el_name:
            other: str = self.__end
        elif self.__end == el_name:
            other: str = self.__start
        else:
            raise Exception("Unknown element name in bond", self)
        self.__effort_causality_direction = (el_name, other)
        self.__flow_causality_direction = (other, el_name)

    def set_flow_causality_direction_towards(self, el_name: str):
        self.set_effort_causality_direction_from(el_name)

    def set_flow_causality_direction_from(self, el_name: str):
        self.set_effort_causality_direction_towards(el_name)

    def __check_causality(self):
        if self.__effort_causality_direction == None:
            raise Exception("Causality not set for bond", self)
        if self.__flow_causality_direction == None:
            raise Exception("Causality not set for bond", self)
        if self.__effort_causality_direction == self.__flow_causality_direction:
            raise Exception("Effort and flow causalities stand in conflict for bond", self)

    def get_effort_causality_direction(self) -> tuple[str,str]|None:
        return self.__effort_causality_direction

    def get_flow_causality_direction(self) -> tuple[str,str]|None:
        return self.__flow_causality_direction

    def get_start(self) -> str:
        return self.__start

    def get_end(self) -> str:
        return self.__end

    def get_index(self) -> int:
        return self.__index

    def get_effort(self, time_var: sp.Symbol|None = None) -> sp.Function:
        if time_var == None:
            return self.__effort
        else:
            return self.__effort(time_var)

    def get_flow(self, time_var: sp.Symbol|None = None) -> sp.Function:
        if time_var == None:
            return self.__flow
        else:
            return self.__flow(time_var)

    def get_displacement(self, time_var: sp.Symbol|None = None) -> sp.Function:
        if time_var == None:
            return self.__displacement
        else:
            return self.__displacement(time_var)

    def get_momentum(self, time_var: sp.Symbol|None = None) -> sp.Function:
        if time_var == None:
            return self.__momentum
        else:
            return self.__momentum(time_var)

