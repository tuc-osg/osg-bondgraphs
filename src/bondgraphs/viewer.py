from __future__ import annotations
import networkx as nx
import sympy as sp
import matplotlib.pyplot as plt

from .bond import Bond
from .equation import BondgraphEquation

plt.rcParams["font.family"] = "serif"
plt.rcParams["mathtext.fontset"] = "dejavuserif"


class BondgraphViewer():
    TITLE_FONT_SIZE = 18
    FONT_SIZE = 14

    def get_node_ids(self) -> list[str]:
        raise NotImplementedError

    def get_bonds(self) -> list[Bond]:
        raise NotImplementedError

    def get_solutions(self, log: bool = False) -> list[dict]:
        raise NotImplementedError

    def get_equations(self) -> list[BondgraphEquation]:
        raise NotImplementedError

    def get_name(self) -> str:
        raise NotImplementedError

    def get_time_var(self) -> sp.Symbol:
        raise NotImplementedError

    def get_tau(self) -> sp.Symbol:
        raise NotImplementedError

    def simulate(
        self,
        start_time: float,
        step_number: int,
        step_size: float,
        variables: list[sp.Function],
    ) -> dict[str,list[float]]:
        raise NotImplementedError

    @staticmethod
    def __create_graph(node_ids: list[str], edges: list[tuple[int,tuple[str,str]]]) -> nx.DiGraph:
        graph: nx.DiGraph = nx.DiGraph()
        graph.add_nodes_from(node_ids)
        graph.add_edges_from([edge for (_, edge) in edges])
        return graph

    @staticmethod
    def __draw_nodes(graph: nx.DiGraph, node_ids: list[str], positioning: dict):
        options: dict = {}
        nx.draw_networkx_nodes(
            graph,
            pos = positioning,
            nodelist = node_ids,
            node_size = 1000,
            node_color = "black",
            alpha = 0.0,
            **options
        )

    @staticmethod
    def __draw_node_labels(graph: nx.DiGraph, node_ids: list[str], positioning: dict):
        node_labels = {}
        for name in node_ids:
            node_labels[name] = r"$" + name + "$"
        nx.draw_networkx_labels(
            graph,
            pos = positioning,
            labels = node_labels,
            font_size = 13,
            font_color = "black",
        )

    @staticmethod
    def __draw_edges(
        graph: nx.DiGraph,
        edges: list[tuple[int,tuple[str,str]]],
        positioning: dict,
        arrowstyle: str
    ):
        nx.draw_networkx_edges(
            graph,
            pos = positioning,
            edgelist = [edge for (_, edge) in edges],
            width = 1,
            alpha = 1.0,
            edge_color = "black",
            arrowsize = 10,
            arrowstyle = arrowstyle,
        )

    @staticmethod
    def __draw_edge_labels(graph: nx.DiGraph, edges: list[tuple[int,tuple[str,str]]], positioning: dict):
        edge_labels = {}
        for idx, edge in edges:
            edge_labels[edge] = r"$(f_{" + str(idx) + "}," + "e_{" + str(idx) + "})$"
        nx.draw_networkx_edge_labels(
            graph,
            pos = positioning,
            edge_labels = edge_labels,
            verticalalignment = "baseline",
            rotate = False,
        )

    def draw_graph(self):
        node_ids: list[str] = self.get_node_ids()
        bonds: list[Bond] = self.get_bonds()
        edges: list[tuple[int,tuple[str,str]]] = [
            (bond.get_index(), (bond.get_start(), bond.get_end())) for bond in bonds
        ]
        graph: nx.DiGraph = self.__create_graph(node_ids, edges)
        positioning: dict = nx.planar_layout(graph)
        scaled_positioning: dict = nx.rescale_layout_dict(positioning, scale=1)
        title: str = "Bond Graph"
        plt.figure(self.get_name() + " - " + title)
        plt.title(title, fontsize=self.TITLE_FONT_SIZE, fontweight="bold")
        self.__draw_nodes(graph, node_ids, scaled_positioning)
        self.__draw_node_labels(graph, node_ids, scaled_positioning)
        causalities: list[tuple[int,tuple[str,str]]] = []
        for bond in bonds:
            dir: tuple[str,str]|None = bond.get_effort_causality_direction()
            if dir == None:
                raise Exception("Causality has not been assigned ")
            causalities.append((bond.get_index(), dir))
        self.__draw_edges(graph, edges, scaled_positioning, "->")
        self.__draw_edges(graph, causalities, scaled_positioning, "-[")
        self.__draw_edge_labels(graph, edges, scaled_positioning)

    def __draw_latex(self, title: str, latex_text: str):
        if "\\cases" in latex_text:
            print("Latex code contains non-representable things.")
            return
        plt.figure(self.get_name() + " - " + title)
        plt.title(title, fontsize=self.TITLE_FONT_SIZE, fontweight="bold")
        # \limits is not printable by matplotlib (other things as well)
        latex_text = latex_text.replace("\\limits", "")
        latex_text = latex_text.replace("\\right", "")
        latex_text = latex_text.replace("\\left", "")
        x_position: float = 0.5
        y_position: float = 0.5
        plt.text(
            x_position,
            y_position,
            latex_text,
            horizontalalignment="center",
            verticalalignment="center",
            fontsize=self.FONT_SIZE,
            linespacing=1.8,
        )
        plt.axis("off")

    def draw_equations(self):
        latex_str: str = ""
        element_equations: list[BondgraphEquation] = self.get_equations()
        for el_eq in element_equations:
            equation = el_eq.get_equation()
            equation_str: str = sp.latex(equation)
            latex_str: str = latex_str + (rf"${equation_str}$" + "\n")
        self.__draw_latex("Equations", latex_str)

    def draw_solution(self, solution_nr: int = 0):
        latex_str: str = ""
        solution = self.get_solutions(log=True)[solution_nr]
        for var in solution:
            equation_str: str = sp.latex(var) + "=" + sp.latex(solution[var])
            latex_str: str = latex_str + (rf"${equation_str}$" + "\n")
        self.__draw_latex("Solutions", latex_str)

    def draw_simulation(
        self,
        start_time: float,
        step_number: int,
        step_size: float,
        variables: list[sp.Function],
        solution_nr: int = 0
    ):
        data_sets: dict[str,list[float]] = self.simulate(
            start_time,
            step_number,
            step_size,
            variables,
            solution_nr=solution_nr,
        )
        title: str = "Simulation Results"
        figure = plt.figure(self.get_name() + " - " + title)
        plt.title(title, fontsize=self.TITLE_FONT_SIZE, fontweight="bold")
        plt.grid(visible=True, which="major", axis="both")
        lines = []
        for var in variables:
            var_name: str = str(var)
            line, = plt.plot(data_sets["t"], data_sets[var_name], label= r"$" + var_name + r"$")
            lines.append(line)
        plt.xlabel("t [s]")
        legend = plt.legend()
        legend_lines: list = legend.get_lines()
        line_dict = {}
        for legend_line, original_line in zip(legend_lines, lines):
            legend_line.set_picker(7)
            line_dict[legend_line] = original_line
            original_line.set_visible(False)
            legend_line.set_alpha(0.2)
        def onpick(event):
            legend_line = event.artist
            original_line = line_dict[legend_line]
            vis = not original_line.get_visible()
            original_line.set_visible(vis)
            if vis:
                legend_line.set_alpha(1.0)
            else:
                legend_line.set_alpha(0.2)
            figure.canvas.draw()
        figure.canvas.mpl_connect("pick_event", onpick)

    def show(self):
        plt.show()
