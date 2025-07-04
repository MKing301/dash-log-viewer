import dash
import time
from dash import dcc, html
from dash.dependencies import Input, Output
from datetime import datetime, timedelta

# Log file options
LOG_FILE_OPTIONS = {
    "Sandbox Log": "/home/pyback/sandbox/app.log",
    "Polars Example Log": "/home/pyback/polars-projects/polars-examples/polars.log",
    "Cities Log": "/home/pyback/pandas-projects/cities/cities.log"
}

app = dash.Dash(__name__)
app.title = "Live Log Viewer with Search"

app.layout = html.Div([
    html.H2("Live Log Viewer"),

    html.Div([
        dcc.Dropdown(
            id='log-file-dropdown',
            options=[{'label': name, 'value': path} for name, path in LOG_FILE_OPTIONS.items()],
            value=list(LOG_FILE_OPTIONS.values())[0],
            style={'width': '40%', 'marginRight': '10px'}
        ),
        dcc.Input(
            id='search-input',
            type='text',
            placeholder='Search logs...',
            debounce=True,
            style={'width': '40%', 'marginRight': '10px'}
        ),
        dcc.DatePickerRange(
            id='date-picker-range',
            start_date_placeholder_text="Start Date",
            end_date_placeholder_text="End Date",
            display_format='YYYY-MM-DD',
            style={'marginRight': '10px'}
        ),
        dcc.Input(
            id='start-time',
            type='text',
            placeholder='Start Time (HH:MM:SS)',
            style={'width': '20%', 'marginRight': '10px'}
        ),
        dcc.Input(
            id='end-time',
            type='text',
            placeholder='End Time (HH:MM:SS)',
            style={'width': '20%', 'marginRight': '10px'}
        ),
        dcc.Checklist(
            id='case-sensitive',
            options=[{'label': 'Case sensitive', 'value': 'CASE'}],
            value=[],
            inline=True,
            style={'display': 'inline-block'}
        ),
    ], style={'marginBottom': '20px'}),

    html.Div(id='last-update', style={'marginBottom': '10px', 'color': 'gray'}),

    dcc.Interval(
        id='interval-component',
        interval=5 * 1000,
        n_intervals=0
    ),

    html.Pre(id='log-output', style={
        'whiteSpace': 'pre-wrap',
        'height': '600px',
        'overflowY': 'scroll',
        'backgroundColor': '#f4f4f4',
        'padding': '10px',
        'border': '1px solid #ccc'
    })
])

@app.callback(
    [Output('log-output', 'children'),
     Output('last-update', 'children')],
    [Input('interval-component', 'n_intervals'),
     Input('log-file-dropdown', 'value'),
     Input('search-input', 'value'),
     Input('case-sensitive', 'value'),
     Input('date-picker-range', 'start_date'),
     Input('date-picker-range', 'end_date'),
     Input('start-time', 'value'),
     Input('end-time', 'value')]
)
def update_logs(n, log_file_path, query, case_option, start_date, end_date, start_time, end_time):
    try:
        with open(log_file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            log_lines = lines[-1000:]  # Limit for performance

            # Filter by search query
            if query:
                if 'CASE' in case_option:
                    log_lines = [line for line in log_lines if query in line]
                else:
                    log_lines = [line for line in log_lines if query.lower() in line.lower()]

            # Extract timestamp with milliseconds
            def extract_timestamp(line):
                try:
                    ts_part = line.split(" | ")[0]
                    return datetime.strptime(ts_part, "%Y-%m-%d %H:%M:%S.%f")
                except:
                    return None

            # Combine date and time
            def parse_datetime(date_str, time_str, is_end=False):
                try:
                    if date_str:
                        if time_str:
                            return datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M:%S")
                        else:
                            if is_end:
                                return datetime.strptime(date_str, "%Y-%m-%d") + timedelta(days=1) - timedelta(milliseconds=1)
                            else:
                                return datetime.strptime(date_str, "%Y-%m-%d")
                    return None
                except:
                    return None

            start_dt = parse_datetime(start_date, start_time)
            end_dt = parse_datetime(end_date, end_time, is_end=True)

            # Filter by time range
            filtered_lines = []
            for line in log_lines:
                ts = extract_timestamp(line)
                if ts is None:
                    continue
                if start_dt and ts < start_dt:
                    continue
                if end_dt and ts > end_dt:
                    continue
                filtered_lines.append(line)

            log_lines = filtered_lines

            log_text = ''.join(log_lines) if log_lines else 'No matching log entries.'
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
            return log_text, f"Last updated: {timestamp}"
    except Exception as e:
        return f"Error reading log file: {e}", ""

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=8050)
