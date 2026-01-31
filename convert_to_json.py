import pandas as pd
import json
import os

INPUT_FILE = "tickets.xlsx"
OUTPUT_FILE = "tickets_structure.json"

def convert_tickets_to_json():
    if not os.path.exists(INPUT_FILE):
        print(f"Error: {INPUT_FILE} not found.")
        return

    # Load the Excel file
    try:
        df = pd.read_excel(INPUT_FILE, engine="openpyxl")
    except Exception as e:
        print(f"Error reading Excel file: {e}")
        return

    # clean up column names (strip whitespace)
    df.columns = df.columns.str.strip()
    
    # Identify necessary columns based on known schema
    # Expected: 'Team Name', 'Person Name', 'Ticket ID', 'Ticket Status', etc.
    required_cols = ['Team Name', 'Person Name']
    for col in required_cols:
        if col not in df.columns:
            print(f"Error: Required column '{col}' not found in Excel file.")
            print(f"Available columns: {list(df.columns)}")
            return

    # Structure the data
    # Root -> Teams -> Members -> Tickets
    
    data_structure = {"teams": []}

    # Group by Team
    for team_name, team_group in df.groupby("Team Name"):
        team_obj = {
            "team_name": team_name,
            "members": []
        }

        # Group by Member within the Team
        for person_name, person_group in team_group.groupby("Person Name"):
            member_obj = {
                "person_name": person_name,
                "tickets": []
            }

            # Iterate over tickets for this person
            for _, row in person_group.iterrows():
                # Convert row to dictionary
                ticket_data = row.to_dict()
                
                # Handle timestamps/dates for JSON serialization
                for key, value in ticket_data.items():
                    if pd.isna(value):
                        ticket_data[key] = None
                    elif isinstance(value, (pd.Timestamp, pd.Timedelta)):
                        ticket_data[key] = str(value)

                # Clean up specific fields as requested (Status, Assignment info is inherent in the user grouping)
                # The user asked for "their tickets, their status, and their assignment"
                # detailed ticket object covers this.
                
                member_obj["tickets"].append(ticket_data)

            team_obj["members"].append(member_obj)
        
        data_structure["teams"].append(team_obj)

    # Write to JSON file
    try:
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            json.dump(data_structure, f, indent=4, ensure_ascii=False)
        print(f"Successfully converted {INPUT_FILE} to {OUTPUT_FILE}")
    except Exception as e:
        print(f"Error writing JSON file: {e}")

if __name__ == "__main__":
    convert_tickets_to_json()
