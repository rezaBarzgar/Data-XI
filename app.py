import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os
import json
from datetime import datetime
import time

# Import your FPL system (assuming it's in fpl_captain_system.py)
from fpl_captain_system import FPLCaptainRecommender

# Page configuration
st.set_page_config(
    page_title="FPL Captain Recommender",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #38003c;
        text-align: center;
        margin-bottom: 2rem;
        font-weight: bold;
    }
    .recommendation-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
        color: white;
    }
    .rank-1 {
        background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
    }
    .rank-2 {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    .rank-3 {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
    }
    .metric-container {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 5px;
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)


def initialize_session_state():
    """Initialize session state variables"""
    if 'recommender' not in st.session_state:
        st.session_state.recommender = None
    if 'recommendations' not in st.session_state:
        st.session_state.recommendations = None
    if 'team_data' not in st.session_state:
        st.session_state.team_data = None


def setup_sidebar():
    """Setup sidebar configuration"""
    st.sidebar.title("⚙️ Configuration")

    # API Key input
    api_key = st.sidebar.text_input(
        "OpenAI API Key",
        type="password",
        help="Enter your OpenAI API key or set OPENAI_API_KEY environment variable"
    )

    # Model selection
    model_options = [
        "gpt-3.5-turbo",
        "gpt-4",
        "gpt-4-turbo-preview",
        "gpt-4o-mini"
    ]
    selected_model = st.sidebar.selectbox(
        "Select LLM Model",
        model_options,
        index=0,
        help="Choose the language model for recommendations"
    )

    # Advanced settings
    with st.sidebar.expander("Advanced Settings"):
        gameweeks_ahead = st.slider(
            "Gameweeks to analyze",
            min_value=1,
            max_value=5,
            value=3,
            help="Number of future gameweeks to consider"
        )

        temperature = st.slider(
            "LLM Temperature",
            min_value=0.0,
            max_value=1.0,
            value=0.1,
            step=0.1,
            help="Lower values make responses more focused"
        )

    return api_key, selected_model, gameweeks_ahead, temperature


def initialize_recommender(api_key, model, temperature):
    """Initialize the FPL recommender"""
    try:
        if api_key:
            recommender = FPLCaptainRecommender(
                llm_model=model,
                openai_api_key=api_key
            )
        else:
            recommender = FPLCaptainRecommender(llm_model=model)

        st.session_state.recommender = recommender
        return True, "Recommender initialized successfully!"
    except Exception as e:
        return False, f"Error initializing recommender: {str(e)}"


def display_team_overview(team_data, recommender):
    """Display team overview information"""
    if not team_data:
        return

    team_info = team_data.get('team_info', {})

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Team Name", team_info.get('name', 'N/A'))
    with col2:
        st.metric("Overall Points", team_info.get('summary_overall_points', 0))
    with col3:
        st.metric("Overall Rank", f"{team_info.get('summary_overall_rank', 0):,}")
    with col4:
        st.metric("Team Value", f"£{team_info.get('last_deadline_value', 0) / 10:.1f}m")


def create_player_performance_chart(team_data, recommender):
    """Create player performance visualization"""
    if not team_data or not recommender:
        return

    try:
        # Get player IDs from team picks
        player_ids = [pick['element'] for pick in team_data['picks']]
        player_stats = recommender.get_player_performance_data(player_ids)

        # Create DataFrame for visualization
        chart_data = []
        for player_id, player in player_stats.items():
            pick_data = next((p for p in team_data['picks'] if p['element'] == player_id), {})
            is_playing = pick_data.get('multiplier', 0) > 0

            chart_data.append({
                'Player': player.name,
                'Total Points': player.total_points,
                'Form': player.form,
                'PPG': player.points_per_game,
                'Price': player.price,
                'Ownership': player.selected_by_percent,
                'Position': player.position,
                'Playing': 'Starting XI' if is_playing else 'Bench'
            })

        df = pd.DataFrame(chart_data)

        # Create subplots
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Total Points vs Form', 'Price vs Points Per Game',
                            'Ownership Distribution', 'Position Breakdown'),
            specs=[[{"secondary_y": False}, {"secondary_y": False}],
                   [{"secondary_y": False}, {"type": "pie"}]]
        )

        # Scatter plot: Total Points vs Form
        fig.add_trace(
            go.Scatter(
                x=df['Form'],
                y=df['Total Points'],
                mode='markers+text',
                text=df['Player'].str.split().str[0],  # First name only
                textposition="top center",
                marker=dict(size=10, color=df['Price'], colorscale='Viridis'),
                name='Players'
            ),
            row=1, col=1
        )

        # Scatter plot: Price vs PPG
        fig.add_trace(
            go.Scatter(
                x=df['Price'],
                y=df['PPG'],
                mode='markers+text',
                text=df['Player'].str.split().str[0],
                textposition="top center",
                marker=dict(size=10, color=df['Total Points'], colorscale='Blues'),
                name='Value Analysis'
            ),
            row=1, col=2
        )

        # Bar chart: Ownership
        fig.add_trace(
            go.Bar(
                x=df['Player'].str.split().str[0],
                y=df['Ownership'],
                marker_color='lightblue',
                name='Ownership %'
            ),
            row=2, col=1
        )

        # Pie chart: Position breakdown
        position_counts = df['Position'].value_counts()
        fig.add_trace(
            go.Pie(
                labels=position_counts.index,
                values=position_counts.values,
                name='Positions'
            ),
            row=2, col=2
        )

        fig.update_layout(height=800, showlegend=False)
        fig.update_xaxes(title_text="Form", row=1, col=1)
        fig.update_yaxes(title_text="Total Points", row=1, col=1)
        fig.update_xaxes(title_text="Price (£m)", row=1, col=2)
        fig.update_yaxes(title_text="Points Per Game", row=1, col=2)
        fig.update_xaxes(title_text="Players", row=2, col=1)
        fig.update_yaxes(title_text="Ownership %", row=2, col=1)

        st.plotly_chart(fig, use_container_width=True)

    except Exception as e:
        st.error(f"Error creating charts: {str(e)}")


