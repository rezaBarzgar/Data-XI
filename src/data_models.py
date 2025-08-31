from datetime import date
from datetime import datetime
from typing import Dict, Any, List
from typing import Optional

from pydantic import BaseModel, Field, ConfigDict


class Overrides(BaseModel):
    rules: Dict[str, Any] = Field(default_factory=dict)
    scoring: Dict[str, Any] = Field(default_factory=dict)
    element_types: List[Any] = Field(default_factory=list)
    pick_multiplier: Optional[int] = None


class Chip(BaseModel):
    id: int
    name: str
    number: int
    start_event: int
    stop_event: int
    chip_type: str
    overrides: Overrides = Field(default_factory=Overrides)


class ChipPlay(BaseModel):
    chip_name: str
    num_played: int


class TopElementInfo(BaseModel):
    id: int
    points: int


class Gameweek(BaseModel):
    id: int
    name: str
    deadline_time: datetime
    release_time: Optional[datetime] = None
    average_entry_score: int
    finished: bool
    data_checked: bool
    highest_scoring_entry: Optional[int] = None
    deadline_time_epoch: int
    deadline_time_game_offset: int
    highest_score: Optional[int] = None
    is_previous: bool
    is_current: bool
    is_next: bool
    cup_leagues_created: bool
    h2h_ko_matches_created: bool
    can_enter: bool
    can_manage: bool
    released: bool
    ranked_count: int
    overrides: Overrides
    chip_plays: List[ChipPlay] = Field(default_factory=list)
    most_selected: Optional[int] = None
    most_transferred_in: Optional[int] = None
    top_element: Optional[int] = None
    top_element_info: Optional[TopElementInfo] = None
    transfers_made: int
    most_captained: Optional[int] = None
    most_vice_captained: Optional[int] = None


class GameSettings(BaseModel):
    league_join_private_max: int
    league_join_public_max: int
    league_max_size_public_classic: int
    league_max_size_public_h2h: int
    league_max_size_private_h2h: int
    league_max_ko_rounds_private_h2h: int
    league_prefix_public: str
    league_points_h2h_win: int
    league_points_h2h_lose: int
    league_points_h2h_draw: int
    league_ko_first_instead_of_random: bool
    cup_start_event_id: Optional[int] = None
    cup_stop_event_id: Optional[int] = None
    cup_qualifying_method: Optional[str] = None
    cup_type: Optional[str] = None
    featured_entries: List[Any] = Field(default_factory=list)
    element_sell_at_purchase_price: bool
    percentile_ranks: List[int]
    underdog_differential: int
    squad_squadplay: int
    squad_squadsize: int
    squad_special_min: Optional[int] = None
    squad_special_max: Optional[int] = None
    squad_team_limit: int
    squad_total_spend: int
    ui_currency_multiplier: int
    ui_use_special_shirts: bool
    ui_special_shirt_exclusions: List[Any] = Field(default_factory=list)
    stats_form_days: int
    sys_vice_captain_enabled: bool
    transfers_cap: int
    transfers_sell_on_fee: float
    max_extra_free_transfers: int
    league_h2h_tiebreak_stats: List[str]
    timezone: str


class Team(BaseModel):
    code: int
    draw: int
    form: Optional[str] = None
    id: int
    loss: int
    name: str
    played: int
    points: int
    position: int
    short_name: str
    strength: int
    team_division: Optional[int] = None
    unavailable: bool
    win: int
    strength_overall_home: int
    strength_overall_away: int
    strength_attack_home: int
    strength_attack_away: int
    strength_defence_home: int
    strength_defence_away: int
    pulse_id: int


class TotalPlayers(BaseModel):
    total_players: int


