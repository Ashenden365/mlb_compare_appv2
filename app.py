# -*- coding: utf-8 -*-
"""
MLB Home Run Pace Tracker — dynamic roster版 (Streamlit)
* 最新ロスター（MLB-StatsAPI, 12hキャッシュ）
* Statcast HRログ＋東京シリーズ例外
* デフォルト選手: Shohei Ohtani × Aaron Judge
* デフォルト開始日: 2025-03-18
"""

import streamlit as st
import pandas as pd
import altair as alt
from datetime import datetime
import statsapi                                 # roster取得
from pybaseball import playerid_reverse_lookup, statcast_batter

# ------------------------------------------------------------------
# 定数
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
# 最新ロスター取得（キャッシュ）
# ------------------------------------------------------------------
@st.cache_data(ttl=12 * 60 * 60)
def build_star_players():
    stars = []
    for team in [t for t in statsapi.get('teams', {'sportIds': 1})['teams']
                 if t['active']]:
        data = statsapi.get('team_roster',
                            {'teamId': team['id'], 'rosterType': 'active'})
        for pl in data.get('roster', []):
            person = pl.get('person', {})
            if person.get('fullName') and person.get('id'):
                stars.append((person['fullName'],
                              person['id'],
                              team['abbreviation']))
    return stars


star_players = build_star_players()
teams        = sorted({t for _, _, t in star_players})
player_map   = {n: (pid, team) for n, pid, team in star_players}

# ------------------------------------------------------------------
# ヘルパー
# ------------------------------------------------------------------
def player_img(pid: int) -> str:
    return (f"https://img.mlbstatic.com/mlb-photos/image/upload/"
            f"w_180,q_100/v1/people/{pid}/headshot/67/current.png")


def fetch_hr(pid: int,
             start: datetime,
             end: datetime,
             team: str) -> pd.DataFrame:
    df = statcast_batter(start_dt=start.strftime('%Y-%m-%d'),
                         end_dt=end.strftime('%Y-%m-%d'),
                         player_id=str(pid))
    if df.empty:
        return df
    df['Date'] = pd.to_datetime(df['game_date'])

    tokyo_days = [TOKYO_START, TOKYO_2]
    mask = (df['Date'].isin(tokyo_days) | (df['Date'] >= REGULAR_START)) \
           if team in {'LAD', 'CHC'} else (df['Date'] >= REGULAR_START)
    df = df[mask]

    df = (df[df['events'] == 'home_run']
          .sort_values('Date')
          .reset_index(drop=True))
    if df.empty:
        return df

    df['HR No'] = df.index + 1
    df['MM-DD'] = df['Date'].dt.strftime('%m-%d')

    def pid2name(x):
        try:
            t = playerid_reverse_lookup([x], key_type='mlbam')
            return t['name_first'][0] + ' ' + t['name_last'][0]
        except Exception:
            return str(x)

    df['Pitcher'] = df['pitcher'].apply(
        lambda x: pid2name(x) if pd.notna(x) else '')
    return df

# ------------------------------------------------------------------
# サイドバー
# ------------------------------------------------------------------
st.sidebar.header("Select Players and Date Range")

team1 = st.sidebar.selectbox("First Player's Team", teams,
                             index=teams.index("LAD") if "LAD" in teams else 0)
team2 = st.sidebar.selectbox("Second Player's Team", teams,
                             index=teams.index("NYY") if "NYY" in teams else 1)

team1_players = [n for n, _, t in star_players if t == team1]
team2_players = [n for n, _, t in star_players if t == team2]

def idx(lst, target): return lst.index(target) if target in lst else 0

p1_name = st.sidebar.selectbox("First Player", team1_players,
                               index=idx(team1_players, "Shohei Ohtani"))
p2_name = st.sidebar.selectbox("Second Player", team2_players,
                               index=idx(team2_players, "Aaron Judge"))

# 🔸 デフォルト開始日を 3/18 に変更
start_date = st.sidebar.date_input("Start date", TOKYO_START)
end_date   = st.sidebar.date_input("End date", datetime(2025, 6, 27))

p1_id, team1_abbr = player_map[p1_name]
p2_id, team2_abbr = player_map[p2_name]

for name, abbr in [(p1_name, team1_abbr), (p2_name, team2_abbr)]:
    if abbr not in {'LAD', 'CHC'} and \
       datetime.combine(start_date, datetime.min.time()) < REGULAR_START:
        st.sidebar.warning(
            f"No official MLB games for {name} ({abbr}) before 2025-03-27.")

# ------------------------------------------------------------------
# メイン表示
# ------------------------------------------------------------------
col1, col2 = st.columns(2)
logs, colors = {}, {p1_name: ROYAL_BLUE, p2_name: ORANGE}

for col, pid, name, abbr in [(col1, p1_id, p1_name, team1_abbr),
                             (col2, p2_id, p2_name, team2_abbr)]:
    with col:
        st.subheader(name)
        st.image(player_img(pid), width=100)
        df = fetch_hr(pid,
                      datetime.combine(start_date, datetime.min.time()),
                      end_date, abbr)
        logs[name] = df
        if df.empty:
            st.info("No HR data in selected period.")
            continue
        st.dataframe(df[['HR No', 'MM-DD',
                         'home_team', 'away_team', 'Pitcher']],
                     use_container_width=True)
        chart = (alt.Chart(df).mark_line(point=False,
                                         color=colors[name])
                 .encode(
                     x=alt.X('Date:T', title='Date (MM-DD)',
                             axis=alt.Axis(format='%m-%d')),
                     y=alt.Y('HR No:Q', title='Cumulative HRs',
                             axis=alt.Axis(format='d'))) +
                 alt.Chart(df).mark_point(size=60, filled=True,
                                          color=colors[name])
                 .encode(x='Date:T', y='HR No:Q'))
        st.altair_chart(chart.properties(title=f"{name} HR Pace"),
                        use_container_width=True)

# ------------------------------------------------------------------
# H2H
# ------------------------------------------------------------------
if all(not logs[n].empty for n in [p1_name, p2_name]):
    st.subheader("Head-to-Head Comparison")
    merged = pd.concat([logs[p1_name].assign(Player=p1_name),
                        logs[p2_name].assign(Player=p2_name)])
    compare = (alt.Chart(merged).mark_line(point=False)
               .encode(
                   x=alt.X('Date:T', title='Date (MM-DD)',
                           axis=alt.Axis(format='%m-%d')),
                   y=alt.Y('HR No:Q', title='Cumulative HRs',
                           axis=alt.Axis(format='d')),
                   color=alt.Color('Player:N',
                                   scale=alt.Scale(
                                       domain=[p1_name, p2_name],
                                       range=[ROYAL_BLUE, ORANGE])),
                   tooltip=['Player', 'Date', 'HR No', 'Pitcher']) +
               alt.Chart(merged).mark_point(size=60, filled=True)
               .encode(x='Date:T', y='HR No:Q', color='Player:N'))
    st.altair_chart(compare, use_container_width=True)

st.caption("Data: Statcast • Rosters: MLB-StatsAPI • Built with Streamlit")
