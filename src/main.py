import inspect

import sympy as sp
import bondgraphs as bg


class Examples():

    @staticmethod
    def simple_example() -> bg.DirectedBondgraph:
        elements: list[bg.Element] = [
            bg.FlowSource("S_f", lambda _: 2),
            bg.Capacitance("C", lambda e, q: 1 * e - q, initial_value=1),
            bg.Resistance("R", lambda e, f: 1 * f - e),
            bg.CommonEffortJunction("0"),
        ]
        bonds: list[tuple[str,str]] = [
            ("S_f", "0"),
            ("0", "C"),
            ("0", "R"),
        ]
        return bg.DirectedBondgraph("Simple Electrical Circuit", elements, bonds)

    @staticmethod
    def rc() -> bg.DirectedBondgraph:
        elements: list[bg.Element] = [
            bg.Capacitance("C", lambda e, q: 1 * e - q, initial_value=2),
            bg.Resistance("R", lambda e, f: 1 * f - e),
            bg.CommonEffortJunction("0"),
        ]
        bonds: list[tuple[str,str]] = [
            ("0", "C"),
            ("0", "R"),
        ]
        return bg.DirectedBondgraph("Simple Electrical Circuit", elements, bonds)

    @staticmethod
    def moving_body() -> bg.DirectedBondgraph:
        elements: list[bg.Element] = [
            bg.Inertance("I", lambda f, p: p - 2 * f, initial_value=0), # Mass = 2
            bg.EffortSource("S_e", lambda _: 1), # Force source
            bg.CommonFlowJunction("1"),
        ]
        bonds: list[tuple[str,str]] = [
            ("S_e", "1"),
            ("1", "I"),
        ]
        return bg.DirectedBondgraph("Simple Moving Body", elements, bonds)

    @staticmethod
    def moving_body_controller() -> bg.DirectedBondgraph:
        mass = 2
        setpoint = 10
        k_p = 5
        elements: list[bg.Element] = [
            bg.EffortSource("S_e", lambda t: sp.sin(t)),
            bg.Inertance("I", lambda f, p: p - mass * f, initial_value=0),
            bg.FlowSensor("D_f"),
            bg.EffortController("G_e", lambda t, y: k_p * (setpoint - y["D_f"])),
            bg.CommonFlowJunction("1"),
        ]
        bonds: list[tuple[str,str]] = [
            ("G_e", "1"),
            ("1", "D_f"),
            ("1", "I"),
            ("S_e", "1"),
        ]
        return bg.DirectedBondgraph("Moving Body Controller", elements, bonds)

    @staticmethod
    def spring_damper() -> bg.DirectedBondgraph:
        elements: list[bg.Element] = [
            bg.EffortSource("S_e", lambda t: 9.81),
            bg.Inertance("I", lambda f, p: p - 2 * f, initial_value=3), # Mass = 2
            bg.Capacitance("C", lambda e, q: q - sp.Rational(1,10) * e, initial_value=5),
            bg.Resistance("R", lambda e, f: e - sp.Rational(1,2) * f), # R=U/I -> U - R*I
            bg.CommonFlowJunction("1"),
        ]
        bonds: list[tuple[str,str]] = [
            ("S_e", "1"),
            ("1", "I"),
            ("1", "C"),
            ("1", "R"),
        ]
        return bg.DirectedBondgraph("Spring Damper System", elements, bonds)

    @staticmethod
    def check_transformer() -> bg.DirectedBondgraph:
        elements: list[bg.Element] = [
            bg.EffortSource("S_e", lambda t: 0),
            bg.Transformer("TF", lambda eff_in, eff_out: eff_in - 5 * eff_out),
            bg.CommonFlowJunction("1"),
            bg.Inertance("I", lambda f, p: p - 2 * f, initial_value=0), # Mass = 2
            bg.Capacitance("C", lambda e, q: q - 3 * e, initial_value=2),
            bg.Resistance("R", lambda e, f: e - 1.5 * f),
        ]
        bonds: list[tuple[str,str]] = [
            ("S_e", "TF"),
            ("TF", "1"),
            ("1", "C"),
            ("1", "I"),
            ("1", "R"),
        ]
        return bg.DirectedBondgraph("Transformer Check", elements, bonds)

    @staticmethod
    def controlled_moving_body() -> bg.DirectedBondgraph:
        elements: list[bg.Element] = [
            bg.Inertance("I", lambda f, p: p - 2 * f, initial_value=5), # Mass = 5
            bg.EffortSource("S_e", lambda t: sp.Piecewise(
                (0, sp.LessThan(t, 3)),
                (3, sp.And(sp.StrictGreaterThan(t, 3), sp.LessThan(t, 7))),
                (-5, sp.StrictGreaterThan(t, 7)),
            )), # Force source
            bg.CommonFlowJunction("1"),
        ]
        bonds: list[tuple[str,str]] = [
            ("S_e", "1"),
            ("1", "I"),
        ]
        return bg.DirectedBondgraph("Simple Moving Body", elements, bonds)

    @staticmethod
    def electrical_bridge() -> bg.DirectedBondgraph:
        elements: list[bg.Element] = [
            bg.Resistance("R_1", lambda e, f: e - 1 * f),
            bg.Resistance("R_2", lambda e, f: e - 1 * f),
            bg.Resistance("R_3", lambda e, f: e - 1 * f),
            bg.Resistance("R_4", lambda e, f: e - 1 * f),
            bg.Resistance("R_5", lambda e, f: e - 1 * f),
            bg.CommonFlowJunction("1_1"),
            bg.CommonFlowJunction("1_2"),
            bg.CommonFlowJunction("1_3"),
            bg.CommonFlowJunction("1_4"),
            bg.CommonFlowJunction("1_5"),
            bg.CommonFlowJunction("1_6"),
            bg.CommonEffortJunction("0_1"),
            bg.CommonEffortJunction("0_2"),
            bg.CommonEffortJunction("0_3"),
            bg.CommonEffortJunction("0_4"),
            bg.EffortSource("S_{e,S}", lambda _: 5),
            bg.EffortSource("S_{e,G}", lambda _: 0),
        ]
        bonds: list[tuple[str,str]] = [
            ("S_{e,S}", "1_1"),
            ("1_1", "0_1"),
            ("0_1", "1_2"),
            ("1_2", "R_1"),
            ("0_1", "1_3"),
            ("1_3", "R_2"),
            ("1_2", "0_2"),
            ("1_3", "0_3"),
            ("0_2", "1_6"),
            ("0_3", "1_6"),
            ("1_6", "R_5"),
            ("0_2", "1_4"),
            ("0_3", "1_5"),
            ("1_4", "R_3"),
            ("1_5", "R_4"),
            ("1_4", "0_4"),
            ("1_5", "0_4"),
            ("0_4", "1_1"),
            ("0_4", "S_{e,G}"),
        ]
        return bg.DirectedBondgraph("Electircal Bridge", elements, bonds)

    @staticmethod
    def causality_assignment_test():
        elements: list[bg.Element] = [
            bg.EffortSource("S_e", lambda t: 0),
            bg.FlowSource("S_f", lambda t: 0),
            bg.Resistance("R_1", lambda e, f: e - 1 * f),
            bg.Resistance("R_2", lambda e, f: e - 1 * f),
            bg.CommonFlowJunction("1_1"),
            bg.CommonFlowJunction("1_2"),
            bg.CommonFlowJunction("1_3"),
            bg.CommonEffortJunction("0_1"),
            bg.CommonEffortJunction("0_2"),
        ]
        bonds: list[tuple[str,str]] = [
            ("0_1", "S_e"),
            ("0_1", "0_2"),
            ("0_1", "1_3"),
            ("0_2", "R_1"),
            ("R_2", "1_3"),
            ("0_2", "1_1"),
            ("1_2", "1_1"),
            ("1_2", "S_f"),
        ]
        return bg.DirectedBondgraph("Causality Assignment", elements, bonds)

    @staticmethod
    def collision():
        elements: list[bg.Element] = [
            bg.Inertance("I_1", lambda f, p: p - 1 * f, initial_value=3),
            bg.CommonFlowJunction("1_1"),
            bg.CommonFlowJunction("1_3"),
            bg.CommonEffortJunction("0_1"),
            bg.Capacitance("C_1", lambda e, q: q - 1 * e, initial_value=0),

            bg.Inertance("I_2", lambda f, p: p - 2 * f, initial_value=-10),
            bg.CommonFlowJunction("1_2"),
            bg.CommonFlowJunction("1_4"),
            bg.CommonEffortJunction("0_2"),
            bg.Capacitance("C_2", lambda e, q: q - 1 * e, initial_value=0),
        ]
        bonds: list[tuple[str,str]] = [
            ("1_1", "I_1"),
            ("1_3", "1_1"),
            ("1_3", "0_1"),
            ("0_1", "1_4"),
            ("0_1", "C_1"),

            ("1_2", "I_2"),
            ("1_4", "1_2"),
            ("1_4", "0_2"),
            ("0_2", "1_3"),
            ("0_2", "C_2"),
        ]
        return bg.DirectedBondgraph("Collision", elements, bonds)

