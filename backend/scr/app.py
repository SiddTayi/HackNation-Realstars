"""
Flask API Server for RealPage AI Resolution System
Endpoints: Auth, Tickets, Knowledge Base, New Knowledge
"""
import pandas as pd
from openai import OpenAI
import time
import os
from rag.db_scripts.db_new_knowledge import (
    insert_new_knowledge,
    retrieve_new_knowledge,
    list_new_knowledge,
    last_row_db as next_nk_id,
)
from rag.db_scripts.db_knowledge_articles import (
    retrieve_kb,
    insert_kb,
    last_row_db as next_kb_id,
)
from rag.db_scripts.db_ticket import (
    insert_ticket,
    retrieve_ticket,
    retrieve_ticket_by_id_string,
    update_ticket,
    get_tickets_by_status,
    last_row_db as next_ticket_id,
)
from rag.db_scripts.db_support_agent import retrieve_agent_by_email, retrieve_agent_by_agent_id
from rag.db_scripts.db_realpage_user import retrieve_user_by_email
from rag.scripts.classification_agent import ClassificationAgent
from rag.scripts.generation_agent import GenerationAgent
import os
import sys
import sqlite3
import jwt
import json
from pathlib import Path
from datetime import datetime, timedelta, timezone
from functools import wraps
from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.security import check_password_hash
from dotenv import load_dotenv
load_dotenv()

# ---------------------------------------------------------------------------
# Path setup – so we can import the existing db helper modules
# ---------------------------------------------------------------------------
BASE_DIR = Path(__file__).parent          # …/backend/scr
RAG_DIR = BASE_DIR / "rag"               # …/backend/scr/rag
DB_DIR = BASE_DIR.parent / "databases"   # …/backend/databases
sys.path.insert(0, str(RAG_DIR))


load_dotenv()

# ---------------------------------------------------------------------------
# App configuration
# ---------------------------------------------------------------------------
app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*", "methods": ["GET", "POST", "PATCH", "DELETE", "OPTIONS"], "allow_headers": ["Content-Type", "Authorization"]}})

# ---------------------------------------------------------------------------
# Initialize AI Agents (lazy loading to avoid startup issues)
# ---------------------------------------------------------------------------
_classification_agent = None
_generation_agent = None

def get_classification_agent():
    """Lazy load classification agent."""
    global _classification_agent
    if _classification_agent is None:
        try:
            _classification_agent = ClassificationAgent()
        except Exception as e:
            print(f"Warning: Could not initialize ClassificationAgent: {e}")
            return None
    return _classification_agent

def get_generation_agent():
    """Lazy load generation agent."""
    global _generation_agent
    if _generation_agent is None:
        try:
            _generation_agent = GenerationAgent()
        except Exception as e:
            print(f"Warning: Could not initialize GenerationAgent: {e}")
            return None
    return _generation_agent

SECRET_KEY = os.getenv("SECRET_KEY", "realpage-hackathon-secret-key")
ALGORITHM = "HS256"
TOKEN_EXPIRY_MINUTES = 30

# Database paths (used for direct queries the helpers don't cover)
REALPAGE_DB = DB_DIR / "realpage.db"
KB_DB = DB_DIR / "knowledge_articles.db"


# ===================================================================
# Helpers
# ===================================================================

def _make_token(payload: dict) -> str:
    """Create a JWT token."""
    payload["exp"] = datetime.now(
        timezone.utc) + timedelta(minutes=TOKEN_EXPIRY_MINUTES)
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def _decode_token(token: str) -> dict:
    """Decode and verify a JWT token."""
    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])


def token_required(f):
    """Decorator that enforces a valid Bearer token."""
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return jsonify({"error": "Missing or invalid Authorization header"}), 401
        token = auth_header.split(" ", 1)[1]
        try:
            payload = _decode_token(token)
            request.user = payload  # attach user info to request
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token expired"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "Invalid token"}), 401
        return f(*args, **kwargs)
    return decorated


def _get_realpage_conn():
    """Return a sqlite3 connection to realpage.db with Row factory."""
    conn = sqlite3.connect(REALPAGE_DB)
    conn.row_factory = sqlite3.Row
    return conn


