import os
import networkx as nx
import json
import logging
from backend.config import settings

logger = logging.getLogger(__name__)

class GraphStore:
    """
    Enhanced Knowledge Graph engine using NetworkX for GraphRAG.
    Supports multi-hop traversal, fuzzy node matching, and bidirectional queries.
    """
    def __init__(self):
        self.graph_path = os.path.join(settings.QDRANT_DB_DIR, "knowledge_graph.json")
        self.graph = nx.DiGraph()
        self._node_index = {}  # Cached lowercase -> original node mapping
        self._bulk_mode = False  # When True, defers save_graph() for batch performance
        self.load_graph()

    def load_graph(self):
        if os.path.exists(self.graph_path):
            try:
                data = json.load(open(self.graph_path, 'r'))
                self.graph = nx.node_link_graph(data)
                self._build_node_index()
                logger.info(f"Loaded Knowledge Graph with {self.graph.number_of_nodes()} nodes and {self.graph.number_of_edges()} edges.")
            except Exception as e:
                logger.error(f"Failed to load graph: {e}")

    def _build_node_index(self):
        """Build a keyword index for fast fuzzy matching."""
        self._node_index = {}
        for node in self.graph.nodes():
            node_lower = node.lower()
            # Index each word in the node name
            for word in node_lower.split():
                if len(word) > 3:
                    if word not in self._node_index:
                        self._node_index[word] = set()
                    self._node_index[word].add(node)

    def save_graph(self):
        try:
            data = nx.node_link_data(self.graph)
            with open(self.graph_path, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save graph: {e}")

    def set_bulk_mode(self, enabled: bool):
        """Enable/disable bulk mode. In bulk mode, save_graph() is deferred for batch performance."""
        self._bulk_mode = enabled
        if not enabled:
            # Leaving bulk mode — flush to disk and rebuild index
            self.save_graph()
            self._build_node_index()

    def flush(self):
        """Force-save the graph to disk and rebuild the index (useful after bulk inserts)."""
        self.save_graph()
        self._build_node_index()

    def add_relationship(self, source: str, relation: str, target: str, attributes: dict = None):
        source = source.lower().strip()
        target = target.lower().strip()
        
        if not self.graph.has_node(source):
            self.graph.add_node(source, type="entity")
        if not self.graph.has_node(target):
            self.graph.add_node(target, type="entity")
            
        attr = attributes or {}
        attr['relation'] = relation
        self.graph.add_edge(source, target, **attr)
        if not self._bulk_mode:
            self.save_graph()

    def _find_matching_nodes(self, query_terms: list[str], max_matches: int = 10) -> set:
        """Find graph nodes that match query terms using the keyword index."""
        matched = set()
        for term in query_terms:
            term = term.lower().strip()
            
            # Exact substring match in node names
            if term in self._node_index:
                matched.update(self._node_index[term])
            
            # Also check if the term is a substring of indexed words
            for indexed_word, nodes in self._node_index.items():
                if term in indexed_word or indexed_word in term:
                    matched.update(nodes)
                    
            if len(matched) >= max_matches:
                break
                
        return matched

    def query_subgraph(self, starting_nodes: list[str], max_depth: int = 2, max_total_relations: int = 100) -> dict:
        """
        Enhanced subgraph query with:
        1. Fuzzy node matching via keyword index
        2. Multi-hop traversal (up to max_depth)
        3. Bidirectional edge traversal (both successors and predecessors)
        4. Hard total relation cap to prevent LLM context overflow
        """
        results = {}
        
        # Use fuzzy matching to find relevant nodes
        matched_nodes = self._find_matching_nodes(starting_nodes)
        
        # Also try direct substring match (original behavior)
        for node in starting_nodes:
            node = node.lower().strip()
            for n in self.graph.nodes():
                if node in n:
                    matched_nodes.add(n)
                    if len(matched_nodes) >= 20:  # Hard cap on matched nodes
                        break
        
        total_relations = 0
        for m_node in matched_nodes:
            if total_relations >= max_total_relations:
                break
            if m_node not in results:
                results[m_node] = []
                
                # Multi-hop: traverse up to max_depth levels
                visited = {m_node}
                current_level = [m_node]
                
                for depth in range(max_depth):
                    if total_relations >= max_total_relations:
                        break
                    next_level = []
                    for node in current_level:
                        # Forward edges (successors)
                        for n in self.graph.successors(node):
                            if n not in visited:
                                rel = self.graph.edges[node, n].get('relation', 'RELATES_TO')
                                results[m_node].append({
                                    "target": n,
                                    "relation": rel,
                                    "depth": depth + 1,
                                    "direction": "outgoing"
                                })
                                visited.add(n)
                                next_level.append(n)
                                total_relations += 1
                        
                        # Backward edges (predecessors) — find what points TO this node
                        for n in self.graph.predecessors(node):
                            if n not in visited:
                                rel = self.graph.edges[n, node].get('relation', 'RELATES_TO')
                                results[m_node].append({
                                    "target": n,
                                    "relation": f"(inverse) {rel}",
                                    "depth": depth + 1,
                                    "direction": "incoming"
                                })
                                visited.add(n)
                                next_level.append(n)
                                total_relations += 1
                    
                    current_level = next_level
                    if not current_level:
                        break
        
        # Per-node limit as secondary safeguard
        for key in results:
            results[key] = results[key][:10]
            
        logger.info(f"GraphRAG query: {len(starting_nodes)} terms -> {len(matched_nodes)} nodes -> {sum(len(v) for v in results.values())} relations")
        return results

graph_store = GraphStore()