def main(params):
    methods: dict = {}
    for (name, method) in inspect.getmembers(Examples, predicate=inspect.isfunction):
        methods[name] = method
    if len(params) < 4 or params[1] == "help":
        print("Please provide <scenario step_number step_size>")
        print("<scenario> in [")
        for name in methods:
            print("  ", name)
        print("]")
        return
    if params[1] not in methods.keys() and params[1] != "all":
        raise Exception("Unknown scenario. Choose one in", methods.keys())
    bgs: list[bg.DirectedBondgraph] = []
    if params[1] == "all":
        for name in methods:
            bgs.append(
                methods[name]()
            )
    else:
        bgs.append(methods[sys.argv[1]]())
    step_number = int(sys.argv[2])
    step_size = float(sys.argv[3])
    for bondgraph in bgs:
        if "dgraph" in sys.argv:
            bondgraph.draw_graph()
        if "deq" in sys.argv:
            bondgraph.draw_equations()
        if "dsol" in sys.argv:
            bondgraph.draw_solution()
        if "dsim" in sys.argv:
            bondgraph.draw_simulation(
                start_time = 0.0,
                step_number = step_number,
                step_size = step_size,
                variables = bondgraph.get_vars(),
            )
        bondgraph.show()


if __name__ == "__main__":
    import sys
    main(sys.argv)