def _get_kb_conn():
    """Return a sqlite3 connection to knowledge_articles.db with Row factory."""
    conn = sqlite3.connect(KB_DB)
    conn.row_factory = sqlite3.Row
    return conn


# ===================================================================
# AUTH ENDPOINTS
# ===================================================================

@app.route("/api/auth/login", methods=["POST"])
def login():
    """
    POST /api/auth/login
    Body: { email, password, user_type }
    user_type: "user" -> realpage_user table
    user_type: "agent" -> support_agent table
    """
    data = request.get_json(silent=True) or {}
    email = data.get("email", "").strip()
    password = data.get("password", "")
    user_type = data.get("user_type", "").strip().lower()

    if not email or not password:
        return jsonify({"error": "email and password are required"}), 400
    if user_type not in ("user", "agent"):
        return jsonify({"error": "user_type must be 'user' or 'agent'"}), 400

    if user_type == "user":
        record = retrieve_user_by_email(email)
        if not record:
            return jsonify({"error": "Invalid credentials"}), 401
        if not check_password_hash(record["password_hash"], password):
            return jsonify({"error": "Invalid credentials"}), 401
        token_payload = {
            "id": record["id"],
            "email": record["email"],
            "name": record["username"],
            "role": record.get("role", "realpage_user"),
        }
    else:  # agent
        record = retrieve_agent_by_email(email)
        if not record:
            return jsonify({"error": "Invalid credentials"}), 401
        if not check_password_hash(record["password_hash"], password):
            return jsonify({"error": "Invalid credentials"}), 401
        token_payload = {
            "id": record["id"],
            "email": record["email"],
            "name": record["username"],
            "role": "agent",
            "agent_id": record["agent_id"],
            "tier": record["tier"],
        }

    token = _make_token(token_payload)

    return jsonify({
        "token": token,
        "user": {
            "id": token_payload.get("agent_id", token_payload["id"]),
            "name": token_payload["name"],
            "email": token_payload["email"],
            "role": token_payload["role"],
        },
    }), 200


@app.route("/api/auth/logout", methods=["POST"])
@token_required
def logout():
    """
    POST /api/auth/logout
    Stateless JWT – just acknowledge.
    """
    return jsonify({"success": True}), 200


# ===================================================================
# TICKET ENDPOINTS
# ===================================================================

@app.route("/api/tickets/upload", methods=["POST"])
@token_required
def upload_tickets():
    """
    POST /api/tickets/upload
    Body: { tickets: [...], submitted_by }
    Creates ticket rows in realpage.db, processes through AI agents, and returns them.
    """
    data = request.get_json(silent=True) or {}
    tickets_data = data.get("tickets", [])
    submitted_by = data.get("submitted_by")

    if not tickets_data:
        return jsonify({"error": "tickets array is required"}), 400

    created_tickets = []
    ai_responses = []

    # Get AI agents
    classification_agent = get_classification_agent()
    generation_agent = get_generation_agent()

    for t in tickets_data:
        new_id = next_ticket_id()
        transcript = t.get("transcript", "")
        
        # Insert ticket into database
        row = insert_ticket(
            ticket_id=new_id,
            conversation_id=t.get("conversation_id", ""),
            channel=t.get("channel"),
            customer_role=t.get("customer_role"),
            product=t.get("product"),
            transcript=transcript,
            first_tier_agent=t.get("agent_name"),
            status="pending",
            created_by=submitted_by,
            category=t.get("category"),
        )

        ticket = retrieve_ticket_by_id_string(new_id)
        ai_result = None

        # Process through AI agents if transcript exists and agents are available
        if transcript and classification_agent:
            try:
                # Step 1: Classification - analyze transcript and find similar cases
                print(f"\n[AI] Processing ticket {new_id} through Classification Agent...")
                classification_output = classification_agent.classify_query(
                    query=transcript,
                    top_k=3,
                    return_all=False
                )

                # Step 2: Generation - generate resolution based on classification
                generation_output = None
                if generation_agent and classification_output:
                    print(f"[AI] Processing ticket {new_id} through Generation Agent...")
                    generation_output = generation_agent.generate(classification_output)

                # Build AI result
                ai_result = {
                    "ticket_id": new_id,
                    "classification": classification_output,
                    "generation": generation_output,
                }

                # Update ticket with AI-generated resolution if available
                if classification_output:
                    rag_response = classification_output.get("RAG_response", {})
                    ai_resolution = rag_response.get("generated_answer", "")
                    resolution_data = rag_response.get("resolution", {})
                    relevancy_score = resolution_data.get("relevancy_score", 0)
                    tier_agent_id = resolution_data.get("agent_id", "agent1")
                    tier = resolution_data.get("tier", 1)
                    
                    # Look up the support agent by tier-based agent_id
                    assigned_agent = retrieve_agent_by_agent_id(tier_agent_id)
                    assigned_to_id = assigned_agent["id"] if assigned_agent else None
                    
                    print(f"[AI] Assigning ticket {new_id} to {tier_agent_id} (tier {tier})")
                    
                    # Update ticket with AI resolution and assignment
                    update_ticket(
                        ticket["id"],
                        ai_resolution=ai_resolution,
                        relevancy_score=relevancy_score,
                        ai_metadata=json.dumps(classification_output),
                        assigned_to=assigned_to_id,
                        tier=f"tier{tier}",
                    )
                    
                    # Refresh ticket data
                    ticket = retrieve_ticket_by_id_string(new_id)

                print(f"[AI] Ticket {new_id} processed successfully")

            except Exception as e:
                print(f"[AI] Error processing ticket {new_id}: {e}")
                ai_result = {"ticket_id": new_id, "error": str(e)}

        if ticket:
            created_tickets.append(ticket)
        if ai_result:
            ai_responses.append(ai_result)

    return jsonify({
        "tickets": created_tickets,
        "ai_processing": ai_responses,
        "total_processed": len(created_tickets),
    }), 201