def display_recommendations(recommendations):
    """Display captain recommendations in a styled format"""
    if not recommendations or 'recommendations' not in recommendations:
        return

    st.markdown("## 🎯 Captain Recommendations")

    for i, rec in enumerate(recommendations['recommendations']):
        rank = rec['rank']
        css_class = f"rank-{rank}"

        st.markdown(f"""
        <div class="recommendation-card {css_class}">
            <h3>#{rank} - {rec['player_name']}</h3>
            <p><strong>Risk Level:</strong> {rec['risk_level']} | 
               <strong>Differential:</strong> {rec['differential_potential']}</p>
            <p><strong>Reasoning:</strong> {rec['reasoning']}</p>
            <p><strong>Key Factors:</strong> {', '.join(rec['key_factors'])}</p>
        </div>
        """, unsafe_allow_html=True)

    # General advice
    if 'general_advice' in recommendations:
        st.markdown("### 💡 General Strategy Advice")
        st.info(recommendations['general_advice'])


def display_detailed_analysis(recommendations, team_data, recommender):
    """Display detailed analysis tabs"""
    if not all([recommendations, team_data, recommender]):
        return

    tab1, tab2, tab3, tab4 = st.tabs(["📊 Player Stats", "🏟️ Fixtures", "📈 Form Analysis", "💰 Value Analysis"])

    with tab1:
        st.subheader("Detailed Player Statistics")
        try:
            player_ids = [pick['element'] for pick in team_data['picks']]
            player_stats = recommender.get_player_performance_data(player_ids)
            ownership_data = recommender.get_ownership_stats(player_ids)
            injury_data = recommender.get_injury_updates(player_ids)

            # Create detailed stats table
            stats_data = []
            for player_id, player in player_stats.items():
                pick_data = next((p for p in team_data['picks'] if p['element'] == player_id), {})
                is_captain_eligible = pick_data.get('multiplier', 0) >= 1

                if is_captain_eligible:
                    stats_data.append({
                        'Player': player.name,
                        'Position': player.position,
                        'Team': player.team,
                        'Price': f"£{player.price}m",
                        'Total Points': player.total_points,
                        'PPG': round(player.points_per_game, 1),
                        'Form': player.form,
                        'Goals': player.goals_scored,
                        'Assists': player.assists,
                        'Bonus': player.bonus,
                        'Ownership': f"{player.selected_by_percent}%",
                        'Status': injury_data.get(player_id, 'Available')
                    })

            if stats_data:
                df_stats = pd.DataFrame(stats_data)
                st.dataframe(df_stats, use_container_width=True)

        except Exception as e:
            st.error(f"Error displaying player stats: {str(e)}")

    with tab2:
        st.subheader("Upcoming Fixtures Analysis")
        try:
            fixtures = recommender.get_upcoming_fixtures()
            bootstrap_data = recommender.fetch_fpl_bootstrap_data()
            teams_lookup = {team['id']: team['name'] for team in bootstrap_data['teams']}

            fixture_data = []
            for fixture in fixtures[:15]:
                home_team = teams_lookup.get(fixture.team_h, 'Unknown')
                away_team = teams_lookup.get(fixture.team_a, 'Unknown')

                fixture_data.append({
                    'Gameweek': fixture.gameweek,
                    'Fixture': f"{home_team} vs {away_team}",
                    'Home Difficulty': fixture.team_h_difficulty,
                    'Away Difficulty': fixture.team_a_difficulty,
                    'Kickoff': fixture.kickoff_time
                })

            if fixture_data:
                df_fixtures = pd.DataFrame(fixture_data)
                st.dataframe(df_fixtures, use_container_width=True)

        except Exception as e:
            st.error(f"Error displaying fixtures: {str(e)}")

    with tab3:
        st.subheader("Form Analysis")
        # Add form trends visualization here
        st.info("Form analysis visualization - coming soon!")

    with tab4:
        st.subheader("Value Analysis")
        # Add value for money analysis here
        st.info("Value analysis - coming soon!")


