from __future__ import annotations
class BondgraphEquation():

    def __init__(self, equation, initial_values: dict = {}):
        self.__equation = equation
        self.__initial_values: dict = initial_values

    def get_equation(self):
        return self.__equation

    def get_initial_values(self) -> dict:
        return self.__initial_values