@app.route("/api/tickets/pending", methods=["GET"])
@token_required
def get_pending_tickets():
    """
    GET /api/tickets/pending?agent_id=agent1
    Returns tickets with status='pending' assigned to the specified agent.
    """
    agent_id_param = request.args.get("agent_id")

    conn = _get_realpage_conn()
    cursor = conn.cursor()

    if agent_id_param:
        # Look up the agent's database ID from support_agent table
        cursor.execute(
            "SELECT id FROM support_agent WHERE agent_id = ?",
            (agent_id_param,),
        )
        agent_row = cursor.fetchone()
        if agent_row:
            # Filter by assigned_to (agent's database ID)
            cursor.execute(
                "SELECT * FROM ticket WHERE status = 'pending' AND assigned_to = ?",
                (agent_row["id"],),
            )
        else:
            # No matching agent – return empty
            conn.close()
            return jsonify({"cases": []}), 200
    else:
        cursor.execute("SELECT * FROM ticket WHERE status = 'pending'")

    rows = cursor.fetchall()
    conn.close()
    cases = [dict(r) for r in rows]
    return jsonify({"cases": cases}), 200


@app.route("/api/tickets/resolved", methods=["GET"])
@token_required
def get_resolved_tickets():
    """
    GET /api/tickets/resolved?agent_id=agent1
    Returns tickets with status IN ('approved', 'rejected') assigned to the specified agent.
    """
    agent_id_param = request.args.get("agent_id")

    conn = _get_realpage_conn()
    cursor = conn.cursor()

    if agent_id_param:
        cursor.execute(
            "SELECT id FROM support_agent WHERE agent_id = ?",
            (agent_id_param,),
        )
        agent_row = cursor.fetchone()
        if agent_row:
            cursor.execute(
                "SELECT * FROM ticket WHERE status IN ('approved', 'rejected') AND assigned_to = ?",
                (agent_row["id"],),
            )
        else:
            conn.close()
            return jsonify({"cases": []}), 200
    else:
        cursor.execute(
            "SELECT * FROM ticket WHERE status IN ('approved', 'rejected')"
        )

    rows = cursor.fetchall()
    conn.close()
    cases = [dict(r) for r in rows]
    return jsonify({"cases": cases}), 200


