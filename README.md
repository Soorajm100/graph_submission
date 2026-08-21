# Mentorship Network — CognoDB + FastAPI

This repository contains a small FastAPI backend that connects to a CognoDB/Neo4j graph database. The sample dataset models a simple mentorship network where people know skills and mentor one another.

Why a graph database?
- Relationships are first-class: mentorship chains, shared-skills, and multi-hop influence are more naturally expressed and efficiently traversed in a graph than in relational joins.

What is included
- FastAPI backend: [app/main.py](app/main.py#L1)
- Neo4j client helper: [app/neo4j_client.py](app/neo4j_client.py#L1)
- Seed script to load sample data: [scripts/seed.py](scripts/seed.py#L1)
- Example parameterised queries: [app/queries.py](app/queries.py#L1)

Setup
1. Copy `.env.example` to `.env` and set your `COGNODB_URI`, `COGNODB_USER`, and `COGNODB_PASSWORD`.
2. Install dependencies:
```
pip install -r requirements.txt
```
3. Load sample data:
```
python scripts/seed.py
```
4. Run the API:
```
uvicorn app.main:app --reload
```

Main queries
- `GET /person/{id}`: fetch a person and immediate relations.
- `GET /person/{id}/mentors`: find mentors up to 2 hops (multi-hop traversal).
- `GET /person/{id}/peers`: find peers that share skills.

DEMO



https://github.com/user-attachments/assets/19730650-6d37-489c-9fae-30ed94d4c98e


