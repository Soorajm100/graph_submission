"""Entrypoint to run the FastAPI app with Uvicorn.

Usage:
    python main.py --port 8000
"""
import os
import argparse

from neo4j_client import dinit


def main():
        parser = argparse.ArgumentParser(description="Run FastAPI app with Uvicorn")
        parser.add_argument("--host", default=os.getenv("HOST", "127.0.0.1"))
        parser.add_argument("--port", type=int, default=int(os.getenv("PORT", "8000")))
        parser.add_argument("--reload", action="store_true", help="enable Uvicorn reload")
        args = parser.parse_args()

        dinit(host=args.host, port=args.port, reload=args.reload)


if __name__ == "__main__":
        main()

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import asyncio
from neo4j_client import create_driver, close_driver, run_cypher
import queries
from relations_api import router as relations_router

app = FastAPI(title="CognoDB/FastAPI Backend")

# include relations router
app.include_router(relations_router)

# Enable CORS for all origins (development/demo convenience)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    try:
        await create_driver()
    except Exception as e:
        # keep app running but record startup failure
        app.state.db_error = str(e)


@app.on_event("shutdown")
async def shutdown_event():
    await close_driver()


@app.get("/health")
async def health():
    if getattr(app.state, "db_error", None):
        return JSONResponse(status_code=503, content={"status": "error", "detail": app.state.db_error})
    try:
        rows = await run_cypher("RETURN 1 as ok")
        return {"status": "ok", "db": rows}
    except Exception as e:
        raise HTTPException(status_code=503, detail=str(e))


@app.get("/person/{person_id}")
async def get_person(person_id: str):
    try:
        rows = await run_cypher(queries.GET_PERSON, {"id": person_id})
        if not rows:
            raise HTTPException(status_code=404, detail="Person not found")
        rec = rows[0]
        return rec
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/person/{person_id}/mentors")
async def get_mentors(person_id: str):
    try:
        rows = await run_cypher(queries.MENTOR_CHAIN, {"id": person_id})
        return {"mentors": rows}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/person/{person_id}/peers")
async def get_peers(person_id: str):
    try:
        rows = await run_cypher(queries.PEER_SKILL_CONNECTIONS, {"id": person_id})
        return {"peers": rows}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/mentors")
async def list_mentors():
    """List all persons who are mentors (have someone mentored by them)."""
    try:
        q = "MATCH (m:Person)<-[:MENTORED_BY]-() RETURN DISTINCT m as mentor"
        rows = await run_cypher(q)
        return {"mentors": rows}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/peers")
async def list_peers():
    """List pairs of people who share skills."""
    try:
        q = (
            "MATCH (p1:Person)-[:KNOWS]->(s:Skill)<-[:KNOWS]-(p2:Person) "
            "WHERE p1.id < p2.id "
            "RETURN p1 as person1, p2 as person2, collect(DISTINCT s.name) as shared_skills"
        )
        rows = await run_cypher(q)
        return {"peer_pairs": rows}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/relation/{a_id}/{b_id}")
async def relation_between(a_id: str, b_id: str):
    """Return the shortest path (up to length 6) between two people."""
    try:
        q = (
            "MATCH (a:Person {id:$a_id}), (b:Person {id:$b_id}) "
            "OPTIONAL MATCH p = shortestPath((a)-[*..6]-(b)) "
            "RETURN p as path"
        )
        rows = await run_cypher(q, {"a_id": a_id, "b_id": b_id})
        return {"relation": rows}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
