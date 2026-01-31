Here is a clean, professional, and realistic README.md file you could use for this project.

```markdown
# EY Query Management Agent

A simple AI-powered internal tool for EY teams to query, manage, and analyze support tickets using natural language.

- Ask questions like:  
  "Show open tickets in Team Alpha"  
  "Who is performing best this month?"  
  "Close ticket #5421"  
  "What's the average resolution time for Team B?"

Built as a quick prototype / demo with a modern chat-like interface + performance dashboard.

## Current Features

- Natural language queries to an AI agent (powered by Azure OpenAI)
- View current conversation in clean chat-style UI
- Basic performance dashboard with:
  - KPI cards (total tickets, open %, closed rate, avg resolution time)
  - Status pie chart
  - Team & person workload bar charts
- Filtering by team / person
- Session-based short-term chat memory (last 8 messages)
- Conversation logging (placeholder – currently minimal)

## Tech Stack (2025–2026 simple & pragmatic)

| Layer              | Technology                          | Purpose / Notes                              |
|--------------------|-------------------------------------|----------------------------------------------|
| Backend            | Python 3 + Flask                    | Web server, routing, session management      |
| AI / Reasoning     | Azure OpenAI                        | GPT-4o / o1-mini / function calling          |
| Data Processing    | pandas + numpy                      | Ticket filtering, grouping, calculations     |
| Charts             | matplotlib → base64 PNG             | Server-side chart generation (embedded)      |
| Frontend           | Bootstrap 5.3 + custom CSS          | Responsive UI, cards, gradients              |
| Short-term Memory  | Flask `session`                     | Current conversation context                 |
| Long-term Memory   | Planned: SQLite                     | Conversation history + ticket state          |
| Logging            | Custom `conversation_logger`        | To be replaced / extended with SQLite        |
| Ticket Source      | Custom `table_db.get_all_tickets_df()` | Currently static (CSV/Excel/DB planned)   |

## Planned / Desired Improvements

- Replace matplotlib with client-side Chart.js / ApexCharts
- Add real SQLite database for:
  - Persistent conversation history per user
  - Long-term context (summaries, key facts)
  - Ticket status updates (close, assign, comment)
- User authentication (simple session or Azure AD)
- Better error handling & Azure OpenAI retry logic
- Rate limiting & cost monitoring
- Optional: move to FastAPI + React/Vite frontend

## Project Structure (current)

```
.
├── app.py                  # Main Flask application
├── agent.py                # AI agent logic (calls Azure OpenAI)
├── conversation_logger.py  # Saves chat messages (placeholder)
├── table_db.py             # Loads ticket data → pandas DataFrame
├── templates/              # (not used – inline render_template_string)
└── requirements.txt        # (add when you create it)
```

## Quick Start (Local Development)

1. Install dependencies

```bash
pip install flask pandas numpy matplotlib openai azure-identity
# or better: create requirements.txt
```

2. Set Azure OpenAI credentials (environment variables recommended)

```bash
export AZURE_OPENAI_ENDPOINT="https://your-resource.openai.azure.com/"
export AZURE_OPENAI_API_KEY="your-key"
# or use Azure AD authentication
```

3. Prepare ticket data  
   Make sure `table_db.py` returns a valid pandas DataFrame with at least these columns:

   - Ticket ID
   - Team Name
   - Assigned To / Person Name
   - Ticket Status (Open, In Progress, Closed, Cancelled)
   - Ticket Create Date, Ticket Closed Date (Excel serial or datetime)

4. Run the app

```bash
python app.py
```

→ Open http://127.0.0.1:5000

## Security & Production Notes

- **Do NOT** use the hardcoded `secret_key` in production
- Never commit Azure API keys
- Add proper input validation (prevent prompt injection)
- Consider moving charts to client-side for better performance
- SQLite is recommended for the first persistent storage step

## Author / Demo

- Created by: Mansur  
- Purpose: Internal EY demo / prototype (2025–2026)

Feel free to fork, improve, or turn this into a more production-ready internal tool.

```

