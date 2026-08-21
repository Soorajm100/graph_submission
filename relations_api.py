from fastapi import APIRouter, HTTPException
from typing import Dict
from neo4j_client import run_cypher

router = APIRouter()


@router.post("/people")
async def create_person(payload: Dict[str, str]):
    """Create a person. Payload: {"id": "alice", "name": "Alice"} """
    if "id" not in payload:
        raise HTTPException(status_code=400, detail="Missing id")
    q = "MERGE (p:Person {id:$id}) SET p += $props RETURN p"
    params = {"id": payload["id"], "props": payload}
    rows = await run_cypher(q, params)
    return {"created": rows}


@router.post("/skills")
async def create_skill(payload: Dict[str, str]):
    """Create a skill. Payload: {"name": "Graph Databases"} """
    if "name" not in payload:
        raise HTTPException(status_code=400, detail="Missing name")
    q = "MERGE (s:Skill {name:$name}) SET s += $props RETURN s"
    params = {"name": payload["name"], "props": payload}
    rows = await run_cypher(q, params)
    return {"created": rows}


@router.post("/relations/mentorship")
async def add_mentorship(payload: Dict[str, str]):
    """Create mentorship relation. Payload: {"mentor_id":"alice","mentee_id":"bob"} """
    mentor = payload.get("mentor_id")
    mentee = payload.get("mentee_id")
    if not mentor or not mentee:
        raise HTTPException(status_code=400, detail="mentor_id and mentee_id required")
    q = (
        "MATCH (m:Person {id:$mentor}), (t:Person {id:$mentee}) "
        "MERGE (t)-[r:MENTORED_BY]->(m) RETURN t,m,r"
    )
    rows = await run_cypher(q, {"mentor": mentor, "mentee": mentee})
    return {"relation": rows}


@router.post("/relations/knows")
async def add_knows(payload: Dict[str, str]):
    """Create KNOWS relation. Payload: {"person_id":"bob","skill_name":"Graph Databases"} """
    pid = payload.get("person_id")
    skill = payload.get("skill_name")
    if not pid or not skill:
        raise HTTPException(status_code=400, detail="person_id and skill_name required")
    q = (
        "MATCH (p:Person {id:$pid}), (s:Skill {name:$skill}) "
        "MERGE (p)-[r:KNOWS]->(s) RETURN p,s,r"
    )
    rows = await run_cypher(q, {"pid": pid, "skill": skill})
    return {"relation": rows}