class Player(BaseModel):
    can_transact: bool
    can_select: bool
    chance_of_playing_next_round: Optional[int] = None
    chance_of_playing_this_round: Optional[int] = None
    code: int
    cost_change_event: int
    cost_change_event_fall: int
    cost_change_start: int
    cost_change_start_fall: int
    dreamteam_count: int
    element_type: int
    ep_next: str
    ep_this: str
    event_points: int
    first_name: str
    form: str
    id: int
    in_dreamteam: bool
    news: str
    news_added: Optional[str] = None
    now_cost: int
    photo: str
    points_per_game: str
    removed: bool
    second_name: str
    selected_by_percent: str
    special: bool
    squad_number: Optional[int] = None
    status: str
    team: int
    team_code: int
    total_points: int
    transfers_in: int
    transfers_in_event: int
    transfers_out: int
    transfers_out_event: int
    value_form: str
    value_season: str
    web_name: str
    region: int
    team_join_date: Optional[date] = None
    birth_date: Optional[date] = None
    has_temporary_code: bool
    opta_code: str
    minutes: int
    goals_scored: int
    assists: int
    clean_sheets: int
    goals_conceded: int
    own_goals: int
    penalties_saved: int
    penalties_missed: int
    yellow_cards: int
    red_cards: int
    saves: int
    bonus: int
    bps: int
    influence: str
    creativity: str
    threat: str
    ict_index: str
    clearances_blocks_interceptions: int
    recoveries: int
    tackles: int
    defensive_contribution: int
    starts: int
    expected_goals: str
    expected_assists: str
    expected_goal_involvements: str
    expected_goals_conceded: str
    influence_rank: int
    influence_rank_type: int
    creativity_rank: int
    creativity_rank_type: int
    threat_rank: int
    threat_rank_type: int
    ict_index_rank: int
    ict_index_rank_type: int
    corners_and_indirect_freekicks_order: Optional[int] = None
    corners_and_indirect_freekicks_text: str
    direct_freekicks_order: Optional[int] = None
    direct_freekicks_text: str
    penalties_order: Optional[int] = None
    penalties_text: str
    expected_goals_per_90: float
    saves_per_90: float
    expected_assists_per_90: float
    expected_goal_involvements_per_90: float
    expected_goals_conceded_per_90: float
    goals_conceded_per_90: float
    now_cost_rank: int
    now_cost_rank_type: int
    form_rank: int
    form_rank_type: int
    points_per_game_rank: int
    points_per_game_rank_type: int
    selected_rank: int
    selected_rank_type: int
    starts_per_90: float
    clean_sheets_per_90: float
    defensive_contribution_per_90: float


class Player(BaseModel):
    can_transact: bool
    can_select: bool
    chance_of_playing_next_round: Optional[int] = None
    chance_of_playing_this_round: Optional[int] = None
    code: int
    cost_change_event: int
    cost_change_event_fall: int
    cost_change_start: int
    cost_change_start_fall: int
    dreamteam_count: int
    element_type: int
    ep_next: str
    ep_this: str
    event_points: int
    first_name: str
    form: str
    id: int
    in_dreamteam: bool
    news: str
    news_added: Optional[str] = None
    now_cost: int
    photo: str
    points_per_game: str
    removed: bool
    second_name: str
    selected_by_percent: str
    special: bool
    squad_number: Optional[int] = None
    status: str
    team: int
    team_code: int
    total_points: int
    transfers_in: int
    transfers_in_event: int
    transfers_out: int
    transfers_out_event: int
    value_form: str
    value_season: str
    web_name: str
    region: int
    team_join_date: Optional[date] = None
    birth_date: Optional[date] = None
    has_temporary_code: bool
    opta_code: str
    minutes: int
    goals_scored: int
    assists: int
    clean_sheets: int
    goals_conceded: int
    own_goals: int
    penalties_saved: int
    penalties_missed: int
    yellow_cards: int
    red_cards: int
    saves: int
    bonus: int
    bps: int
    influence: str
    creativity: str
    threat: str
    ict_index: str
    clearances_blocks_interceptions: int
    recoveries: int
    tackles: int
    defensive_contribution: int
    starts: int
    expected_goals: str
    expected_assists: str
    expected_goal_involvements: str
    expected_goals_conceded: str
    influence_rank: int
    influence_rank_type: int
    creativity_rank: int
    creativity_rank_type: int
    threat_rank: int
    threat_rank_type: int
    ict_index_rank: int
    ict_index_rank_type: int
    corners_and_indirect_freekicks_order: Optional[int] = None
    corners_and_indirect_freekicks_text: str
    direct_freekicks_order: Optional[int] = None
    direct_freekicks_text: str
    penalties_order: Optional[int] = None
    penalties_text: str
    expected_goals_per_90: float
    saves_per_90: float
    expected_assists_per_90: float
    expected_goal_involvements_per_90: float
    expected_goals_conceded_per_90: float
    goals_conceded_per_90: float
    now_cost_rank: int
    now_cost_rank_type: int
    form_rank: int
    form_rank_type: int
    points_per_game_rank: int
    points_per_game_rank_type: int
    selected_rank: int
    selected_rank_type: int
    starts_per_90: float
    clean_sheets_per_90: float
    defensive_contribution_per_90: float


