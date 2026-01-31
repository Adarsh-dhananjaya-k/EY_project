from flask import Flask, request, render_template_string, session
from agent import ask_agent
from conversation_logger import log_conversation
from table_db import get_all_tickets_df
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import io
import base64
import traceback
from datetime import datetime
import pandas as pd
import numpy as np

app = Flask(__name__)
app.secret_key = "ey_demo_secret_key_2025"

DEMO_USER_ID = "manager_01"


def plot_to_img(fig):
    buf = io.BytesIO()
    fig.savefig(buf, format='png', bbox_inches='tight', dpi=110)
    buf.seek(0)
    img_str = base64.b64encode(buf.read()).decode('utf-8')
    buf.close()
    plt.close(fig)
    return img_str


@app.route("/", methods=["GET", "POST"])
def home():
    response = ""
    error = None
    current_year = datetime.now().year

    if request.method == "POST":
        user_msg = request.form.get("msg", "").strip()
        if not user_msg:
            error = "Please enter a query."
        else:
            try:
                chat_history = session.get('chat_history', [])
                response = ask_agent(user_msg, chat_history, user_id=DEMO_USER_ID)
                log_conversation(DEMO_USER_ID, user_msg, response)

                chat_history.append({"role": "user", "content": user_msg})
                chat_history.append({"role": "assistant", "content": response})
                session['chat_history'] = chat_history[-8:]
            except Exception as e:
                error = f"Error: {str(e)}"
                traceback.print_exc()

    return render_template_string("""
    <!DOCTYPE html>
    <html lang="en" data-bs-theme="light">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>EY Query Agent</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css">
        <style>
            :root {
                --ey-blue:    #0047ab;
                --ey-blue-dk: #003087;
                --ey-gray:    #f0f2f5;
                --success:    #28a745;
                --warning:    #ffc107;
                --danger:     #dc3545;
                --info:       #0dcaf0;
            }
            body {
                background: linear-gradient(135deg, #f5f7fa 0%, #e4e9fd 100%);
                min-height: 100vh;
                font-family: system-ui, -apple-system, "Segoe UI", Roboto, sans-serif;
                color: #1a1f36;
            }
            .navbar {
                background: var(--ey-blue) !important;
                box-shadow: 0 2px 12px rgba(0,0,0,0.15);
            }
            .chat-container {
                max-width: 920px;
                margin: 2.5rem auto;
                padding: 0 1rem;
            }
            .chat-card {
                background: white;
                border-radius: 16px;
                box-shadow: 0 10px 38px rgba(0,0,0,0.09);
                overflow: hidden;
                border: none;
            }
            .chat-header {
                background: var(--ey-blue);
                color: white;
                padding: 1.25rem 1.75rem;
                font-weight: 600;
                font-size: 1.25rem;
            }
            .input-group-lg .form-control {
                border-radius: 12px 0 0 12px;
                border: 1px solid #d1d9e6;
                padding: 0.9rem 1.4rem;
                font-size: 1.1rem;
                box-shadow: inset 0 1px 3px rgba(0,0,0,0.05);
            }
            .input-group-lg .btn {
                border-radius: 0 12px 12px 0;
                padding: 0 2rem;
                background: var(--ey-blue);
                border: none;
                font-weight: 600;
                transition: background 0.2s;
            }
            .input-group-lg .btn:hover {
                background: var(--ey-blue-dk);
            }
            .response-box {
                background: #f8fbff;
                border-left: 5px solid var(--ey-blue);
                padding: 1.6rem;
                border-radius: 12px;
                margin-top: 1.8rem;
                line-height: 1.65;
                white-space: pre-wrap;
                box-shadow: 0 3px 14px rgba(0,71,171,0.08);
            }
            .alert {
                border-radius: 10px;
                padding: 1rem 1.5rem;
            }
            footer {
                color: #6c757d;
                font-size: 0.92rem;
                padding: 2.5rem 0 1.5rem;
                text-align: center;
            }
            @media (max-width: 576px) {
                .chat-container { margin: 1.2rem; }
                .chat-header { font-size: 1.1rem; padding: 1rem 1.25rem; }
            }
        </style>
    </head>
    <body>

        <nav class="navbar navbar-dark">
            <div class="container-fluid px-4">
                <span class="navbar-brand mb-0 h5">EY Query Management Agent</span>
                <span class="text-white small">Demo • Mansur</span>
            </div>
        </nav>

        <div class="chat-container">

            <div class="chat-card">
                <div class="chat-header d-flex align-items-center">
                    <i class="fas fa-robot me-3 fs-4"></i>
                    AI Assistant – Tickets & Insights
                </div>

                <div class="card-body p-4 p-md-5">
                    <form method="post">
                        <div class="input-group input-group-lg mb-4">
                            <input type="text" class="form-control shadow-sm" name="msg"
                                   placeholder="e.g. show open tickets in Team Alpha   or   close ticket 5421   or   who is performing best?"
                                   autofocus autocomplete="off" required>
                            <button class="btn btn-primary px-4" type="submit">
                                <i class="fas fa-paper-plane me-2"></i>Send
                            </button>
                        </div>
                    </form>

                    {% if error %}
                    <div class="alert alert-danger d-flex align-items-center gap-3">
                        <i class="fas fa-exclamation-circle fs-4"></i>
                        {{ error }}
                    </div>
                    {% endif %}

                    {% if response %}
                    <div class="response-box">
                        <div class="d-flex align-items-center mb-3">
                            <i class="fas fa-robot text-primary me-3 fs-4"></i>
                            <strong class="text-primary fs-5">Response</strong>
                        </div>
                        {{ response | safe }}
                    </div>
                    {% endif %}

                    <div class="text-center mt-5 pt-4 border-top">
                        <a href="/dashboard" class="btn btn-outline-primary btn-lg px-5 py-3 shadow-sm">
                            <i class="fas fa-chart-line me-2"></i> View Performance Dashboard
                        </a>
                    </div>
                </div>
            </div>
        </div>

        <footer>
            EY Query Management Demo • {{ current_year }}
            <div class="small mt-1 text-muted">Internal demonstration only</div>
        </footer>

        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js"></script>
    </body>
    </html>
    """, response=response, error=error, current_year=current_year)


