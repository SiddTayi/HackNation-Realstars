"""
Seed script to insert 3 dummy support agents into realpage.db
Run once: python seed_agents.py
"""

from db_scripts.db_support_agent import insert_agent, retrieve_agent_by_email
from werkzeug.security import generate_password_hash
import sys
from pathlib import Path

# Add rag dir to path so we can import db helpers
# seed_agents.py is in backend/scr/utils/ -> need backend/scr/rag/
sys.path.insert(0, str(Path(__file__).parent.parent / "rag"))


AGENTS = [
    {
        "username": "agent_one",
        "email": "agent1@example.com",
        "password_hash": generate_password_hash("password1"),
        "agent_id": "agent1",
        "tier": "1",
    },
    {
        "username": "agent_two",
        "email": "agent2@example.com",
        "password_hash": generate_password_hash("password2"),
        "agent_id": "agent2",
        "tier": "2",
    },
    {
        "username": "agent_three",
        "email": "agent3@example.com",
        "password_hash": generate_password_hash("password3"),
        "agent_id": "agent3",
        "tier": "3",
    },
]


def seed():
    print("Seeding support agents...")
    for agent in AGENTS:
        existing = retrieve_agent_by_email(agent["email"])
        if existing:
            print(f"  Skipped (already exists): {agent['email']}")
            continue
        result = insert_agent(**agent)
        if result:
            print(f"  Inserted: {agent['email']} (id={result})")
        else:
            print(f"  FAILED: {agent['email']}")
    print("Done.")


if __name__ == "__main__":
    seed()
