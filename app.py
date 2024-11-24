import dash
from dash import dcc, html, Input, Output
import pandas as pd
import plotly.graph_objects as go

# Debug: Confirm the script is starting
print("Script is starting...")

# Load the data from the provided CSV file
df = pd.read_csv('data.csv')

# Debug: Confirm data is loaded
print("Data loaded successfully:")
print(df.head())

# Convert dollar columns from strings to numbers for proper calculations
for col in df.columns:
    if "_Dollars" in col:
        df[col] = df[col].replace(r'[\$,]', '', regex=True).astype(float)

# Dynamically extract all sector names from the columns
sector_columns = [col.split("_Awards")[0] for col in df.columns if "_Awards" in col]
sectors = list(set(sector_columns))  # Get unique sector names

# Debug: Print the list of sectors
print("Available sectors:", sectors)

# Initialize the Dash app
app = dash.Dash(__name__)

# App layout with "Select All" checkbox
app.layout = html.Div([
    html.H1("8(a) Federal Awards and Dollars Dashboard", style={"textAlign": "center", "color": "#4CAF50"}),
    
    # "Select All" option and checklist for industry sectors
    html.Label("Select Industry Sectors:", style={"fontWeight": "bold"}),
    dcc.Checklist(
        id='select-all-checkbox',
        options=[{'label': 'Select All', 'value': 'ALL'}],
        value=['ALL'],  # Default is "Select All"
        inline=True,
        style={"padding": "10px"}
    ),
    dcc.Checklist(
        id='sector-checklist',
        options=[{'label': sector.replace("_", " "), 'value': sector} for sector in sectors],
        value=sectors,  # Default is all sectors selected
        inline=True,
        style={"padding": "10px"}
    ),
    
    # Chart area
    dcc.Graph(id='combo-chart', style={"padding": "20px"}),
])

# Callback to handle "Select All" logic
@app.callback(
    Output('sector-checklist', 'value'),
    [Input('select-all-checkbox', 'value')],
    [Input('sector-checklist', 'value')]
)
def toggle_select_all(select_all_value, selected_sectors):
    # If "Select All" is checked, return all sectors
    if 'ALL' in select_all_value:
        return sectors
    # Otherwise, return the currently selected sectors
    return selected_sectors

# Callback to update the chart based on selected sectors
@app.callback(
    Output('combo-chart', 'figure'),
    [Input('sector-checklist', 'value')]
)
def update_chart(selected_sectors):
    # Debug: Print selected sectors
    print("Selected sectors:", selected_sectors)

    # Initialize a combined awards and dollars DataFrame
    combined_df = pd.DataFrame({'Month': df['Month'], 'Awards': 0, 'Dollars': 0})

    # Aggregate data for selected sectors
    for sector in selected_sectors:
        awards_col = f"{sector}_Awards"
        dollars_col = f"{sector}_Dollars"
        
        if awards_col in df.columns and dollars_col in df.columns:
            combined_df['Awards'] += df[awards_col]
            combined_df['Dollars'] += df[dollars_col]

    # Convert dollars to millions for display purposes
    combined_df['Dollars'] = combined_df['Dollars'].round(0)

    # Create the figure
    fig = go.Figure()

    # Add the bar chart for contract awards
    fig.add_trace(go.Bar(
        x=combined_df['Month'],
        y=combined_df['Awards'],
        name='Awards',
        marker_color='#FFA726',
        opacity=0.8,
        text=combined_df['Awards'].apply(lambda x: f"{x:,}"),  # Format as numbers with commas
        textposition='auto'
    ))

    # Add the line chart for contract dollars
    fig.add_trace(go.Scatter(
        x=combined_df['Month'],
        y=combined_df['Dollars'],
        name='Dollars',
        mode='lines+markers+text',
        line=dict(color='#42A5F5', width=3),
        marker=dict(size=8, symbol='circle', color='#1E88E5', line=dict(width=2, color='white')),
        text=combined_df['Dollars'].apply(lambda x: f"${x:,.0f}"),  # Format as dollars with commas and rounding
        textposition='top center'
    ))

    # Update layout
    fig.update_layout(
        title={
            "text": "Combined Awards and Dollars (FY 2024)",
            "y": 0.9,
            "x": 0.5,
            "xanchor": "center",
            "yanchor": "top"
        },
        title_font=dict(size=20, color="#263238"),
        xaxis=dict(
            title="Month",
            showgrid=False,
            zeroline=False,
            tickangle=45,
            title_font=dict(size=14, color="#263238")
        ),
        yaxis=dict(
            title="Count of Awards / Dollars",
            showgrid=True,
            gridcolor='lightgrey',
            zeroline=False,
            title_font=dict(size=14, color="#263238")
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(size=12, color="#263238")
        ),
        plot_bgcolor="#F9F9F9",
        paper_bgcolor="#F4F4F8",
        margin=dict(t=50, b=50, l=50, r=50)
    )
    
    return fig

if __name__ == '__main__':
    print("Starting the server...")
    app.run_server(debug=True, port=8050)