@app.route("/dashboard", methods=["GET", "POST"])
def dashboard():
    current_year = datetime.now().year
    
    try:
        df = get_all_tickets_df().copy()
        
        teams = sorted(df["Team Name"].dropna().unique()) if "Team Name" in df.columns else []
        person_col = next((col for col in ["Person Name", "Assigned To", "Agent Name", "Person"] if col in df.columns), None)
        persons = sorted(df[person_col].dropna().unique()) if person_col else []

        selected_team   = request.form.get("team_filter")   or request.args.get("team_filter",   "")
        selected_person = request.form.get("person_filter") or request.args.get("person_filter", "")

        filtered_df = df.copy()
        filter_title = "All Tickets"
        if selected_team and selected_team in teams:
            filtered_df = filtered_df[filtered_df["Team Name"] == selected_team]
            filter_title = f"Team: {selected_team}"
        if selected_person and person_col and selected_person in persons:
            filtered_df = filtered_df[filtered_df[person_col] == selected_person]
            if filter_title != "All Tickets":
                filter_title += f" • {person_col}: {selected_person}"
            else:
                filter_title = f"{person_col}: {selected_person}"

        # KPIs
        total = len(filtered_df)
        status_counts = filtered_df["Ticket Status"].value_counts()
        open_c    = status_counts.get("Open", 0)
        closed_c  = status_counts.get("Closed", 0)
        inprog_c  = status_counts.get("In Progress", 0)
        cancel_c  = status_counts.get("Cancelled", 0)

        rates = {
            "closed":  round(closed_c / total * 100, 1) if total else 0,
            "open":    round(open_c   / total * 100, 1) if total else 0,
            "cancel":  round(cancel_c / total * 100, 1) if total else 0,
            "inprog":  round(inprog_c / total * 100, 1) if total else 0
        }

        # Resolution time
        avg_resolution_str = "N/A"
        resolution_color = "text-muted"
        if "Ticket Create Date" in filtered_df.columns and "Ticket Closed Date" in filtered_df.columns:
            create_raw = pd.to_numeric(filtered_df["Ticket Create Date"], errors='coerce')
            closed_raw = pd.to_numeric(filtered_df["Ticket Closed Date"], errors='coerce')

            create_raw = create_raw.where((create_raw >= 30000) & (create_raw <= 60000), np.nan)
            closed_raw = closed_raw.where((closed_raw >= 30000) & (closed_raw <= 60000), np.nan)

            origin = pd.Timestamp("1899-12-30")
            filtered_df["Ticket Create Date"] = origin + pd.to_timedelta(create_raw, unit='D')
            filtered_df["Ticket Closed Date"] = origin + pd.to_timedelta(closed_raw, unit='D')

            closed_tickets = filtered_df[
                (filtered_df["Ticket Status"] == "Closed") &
                filtered_df["Ticket Create Date"].notna() &
                filtered_df["Ticket Closed Date"].notna() &
                (filtered_df["Ticket Closed Date"] > filtered_df["Ticket Create Date"])
            ].copy()

            if not closed_tickets.empty:
                delta = closed_tickets["Ticket Closed Date"] - closed_tickets["Ticket Create Date"]
                hours = delta.dt.total_seconds() / 3600
                valid_hours = hours[hours > 0]
                if not valid_hours.empty:
                    avg = valid_hours.mean()
                    avg_resolution_str = f"{avg:.1f} hrs"
                    if avg < 24:    resolution_color = "text-success"
                    elif avg > 72:  resolution_color = "text-danger"
                    else:           resolution_color = "text-warning"

        # Charts
        # Pie
        fig_pie, ax_pie = plt.subplots(figsize=(6, 5.5))
        pie_data, pie_labels, pie_colors = [], [], ['#28a745', '#0d6efd', '#ffc107', '#dc3545']
        for status, color in zip(["Open", "Closed", "In Progress", "Cancelled"], pie_colors):
            cnt = status_counts.get(status, 0)
            if cnt > 0:
                pie_data.append(cnt)
                pie_labels.append(f"{status} ({cnt})")
        if pie_data:
            ax_pie.pie(pie_data, labels=pie_labels, autopct='%1.0f%%', startangle=90,
                       colors=pie_colors[:len(pie_data)], textprops={'fontsize':12})
            ax_pie.set_title(f"Status Overview\n{filter_title}", fontsize=14, pad=20)
        else:
            ax_pie.text(0.5, 0.5, "No data", ha='center', va='center', fontsize=14)
        pie_img = plot_to_img(fig_pie)

        # Team bar (only if not filtered by team)
        team_img = None
        if not selected_team and "Team Name" in df.columns:
            team_status = filtered_df.groupby(["Team Name", "Ticket Status"]).size().unstack(fill_value=0)
            team_status = team_status.reindex(columns=["Open","In Progress","Closed","Cancelled"], fill_value=0)
            fig_team, ax_team = plt.subplots(figsize=(10, 6))
            team_status.plot(kind='bar', stacked=True, ax=ax_team,
                             color=['#28a745','#ffc107','#0d6efd','#dc3545'])
            ax_team.set_title("Tickets by Team & Status", fontsize=14)
            ax_team.set_ylabel("Count")
            ax_team.tick_params(axis='x', rotation=45)
            ax_team.legend(bbox_to_anchor=(1.02,1), loc='upper left')
            plt.tight_layout()
            team_img = plot_to_img(fig_team)

        # Person bar (only if not filtered by person)
        person_img = None
        if person_col and not selected_person:
            person_status = filtered_df.groupby([person_col, "Ticket Status"]).size().unstack(fill_value=0)
            person_status = person_status.reindex(columns=["Open","In Progress","Closed","Cancelled"], fill_value=0)
            fig_person, ax_person = plt.subplots(figsize=(11, 6.5))
            person_status.plot(kind='bar', ax=ax_person,
                               color=['#28a745','#ffc107','#0d6efd','#dc3545'])
            ax_person.set_title(f"Tickets by {person_col} (Workload)", fontsize=14)
            ax_person.set_ylabel("Count")
            ax_person.tick_params(axis='x', rotation=60, labelsize=9)
            ax_person.legend(bbox_to_anchor=(1.02,1), loc='upper left')
            plt.tight_layout()
            person_img = plot_to_img(fig_person)

        return render_template_string("""
        <!DOCTYPE html>
        <html lang="en" data-bs-theme="light">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>EY Dashboard</title>
            <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
            <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css">
            <style>
                :root {
                    --ey-blue:    #0047ab;
                    --ey-blue-dk: #003087;
                    --success:    #28a745;
                    --warning:    #ffc107;
                    --danger:     #dc3545;
                }
                body {
                    background: linear-gradient(145deg, #f8f9fc 0%, #eef2ff 100%);
                    color: #1e293b;
                    min-height: 100vh;
                }
                .navbar { background: var(--ey-blue) !important; box-shadow: 0 2px 12px rgba(0,0,0,0.15); }
                .card {
                    border: none;
                    border-radius: 16px;
                    box-shadow: 0 8px 32px rgba(0,0,0,0.07);
                    overflow: hidden;
                }
                .kpi-value {
                    font-size: 2.8rem;
                    font-weight: 700;
                    letter-spacing: -0.6px;
                }
                .form-select, .form-control {
                    border-radius: 10px;
                    border: 1px solid #cbd5e1;
                }
                .btn-primary {
                    background: var(--ey-blue);
                    border: none;
                    border-radius: 10px;
                    font-weight: 600;
                }
                .btn-primary:hover { background: var(--ey-blue-dk); }
                img.img-fluid {
                    border-radius: 10px;
                    box-shadow: 0 4px 16px rgba(0,0,0,0.06);
                }
                @media (max-width: 768px) {
                    .kpi-value { font-size: 2.2rem; }
                    .card-body { padding: 1.5rem; }
                }
            </style>
        </head>
        <body>

            <nav class="navbar navbar-dark">
                <div class="container">
                    <a class="navbar-brand" href="/">EY Query Agent</a>
                    <span class="navbar-text">Dashboard</span>
                </div>
            </nav>

            <div class="container my-5">
                <h1 class="text-center mb-3 fw-bold text-dark">Ticket Performance</h1>
                <h5 class="text-center text-muted mb-4">Showing: {{ filter_title }}</h5>

                <!-- Filters -->
                <div class="card mb-5 shadow-sm">
                    <div class="card-body">
                        <form method="post" class="row g-3 align-items-end">
                            <div class="col-md-5">
                                <label class="form-label fw-medium">Team</label>
                                <select name="team_filter" class="form-select">
                                    <option value="">All Teams</option>
                                    {% for team in teams %}
                                    <option value="{{ team }}" {% if team == selected_team %}selected{% endif %}>{{ team }}</option>
                                    {% endfor %}
                                </select>
                            </div>
                            {% if persons %}
                            <div class="col-md-5">
                                <label class="form-label fw-medium">{{ person_col or 'Person' }}</label>
                                <select name="person_filter" class="form-select">
                                    <option value="">All Persons</option>
                                    {% for p in persons %}
                                    <option value="{{ p }}" {% if p == selected_person %}selected{% endif %}>{{ p }}</option>
                                    {% endfor %}
                                </select>
                            </div>
                            {% endif %}
                            <div class="col-md-2">
                                <button type="submit" class="btn btn-primary w-100">Apply</button>
                            </div>
                        </form>
                    </div>
                </div>

                <!-- KPIs -->
                <div class="row g-4 mb-5">
                    <div class="col-md-3">
                        <div class="card text-center shadow-sm">
                            <div class="card-body py-4">
                                <h5 class="text-muted mb-2">Total Tickets</h5>
                                <p class="kpi-value text-primary">{{ total }}</p>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-3">
                        <div class="card text-center shadow-sm">
                            <div class="card-body py-4">
                                <h5 class="text-muted mb-2">Open Tickets</h5>
                                <p class="kpi-value {% if rates.open > 40 %}text-danger{% elif rates.open > 25 %}text-warning{% else %}text-success{% endif %}">
                                    {{ open_c }} <small>({{ rates.open }}%)</small>
                                </p>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-3">
                        <div class="card text-center shadow-sm">
                            <div class="card-body py-4">
                                <h5 class="text-muted mb-2">Avg Resolution Time</h5>
                                <p class="kpi-value {{ resolution_color }}">{{ avg_resolution_str }}</p>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-3">
                        <div class="card text-center shadow-sm">
                            <div class="card-body py-4">
                                <h5 class="text-muted mb-2">Closed Rate</h5>
                                <p class="kpi-value {% if rates.closed < 60 %}text-danger{% elif rates.closed < 80 %}text-warning{% else %}text-success{% endif %}">
                                    {{ rates.closed }}%
                                </p>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Charts -->
                <div class="row g-4">
                    <div class="col-lg-6">
                        <div class="card shadow-sm">
                            <div class="card-body">
                                <h5 class="card-title text-center mb-4">Status Distribution</h5>
                                <img src="data:image/png;base64,{{ pie_img }}" class="img-fluid d-block mx-auto" alt="Status Pie">
                            </div>
                        </div>
                    </div>

                    {% if team_img %}
                    <div class="col-lg-6">
                        <div class="card shadow-sm">
                            <div class="card-body">
                                <h5 class="card-title text-center mb-4">By Team & Status</h5>
                                <img src="data:image/png;base64,{{ team_img }}" class="img-fluid d-block mx-auto" alt="Team Chart">
                            </div>
                        </div>
                    </div>
                    {% endif %}

                    {% if person_img %}
                    <div class="col-12">
                        <div class="card shadow-sm">
                            <div class="card-body">
                                <h5 class="card-title text-center mb-4">Workload by {{ person_col or 'Person' }}</h5>
                                <img src="data:image/png;base64,{{ person_img }}" class="img-fluid d-block mx-auto" alt="Person Workload">
                            </div>
                        </div>
                    </div>
                    {% endif %}
                </div>

                <div class="text-center mt-5">
                    <a href="/dashboard" class="btn btn-outline-secondary me-3 px-4">Refresh</a>
                    <a href="/" class="btn btn-primary px-5 py-3">← Back to Chat</a>
                </div>
            </div>

            <footer class="text-center py-4 text-muted bg-white border-top">
                EY Query Management Demo • {{ current_year }}
            </footer>

            <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js"></script>
        </body>
        </html>
        """, 
        total=total, open_c=open_c, closed_c=closed_c,
        rates=rates, avg_resolution_str=avg_resolution_str, resolution_color=resolution_color,
        pie_img=pie_img, team_img=team_img, person_img=person_img,
        teams=teams, persons=persons, selected_team=selected_team, selected_person=selected_person,
        person_col=person_col or "Person", filter_title=filter_title, current_year=current_year)

    except Exception as e:
        return f"""
        <div class="container my-5">
            <div class="alert alert-danger">
                <h4>Dashboard Error</h4>
                <p>{str(e)}</p>
                <pre class="bg-light p-3 rounded">{traceback.format_exc()}</pre>
                <a href="/" class="btn btn-outline-secondary">Back to Agent</a>
            </div>
        </div>
        """


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)