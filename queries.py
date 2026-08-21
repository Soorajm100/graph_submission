from typing import Dict

# Example parameterised queries used by the API and seed script.

GET_PERSON = (
    "MATCH (p:Person {id: $id}) OPTIONAL MATCH (p)-[r]->(o) "
    "RETURN p as person, collect({rel: type(r), to: o}) as relations"
)

# Multi-hop mentorship chain: find mentors up to 2 hops
MENTOR_CHAIN = (
    "MATCH (p:Person {id: $id})-[:MENTORED_BY*1..2]->(mentor) "
    "RETURN DISTINCT mentor"
)

# Example of a query that's awkward in SQL: find people who share skills via multi-hop
PEER_SKILL_CONNECTIONS = (
    "MATCH (p:Person {id: $id})-[:KNOWS]->(s:Skill)<-[:KNOWS]-(peer) "
    "RETURN DISTINCT peer, collect(s.name) as shared_skills"
)
