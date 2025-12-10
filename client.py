#“Format the LLM’s responses so they appear clean, well-structured, and easy to read. The output should be delivered step-by-step, with each part displayed sequentially rather than all at once.” 
# app.py - Refactored TechnoBot Flask Web Client (Structured LLM Output)
import os
import asyncio
import time
from tabulate import tabulate
from dotenv import load_dotenv
from groq import Groq
from fastmcp import Client 
from flask import Flask, request, render_template
from markupsafe import Markup
from typing import Any, Dict, List, Optional

# ---------------------------
# Setup & Configuration
# ---------------------------
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv("FLASK_SECRET_KEY", os.urandom(24))

MCP_URL: str = os.getenv("MCP_URL", "http://127.0.0.1:8000/mcp")
GROQ_API_KEY: Optional[str] = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY environment variable is not set.")

groq_client = Groq(api_key=GROQ_API_KEY)

# ----------------------------------------------------------
# LLM Function
# ----------------------------------------------------------
def call_llm(prompt: str) -> str:
    try:
        resp = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
            max_tokens=2000
        )
        return resp.choices[0].message.content
    except Exception as e:
        return f"LLM Error: {e}"

# ----------------------------------------------------------
# MCP Tool Calls
# ----------------------------------------------------------
async def call_tool_async(tool: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    params = params or {}
    try:
        async with Client(MCP_URL) as client:
            response = await client.call_tool(tool, params)
            return response.data if hasattr(response, "data") else response
    except Exception as e:
        return {"error": f"Tool connection failed: {e}"}

def call_tool(tool: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    try:
        return asyncio.run(call_tool_async(tool, params))
    except Exception as e:
        return {"error": f"Asyncio execution error: {e}"}

# ----------------------------------------------------------
# Ticket Detection
# ----------------------------------------------------------
def is_ticket_query(q: str) -> bool:
    q = q.lower()
    return any(keyword in q for keyword in ["ticket", "raise ticket", "my ticket status"])

# ----------------------------------------------------------
# Main Agent Logic
# ----------------------------------------------------------
def agentic_query(q: str) -> str:
    output: List[str] = []

    # ------------------------------------------
    # 1. TICKET MODE
    # ------------------------------------------
    if is_ticket_query(q):
        output.append("<h2 class='text-xl text-green-400 border-b border-green-500 pb-2 mb-4'>🎟️ Ticket Information</h2>")
        data = call_tool("get_ticket_info")

        if "error" in data:
            output.append(f"<p class='text-red-500'>{data['error']}</p>")
            return "\n".join(output)

        # Format tool output
        ticket_text = (
            f"Ticket ID: {data.get('ticket_id', 'N/A')}\n"
            f"Agent Name: {data.get('agent_name', 'N/A')}\n"
            f"Country: {data.get('country', 'N/A')}"
        )

        output.append("<pre class='bg-black p-4 rounded-md text-yellow-200 border border-yellow-400'>")
        output.append(ticket_text)
        output.append("</pre>")

        # -------------------------------
        # Structured LLM Summary (Option C → Plain Text Headers)
        # -------------------------------
        prompt = f"""
You MUST respond ONLY in this strict structured format:

HEADER:
- Summary Title
- Current Ticket Status (infer if missing)
- Priority (infer logically)
- Short one-line overview

BODY:
1. Explanation of the ticket information
2. What the data implies
3. Actions already taken
4. Recommended next steps for the user
5. Any warnings or delays

FOOTER:
- Expected resolution time (logical assumption)
- Helpful guidance or closing line

----------------------
User Query:
{q}

Ticket Data:
{ticket_text}
"""

        llm_result = call_llm(prompt)

        output.append("<h3 class='text-lg text-green-400 mt-4'>🧠 Structured Ticket Summary</h3>")
        output.append(f"<pre class='bg-gray-900 p-4 rounded-md text-white border border-green-500'>{llm_result}</pre>")

        return "\n".join(output)

    # ------------------------------------------
    # 2. DEEP ANSWER MODE
    # ------------------------------------------
    output.append("<h2 class='text-xl text-green-400 border-b border-green-500 pb-2 mb-4'>🔧 Deep Technical Answer</h2>")

    search_tools = ["resource_search", "duckduckgo_search", "web_search"]
    combined_results: List[Dict[str, Any]] = []

    for tool in search_tools:
        res_data = call_tool(tool, {"query": q})
        results: List[Dict[str, Any]] = res_data.get("results", [])

        output.append(f"<h3 class='text-lg text-green-400 mt-4'>Results from `{tool}`</h3>")

        if results:
            table_data = [
                [
                    r.get("title", "N/A"),
                    f"<a href='{r.get('url', '#')}' target='_blank' class='text-cyan-400'>{r.get('url', 'N/A')}</a>"
                ]
                for r in results
            ]
            html_table = tabulate(table_data, headers=["Title", "URL"], tablefmt="html")
            output.append(html_table)
            combined_results.extend(results)
        else:
            output.append("<p class='text-gray-500'>No results.</p>")

    # ------------------------------------------
    # Deep Technical Structured LLM Response
    # ------------------------------------------
    prompt = f"""
Provide a detailed, structured technical answer using ONLY this format:

TECHNICAL HEADER:
- Main Technical Topic (1 line)
- 2–3 line overview
- Tools consulted: {search_tools}

ANALYSIS:
1. Direct explanation of the user query
2. Key technical concepts involved
3. Breakdown of how the technology works
4. Insights extracted from search results:
{combined_results}

EXECUTION STEPS:
- Step-by-step instructions
- Commands or configurations (if applicable)
- Best practices

CONCLUSION:
- Final recommendation
- Potential issues to watch out for
- One-line summary advice

---------------------
User Query:
{q}
"""

    llm_response = call_llm(prompt)

    output.append("<h3 class='text-lg text-green-400 mt-4'>🧠 Technical Analysis</h3>")
    output.append(f"<pre class='bg-gray-900 p-4 rounded-md text-white border border-green-500'>{llm_response}</pre>")

    return "\n".join(output)

# ----------------------------------------------------------
# Flask Routes
# ----------------------------------------------------------
@app.route("/", methods=["GET", "POST"])
def index():
    result: Optional[Markup] = None
    query: str = ""

    if request.method == "POST":
        query = request.form.get("query", "").strip()

        if query:
            start = time.time()
            raw_result = agentic_query(query)
            end = time.time()

            result = Markup(raw_result)
            result += Markup(f"<p class='text-sm text-gray-400 mt-6 pt-3 border-t border-gray-700'>Processed in {end - start:.2f} sec</p>")

    return render_template("index.html", result=result, query=query)

# ----------------------------------------------------------
# Run Flask App
# ----------------------------------------------------------
if __name__ == "__main__":
    print("🚀 TechnoBot running at http://127.0.0.1:5000/")
    app.run(debug=True, host="0.0.0.0", port=5000)