@app.route("/api/tickets/<ticket_id>", methods=["GET"])
@token_required
def get_ticket(ticket_id):
    """
    GET /api/tickets/{id}
    Returns a single ticket by its ticket_id string (e.g. CS-35956164).
    """
    ticket = retrieve_ticket_by_id_string(ticket_id)
    if not ticket:
        return jsonify({"error": "Ticket not found"}), 404
    return jsonify({"ticket": ticket}), 200


@app.route("/api/tickets/<ticket_id>", methods=["PATCH"])
@token_required
def patch_ticket(ticket_id):
    """
    PATCH /api/tickets/{id}
    Body: { status, edited_resolution }
    Updates the ticket's status and/or edited_resolution.
    """
    data = request.get_json(silent=True) or {}
    new_status = data.get("status")
    edited_resolution = data.get("edited_resolution")

    # Find the ticket first to get its internal integer id
    ticket = retrieve_ticket_by_id_string(ticket_id)
    if not ticket:
        return jsonify({"error": "Ticket not found"}), 404

    updates = {}
    if new_status:
        updates["status"] = new_status
    if edited_resolution is not None:
        updates["edited_resolution"] = edited_resolution
    # Automatically set timestamps
    now = datetime.now(timezone.utc).isoformat()
    updates["updated_at"] = now
    if new_status in ("approved", "rejected"):
        updates["resolved_at"] = now

    if not updates:
        return jsonify({"error": "Nothing to update"}), 400

    success = update_ticket(ticket["id"], **updates)
    if not success:
        return jsonify({"error": "Failed to update ticket"}), 500

    # Return the refreshed ticket
    updated = retrieve_ticket_by_id_string(ticket_id)
    return jsonify({"ticket": updated}), 200


# ===================================================================
# KNOWLEDGE BASE ENDPOINTS
# ===================================================================

@app.route("/api/knowledge", methods=["GET"])
@token_required
def list_knowledge():
    """
    GET /api/knowledge
    Returns all knowledge articles from new_knowledge table in realpage.db.
    """
    articles = list_new_knowledge()
    return jsonify({"articles": articles}), 200


@app.route("/api/knowledge/<kb_id>", methods=["GET"])
@token_required
def get_knowledge(kb_id):
    """
    GET /api/knowledge/{id}
    Returns a single KB article by KB_Article_ID.
    """
    article = retrieve_kb(kb_id)
    if not article:
        return jsonify({"error": "KB article not found"}), 404
    return jsonify({"article": article}), 200


@app.route("/api/knowledge", methods=["POST"])
@token_required
def create_knowledge():
    """
    POST /api/knowledge
    Body: { ticket_id, issue_summary, resolution, category, product, root_cause, tags }
    Dual-write: inserts into knowledge_articles.db AND new_knowledge table in realpage.db.
    """
    data = request.get_json(silent=True) or {}
    resolution = data.get("resolution", "")
    if not resolution:
        return jsonify({"error": "resolution is required"}), 400

    now = datetime.now(timezone.utc).isoformat()
    new_id = next_kb_id()

    # Extract fields
    ticket_id = data.get("ticket_id", "")
    issue_summary = data.get("issue_summary", "")
    category = data.get("category", "")
    product = data.get("product", "")
    root_cause = data.get("root_cause", "")
    tags = data.get("tags", product)  # fallback to product if no tags

    # 1) Insert into knowledge_articles.db
    kb_row = {
        "KB_Article_ID": new_id,
        "Title": issue_summary or f"Resolution for {ticket_id}",
        "Body": resolution,
        "Tags": tags,
        "Module": product,
        "Category": category or product,
        "Created_At": now,
        "Updated_At": now,
        "Status": "Active",
        "Source_Type": "APPROVED_TICKET",
    }

    success = insert_kb(**kb_row)
    if not success:
        return jsonify({"error": "Failed to create KB article"}), 500

    # 2) Also insert into new_knowledge table in realpage.db
    nk_row = {
        "knowledge_id": new_id,
        "ticket_id": ticket_id,
        "conversation_id": "",
        "product": product,
        "resolution": resolution,
        "reference_articles": "",
        "created_by": request.user.get("id"),
        "created_at": now,
    }

    insert_new_knowledge(**nk_row)

    return jsonify({"article": kb_row, "new_knowledge": nk_row, "success": True}), 201


