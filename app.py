import dash
import time
from dash import dcc, html
from dash.dependencies import Input, Output
from datetime import datetime



LOG_FILE_PATH = "/home/pyback/sandbox/app.log"

app = dash.Dash(__name__)
app.title = "Live Log Viewer with Search"

app.layout = html.Div([
    html.H2("Live Log Viewer"),

    html.Div([
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
     Input('search-input', 'value'),
     Input('case-sensitive', 'value'),
     Input('date-picker-range', 'start_date'),
     Input('date-picker-range', 'end_date')]
)
def update_logs(n, query, case_option, start_date, end_date):
    try:
        with open(LOG_FILE_PATH, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            log_lines = lines[-1000:]  # Limit for performance

            # Filter by search query
            if query:
                if 'CASE' in case_option:
                    log_lines = [line for line in log_lines if query in line]
                else:
                    log_lines = [line for line in log_lines if query.lower() in line.lower()]

            # Filter by date range
            def extract_timestamp(line):
                # Adjust this pattern to match your log format
                try:
                    return datetime.strptime(line[:19], "%Y-%m-%d %H:%M:%S")
                except:
                    return None

            if start_date or end_date:
                start_dt = datetime.strptime(start_date, "%Y-%m-%d") if start_date else None
                end_dt = datetime.strptime(end_date, "%Y-%m-%d") if end_date else None

                filtered_lines = []
                for line in log_lines:
                    ts = extract_timestamp(line)
                    if not ts:
                        continue
                    if (not start_dt or ts.date() >= start_dt.date()) and \
                       (not end_dt or ts.date() <= end_dt.date()):
                        filtered_lines.append(line)
                log_lines = filtered_lines

            log_text = ''.join(log_lines) if log_lines else 'No matching log entries.'
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
            return log_text, f"Last updated: {timestamp}"
    except Exception as e:
        return f"Error reading log file: {e}", ""

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=8050)
