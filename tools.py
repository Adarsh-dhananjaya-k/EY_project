from table_db import get_all_tickets_df, update_ticket
import pandas as pd
import numpy as np
import json
import os

JSON_FILE = "tickets_structure.json"

def query_tickets_json(team_name: str = None, person_name: str = None, status: str = None, priority: str = None, ticket_category: str = None, 
                       ticket_id: str = None, person_id: str = None, create_date: str = None, closed_date: str = None):
    """
    Query the hierarchical JSON data for tickets based on ALL available fields.
    Args:
        team_name: Filter by Team Name (e.g., 'A', 'B')
        person_name: Filter by Person Name
        status: Filter by 'Ticket Status' (Open, Closed, In Progress)
        priority: Filter by 'Ticket Priority' (High, Medium, Low)
        ticket_category: Filter by 'Ticket Category' (Hardware, Software)
        ticket_id: Filter by 'Ticket ID'
        person_id: Filter by 'Person ID'
        create_date: Filter by 'Ticket Create Date'
        closed_date: Filter by 'Ticket Closed Date'
    """
    if not os.path.exists(JSON_FILE):
        return "Error: tickets_structure.json not found. Please run the conversion script first."

    try:
        with open(JSON_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        return f"Error reading JSON file: {str(e)}"

    results = []
    
    # helper to check if a ticket matches filters
    def ticket_matches(ticket):
        # Case insensitive string comparisons, direct equality for IDs
        if status and ticket.get("Ticket Status", "").lower() != status.lower(): return False
        if priority and ticket.get("Ticket Priority", "").lower() != priority.lower(): return False
        if ticket_category and ticket.get("Ticket Category", "").lower() != ticket_category.lower(): return False
        if ticket_id and str(ticket.get("Ticket ID", "")) != str(ticket_id): return False
        if person_id and str(ticket.get("Person ID", "")) != str(person_id): return False
        
        # Date string matching (exact match for simplicity, can be expanded to range if needed)
        if create_date and str(ticket.get("Ticket Create Date", "")) != create_date: return False
        if closed_date and str(ticket.get("Ticket Closed Date", "")) != closed_date: return False
        
        return True

    teams_to_search = data.get("teams", [])
    
    # Filter by Team Level
    if team_name:
        teams_to_search = [t for t in teams_to_search if t["team_name"].lower() == team_name.lower()]
        if not teams_to_search:
            return f"No data found for Team '{team_name}'."

    for team in teams_to_search:
        members_to_search = team.get("members", [])
        
        # Filter by Person Level
        if person_name:
            members_to_search = [m for m in members_to_search if m["person_name"].lower() == person_name.lower()]
        
        for member in members_to_search:
            # Filter Tickets
            for ticket in member.get("tickets", []):
                if ticket_matches(ticket):
                    results.append(ticket)

    if not results:
        return "No tickets found matching your criteria."

    # Return a concise summary if too many results
    count = len(results)
    if count > 10:
        return f"Found {count} matching tickets. Here are the first 10:\n" + json.dumps(results[:10], indent=2)
    
    return json.dumps(results, indent=2)


def get_ticket_summary():
    df = get_all_tickets_df()
    total = len(df)
    open_count = len(df[df["Ticket Status"] != "Closed"])
    closed_count = len(df[df["Ticket Status"] == "Closed"])
    return f"Total Tickets: {total}\nOpen Tickets: {open_count}\nClosed Tickets: {closed_count}"


def get_team_performance():
    df = get_all_tickets_df()
    performance = df.groupby("Team Name")["Ticket ID"].count().sort_values(ascending=False)
    return "Tickets per team:\n" + performance.to_string()


def get_ticket_details(ticket_id: str):
    df = get_all_tickets_df()
    ticket = df[df["Ticket ID"] == int(ticket_id)]
    if ticket.empty:
        return f"No ticket found with ID {ticket_id}"
    return ticket.to_string(index=False)


def get_open_tickets_by_team(team: str):
    df = get_all_tickets_df()
    filtered = df[(df["Team Name"].str.lower() == team.lower()) & (df["Ticket Status"] != "Closed")]
    if filtered.empty:
        return f"No open tickets for team '{team}'"
    return filtered.to_string(index=False)


from convert_to_json import convert_tickets_to_json

def close_ticket(ticket_id: str):
    success = update_ticket(ticket_id, "Ticket Status", "Closed")
    if success:
        convert_tickets_to_json()
        return f"Ticket {ticket_id} CLOSED." 
    return f"Ticket {ticket_id} not found."


def reopen_ticket(ticket_id: str):
    success = update_ticket(ticket_id, "Ticket Status", "Open")
    if success:
        convert_tickets_to_json()
        return f"Ticket {ticket_id} REOPENED."
    return f"Ticket {ticket_id} not found."


def assign_ticket(ticket_id: str, team: str = None, person_name: str = None):
    success = False
    msg_parts = []
    
    if team:
        if update_ticket(ticket_id, "Team Name", team):
            success = True
            msg_parts.append(f"Team set to {team}")
    
    if person_name:
        if update_ticket(ticket_id, "Person Name", person_name):
            success = True
            msg_parts.append(f"Assigned to {person_name}")

    if success:
        convert_tickets_to_json()
        return f"Ticket {ticket_id} updated: " + ", ".join(msg_parts)
    
    return f"Ticket {ticket_id} not found or no changes made."


def change_priority(ticket_id: str, priority: str):
    success = update_ticket(ticket_id, "Ticket Priority", priority)
    if success:
        convert_tickets_to_json()
        return f"Priority of {ticket_id} set to {priority}."
    return f"Ticket {ticket_id} not found."


# ────────────────────────────────────────────────
# NEW: Performance & Analytics Tools (for Part 1)
# ────────────────────────────────────────────────

def get_team_with_most_open_tickets():
    """Find team with the most open tickets."""
    df = get_all_tickets_df()
    open_tickets = df[df["Ticket Status"] != "Closed"]
    if open_tickets.empty:
        return "No open tickets at the moment."
    team_counts = open_tickets.groupby("Team Name").size().sort_values(ascending=False)
    top_team = team_counts.index[0]
    count = team_counts.iloc[0]
    return f"Team with the most open tickets: **{top_team}** ({count} open tickets)"


def get_high_priority_open_tickets():
    """Count and breakdown of high/critical open tickets."""
    df = get_all_tickets_df()
    high_open = df[(df["Ticket Status"] == "Open") & (df["Ticket Priority"].isin(["High", "Critical"]))]
    count = len(high_open)
    if count == 0:
        return "No high or critical priority tickets are open."
    teams = high_open.groupby("Team Name").size().sort_values(ascending=False)
    return f"There are **{count} high/critical priority open tickets**.\nBreakdown by team:\n" + teams.to_string()


def get_average_resolution_time_per_team():
    """Average resolution time per team in hours (for closed tickets)."""
    df = get_all_tickets_df()
    if "Ticket Create Date" not in df.columns or "Ticket Closed Date" not in df.columns:
        return "Missing date columns — cannot calculate resolution time."

    create_raw = pd.to_numeric(df["Ticket Create Date"], errors='coerce')
    closed_raw = pd.to_numeric(df["Ticket Closed Date"], errors='coerce')

    create_raw = create_raw.where((create_raw >= 30000) & (create_raw <= 60000), np.nan)
    closed_raw = closed_raw.where((closed_raw >= 30000) & (closed_raw <= 60000), np.nan)

    origin = pd.Timestamp("1899-12-30")
    df["Create Dt"] = origin + pd.to_timedelta(create_raw, unit='D')
    df["Close Dt"] = origin + pd.to_timedelta(closed_raw, unit='D')

    closed = df[(df["Ticket Status"] == "Closed") & df["Create Dt"].notna() & df["Close Dt"].notna()]
    if closed.empty:
        return "No closed tickets to calculate resolution time."

    closed["Resolution Hours"] = (closed["Close Dt"] - closed["Create Dt"]).dt.total_seconds() / 3600
    valid_hours = closed["Resolution Hours"][closed["Resolution Hours"] > 0]
    if valid_hours.empty:
        return "No valid resolution times."

    avg_per_team = closed.groupby("Team Name")["Resolution Hours"].mean().round(1)
    return "Average resolution time per team (hours):\n" + avg_per_team.to_string()


def get_overloaded_agents(threshold=10):
    """Find agents with many tickets (default threshold 10)."""
    df = get_all_tickets_df()
    if "Person Name" not in df.columns:
        return "No 'Person Name' column found."
    counts = df.groupby("Person Name").size().sort_values(ascending=False)
    overloaded = counts[counts >= threshold]
    if overloaded.empty:
        return f"No agents with {threshold}+ tickets."
    return f"Overloaded agents ({threshold}+ tickets):\n" + overloaded.to_string()


def get_performance_by_person_in_team(team_name: str):
    """Performance summary (closed count, avg resolution) per person in a specific team."""
    df = get_all_tickets_df()
    if "Team Name" not in df.columns or "Person Name" not in df.columns:
        return "Missing required columns (Team Name or Person Name)."

    team_df = df[df["Team Name"].str.lower() == team_name.lower()]
    if team_df.empty:
        return f"No tickets found for team '{team_name}'."

    closed = team_df[team_df["Ticket Status"] == "Closed"]
    closed_count = closed.groupby("Person Name").size()

    resolution_per_person = "Not available (missing date columns)"
    if "Ticket Create Date" in df.columns and "Ticket Closed Date" in df.columns:
        create_raw = pd.to_numeric(team_df["Ticket Create Date"], errors='coerce')
        closed_raw = pd.to_numeric(team_df["Ticket Closed Date"], errors='coerce')
        origin = pd.Timestamp("1899-12-30")
        team_df["Create Dt"] = origin + pd.to_timedelta(create_raw, unit='D')
        team_df["Close Dt"] = origin + pd.to_timedelta(closed_raw, unit='D')
        closed_tix = team_df[(team_df["Ticket Status"] == "Closed") & team_df["Create Dt"].notna() & team_df["Close Dt"].notna()]
        if not closed_tix.empty:
            closed_tix["Resolution Hours"] = (closed_tix["Close Dt"] - closed_tix["Create Dt"]).dt.total_seconds() / 3600
            resolution_per_person = closed_tix.groupby("Person Name")["Resolution Hours"].mean().round(1).to_string()

    result = f"Performance in Team {team_name}:\n"
    if not closed_count.empty:
        result += "Closed tickets per person:\n" + closed_count.sort_values(ascending=False).to_string() + "\n\n"
    result += f"Average resolution time per person:\n{resolution_per_person}"
    return result


def get_top_performer_in_team(team_name: str):
    """Find the top performing person in a team (based on most closed tickets)."""
    df = get_all_tickets_df()
    team_df = df[df["Team Name"].str.lower() == team_name.lower()]
    if team_df.empty:
        return f"No tickets for team '{team_name}'."

    closed = team_df[team_df["Ticket Status"] == "Closed"]
    if closed.empty:
        return f"No closed tickets in team '{team_name}' — no performance ranking possible."

    top = closed.groupby("Person Name").size().sort_values(ascending=False)
    best_person = top.index[0]
    count = top.iloc[0]
    return f"Top performer in Team {team_name}: **{best_person}** with {count} closed tickets."