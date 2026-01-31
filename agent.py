import json
import sqlite3
import os
from datetime import datetime
from config import get_azure_client, get_deployment_name
import tools

client = get_azure_client()
DEPLOYMENT = get_deployment_name()

# SQLite for long-term memory
DB_FILE = "conversations.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS conversations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            role TEXT NOT NULL,
            content TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

init_db()


def save_message(user_id, role, content):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''
        INSERT INTO conversations (user_id, timestamp, role, content)
        VALUES (?, ?, ?, ?)
    ''', (user_id, datetime.now().isoformat(), role, content))
    conn.commit()
    conn.close()


def load_long_term_history(user_id, limit=12):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''
        SELECT role, content FROM conversations 
        WHERE user_id = ? 
        ORDER BY timestamp DESC LIMIT ?
    ''', (user_id, limit))
    rows = c.fetchall()
    conn.close()
    history = [{"role": role, "content": content} for role, content in reversed(rows)]
    return history


tools_map = {
    "get_ticket_summary": tools.get_ticket_summary,
    "get_team_performance": tools.get_team_performance,
    "get_ticket_details": tools.get_ticket_details,
    "get_open_tickets_by_team": tools.get_open_tickets_by_team,
    "close_ticket": tools.close_ticket,
    "assign_ticket": tools.assign_ticket,
    "reopen_ticket": tools.reopen_ticket,
    "change_priority": tools.change_priority,
    "get_team_with_most_open_tickets": tools.get_team_with_most_open_tickets,
    "get_high_priority_open_tickets": tools.get_high_priority_open_tickets,
    "get_average_resolution_time_per_team": tools.get_average_resolution_time_per_team,
    "get_overloaded_agents": tools.get_overloaded_agents,
    "get_performance_by_person_in_team": tools.get_performance_by_person_in_team,
    "get_top_performer_in_team": tools.get_top_performer_in_team,
    "query_tickets_json": tools.query_tickets_json,
}


