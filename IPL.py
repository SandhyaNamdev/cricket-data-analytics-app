import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# --- Page Configuration ---
st.set_page_config(
    page_title="Player Performance Comparison",
    page_icon="🏏",
    layout="wide",
)

# --- Load Data ---
@st.cache_data
def load_data(file_source):
    """Loads data from a file path or uploaded file object."""
    try:
        df = pd.read_csv(file_source)
        # Create a 'year' column from the 'id' column for analysis
        df['year'] = df['id'].astype(str).str[:4].astype(int)
        return df
    except FileNotFoundError:
        st.error("Error: The default file `ball_by_ball_ipl_data.csv` was not found. Please upload a file.")
        return None
    except Exception as e:
        st.error(f"An error occurred while loading the data: {e}")
        return None

# --- Column Names (Hardcoded for simplicity) ---
PLAYER_COL = 'batter_name'
RUNS_COL = 'batsman_run'
TEAM_COL = 'bowling_team'
YEAR_COL = 'year'

# --- Main App Logic ---
st.title("🏏 IPL Player Performance Comparison")

# --- Sidebar for Data Upload and Player Selection ---
st.sidebar.title("Controls")
uploaded_file = st.sidebar.file_uploader("Upload your IPL data (CSV)", type="csv")

df = None
if uploaded_file is not None:
    # If a file is uploaded, use it
    df = load_data(uploaded_file)
else:
    # Otherwise, try to load the default local file
    df = load_data('ball_by_ball_ipl_data.csv')


if df is not None:
    st.markdown("Select two or more players to compare their performance metrics.")

    # --- Sidebar for Player Selection ---
    st.sidebar.header("Select Players")
    all_players = sorted(df[PLAYER_COL].unique())
    default_players = ["V Kohli", "RG Sharma"] if "V Kohli" in all_players and "RG Sharma" in all_players else all_players[:2]
    
    selected_players = st.sidebar.multiselect(
        "Choose players to compare:",
        options=all_players,
        default=default_players
    )

    # --- Analysis Section ---
    if len(selected_players) < 2:
        st.warning("Please select at least two players to start the comparison.")
    else:
        # Filter data for the selected players
        players_df = df[df[PLAYER_COL].isin(selected_players)].copy()

        st.header("Overall Career Summary")
        
        # --- Calculate Summary Stats ---
        summary_stats = players_df.groupby(PLAYER_COL).agg(
            Total_Runs=(RUNS_COL, 'sum'),
            Balls_Faced=(RUNS_COL, 'count'),
            Fours=(RUNS_COL, lambda x: (x == 4).sum()),
            Sixes=(RUNS_COL, lambda x: (x == 6).sum())
        ).reset_index()
        
        summary_stats['Strike_Rate'] = (summary_stats['Total_Runs'] / summary_stats['Balls_Faced'] * 100).round(2)
        st.dataframe(summary_stats.set_index(PLAYER_COL), use_container_width=True)
        st.markdown("---")

        # --- Create Tabs for Different Visualizations ---
        tab1, tab2, tab3, tab4 = st.tabs(["Yearly Runs", "Yearly Strike Rate", "Runs vs Teams", "Boundary Analysis"])

        with tab1:
            st.subheader("Year-on-Year Run Totals")
            yearly_runs = players_df.groupby([YEAR_COL, PLAYER_COL])[RUNS_COL].sum().reset_index()
            
            fig_yearly = px.line(
                yearly_runs,
                x=YEAR_COL,
                y=RUNS_COL,
                color=PLAYER_COL,
                title="Total Runs Scored Each Year",
                labels={RUNS_COL: "Total Runs", YEAR_COL: "Year"},
                markers=True,
                template='plotly_white'
            )
            st.plotly_chart(fig_yearly, use_container_width=True)

        with tab2:
            st.subheader("Year-on-Year Strike Rate")
            yearly_stats = players_df.groupby([YEAR_COL, PLAYER_COL]).agg(
                Total_Runs=(RUNS_COL, 'sum'),
                Balls_Faced=(RUNS_COL, 'count')
            ).reset_index()
            # Avoid division by zero for years where a player didn't face any balls
            yearly_stats = yearly_stats[yearly_stats['Balls_Faced'] > 0]
            yearly_stats['Strike_Rate'] = (yearly_stats['Total_Runs'] / yearly_stats['Balls_Faced'] * 100).round(2)
            
            fig_sr_yearly = px.line(
                yearly_stats,
                x=YEAR_COL,
                y='Strike_Rate',
                color=PLAYER_COL,
                title="Strike Rate Trend Over the Years",
                labels={'Strike_Rate': "Strike Rate", YEAR_COL: "Year"},
                markers=True,
                template='plotly_white'
            )
            st.plotly_chart(fig_sr_yearly, use_container_width=True)

        with tab3:
            st.subheader("Runs Scored Against Each Team")
            runs_vs_team = players_df.groupby([PLAYER_COL, TEAM_COL])[RUNS_COL].sum().reset_index()
            
            fig_vs_team = px.bar(
                runs_vs_team,
                x=TEAM_COL,
                y=RUNS_COL,
                color=PLAYER_COL,
                barmode='group',
                title="Runs Scored Against Opponent Teams",
                labels={RUNS_COL: "Total Runs", TEAM_COL: "Opponent Team"},
                template='plotly_white'
            )
            st.plotly_chart(fig_vs_team, use_container_width=True)
            
        with tab4:
            st.subheader("Career Fours and Sixes")
            # Use the already calculated summary_stats
            boundary_data = summary_stats[[PLAYER_COL, 'Fours', 'Sixes']].melt(
                id_vars=PLAYER_COL, 
                var_name='Boundary Type', 
                value_name='Count'
            )
            
            fig_boundaries = px.bar(
                boundary_data,
                x=PLAYER_COL,
                y='Count',
                color='Boundary Type',
                barmode='group',
                title="Total Career Fours vs. Sixes",
                labels={PLAYER_COL: "Player", 'Count': "Total Count"},
                template='plotly_white'
            )
            st.plotly_chart(fig_boundaries, use_container_width=True)

else:
    st.info("👋 Welcome! Please upload a CSV file using the sidebar to begin analysis.")

