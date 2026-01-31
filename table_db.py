import pandas as pd
import os

FILE = "tickets.xlsx"


def get_all_tickets_df():
    if not os.path.exists(FILE):
        raise FileNotFoundError(f"{FILE} not found. Please create it.")
    return pd.read_excel(FILE, engine="openpyxl")


def save_df(df):
    df.to_excel(FILE, index=False, engine="openpyxl")


from datetime import datetime

def update_ticket(ticket_id: str, field: str, value: str):
    try:
        df = get_all_tickets_df()
        
        # Ensure we can match regardless of string/int types
        # Convert search ID to string
        search_id = str(ticket_id).strip()
        
        # Convert DataFrame column to string for comparison
        # This avoids int vs string mismatch issues
        # We use a mask for the update to avoid modifying the ID column permanently if we don't want to
        # But for reliability, searching as string is safest.
        
        # Find the index of the matching ticket
        # cast column to string temporarily for search
        mask = df["Ticket ID"].astype(str).str.strip() == search_id
        
        if not mask.any():
            print(f"Ticket {ticket_id} not found in DB.")
            print(f"DEBUG: Searching for '{search_id}' (type: {type(search_id)})")
            print(f"DEBUG: Available IDs (first 5): {df['Ticket ID'].astype(str).head().tolist()}")
            return False

        print(f"UPDATE: Ticket {ticket_id} → {field} = {value}")
        
        # Update using the boolean mask
        df.loc[mask, field] = value
        df.loc[mask, "Ticket Updated Date"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        save_df(df)
        print("Saved.")
        return True
    except Exception as e:
        print(f"Update failed: {str(e)}")
        return False