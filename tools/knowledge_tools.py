from typing import List, Dict, Any, TypedDict
import json
import os

MEMORY_FILE_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..", "persistent_memory.json"
)


class Entity(TypedDict):
    name: str
    entityType: str
    observations: List[str]


class Relation(TypedDict):
    from_: str
    to: str
    relationType: str


class KnowledgeGraph(TypedDict):
    entities: List[Entity]
    relations: List[Relation]


class KnowledgeGraphManager:
    def __init__(self):
        self.memory_file_path = os.path.abspath(MEMORY_FILE_PATH)

    def _load_graph(self) -> KnowledgeGraph:
        entities: List[Entity] = []
        relations: List[Relation] = []
        if not os.path.exists(self.memory_file_path):
            return {"entities": [], "relations": []}
        with open(self.memory_file_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                item = json.loads(line)
                if item.get("type") == "entity":
                    # Remove the "type" field for compatibility
                    entity = {k: v for k, v in item.items() if k != "type"}
                    entities.append(entity)  # type: ignore
                elif item.get("type") == "relation":
                    relation = {
                        k if k != "from" else "from_": v
                        for k, v in item.items()
                        if k != "type"
                    }
                    relations.append(relation)  # type: ignore
        return {"entities": entities, "relations": relations}

    def _save_graph(self, graph: KnowledgeGraph) -> None:
        lines = []
        for e in graph["entities"]:
            entity = {"type": "entity", **e}
            lines.append(json.dumps(entity, ensure_ascii=False))
        for r in graph["relations"]:
            # Convert "from_" back to "from" for storage
            relation = {
                "type": "relation",
                **{k if k != "from_" else "from": v for k, v in r.items()},
            }
            lines.append(json.dumps(relation, ensure_ascii=False))
        with open(self.memory_file_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))

    def memory_create_entities(self, params: dict) -> list:
        """
        Create multiple new entities in the knowledge graph
        Expects: {"entities": [ ... ]}
        """
        entities = params["entities"]
        graph = self._load_graph()
        existing_names = {e["name"] for e in graph["entities"]}
        new_entities = [e for e in entities if e["name"] not in existing_names]
        graph["entities"].extend(new_entities)
        self._save_graph(graph)
        return new_entities

    def memory_create_relations(self, params: dict) -> list:
        """
        Create multiple new relations between entities in the knowledge graph. Relations should be in active voice
        Expects: {"relations": [ ... ]}
        """
        relations = params["relations"]
        graph = self._load_graph()

        def rel_key(r):
            return (r["from_"], r["to"], r["relationType"])

        existing = {rel_key(r) for r in graph["relations"]}
        new_relations = [r for r in relations if rel_key(r) not in existing]
        graph["relations"].extend(new_relations)
        self._save_graph(graph)
        return new_relations

    def memory_add_observations(self, params: dict) -> list:
        """
        Add new observations to existing entities in the knowledge graph
        Expects: {"observations": [ ... ]}
        """
        observations = params["observations"]
        graph = self._load_graph()
        results = []
        for obs in observations:
            entity = next(
                (e for e in graph["entities"] if e["name"] == obs["entityName"]), None
            )
            if not entity:
                raise ValueError(f"Entity with name {obs['entityName']} not found")
            new_obs = [c for c in obs["contents"] if c not in entity["observations"]]
            entity["observations"].extend(new_obs)
            results.append(
                {"entityName": obs["entityName"], "addedObservations": new_obs}
            )
        self._save_graph(graph)
        return results

    def memory_delete_entities(self, params: dict) -> None:
        """
        Delete multiple entities and their associated relations from the knowledge graph
        Expects: {"entity_names": [ ... ]}
        """
        entity_names = params["entity_names"]
        graph = self._load_graph()
        graph["entities"] = [
            e for e in graph["entities"] if e["name"] not in entity_names
        ]
        graph["relations"] = [
            r
            for r in graph["relations"]
            if r["from_"] not in entity_names and r["to"] not in entity_names
        ]
        self._save_graph(graph)

    def memory_delete_observations(self, params: dict) -> None:
        """
        Delete specific observations from entities in the knowledge graph
        Expects: {"deletions": [ ... ]}
        """
        deletions = params["deletions"]
        graph = self._load_graph()
        for d in deletions:
            entity = next(
                (e for e in graph["entities"] if e["name"] == d["entityName"]), None
            )
            if entity:
                entity["observations"] = [
                    o for o in entity["observations"] if o not in d["observations"]
                ]
        self._save_graph(graph)

    def memory_delete_relations(self, params: dict) -> None:
        """
        Delete multiple relations from the knowledge graph"
        Expects: {"relations": [ ... ]}
        """
        relations = params["relations"]
        graph = self._load_graph()

        def rel_key(r):
            return (r["from_"], r["to"], r["relationType"])

        to_delete = {rel_key(r) for r in relations}
        graph["relations"] = [
            r for r in graph["relations"] if rel_key(r) not in to_delete
        ]
        self._save_graph(graph)

    def memory_read_graph(self, params: dict = None) -> KnowledgeGraph:
        """
        Read the entire knowledge graph.
        Expects: {} (no parameters needed)
        """
        return self._load_graph()

    def memory_search_nodes(self, params: dict) -> KnowledgeGraph:
        """
        Search for nodes in the knowledge graph based on a query
        Expects: {"query": "..."}
        """
        query = params["query"]
        graph = self._load_graph()
        q = query.lower()
        filtered_entities = [
            e
            for e in graph["entities"]
            if q in e["name"].lower()
            or q in e["entityType"].lower()
            or any(q in o.lower() for o in e["observations"])
        ]
        filtered_names = {e["name"] for e in filtered_entities}
        filtered_relations = [
            r
            for r in graph["relations"]
            if r["from_"] in filtered_names and r["to"] in filtered_names
        ]
        return {"entities": filtered_entities, "relations": filtered_relations}

    def memory_open_nodes(self, params: dict) -> KnowledgeGraph:
        """
        Open specific nodes in the knowledge graph by their names
        Expects: {"names": [ ... ]}
        """
        names = params["names"]
        graph = self._load_graph()
        filtered_entities = [e for e in graph["entities"] if e["name"] in names]
        filtered_names = {e["name"] for e in filtered_entities}
        filtered_relations = [
            r
            for r in graph["relations"]
            if r["from_"] in filtered_names and r["to"] in filtered_names
        ]
        return {"entities": filtered_entities, "relations": filtered_relations}
