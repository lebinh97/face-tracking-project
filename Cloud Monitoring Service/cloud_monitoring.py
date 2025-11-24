import dash
from dash import dcc, html, Input, Output
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd
import json
import time
import os
import subprocess
import re

# --- CONFIGURATION ---
JSON_FILE_PATH = '/home/bngl1/projects/cs5939/Cloud Monitoring Service/container_logs.json'

CONTAINER_LIST = [
    "face-extract-api",
    "face-analysis-api",
    "face-encode-api"
]
# ---------------------

# ========== DOCKER LOG FUNCTION (added only this) ==========
def get_recent_docker_logs_simple(container_name, time_ago="1m"):
    try:
        result = subprocess.run(
            ['docker', 'logs', '--since', time_ago, container_name],
            capture_output=True,
            text=True,
            check=True
        )
        logs = result.stdout

        filtered = []
        for line in logs.splitlines():
            if "GET /metrics" in line:
                continue
            filtered.append(line)
        return "\n".join(filtered)

    except Exception as e:
        return f"Error: {e}"
# ============================================================


app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

app.layout = dbc.Container([

    # Header
    dbc.Row([
        dbc.Col([
            html.H1("Container Monitor", className="text-center mt-4 mb-3"),
        ], width=12)
    ]),

    # Dropdown
    dbc.Row([
        dbc.Col([
            html.Label("Select Container:", className="fw-bold"),
            dcc.Dropdown(
                id="container-dropdown",
                options=[{"label": c, "value": c} for c in CONTAINER_LIST],
                value=CONTAINER_LIST[0],
                clearable=False,
                className="mb-4"
            )
        ], width={"size": 6, "offset": 3})
    ]),

    # ---------------------------------------------------
    # ROW 1 — METRICS SUMMARY (left) + LOG OUTPUT (right)
    # ---------------------------------------------------
    dbc.Row([

        # LEFT 6 COL: METRIC SUMMARY
        dbc.Col([
            html.H4("Latest Container Metrics", className="mt-4 mb-3"),
            html.Pre(
                id="latest-metrics",
                style={
                    "whiteSpace": "pre-wrap",
                    "backgroundColor": "#111",
                    "color": "white",
                    "padding": "15px",
                    "borderRadius": "8px",
                    "height": "280px",
                    "overflowY": "scroll",
                    "fontSize": "13px"
                }    
            )
        ], width=6),

        # RIGHT 6 COL: LOG PANEL
        dbc.Col([
            html.H4("Recent Logs (Last 60 sec)", className="mt-4 mb-2"),
            html.Pre(
                id="log-output",
                style={
                    "whiteSpace": "pre-wrap",
                    "backgroundColor": "#111",
                    "color": "white",
                    "padding": "15px",
                    "borderRadius": "8px",
                    "height": "280px",
                    "overflowY": "scroll",
                    "fontSize": "13px"
                }
            )
        ], width=6),

    ]),

    # ---------------------------------------------------
    # ROW 2 — TWO CHARTS (unchanged)
    # ---------------------------------------------------
    dbc.Row([
        dbc.Col([dcc.Graph(id='ram-percent-chart', config={'displayModeBar': False})],
                width=6, className="p-2"),

        dbc.Col([dcc.Graph(id='cpu-percent-chart', config={'displayModeBar': False})],
                width=6, className="p-2")
    ], className="g-3"),

    dcc.Interval(id='interval-component', interval=2000, n_intervals=0)

], fluid=True, className="bg-light p-4")


# ============================================================
# CALLBACK (only *1 line added*: Output('log-output','children')
# ============================================================
@app.callback(
    [
        Output('ram-percent-chart', 'figure'),
        Output('cpu-percent-chart', 'figure'),
        Output('log-output', 'children'),
        Output('latest-metrics', 'children')  # NEW
    ],
    [Input('interval-component', 'n_intervals'),
     Input('container-dropdown', 'value')]
)

def update_graphs(n, selected_container):

    # Fetch logs for the SELECTED container (not hardcoded!)
    logs = get_recent_docker_logs_simple(selected_container, "1m")

    empty_fig = px.line(title="No data available")
    empty_fig.update_layout(template="plotly_white")

    # Default for latest metrics
    latest_metrics_str = "No metric data"

    if not os.path.exists(JSON_FILE_PATH):
        return empty_fig, empty_fig, logs, latest_metrics_str  # ✅ 4 items

    try:
        with open(JSON_FILE_PATH, 'r') as f:
            data = json.load(f)

        container_logs = data.get(selected_container, [])

        if not container_logs:
            return empty_fig, empty_fig, logs, latest_metrics_str  # ✅

        df = pd.DataFrame(container_logs)

        required_columns = ['timestamp', 'memory_usage_bytes',
                            'memory_limit_bytes', 'cpu_percent']
        if not all(col in df.columns for col in required_columns):
            return empty_fig, empty_fig, logs, latest_metrics_str  # ✅

        df["datetime"] = pd.to_datetime(df["timestamp"], unit="s")
        df["memory_percent"] = (df["memory_usage_bytes"] / df["memory_limit_bytes"]) * 100

        now = time.time()
        df = df[df["timestamp"] > now - 60]

        if df.empty:
            ram_empty = px.line(title="No RAM data").update_layout(template="plotly_white")
            cpu_empty = px.line(title="No CPU data").update_layout(template="plotly_white")
            return ram_empty, cpu_empty, logs, latest_metrics_str  # ✅

        # Get latest metric entry for display
        latest_row = df.iloc[-1]
        latest_metrics_str = (
            f"Uptime (min): {latest_row['uptime_seconds']}\n"
            f"CPU %: {latest_row['cpu_percent']:.2f}\n"
            f"RAM %: {latest_row['memory_percent']:.2f}\n"
            f"Memory Usage: {latest_row['memory_usage_bytes'] / (1024**2):.1f} MB\n"
            f"Memory Limit: {latest_row['memory_limit_bytes'] / (1024**2):.1f} MB"
        )

        # RAM chart
        ram_fig = px.line(
            df, x="datetime", y="memory_percent",
            title=f"RAM Usage: {selected_container}",
            markers=True, line_shape='linear'
        )
        ram_fig.update_traces(line_color='blue')
        ram_fig.update_layout(
            xaxis_title="Time", yaxis_title="RAM Usage (%)",
            yaxis_range=[max(0, df["memory_percent"].min() - 2), df["memory_percent"].max() + 2],
            template="plotly_white", hovermode="x unified"
        )

        # CPU chart
        cpu_fig = px.line(
            df, x="datetime", y="cpu_percent",
            title=f"CPU Usage: {selected_container}",
            markers=True, line_shape='linear'
        )
        cpu_fig.update_traces(line_color='red')
        cpu_fig.update_layout(
            xaxis_title="Time", yaxis_title="CPU Usage (%)",
            yaxis_range=[max(0, df["cpu_percent"].min() - 0.3), df["cpu_percent"].max() + 0.3],
            template="plotly_white", hovermode="x unified"
        )

        return ram_fig, cpu_fig, logs, latest_metrics_str  # ✅ 4 items

    except Exception as e:
        print("Error:", e)
        return empty_fig, empty_fig, logs, f"Error: {str(e)}"  # ✅


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=7999, debug=False)
