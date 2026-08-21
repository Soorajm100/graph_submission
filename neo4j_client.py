import os
from dotenv import load_dotenv
from neo4j import AsyncGraphDatabase
from typing import Any, Dict, List

load_dotenv()

_URI = os.getenv("COGNODB_URI") or os.getenv("NEO4J_URI") or "bolt://localhost:7687"
_USER = os.getenv("COGNODB_USER") or os.getenv("NEO4J_USER") or os.getenv("NEO4J_USER") or "neo4j"
_PASSWORD = os.getenv("COGNODB_PASSWORD") or os.getenv("NEO4J_PASSWORD")

driver = None

async def create_driver():
    global driver
    if driver is None:
        if not _PASSWORD:
            raise RuntimeError("Database password not set in environment")
        driver = AsyncGraphDatabase.driver(_URI, auth=(_USER, _PASSWORD))
    return driver

async def close_driver():
    global driver
    if driver:
        await driver.close()
        driver = None

async def run_cypher(query: str, params: Dict[str, Any] = None) -> List[Dict[str, Any]]:
    if driver is None:
        raise RuntimeError("Driver not initialized")
    async with driver.session() as session:
        result = await session.run(query, params or {})
        rows = []

        def _serialize_value(v):
            if v is None:
                return None
            if isinstance(v, (str, int, float, bool)):
                return v
            if isinstance(v, (list, tuple)):
                return [_serialize_value(i) for i in v]
            if isinstance(v, dict):
                return {k: _serialize_value(val) for k, val in v.items()}
            # Node-like
            if hasattr(v, "labels") and hasattr(v, "id"):
                try:
                    props = dict(v)
                except Exception:
                    props = {}
                return {"_node": True, "labels": list(v.labels), "id": getattr(v, "id", None), "properties": props}
            # Relationship-like
            if hasattr(v, "type") and (hasattr(v, "start_node") or hasattr(v, "start")):
                try:
                    props = dict(v)
                except Exception:
                    props = {}
                start = getattr(v, "start_node", None) or getattr(v, "start", None)
                end = getattr(v, "end_node", None) or getattr(v, "end", None)
                start_id = getattr(start, "id", None) if start is not None else None
                end_id = getattr(end, "id", None) if end is not None else None
                return {"_rel": True, "type": getattr(v, "type", None), "start": start_id, "end": end_id, "properties": props}
            # Path-like
            if hasattr(v, "nodes") and hasattr(v, "relationships"):
                return {"_path": True, "nodes": [_serialize_value(n) for n in v.nodes], "relationships": [_serialize_value(r) for r in v.relationships]}
            try:
                return dict(v)
            except Exception:
                return str(v)

        async for record in result:
            data = {}
            for k in record.keys():
                data[k] = _serialize_value(record.get(k))
            rows.append(data)
        return rows


def dinit(host: str = "127.0.0.1", port: int = 8000, reload: bool = False) -> None:
    """Start the Uvicorn server serving the FastAPI app.

    Example: dinit(port=8000)
    """
    try:
        import uvicorn
    except Exception as e:
        raise RuntimeError("uvicorn is required to run the server") from e

    # Serve the app located at main:app (module `main.py` at repo root)
    uvicorn.run("main:app", host=host, port=port, reload=reload)
