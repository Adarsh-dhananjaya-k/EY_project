import pandas as pd
import os

FILE = "tickets.xlsx"


def get_all_tickets_df():
    if not os.path.exists(FILE):
        raise FileNotFoundError(f"{FILE} not found. Please create it.")
    return pd.read_excel(FILE, engine="openpyxl")


def save_df(df):
    df.to_excel(FILE, index=False, engine="openpyxl")


def update_ticket(ticket_id: str, field: str, value: str):
    try:
        df = get_all_tickets_df()
        tid = int(ticket_id)
        if tid not in df["Ticket ID"].values:
            print(f"Ticket {ticket_id} not found.")
            return False

        print(f"UPDATE: Ticket {ticket_id} → {field} = {value}")
        df.loc[df["Ticket ID"] == tid, field] = value
        save_df(df)
        print("Saved.")
        return True
    except Exception as e:
        print(f"Update failed: {e}")
        return False