@app.route("/api/knowledge/search", methods=["GET"])
@token_required
def search_knowledge():
    """
    GET /api/knowledge/search?q=search_query
    Searches KB articles by Title or Body using LIKE.
    """
    query = request.args.get("q", "").strip()
    if not query:
        return jsonify({"results": []}), 200

    conn = _get_kb_conn()
    cursor = conn.cursor()
    like_pattern = f"%{query}%"
    cursor.execute(
        "SELECT * FROM knowledge_articles WHERE Title LIKE ? OR Body LIKE ? ORDER BY Created_At DESC LIMIT 50",
        (like_pattern, like_pattern),
    )
    rows = cursor.fetchall()
    conn.close()
    results = [dict(r) for r in rows]
    return jsonify({"results": results}), 200


# ===================================================================
# NEW KNOWLEDGE ENDPOINTS
# ===================================================================

@app.route("/api/new-knowledge", methods=["GET"])
@token_required
def list_new_knowledge_items():
    """
    GET /api/new-knowledge
    Returns all rows from the new_knowledge table (approved resolutions).
    """
    items = list_new_knowledge()
    return jsonify({"items": items}), 200


@app.route("/api/new-knowledge/<knowledge_id>", methods=["GET"])
@token_required
def get_new_knowledge_item(knowledge_id):
    """
    GET /api/new-knowledge/{knowledge_id}
    Returns a single new_knowledge row by its knowledge_id.
    """
    item = retrieve_new_knowledge(knowledge_id)
    if not item:
        return jsonify({"error": "New knowledge entry not found"}), 404
    return jsonify({"item": item}), 200


# ===================================================================
# RAG SEARCH ENDPOINT
# ===================================================================

@app.route("/api/rag/search", methods=["GET"])
@token_required
def rag_search():
    """
    GET /api/rag/search?q=query&top_k=3
    Performs RAG-powered semantic search using enhanced_query.py logic
    Returns similar tickets/cases from the vector store
    """
    query = request.args.get("q", "").strip()
    top_k = int(request.args.get("top_k", 3))

    if not query:
        return jsonify({"error": "Query parameter 'q' is required"}), 400

    if top_k > 10:
        top_k = 10  # Limit to prevent excessive results

    try:
        # Import the RAG query function
        from rag.scripts.enhanced_query import query_vectorstore

        # Perform RAG search
        results = query_vectorstore(query, top_k=top_k)

        # Transform results to frontend-friendly format
        formatted_results = []
        for result in results:
            doc_data = result.get('data', {})
            formatted_results.append({
                "caseId": doc_data.get('Ticket_Number', 'N/A'),
                "issue": doc_data.get('Issue_Summary', doc_data.get('Subject', 'N/A')),
                "description": doc_data.get('Description', 'N/A'),
                "category": doc_data.get('Category_x', 'N/A'),
                "module": doc_data.get('Module_generated_kb', 'N/A'),
                "priority": doc_data.get('Priority', 'N/A'),
                "tier": doc_data.get('Tier', 'N/A'),
                "resolution": doc_data.get('Resolution', 'N/A'),
                "rootCause": doc_data.get('Root_Cause', 'N/A'),
                "tags": doc_data.get('Tags_generated_kb', 'N/A'),
                "transcript": doc_data.get('Transcript', 'N/A'),
                "answerType": doc_data.get('Answer_Type', 'N/A'),
                "relevanceScore": result.get('similarity_score', 0),
                "distance": result.get('distance', 0),
            })

        return jsonify({
            "success": True,
            "query": query,
            "results": formatted_results,
            "total": len(formatted_results),
        }), 200

    except FileNotFoundError as e:
        return jsonify({
            "error": "Vector store not found. Please ensure the RAG system has been initialized.",
            "details": str(e)
        }), 404
    except Exception as e:
        print(f"Error in RAG search: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "error": "Failed to perform RAG search",
            "details": str(e)
        }), 500


# ===================================================================
# Entry point
# ===================================================================

if __name__ == "__main__":
    print("Starting Flask server on http://localhost:5000")
    print(f"  realpage.db : {REALPAGE_DB}")
    print(f"  knowledge   : {KB_DB}")
    app.run(debug=True, port=5000)