def main():
    """Main Streamlit application"""
    initialize_session_state()

    # Header
    st.markdown('<h1 class="main-header">⚽ FPL Captain Recommender</h1>', unsafe_allow_html=True)
    st.markdown("Get AI-powered captain recommendations for your Fantasy Premier League team")

    # Sidebar configuration
    api_key, selected_model, gameweeks_ahead, temperature = setup_sidebar()

    # Main content area
    col1, col2 = st.columns([2, 1])

    with col1:
        # Team ID input
        team_id = st.number_input(
            "Enter your FPL Team ID",
            min_value=1,
            max_value=10000000,
            value=1,
            help="You can find your team ID in the URL when viewing your team on the FPL website"
        )

        # Initialize recommender button
        if st.button("🚀 Initialize Recommender", type="primary"):
            with st.spinner("Initializing recommender..."):
                success, message = initialize_recommender(api_key, selected_model, temperature)
                if success:
                    st.success(message)
                else:
                    st.error(message)

    with col2:
        st.markdown("### ℹ️ How to find your Team ID")
        st.markdown("""
        1. Go to the FPL website
        2. Navigate to your team
        3. Look at the URL: `fantasy.premierleague.com/entry/[YOUR_ID]/`
        4. Copy the number from the URL
        """)

    # Get recommendations button
    if st.session_state.recommender and st.button("🎯 Get Captain Recommendations", type="secondary"):
        with st.spinner("Fetching team data and generating recommendations..."):
            try:
                # Progress bar
                progress_bar = st.progress(0)
                progress_bar.progress(25, text="Fetching team data...")

                # Get recommendations
                recommendations = st.session_state.recommender.get_captain_recommendations(team_id)
                progress_bar.progress(75, text="Analyzing data...")

                # Get team data for additional analysis
                team_data = st.session_state.recommender.fetch_fpl_team_data(team_id)

                progress_bar.progress(100, text="Complete!")
                time.sleep(0.5)
                progress_bar.empty()

                # Store in session state
                st.session_state.recommendations = recommendations
                st.session_state.team_data = team_data

                if 'error' in recommendations:
                    st.error(f"Error: {recommendations['error']}")
                else:
                    st.success("Recommendations generated successfully!")

            except Exception as e:
                st.error(f"Error getting recommendations: {str(e)}")

    # Display results if available
    if st.session_state.recommendations and 'recommendations' in st.session_state.recommendations:

        # Team overview
        st.markdown("## 📋 Team Overview")
        display_team_overview(st.session_state.team_data, st.session_state.recommender)

        # Recommendations
        display_recommendations(st.session_state.recommendations)

        # Player performance charts
        st.markdown("## 📊 Team Analysis")
        create_player_performance_chart(st.session_state.team_data, st.session_state.recommender)

        # Detailed analysis
        display_detailed_analysis(
            st.session_state.recommendations,
            st.session_state.team_data,
            st.session_state.recommender
        )

        # Export options
        st.markdown("## 📥 Export")
        col1, col2 = st.columns(2)

        with col1:
            if st.button("📋 Copy Recommendations"):
                recommendations_text = ""
                for rec in st.session_state.recommendations['recommendations']:
                    recommendations_text += f"{rec['rank']}. {rec['player_name']} - {rec['reasoning']}\n"
                st.text_area("Copy this text:", recommendations_text, height=200)

        with col2:
            # Download as JSON
            json_data = json.dumps(st.session_state.recommendations, indent=2)
            st.download_button(
                label="💾 Download as JSON",
                data=json_data,
                file_name=f"fpl_recommendations_{team_id}_{datetime.now().strftime('%Y%m%d_%H%M')}.json",
                mime="application/json"
            )

    # Footer
    st.markdown("---")
    st.markdown("Built with ❤️ using Streamlit and LangChain | Data from Fantasy Premier League API")


if __name__ == "__main__":
    main()