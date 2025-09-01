import requests
import json
import os
from dotenv import load_dotenv
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_openai import ChatOpenAI  # or your preferred LLM
import time

load_dotenv()

@dataclass
class PlayerData:
    """Data class for player information"""
    id: int
    name: str
    team: str
    position: str
    price: float
    total_points: int
    form: float
    points_per_game: float
    selected_by_percent: float
    goals_scored: int
    assists: int
    clean_sheets: int
    minutes: int
    bonus: int
    now_cost: int


@dataclass
class FixtureData:
    """Data class for fixture information"""
    team_h: int
    team_a: int
    team_h_difficulty: int
    team_a_difficulty: int
    kickoff_time: str
    gameweek: int


class FPLCaptainRecommender:
    def __init__(self, llm_model="gpt-5-nano", openai_api_key=None):
        self.base_url = "https://fantasy.premierleague.com/api"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })

        # Get API key from environment or parameter
        api_key = openai_api_key or os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError(
                "OpenAI API key not found. Please set the OPENAI_API_KEY environment variable "
                "or pass it as openai_api_key parameter."
            )

        # Initialize LangChain components
        self.llm = ChatOpenAI(
            model=llm_model,
            openai_api_key=api_key
        )
        self.output_parser = JsonOutputParser()

        # Cache for API data
        self._bootstrap_cache = None
        self._fixtures_cache = None
        self._teams_cache = None

    def fetch_fpl_bootstrap_data(self) -> Dict[str, Any]:
        """Fetch main FPL bootstrap data (players, teams, gameweeks)"""
        if self._bootstrap_cache:
            return self._bootstrap_cache

        try:
            response = self.session.get(f"{self.base_url}/bootstrap-static/")
            response.raise_for_status()
            self._bootstrap_cache = response.json()
            return self._bootstrap_cache
        except requests.RequestException as e:
            raise Exception(f"Failed to fetch bootstrap data: {e}")

    def fetch_fpl_team_data(self, team_id: int) -> Dict[str, Any]:
        """Fetch specific team data including picks"""
        try:
            response = self.session.get(f"{self.base_url}/entry/{team_id}/")
            response.raise_for_status()
            team_info = response.json()

            # Get current picks
            current_gw = self.get_current_gameweek()
            picks_response = self.session.get(f"{self.base_url}/entry/{team_id}/event/{current_gw}/picks/")
            picks_response.raise_for_status()
            picks_data = picks_response.json()

            return {
                'team_info': team_info,
                'picks': picks_data.get('picks', []),
                'active_chip': picks_data.get('active_chip'),
                'automatic_subs': picks_data.get('automatic_subs', [])
            }
        except requests.RequestException as e:
            raise Exception(f"Failed to fetch team data for ID {team_id}: {e}")

    def get_current_gameweek(self) -> int:
        """Get current active gameweek"""
        bootstrap_data = self.fetch_fpl_bootstrap_data()
        events = bootstrap_data.get('events', [])

        for event in events:
            if event.get('is_current'):
                return event['id']

        # Fallback: find next gameweek
        for event in events:
            if event.get('is_next'):
                return event['id']

        return 1  # Default fallback

    def get_upcoming_fixtures(self, gameweeks: int = 3) -> List[FixtureData]:
        """Get upcoming fixtures for next few gameweeks"""
        if self._fixtures_cache:
            return self._fixtures_cache

        try:
            response = self.session.get(f"{self.base_url}/fixtures/")
            response.raise_for_status()
            fixtures_data = response.json()

            current_gw = self.get_current_gameweek()
            upcoming_fixtures = []

            for fixture in fixtures_data:
                if (fixture.get('event') and
                        current_gw <= fixture['event'] <= current_gw + gameweeks - 1 and
                        not fixture.get('finished')):
                    upcoming_fixtures.append(FixtureData(
                        team_h=fixture['team_h'],
                        team_a=fixture['team_a'],
                        team_h_difficulty=fixture['team_h_difficulty'],
                        team_a_difficulty=fixture['team_a_difficulty'],
                        kickoff_time=fixture['kickoff_time'],
                        gameweek=fixture['event']
                    ))

            self._fixtures_cache = upcoming_fixtures
            return upcoming_fixtures
        except requests.RequestException as e:
            raise Exception(f"Failed to fetch fixtures: {e}")

    def get_player_performance_data(self, player_ids: List[int]) -> Dict[int, PlayerData]:
        """Get detailed performance data for specific players"""
        bootstrap_data = self.fetch_fpl_bootstrap_data()
        players_data = bootstrap_data.get('elements', [])
        teams_data = bootstrap_data.get('teams', [])
        positions_data = bootstrap_data.get('element_types', [])

        # Create lookup dictionaries
        teams_lookup = {team['id']: team['name'] for team in teams_data}
        positions_lookup = {pos['id']: pos['singular_name'] for pos in positions_data}

        player_performance = {}

        for player in players_data:
            if player['id'] in player_ids:
                player_performance[player['id']] = PlayerData(
                    id=player['id'],
                    name=f"{player['first_name']} {player['second_name']}",
                    team=teams_lookup.get(player['team'], 'Unknown'),
                    position=positions_lookup.get(player['element_type'], 'Unknown'),
                    price=player['now_cost'] / 10.0,  # Convert from FPL format
                    total_points=player['total_points'],
                    form=float(player['form']),
                    points_per_game=float(player['points_per_game']),
                    selected_by_percent=float(player['selected_by_percent']),
                    goals_scored=player['goals_scored'],
                    assists=player['assists'],
                    clean_sheets=player['clean_sheets'],
                    minutes=player['minutes'],
                    bonus=player['bonus'],
                    now_cost=player['now_cost']
                )

        return player_performance

    def get_injury_updates(self, player_ids: List[int]) -> Dict[int, str]:
        """Get injury/availability status for players"""
        bootstrap_data = self.fetch_fpl_bootstrap_data()
        players_data = bootstrap_data.get('elements', [])

        injury_status = {}

        for player in players_data:
            if player['id'] in player_ids:
                status = []
                if player.get('chance_of_playing_next_round') is not None:
                    if player['chance_of_playing_next_round'] < 100:
                        status.append(f"Injury risk: {player['chance_of_playing_next_round']}%")

                if player.get('news'):
                    status.append(player['news'])

                injury_status[player['id']] = '; '.join(status) if status else 'Available'

        return injury_status

    def get_ownership_stats(self, player_ids: List[int]) -> Dict[int, Dict[str, float]]:
        """Get ownership statistics for players"""
        bootstrap_data = self.fetch_fpl_bootstrap_data()
        players_data = bootstrap_data.get('elements', [])

        ownership_data = {}

        for player in players_data:
            if player['id'] in player_ids:
                ownership_data[player['id']] = {
                    'selected_by_percent': float(player['selected_by_percent']),
                    'transfers_in_event': player.get('transfers_in_event', 0),
                    'transfers_out_event': player.get('transfers_out_event', 0),
                    'cost_change_event': player.get('cost_change_event', 0)
                }

        return ownership_data

    def get_team_fixture_difficulty(self, team_id: int, gameweeks: int = 3) -> List[int]:
        """Get fixture difficulty for a team over next few gameweeks"""
        fixtures = self.get_upcoming_fixtures(gameweeks)
        bootstrap_data = self.fetch_fpl_bootstrap_data()
        teams = {team['id']: team for team in bootstrap_data.get('teams', [])}

        difficulties = []

        for fixture in fixtures:
            if fixture.team_h == team_id:
                difficulties.append(fixture.team_h_difficulty)
            elif fixture.team_a == team_id:
                difficulties.append(fixture.team_a_difficulty)

        return difficulties

    def format_captain_prompt(self, context: Dict[str, Any]) -> str:
        """Format the context data into a comprehensive prompt"""

        prompt_template = """
You are an expert Fantasy Premier League analyst. Your task is to recommend 3 different captain choices for the given team, ranking them from best to worst with detailed reasoning.

CURRENT GAMEWEEK: {current_gameweek}

AVAILABLE CAPTAIN OPTIONS:
{player_details}

UPCOMING FIXTURES (next 3 gameweeks):
{fixture_analysis}

INJURY/AVAILABILITY NEWS:
{injury_news}

OWNERSHIP DATA:
{ownership_info}

Please analyze and provide exactly 3 captain recommendations in the following JSON format:
{{
    "recommendations": [
        {{
            "rank": 1,
            "player_name": "Player Name",
            "player_id": 123,
            "reasoning": "Detailed explanation of why this is the best choice",
            "key_factors": ["factor1", "factor2", "factor3"],
            "risk_level": "Low/Medium/High",
            "differential_potential": "Template/Semi-differential/High differential"
        }},
        {{
            "rank": 2,
            "player_name": "Player Name", 
            "player_id": 456,
            "reasoning": "Detailed explanation",
            "key_factors": ["factor1", "factor2"],
            "risk_level": "Low/Medium/High",
            "differential_potential": "Template/Semi-differential/High differential"
        }},
        {{
            "rank": 3,
            "player_name": "Player Name",
            "player_id": 789, 
            "reasoning": "Detailed explanation",
            "key_factors": ["factor1", "factor2"],
            "risk_level": "Low/Medium/High",
            "differential_potential": "Template/Semi-differential/High differential"
        }}
    ],
    "general_advice": "Overall strategy considerations for this gameweek"
}}

Consider these factors in your analysis:
1. Recent form and consistency
2. Fixture difficulty and matchup analysis  
3. Injury/rotation risks
4. Ownership levels and differential potential
5. Historical performance vs upcoming opponents
6. Price and value considerations
7. Team motivation and context

Focus on players who are likely to start and have good scoring potential.
"""

        return prompt_template.format(**context)

    def get_captain_recommendations(self, team_id: int) -> Dict[str, Any]:
        """Main function to get captain recommendations"""
        try:
            print(f"Fetching data for team {team_id}...")

            # Fetch team data
            team_data = self.fetch_fpl_team_data(team_id)

            # Get current gameweek info
            current_gw = self.get_current_gameweek()

            # Extract player IDs from team picks
            player_ids = [pick['element'] for pick in team_data['picks']]

            print(f"Getting performance data for {len(player_ids)} players...")

            # Get detailed player data
            player_stats = self.get_player_performance_data(player_ids)
            injury_news = self.get_injury_updates(player_ids)
            ownership_data = self.get_ownership_stats(player_ids)
            fixtures = self.get_upcoming_fixtures()

            # Format player details for prompt
            player_details = []
            for player_id, player in player_stats.items():
                pick_data = next((p for p in team_data['picks'] if p['element'] == player_id), {})
                is_captain_eligible = pick_data.get('multiplier', 1) >= 1  # Not benched

                if is_captain_eligible:
                    # Get team fixture difficulties
                    team_id_for_player = next((team['id'] for team in self.fetch_fpl_bootstrap_data()['teams']
                                               if team['name'] == player.team), 0)
                    fixture_difficulties = self.get_team_fixture_difficulty(team_id_for_player)

                    player_detail = f"""
- {player.name} ({player.team}) - {player.position}
  * Price: £{player.price}m | Total Points: {player.total_points} | Form: {player.form}
  * PPG: {player.points_per_game} | Goals: {player.goals_scored} | Assists: {player.assists}
  * Ownership: {player.selected_by_percent}% | Minutes: {player.minutes}
  * Fixture Difficulty (next 3): {fixture_difficulties}
  * Status: {injury_news.get(player_id, 'Available')}
"""
                    player_details.append(player_detail)

            # Format fixtures for context
            fixture_analysis = []
            bootstrap_data = self.fetch_fpl_bootstrap_data()
            teams_lookup = {team['id']: team['short_name'] for team in bootstrap_data['teams']}

            for fixture in fixtures[:15]:  # Show next 15 fixtures
                home_team = teams_lookup.get(fixture.team_h, 'UNK')
                away_team = teams_lookup.get(fixture.team_a, 'UNK')
                fixture_analysis.append(
                    f"GW{fixture.gameweek}: {home_team} vs {away_team} "
                    f"(Difficulty: {fixture.team_h_difficulty}-{fixture.team_a_difficulty})"
                )

            # Compile context for prompt
            context = {
                'current_gameweek': current_gw,
                'player_details': '\n'.join(player_details),
                'fixture_analysis': '\n'.join(fixture_analysis),
                'injury_news': '\n'.join([f"- {player_stats[pid].name}: {status}"
                                          for pid, status in injury_news.items() if status != 'Available']),
                'ownership_info': '\n'.join([f"- {player_stats[pid].name}: {data['selected_by_percent']}% owned, "
                                             f"Transfers: +{data['transfers_in_event']} -{data['transfers_out_event']}"
                                             for pid, data in ownership_data.items()])
            }

            # Format prompt
            prompt = self.format_captain_prompt(context)

            print("Calling LLM for recommendations...")

            # Call LLM
            response = self.llm.invoke(prompt)

            try:
                recommendations = json.loads(response.content)
                return recommendations
            except json.JSONDecodeError:
                # Fallback: try to extract JSON from response
                import re
                json_match = re.search(r'\{.*\}', response.content, re.DOTALL)
                if json_match:
                    return json.loads(json_match.group())
                else:
                    return {
                        "error": "Failed to parse LLM response",
                        "raw_response": response.content
                    }

        except Exception as e:
            return {
                "error": f"Error getting recommendations: {str(e)}",
                "team_id": team_id
            }


# Example usage
def main():
    # Initialize the recommender (API key will be loaded from environment)
    try:
        recommender = FPLCaptainRecommender()
    except ValueError as e:
        print(f"Configuration Error: {e}")
        return

    # Example team ID (replace with actual team ID)
    team_id = 4213233  # Replace with a valid FPL team ID

    try:
        recommendations = recommender.get_captain_recommendations(team_id)

        if "error" in recommendations:
            print(f"Error: {recommendations['error']}")
        else:
            print("=== CAPTAIN RECOMMENDATIONS ===\n")

            for rec in recommendations.get('recommendations', []):
                print(f"{rec['rank']}. {rec['player_name']}")
                print(f"   Risk Level: {rec['risk_level']}")
                print(f"   Differential: {rec['differential_potential']}")
                print(f"   Reasoning: {rec['reasoning']}")
                print(f"   Key Factors: {', '.join(rec['key_factors'])}")
                print()

            if 'general_advice' in recommendations:
                print(f"General Advice: {recommendations['general_advice']}")

    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()