def ask_agent(user_msg: str, short_term_history: list = None, user_id: str = "manager_01"):
    if short_term_history is None:
        short_term_history = []

    long_term_history = load_long_term_history(user_id, limit=12)

    system_prompt = """
You are an AI Query Management Agent for EY — professional, accurate, action-oriented.

Core Rules:

1. ACTIONS (close, reopen, assign, change priority):
   - ALWAYS call the correct tool. 
   - NEVER describe the action in text only — execute it.
   - Confirm with updated ticket details after success.

2. PERFORMANCE / ANALYTICS / OPERATIONAL QUERIES
   Examples: "how is the team managing the queries?", "team performance?", "workload?", "process performance?", "KPIs?", "statistics?", 
   "which team has the most open tickets?", "average resolution time?", "who is overloaded?", "high priority open tickets?", "performance in team A?", "top performer in team B?"
   - Use available analysis tools (get_team_with_most_open_tickets, get_average_resolution_time_per_team, get_performance_by_person_in_team, etc.) to give exact, concise answers.
   - If the question needs full charts or detailed KPIs — reply briefly and direct to /dashboard.
   - Do NOT hallucinate numbers, charts, or stats — use tools or redirect.

3. CONTEXTUAL UNDERSTANDING
   - Use the full conversation history (long-term from past sessions + short-term from current session) to understand references like 'it', 'that ticket', 'the one I mentioned earlier', 'last issue'.
   - Maintain continuity across turns and sessions — remember previous tickets, actions, and user preferences.

4. GENERAL
   - Be concise, polite, helpful.
   - If missing critical info (e.g. ticket ID for action) → ask politely.
   - Never assume ticket IDs or statuses — verify via tools when needed.
"""

    messages = [{"role": "system", "content": system_prompt}]

    for msg in long_term_history:
        messages.append(msg)

    for msg in short_term_history:
        messages.append(msg)

    messages.append({"role": "user", "content": user_msg})

    tools_definition = [
        {
            "type": "function",
            "function": {
                "name": "get_ticket_summary",
                "description": "Get overall ticket counts (total, open, closed)",
                "parameters": {"type": "object", "properties": {}}
            }
        },
        {
            "type": "function",
            "function": {
                "name": "get_team_performance",
                "description": "Get ticket count grouped by team",
                "parameters": {"type": "object", "properties": {}}
            }
        },
        {
            "type": "function",
            "function": {
                "name": "get_ticket_details",
                "description": "Get full details of a specific ticket",
                "parameters": {
                    "type": "object",
                    "properties": {"ticket_id": {"type": "string"}},
                    "required": ["ticket_id"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "get_open_tickets_by_team",
                "description": "List open tickets for a specific team",
                "parameters": {
                    "type": "object",
                    "properties": {"team": {"type": "string"}},
                    "required": ["team"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "close_ticket",
                "description": "Close a ticket (set status to Closed)",
                "parameters": {
                    "type": "object",
                    "properties": {"ticket_id": {"type": "string"}},
                    "required": ["ticket_id"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "reopen_ticket",
                "description": "Reopen a ticket (set status to Open)",
                "parameters": {
                    "type": "object",
                    "properties": {"ticket_id": {"type": "string"}},
                    "required": ["ticket_id"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "assign_ticket",
                "description": "Assign or reassign ticket to a team and/or a specific person.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "ticket_id": {"type": "string"},
                        "team": {"type": "string", "description": "Name of the team (optional)"},
                        "person_name": {"type": "string", "description": "Name of the person to assign to (optional)"}
                    },
                    "required": ["ticket_id"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "change_priority",
                "description": "Update ticket priority level",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "ticket_id": {"type": "string"},
                        "priority": {"type": "string"}
                    },
                    "required": ["ticket_id", "priority"]
                }
            }
        },
        # NEW analysis tools for Part 1
        {
            "type": "function",
            "function": {
                "name": "get_team_with_most_open_tickets",
                "description": "Find team with the most open tickets",
                "parameters": {"type": "object", "properties": {}}
            }
        },
        {
            "type": "function",
            "function": {
                "name": "get_high_priority_open_tickets",
                "description": "Count and breakdown of high/critical open tickets",
                "parameters": {"type": "object", "properties": {}}
            }
        },
        {
            "type": "function",
            "function": {
                "name": "get_average_resolution_time_per_team",
                "description": "Average resolution time per team in hours",
                "parameters": {"type": "object", "properties": {}}
            }
        },
        {
            "type": "function",
            "function": {
                "name": "get_overloaded_agents",
                "description": "Find agents with many tickets (default threshold 10)",
                "parameters": {"type": "object", "properties": {}}
            }
        },
        {
            "type": "function",
            "function": {
                "name": "get_performance_by_person_in_team",
                "description": "Get performance stats (closed count, resolution time) per person in a specific team",
                "parameters": {
                    "type": "object",
                    "properties": {"team_name": {"type": "string"}},
                    "required": ["team_name"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "get_top_performer_in_team",
                "description": "Find the top performing person in a team based on closed tickets",
                "parameters": {
                    "type": "object",
                    "properties": {"team_name": {"type": "string"}},
                    "required": ["team_name"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "query_tickets_json",
                "description": "Query the hierarchical JSON data for tickets based on any combination of ticket fields.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "team_name": {"type": "string", "description": "Filter by Team Name (A, B, C...)"},
                        "person_name": {"type": "string", "description": "Filter by Person Name"},
                        "status": {"type": "string", "description": "Ticket Status (Open, Closed, In Progress)"},
                        "priority": {"type": "string", "description": "Ticket Priority (High, Medium, Low)"},
                        "ticket_category": {"type": "string", "description": "Ticket Category (Hardware, Software)"},
                        "ticket_id": {"type": "string", "description": "Exact Ticket ID"},
                        "person_id": {"type": "string", "description": "Exact Person ID"},
                        "create_date": {"type": "string", "description": "Ticket Create Date (YYYY-MM-DD HH:MM:SS)"},
                        "closed_date": {"type": "string", "description": "Ticket Closed Date (YYYY-MM-DD HH:MM:SS)"}
                    }
                }
            }
        }
    ]

    # First call
    first = client.chat.completions.create(
        model=DEPLOYMENT,
        messages=messages,
        tools=tools_definition,
        tool_choice="auto",
    )

    msg = first.choices[0].message

    if msg.tool_calls:
        tool_call = msg.tool_calls[0]
        tool_name = tool_call.function.name
        args = json.loads(tool_call.function.arguments or "{}")

        try:
            result = tools_map[tool_name](**args)
        except Exception as e:
            result = f"Error: {str(e)}"

        save_message(user_id, "assistant", f"Executed {tool_name} → {result}")

        messages.append({
            "role": "assistant",
            "tool_calls": [{"id": tool_call.id, "type": "function", "function": {"name": tool_name, "arguments": json.dumps(args)}}]
        })
        messages.append({"role": "tool", "tool_call_id": tool_call.id, "content": str(result)})

        second = client.chat.completions.create(
            model=DEPLOYMENT,
            messages=messages,
            tools=tools_definition,
        )

        final_content = second.choices[0].message.content or "Action completed."
        final_content = final_content.strip()

        save_message(user_id, "assistant", final_content)

        return final_content

    final_content = (msg.content or "Understood.").strip()

    save_message(user_id, "user", user_msg)
    save_message(user_id, "assistant", final_content)

    return final_content