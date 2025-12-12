from __future__ import annotations
from .equation import BondgraphEquation

import sympy as sp

class Solver():

    @staticmethod
    def get_simplified_equations(equations: list) -> list:
        results: list = sp.solve(equations, rational=True, dict=True)
        if len(results) == 0:
            return equations
        res = results[0]
        simplified_equations: list = []
        for var in res:
            simplified_equations.append(
                sp.Equality(var, res[var].doit())
            )
        return simplified_equations

    @staticmethod
    def get_initial_equations(
        equations: list,
        time_var: sp.Symbol,
        tau: sp.Symbol,
    ) -> list:
        initial_equations: list = []
        for eq in equations:
            if eq.has(sp.Derivative):
                e = sp.integrate(
                    eq.subs(time_var, tau),
                    (tau, 0, time_var)
                )
            else:
                e = eq
            res = e.subs(time_var, 0).doit()
            if res != True:
                initial_equations.append(res)
        return initial_equations

    @staticmethod
    def get_initial_values(
        bg_equations: list,
        initial_equations: list,
        var_funcs: list[sp.Function],
    ) -> dict:
        initial_vars: list[sp.Function] = []
        for f in var_funcs:
            initial_vars.append(f(0))
        # Additionally set initial values that are given by application
        for eq in bg_equations:
            ics: dict = eq.get_initial_values()
            for key in ics:
                initial_equations.append(
                    sp.Equality(key, sp.nsimplify(ics[key]))
                )
        initial_values: dict = sp.solve(initial_equations, initial_vars, rational=True, dict=True)[0]
        return initial_values

    @staticmethod
    def remove_integrals(equations: list, time_var: sp.Symbol) -> list:
        derivative_equations: list = []
        for eq in equations:
            if eq.has(sp.Integral):
                try:
                    equal = sp.Equality(
                        sp.Derivative(eq.lhs, time_var).doit(),
                        sp.Derivative(eq.rhs, time_var).doit(),
                    )
                    derivative_equations.append(equal)
                except Exception as exc:
                    print(exc)
            else:
                derivative_equations.append(eq)
        return derivative_equations

    @staticmethod
    def has_integrals_or_derivatives(equations: list) -> bool:
        for eq in equations:
            if eq.has(sp.Integral) or eq.has(sp.Derivative):
                return True

        return False

    @staticmethod
    def instantiate_solution(
        solution: dict,
        vars: list,
        initial_values: dict,
        time_var: sp.Symbol,
        log: bool
    ) -> dict:
        # Calculate values of constants at t=0 (depend on initial values)
        constants: dict = sp.solve(
            [dv.subs(time_var, 0).doit() for dv in solution],
            simplify=False,
            rational=True,
        )
        subs_constants: dict = {}
        # Substitute initial values in constants
        for c in constants:
            subs_constants[c] = constants[c].subs(initial_values)
        # Substutitute calculated constant values in equations
        eq_subst: list = [eq.subs(subs_constants).doit() for eq in solution]
        if log:
            print("Constants:")
            for c in constants:
                print(c, "=", constants[c])
            print()
            print("Substituted constants:")
            for c in subs_constants:
                print(c, "=", subs_constants[c])
            print()
            print("Equations with replaced constants:")
            for eq in eq_subst:
                print(eq)
            print()
        solution = sp.solve(eq_subst, vars, rational=True, dict=True)[0]
        return solution

    @staticmethod
    def get_solutions(
        bg_equations: list[BondgraphEquation],
        vars: list[sp.Function],
        var_funcs: list[sp.Function],
        time_var: sp.Symbol,
        tau: sp.Symbol,
        log: bool=False,
    ) -> list[dict]:
        if log:
            print("Variables:")
            print(vars)
            print()

        equations: list = [e.get_equation() for e in bg_equations]
        if log:
            print("Initial Equations:")
            for eq in equations:
                print(eq)
            print()

        simplified_equations: list = Solver.get_simplified_equations(equations)
        if log:
            print("Simplified equations:")
            for eq in simplified_equations:
                print(eq)
            print()

        derivative_equations: list = Solver.remove_integrals(
            simplified_equations,
            time_var,
        )
        if log:
            print("Derivative equations:")
            for de in derivative_equations:
                print(de)
            print()
        for eq in derivative_equations:
            if eq.has(sp.Integral):
                raise Exception("Integrals still present in derivative equations.")

        initial_equations: list = Solver.get_initial_equations(
            equations,
            time_var,
            tau
        )
        if log:
            print("Initial value equations:")
            for eq in initial_equations:
                print(eq)
            print()

        initial_values: dict = Solver.get_initial_values(
            bg_equations,
            initial_equations,
            var_funcs,
        )
        if log:
            print("Initial values:")
            for var in initial_values:
                print(var, "=", initial_values[var])
            print()
        if len(initial_values) == 0:
            raise Exception("Contradiction in initial values")

        # Directly solve algebraically, if no derivatives or integrals
        if not Solver.has_integrals_or_derivatives(derivative_equations):
            solutions: list[dict] = sp.solve(derivative_equations, vars, dict=True, rational=True)
            print("No storage element present")
            for idx, sol in enumerate(solutions):
                print("Solution", idx)
                for var in sol:
                    print(var, "=", sol[var])
            return solutions

        # Solve system of ODE's
        derivative_solutions: list = sp.solvers.ode.systems.dsolve_system(
            derivative_equations,
            vars,
            time_var,
            # ics=initial_values, # WARN: Does not work because of bug?
            doit=False,
            simplify=False,
        )
        if log:
            print("Solved derivative solutions:")
            for idx, sol in enumerate(derivative_solutions):
                print("Solution", idx)
                for eq in sol:
                    print(eq)
            print()

        # Create final solutions
        solutions: list[dict] = []
        for sol in derivative_solutions:
            solution: dict = Solver.instantiate_solution(
                sol,
                vars,
                initial_values,
                time_var,
                log,
            )
            solutions.append(solution)
        if log:
            print("Solutions:")
            for idx, sol in enumerate(solutions):
                print("Solution", idx)
                for var in sol:
                    print(var, "=", sol[var])
            print()

        return solutions
