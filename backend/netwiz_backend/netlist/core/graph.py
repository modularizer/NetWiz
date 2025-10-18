import networkx as nx

from netwiz_backend.netlist.core.models import Netlist


def to_graph(nl: Netlist) -> nx.Graph:
    G = nx.Graph()
    for c in nl.components:
        G.add_node(("comp", c.id), kind="component", data=c)
    for n in nl.nets:
        G.add_node(("net", n.id), kind="net", data=n)
        for conn in n.connections:
            G.add_edge(("comp", conn.component), ("net", n.id), pin=conn.pin)
    return G