class StatEntry(BaseModel):
    value: int
    element: int


class Stat(BaseModel):
    identifier: str
    a: List[StatEntry]
    h: List[StatEntry]


class Match(BaseModel):
    code: int
    event: int
    finished: bool
    finished_provisional: bool
    id: int
    kickoff_time: datetime
    minutes: int
    provisional_start_time: bool
    started: bool
    team_a: int
    team_a_score: int
    team_h: int
    team_h_score: int
    stats: List[Stat]
    team_h_difficulty: int
    team_a_difficulty: int
    pulse_id: int


class PlayerFixture(BaseModel):
    id: int
    code: int
    team_h: int
    team_h_score: Optional[int] = None
    team_a: int
    team_a_score: Optional[int] = None
    event: int
    finished: bool
    minutes: int
    provisional_start_time: bool
    kickoff_time: datetime
    event_name: str
    is_home: bool
    difficulty: int


class PlayerHistoryEntry(BaseModel):
    element: int
    fixture: int
    opponent_team: int
    total_points: int
    was_home: bool
    kickoff_time: datetime
    team_h_score: int
    team_a_score: int
    round: int
    modified: bool
    minutes: int
    goals_scored: int
    assists: int
    clean_sheets: int
    goals_conceded: int
    own_goals: int
    penalties_saved: int
    penalties_missed: int
    yellow_cards: int
    red_cards: int
    saves: int
    bonus: int
    bps: int
    influence: str
    creativity: str
    threat: str
    ict_index: str
    clearances_blocks_interceptions: int
    recoveries: int
    tackles: int
    defensive_contribution: int
    starts: int
    expected_goals: str
    expected_assists: str
    expected_goal_involvements: str
    expected_goals_conceded: str
    value: int
    transfers_balance: int
    selected: int
    transfers_in: int
    transfers_out: int


class PlayerPastHistory(BaseModel):
    season_name: str
    element_code: int
    start_cost: int
    end_cost: int
    total_points: int
    minutes: int
    goals_scored: int
    assists: int
    clean_sheets: int
    goals_conceded: int
    own_goals: int
    penalties_saved: int
    penalties_missed: int
    yellow_cards: int
    red_cards: int
    saves: int
    bonus: int
    bps: int
    influence: str
    creativity: str
    threat: str
    ict_index: str
    clearances_blocks_interceptions: int
    recoveries: int
    tackles: int
    defensive_contribution: int
    starts: int
    expected_goals: str
    expected_assists: str
    expected_goal_involvements: str
    expected_goals_conceded: str


class PlayerSummary(BaseModel):
    fixtures: List[PlayerFixture]
    history: List[PlayerHistoryEntry]
    past_history: List[PlayerPastHistory]


class _AllowExtras(BaseModel):
    model_config = ConfigDict(extra="allow")


class LiveStats(_AllowExtras):
    minutes: int
    goals_scored: int
    assists: int
    clean_sheets: int
    goals_conceded: int
    own_goals: int
    penalties_saved: int
    penalties_missed: int
    yellow_cards: int
    red_cards: int
    saves: int
    bonus: int
    bps: int
    total_points: int
    in_dreamteam: bool
    influence: float
    creativity: float
    threat: float
    ict_index: float


