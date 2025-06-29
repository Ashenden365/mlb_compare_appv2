# -*- coding: utf-8 -*-
"""
MLB Home Run Pace Tracker — dynamic roster version (Streamlit)
=============================================================
*   自動で最新ロスターを取得（MLB-StatsAPI）。
*   Statcast HRログに東京シリーズ例外ロジックを適用。
*   Streamlit でインタラクティブ比較表示。

起動方法:
    streamlit run app.py

依存ライブラリ (requirements.txt):
    streamlit
    pandas
    altair
    pybaseball
    MLB-StatsAPI
"""

# ------------------------------------------------------------------
# Imports
# ------------------------------------------------------------------
import streamlit as st
import pandas as pd
import altair as alt
from datetime import datetime, date

import statsapi
from pybaseball import playerid_reverse_lookup, statcast_batter

# ------------------------------------------------------------------
# Constants
# ------------------------------------------------------------------
TOKYO_START   = datetime(2025, 3, 18)
TOKYO_2       = datetime(2025, 3, 19)
REGULAR_START = datetime(2025, 3, 27)

ROYAL_BLUE = "#1E90FF"
ORANGE     = "#FF8000"

st.set_page_config(layout="wide",
                   page_title="MLB 2025 Home Run Pace Tracker")
st.title("MLB Home Run Pace Comparison — 2025 Season (Dynamic Rosters)")

# ------------------------------------------------------------------
# Build latest roster list (cached)
# ------------------------------------------------------------------
@st.cache_data(ttl=12 * 60 * 60)  # 12h キャッシュ
def build_star_players():
    teams_raw = statsapi.get('teams', {'sportIds': 1})['teams']
    active_teams = [t for t in teams_raw if t['active']]

    stars = []
    for team in active_teams:
        data = statsapi.get('team_roster', {
            'teamId': team['id'],
            'rosterType': 'active'
        })
        for player in data.get('roster', []):
            person = player.get('person', {})
            name   = person.get('fullName')
            pid    = person.get('id')
            if name and pid:
                stars.append((name, pid, team['abbreviation']))
    return stars

star_players = build_star_players()
teams        = sorted({t for _, _, t in star_players})
player_map   = {name: (pid, team) for name, pid, team in star_players}

# デフォルト指定
DEFAULT_PLAYER1 = "Shohei Ohtani"
DEFAULT_TEAM1 = "LAD"
DEFAULT_PLAYER2 = "Aaron Judge"
DEFAULT_TEAM2 = "NYY"

# ------------------------------------------------------------------
# Helper functions
# ------------------------------------------------------------------
def get_player_image(pid: int) -> str:
    return (f"https://img.mlbstatic.com/mlb-photos/image/upload/"
            f"w_180,q_100/v1/people/{pid}/headshot/67/current.png")

def fetch_hr_log(pid: int,
                 start: datetime,
                 end: datetime,
                 team_abbr: str) -> pd.DataFrame:
    df = statcast_batter(start_dt=start.strftime('%Y-%m-%d'),
                         end_dt=end.strftime('%Y-%m-%d'),
                         player_id=str(pid))
    if df.empty:
        return df

    df['Date'] = pd.to_datetime(df['game_date'])
    tokyo_days = [TOKYO_START, TOKYO_2]
    if team_abbr in {'LAD', 'CHC'}:
        mask = df['Date'].isin(tokyo_days) | (df['Date'] >= REGULAR_START)
    else:
        mask = df['Date'] >= REGULAR_START
    df = df.loc[mask]

    df_hr = (df[df['events'] == 'home_run']
             .copy()
             .sort_values('Date')
             .reset_index(drop=True))

    if df_hr.empty:
        return df_hr

    df_hr['HR No'] = df_hr.index + 1
    df_hr['MM-DD'] = df_hr['Date'].dt.strftime('%m-%d')

    def pid2name(p):
        try:
            t = playerid_reverse_lookup([p], key_type='mlbam')
            return t['name_first'][0] + ' ' + t['name_last'][0]
        except Exception:
            return str(p)
    df_hr['Pitcher'] = df_hr['pitcher'].apply(
        lambda x: pid2name(x) if pd.notna(x) else '')

    return df_hr

# ------------------------------------------------------------------
# Sidebar UI
# ------------------------------------------------------------------
st.sidebar.header("Select Players and Date Range")

