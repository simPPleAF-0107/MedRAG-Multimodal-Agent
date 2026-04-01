import os
import networkx as nx
import json
import logging
from backend.config import settings

logger = logging.getLogger(__name__)

class GraphStore:
    """
    A lightweight Knowledge Graph engine using NetworkX for GraphRAG.
    Stores and queries relationships like: (Symptom) -> 'INDICATES' -> (Disease) -> 'TREATED_BY' -> (Medication)
    """
    def __init__(self):
        self.graph_path = os.path.join(settings.QDRANT_DB_DIR, "knowledge_graph.json")
        self.graph = nx.DiGraph()
        self.load_graph()

    def load_graph(self):
        """Loads graph from disk if it exists."""
        if os.path.exists(self.graph_path):
            try:
                data = json.load(open(self.graph_path, 'r'))
                self.graph = nx.node_link_graph(data)
                logger.info(f"Loaded Knowledge Graph with {self.graph.number_of_nodes()} nodes.")
            except Exception as e:
                logger.error(f"Failed to load graph: {e}")

    def save_graph(self):
        """Saves graph to disk."""
        try:
            data = nx.node_link_data(self.graph)
            with open(self.graph_path, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save graph: {e}")

    def add_relationship(self, source: str, relation: str, target: str, attributes: dict = None):
        """Add an edge between two concepts (e.g., 'Chest Pain' -> INDICATES -> 'Heart Attack')"""
        source = source.lower().strip()
        target = target.lower().strip()
        
        if not self.graph.has_node(source):
            self.graph.add_node(source, type="entity")
        if not self.graph.has_node(target):
            self.graph.add_node(target, type="entity")
            
        attr = attributes or {}
        attr['relation'] = relation
        self.graph.add_edge(source, target, **attr)
        self.save_graph()

    def query_subgraph(self, starting_nodes: list[str], max_depth: int = 2) -> dict:
        """
        Retrieves a subgraph for given symptoms/entities to ground the LLM.
        """
        results = {}
        for node in starting_nodes:
            node = node.lower().strip()
            # Try to match substrings if exact node isn't found
            matched_nodes = [n for n in self.graph.nodes() if node in n]
            
            for m_node in matched_nodes:
                if m_node not in results:
                    results[m_node] = []
                    # Get neighbors up to depth 1 for now
                    neighbors = self.graph.successors(m_node)
                    for n in neighbors:
                        rel = self.graph.edges[m_node, n].get('relation', 'RELATES_TO')
                        results[m_node].append({
                            "target": n,
                            "relation": rel
                        })
        return results

graph_store = GraphStore()