class ExplainBreakdown(_AllowExtras):
    identifier: str
    points: int
    value: int


class ExplainFixture(_AllowExtras):
    fixture: int
    stats: List[ExplainBreakdown]


class LiveElement(_AllowExtras):
    id: int
    stats: LiveStats
    explain: List[ExplainFixture]


class EventLive(_AllowExtras):
    elements: List[LiveElement]


class ActivePhase(BaseModel):
    phase: int
    rank: int
    last_rank: int
    rank_sort: int
    total: int
    league_id: int
    rank_count: int
    entry_percentile_rank: int


class ClassicLeague(BaseModel):
    id: int
    name: str
    short_name: str
    created: datetime
    closed: bool
    rank: Optional[int] = None
    max_entries: Optional[int] = None
    league_type: str
    scoring: str
    admin_entry: Optional[int] = None
    start_event: int
    entry_can_leave: bool
    entry_can_admin: bool
    entry_can_invite: bool
    has_cup: bool
    cup_league: Optional[int] = None
    cup_qualified: Optional[bool] = None
    rank_count: int
    entry_percentile_rank: int
    active_phases: List[ActivePhase]
    entry_rank: int
    entry_last_rank: int


class CupStatus(BaseModel):
    qualification_event: Optional[int] = None
    qualification_numbers: Optional[int] = None
    qualification_rank: Optional[int] = None
    qualification_state: Optional[str] = None


class Cup(BaseModel):
    matches: List[Any] = Field(default_factory=list)
    status: CupStatus
    cup_league: Optional[int] = None


class Leagues(BaseModel):
    classic: List[ClassicLeague] = Field(default_factory=list)
    h2h: List[Any] = Field(default_factory=list)
    cup: Cup
    cup_matches: List[Any] = Field(default_factory=list)


class Manager(BaseModel):
    id: int
    joined_time: datetime
    started_event: int
    favourite_team: int
    player_first_name: str
    player_last_name: str
    player_region_id: int
    player_region_name: str
    player_region_iso_code_short: str
    player_region_iso_code_long: str
    years_active: int
    summary_overall_points: int
    summary_overall_rank: int
    summary_event_points: int
    summary_event_rank: int
    current_event: int
    leagues: Leagues
    name: str
    name_change_blocked: bool
    entered_events: List[int]
    kit: Optional[str] = None
    last_deadline_bank: int
    last_deadline_value: int
    last_deadline_total_transfers: int
    club_badge_src: Optional[str] = None


class ManagerHistoryCurrent(BaseModel):
    event: int
    points: int
    total_points: int
    rank: int
    rank_sort: int
    overall_rank: int
    percentile_rank: int
    bank: int
    value: int
    event_transfers: int
    event_transfers_cost: int
    points_on_bench: int


class ManagerHistoryPast(BaseModel):
    season_name: str
    total_points: int
    rank: int


class ManagerHistoryChip(BaseModel):
    name: str
    time: datetime
    event: int


class ManagerHistory(BaseModel):
    current: List[ManagerHistoryCurrent]
    past: List[ManagerHistoryPast]
    chips: List[ManagerHistoryChip]


class Transfer(BaseModel):
    element_in: int
    element_in_cost: int
    element_out: int
    element_out_cost: int
    entry: int
    event: int
    time: datetime


class Transfers(BaseModel):
    transfers: List[Transfer]


class LeagueStandingEntry(BaseModel):
    id: int
    event_total: int
    player_name: str
    rank: int
    last_rank: int
    rank_sort: int
    total: int
    entry: int
    entry_name: str
    has_played: bool


class LeagueStandings(BaseModel):
    has_next: bool
    page: int
    results: List[LeagueStandingEntry]


# TODO pydantic class for -> Manager Team, Manager Data, Event Status, MVP Teams, Best Leagues