today = date.today()
start_date = st.sidebar.date_input("Start date", TOKYO_START)
end_date   = st.sidebar.date_input("End date", today)

team1_default_idx = teams.index(DEFAULT_TEAM1) if DEFAULT_TEAM1 in teams else 0
team2_default_idx = teams.index(DEFAULT_TEAM2) if DEFAULT_TEAM2 in teams else 1
team1_abbr = st.sidebar.selectbox(
    "First Player's Team", teams,
    index=team1_default_idx)
team2_abbr = st.sidebar.selectbox(
    "Second Player's Team", teams,
    index=team2_default_idx)

team1_players = [n for n, _, t in star_players if t == team1_abbr]
team2_players = [n for n, _, t in star_players if t == team2_abbr]

player1_default_idx = team1_players.index(DEFAULT_PLAYER1) if DEFAULT_PLAYER1 in team1_players else 0
player2_default_idx = team2_players.index(DEFAULT_PLAYER2) if DEFAULT_PLAYER2 in team2_players else 0
player1_name = st.sidebar.selectbox("First Player", team1_players, index=player1_default_idx)
player2_name = st.sidebar.selectbox("Second Player", team2_players, index=player2_default_idx)

p1_id, team1_code = player_map[player1_name]
p2_id, team2_code = player_map[player2_name]

for name, code in [(player1_name, team1_code),
                   (player2_name, team2_code)]:
    if code not in {'LAD', 'CHC'} \
       and datetime.combine(start_date, datetime.min.time()) < REGULAR_START:
        st.sidebar.warning(
            f"No official MLB games for {name} ({code}) before 2025-03-27.")

# ------------------------------------------------------------------
# Display columns
# ------------------------------------------------------------------
col1, col2 = st.columns(2)
logs = {}
color_map = {player1_name: ROYAL_BLUE, player2_name: ORANGE}

for col, pid, name, code in [
    (col1, p1_id, player1_name, team1_code),
    (col2, p2_id, player2_name, team2_code)
]:
    with col:
        st.subheader(name)
        st.image(get_player_image(pid), width=100)

        df_hr = fetch_hr_log(
            pid,
            datetime.combine(start_date, datetime.min.time()),
            end_date,
            code
        )
        logs[name] = df_hr

        if df_hr.empty:
            st.info("No HR data in selected period.")
            continue

        st.dataframe(
            df_hr[['HR No', 'MM-DD',
                   'home_team', 'away_team', 'Pitcher']],
            use_container_width=True)

        chart = (alt.Chart(df_hr)
                 .mark_line(point=False, color=color_map[name])
                 .encode(
                     x=alt.X('Date:T',
                             title='Date (MM-DD)',
                             axis=alt.Axis(format='%m-%d')),
                     y=alt.Y('HR No:Q',
                             title='Cumulative HRs',
                             axis=alt.Axis(format='d'))
                 ) +
                 alt.Chart(df_hr)
                 .mark_point(size=60, filled=True,
                             color=color_map[name])
                 .encode(x='Date:T', y='HR No:Q'))

        st.altair_chart(chart.properties(title=f"{name} HR Pace"),
                        use_container_width=True)

# ------------------------------------------------------------------
# Head-to-Head comparison
# ------------------------------------------------------------------
if all(not logs[n].empty for n in [player1_name, player2_name]):
    st.subheader("Head-to-Head Comparison")

    merged = pd.concat([
        logs[player1_name].assign(Player=player1_name),
        logs[player2_name].assign(Player=player2_name)
    ])

    comparison = (
        alt.Chart(merged)
        .mark_line(point=False)
        .encode(
            x=alt.X('Date:T',
                    title='Date (MM-DD)',
                    axis=alt.Axis(format='%m-%d')),
            y=alt.Y('HR No:Q',
                    title='Cumulative HRs',
                    axis=alt.Axis(format='d')),
            color=alt.Color('Player:N',
                            scale=alt.Scale(
                                domain=[player1_name, player2_name],
                                range=[ROYAL_BLUE, ORANGE])),
            tooltip=['Player', 'Date', 'HR No', 'Pitcher']
        )
        + alt.Chart(merged)
        .mark_point(size=60, filled=True)
        .encode(
            x='Date:T',
            y='HR No:Q',
            color='Player:N'
        )
    )
    st.altair_chart(comparison,
                    use_container_width=True)

st.caption("Data: Statcast (pybaseball) • Rosters: MLB-StatsAPI • Built with Streamlit")
