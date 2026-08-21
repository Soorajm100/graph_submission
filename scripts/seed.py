"""
Seed script to populate a CognoDB / Neo4j instance with sample mentorship graph data.

Run:
  python scripts/seed.py

It reads DB connection info from environment variables (`COGNODB_URI`, `COGNODB_USER`, `COGNODB_PASSWORD`).
"""
import os
from dotenv import load_dotenv
from neo4j import GraphDatabase

load_dotenv()

URI = os.getenv("COGNODB_URI") or os.getenv("NEO4J_URI") or "bolt://localhost:7687"
USER = os.getenv("COGNODB_USER") or "neo4j"
PASSWORD = os.getenv("COGNODB_PASSWORD")

if not PASSWORD:
    raise RuntimeError("Please set COGNODB_PASSWORD (or NEO4J_PASSWORD) in the environment before running this script")

driver = GraphDatabase.driver(URI, auth=(USER, PASSWORD))

def run_statements(tx):
    # Create constraints / indexes
    r = tx.run("CREATE CONSTRAINT IF NOT EXISTS FOR (p:Person) REQUIRE p.id IS UNIQUE")
    r.consume()
    r = tx.run("CREATE CONSTRAINT IF NOT EXISTS FOR (s:Skill) REQUIRE s.name IS UNIQUE")
    r.consume()

    # Create sample people
    people = [
        {"id": "alice", "name": "Alice"},
        {"id": "bob", "name": "Bob"},
        {"id": "carol", "name": "Carol"},
        {"id": "dave", "name": "Dave"}
    ]
    for p in people:
        r = tx.run("MERGE (x:Person {id: $id}) SET x.name = $name", p)
        r.consume()

    # Skills
    skills = [
        {"name": "Graph Databases"}, {"name": "Python"}, {"name": "Data Modeling"}
    ]
    for s in skills:
        r = tx.run("MERGE (sk:Skill {name: $name})", s)
        r.consume()

    # Relationships: who knows which skill
    r = tx.run(
        "MATCH (a:Person {id:'alice'}), (s:Skill {name:'Graph Databases'}) MERGE (a)-[:KNOWS]->(s)"
    )
    r.consume()
    r = tx.run(
        "MATCH (b:Person {id:'bob'}), (s:Skill {name:'Python'}) MERGE (b)-[:KNOWS]->(s)"
    )
    r.consume()
    r = tx.run(
        "MATCH (c:Person {id:'carol'}), (s:Skill {name:'Data Modeling'}) MERGE (c)-[:KNOWS]->(s)"
    )
    r.consume()

    # Mentorship relationships (Bob mentored by Alice; Carol mentored by Bob; Dave mentored by Carol)
    r = tx.run("MATCH (a:Person {id:'alice'}), (b:Person {id:'bob'}) MERGE (b)-[:MENTORED_BY]->(a)")
    r.consume()
    r = tx.run("MATCH (b:Person {id:'bob'}), (c:Person {id:'carol'}) MERGE (c)-[:MENTORED_BY]->(b)")
    r.consume()
    r = tx.run("MATCH (c:Person {id:'carol'}), (d:Person {id:'dave'}) MERGE (d)-[:MENTORED_BY]->(c)")
    r.consume()


def main():
    with driver.session() as session:
        # neo4j Python driver v5 uses `execute_write` instead of `write_transaction`
        session.execute_write(run_statements)

    print("Seed data loaded.")


if __name__ == "__main__":
    main()
