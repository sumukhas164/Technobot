# server.py - TechnoBot MCP Server (with MySQL Ticket Tool, FastMCP)
import os
from fastmcp import FastMCP
from ddgs import DDGS
import mysql.connector
from dotenv import load_dotenv

# ---------------------------------------------
# Load ENV
# ---------------------------------------------
load_dotenv()
MYSQL_CONFIG = {
    "host": os.getenv("MYSQL_HOST", "localhost"),
    "user": os.getenv("MYSQL_USER", "root"),
    "password": os.getenv("MYSQL_PASSWORD"),
    "database": os.getenv("MYSQL_DATABASE", "technical_db")
}

# ---------------------------------------------
# DB Connection
# ---------------------------------------------
def get_db():
    try:
        return mysql.connector.connect(**MYSQL_CONFIG)
    except Exception as e:
        print("DB ERROR:", e)
        return None

# ---------------------------------------------
# FastMCP Init
# ---------------------------------------------
mcp = FastMCP("TechnoBot MCP Server")

# ---------------------------------------------
# Tools
# ---------------------------------------------
@mcp.tool
def resource_search(query: str) -> dict:
    """General resource search using DuckDuckGo."""
    try:
        with DDGS() as ddg:
            results = ddg.text(query, max_results=5)

        formatted = [{
            "title": r.get("title") or "No Title",
            "snippet": r.get("body") or "",
            "url": r.get("href") or ""
        } for r in results]

        return {"results": formatted}

    except Exception as e:
        return {"error": f"resource_search failed: {e}"}

@mcp.tool
def web_search(query: str) -> dict:
    """General-purpose web search"""
    try:
        with DDGS() as ddg:
            res = ddg.text(query, max_results=5)
        return {"results": res}
    except Exception as e:
        return {"error": f"web_search failed: {e}"}

@mcp.tool
def duckduckgo_search(query: str) -> dict:
    """Technical search with consistent formatting"""
    try:
        with DDGS() as ddg:
            res = ddg.text(query, max_results=5)

        formatted = [{
            "title": r.get("title") or "No Title",
            "snippet": r.get("body") or "",
            "url": r.get("href") or ""
        } for r in res]

        return {"results": formatted}

    except Exception as e:
        return {"error": f"duckduckgo_search failed: {e}"}

# ---------------------------------------------------
# 🎟️ RANDOM TICKET FETCHER (CLEAN REDUCED OUTPUT)
# ---------------------------------------------------
@mcp.tool
def get_ticket_info() -> dict:
    """
    Fetch a RANDOM ticket but only return:
    - ticket_id
    - agent_name
    - country
    """
    db = get_db()
    if not db:
        return {"error": "DB connection failed"}

    cursor = db.cursor(dictionary=True)

    query = """
        SELECT `Ticket ID`, `Agent Name`, `Country`
        FROM techno
        ORDER BY RAND()
        LIMIT 1;
    """

    cursor.execute(query)
    row = cursor.fetchone()
    cursor.close()
    db.close()

    if not row:
        return {"error": "No ticket found"}

    # Normalize keys
    return {
        "ticket_id": row.get("Ticket ID"),
        "agent_name": row.get("Agent Name"),
        "country": row.get("Country")
    }

# ---------------------------------------------
# Start Server
# ---------------------------------------------
if __name__ == "__main__":
    print("🚀 TechnoBot MCP Server running on http://0.0.0.0:8000/mcp")
    mcp.run(
        transport="http",
        host="0.0.0.0",
        port=8000,
        path="/mcp"
    )
