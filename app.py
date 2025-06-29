import streamlit as st
import pandas as pd
import altair as alt
from datetime import datetime
import statsapi
from pybaseball import playerid_reverse_lookup, statcast_batter

TOKYO_START   = datetime(2025, 3, 18)
TOKYO_2       = datetime(2025, 3, 19)
REGULAR_START = datetime(2025, 3, 27)

ROYAL_BLUE = "#1E90FF"
ORANGE     = "#FF8000"

st.set_page_config(layout="wide", page_title="MLB 2025 Home Run Pace Tracker")
st.title("MLB Home Run Pace Comparison — 2025 Season (Dynamic Rosters)")

@st.cache_data(ttl=12 * 60 * 60)
def get_team_info():
    teams_raw = statsapi.get('teams', {'sportIds': 1})['teams']
    team_info = {}
    for t in teams_raw:
        if t['active']:
            abbr = t['abbreviation']
            team_info[abbr] = {
                'id': t['id'],
                'name': t['name'],
                'logo': f"https://www.mlbstatic.com/team-logos/{t['id']}.svg",
                'slug': t.get('teamName', '').lower().replace(' ', '-'),
                'division': t['division']['name']  # 例: "American League West"
            }
    return team_info

team_info = get_team_info()
team_abbrs = sorted(team_info.keys())
team_names = [team_info[a]['name'] for a in team_abbrs]
abbr_by_name = {team_info[a]['name']: a for a in team_abbrs}

@st.cache_data(ttl=12 * 60 * 60)
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
player_map   = {name: (pid, team) for name, pid, team in star_players}

def get_player_image(pid: int) -> str:
    return (f"https://img.mlbstatic.com/mlb-photos/image/upload/"
            f"w_180,q_100/v1/people/{pid}/headshot/67/current.png")

def fetch_hr_log(pid: int, start: datetime, end: datetime, team_abbr: str) -> pd.DataFrame:
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

# ----------------------------------------
# Sidebar UI
# ----------------------------------------
st.sidebar.header("Select Players and Date Range")

st.sidebar.markdown(
    "<span style='color:#d97706; font-weight:bold;'>⚠️ Note:</span> "
    "Only players currently on the official MLB active roster are shown in the dropdowns. "
    "Players not on an active roster (e.g., due to injury or other status) will not appear.",
    unsafe_allow_html=True
)

default_team1 = "Los Angeles Dodgers"
team1_name = st.sidebar.selectbox(
    "First Player's Team", team_names,
    index=team_names.index(default_team1) if default_team1 in team_names else 0)
team1_abbr = abbr_by_name[team1_name]

team1_players = [n for n, _, t in star_players if t == team1_abbr]
default_player1 = "Shohei Ohtani"
player1_name = st.sidebar.selectbox(
    "First Player", team1_players,
    index=team1_players.index(default_player1) if default_player1 in team1_players else 0)

default_team2 = "New York Yankees"
team2_name = st.sidebar.selectbox(
    "Second Player's Team", team_names,
    index=team_names.index(default_team2) if default_team2 in team_names else 0)
team2_abbr = abbr_by_name[team2_name]

team2_players = [n for n, _, t in star_players if t == team2_abbr]
default_player2 = "Aaron Judge"
player2_name = st.sidebar.selectbox(
    "Second Player", team2_players,
    index=team2_players.index(default_player2) if default_player2 in team2_players else 0)

start_date = st.sidebar.date_input("Start date", TOKYO_START)
end_date = st.sidebar.date_input("End date", datetime.today())

no_game_msgs = []
if team1_abbr not in {'LAD', 'CHC'} and datetime.combine(start_date, datetime.min.time()) < REGULAR_START:
    no_game_msgs.append(f"No official MLB games for {player1_name} ({team1_abbr}) before 2025-03-27.")
if team2_abbr not in {'LAD', 'CHC'} and datetime.combine(start_date, datetime.min.time()) < REGULAR_START:
    no_game_msgs.append(f"No official MLB games for {player2_name} ({team2_abbr}) before 2025-03-27.")
if no_game_msgs:
    for msg in no_game_msgs:
        st.sidebar.warning(msg)

# === MLB Teams Official Links（リーグ・地区別、枠線なし）をサイドバー一番下に配置 ===
st.sidebar.markdown("#### MLB Teams (links to official sites)")

# Divisionごとのマッピング
division_map = {
    'American League': {
        'East':    [],
        'Central': [],
        'West':    []
    },
    'National League': {
        'East':    [],
        'Central': [],
        'West':    []
    }
}
division_name_map = {
    'American League East': ('American League', 'East'),
    'American League Central': ('American League', 'Central'),
    'American League West': ('American League', 'West'),
    'National League East': ('National League', 'East'),
    'National League Central': ('National League', 'Central'),
    'National League West': ('National League', 'West')
}

for abbr in team_abbrs:
    info = team_info[abbr]
    div_full = info['division']
    league, division = division_name_map[div_full]
    url = f"https://www.mlb.com/{info['slug']}"
    # 略称＋ロゴ＋公式リンク、チーム名はabbr
    entry = (
        f'<a href="{url}" target="_blank">'
        f'<img src="{info["logo"]}" width="22" style="vertical-align:middle;margin-right:4px;">'
        f'{abbr}</a>'
    )
    division_map[league][division].append(entry)

def render_division_block_sidebar(division, entries):
    st.sidebar.markdown(f"**{division}**")
    col_count = 6
    rows = [entries[i:i+col_count] for i in range(0, len(entries), col_count)]
    # 枠線なしでグリッド表示
    table_html = '<table style="border-collapse:collapse;border:none;">'
    for row in rows:
        table_html += '<tr style="border:none;">' + ''.join(
            f'<td style="padding:2px 8px;border:none;background:transparent;">{cell}</td>' for cell in row
        ) + '</tr>'
    table_html += '</table>'
    st.sidebar.markdown(table_html, unsafe_allow_html=True)

for league in ['American League', 'National League']:
    st.sidebar.markdown(f"### {league}")
    for division in ['East', 'Central', 'West']:
        entries = division_map[league][division]
        if entries:
            render_division_block_sidebar(division, entries)

# ----------------------------------------
# Main content
# ----------------------------------------
p1_id, team1_code = player_map[player1_name]
p2_id, team2_code = player_map[player2_name]

col1, col2 = st.columns(2)
logs = {}
color_map = {player1_name: ROYAL_BLUE, player2_name: ORANGE}

for col, pid, name, code in [
    (col1, p1_id, player1_name, team1_code),
    (col2, p2_id, player2_name, team2_code)
]:
    with col:
        st.subheader(f"{name} ({team_info[code]['name']})")
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
            df_hr[['HR No', 'MM-DD', 'home_team', 'away_team', 'Pitcher']],
            use_container_width=True)
        chart = (alt.Chart(df_hr)
                 .mark_line(point=False, color=color_map[name])
                 .encode(
                     x=alt.X('Date:T', title='Date (MM-DD)', axis=alt.Axis(format='%m-%d')),
                     y=alt.Y('HR No:Q', title='Cumulative HRs', axis=alt.Axis(format='d'))
                 ) +
                 alt.Chart(df_hr)
                 .mark_point(size=60, filled=True, color=color_map[name])
                 .encode(x='Date:T', y='HR No:Q'))
        st.altair_chart(chart.properties(title=f"{name} HR Pace"), use_container_width=True)

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
            x=alt.X('Date:T', title='Date (MM-DD)', axis=alt.Axis(format='%m-%d')),
            y=alt.Y('HR No:Q', title='Cumulative HRs', axis=alt.Axis(format='d')),
            color=alt.Color('Player:N', scale=alt.Scale(
                domain=[player1_name, player2_name],
                range=[ROYAL_BLUE, ORANGE])),
            tooltip=['Player', 'Date', 'HR No', 'Pitcher']
        )
        + alt.Chart(merged)
        .mark_point(size=60, filled=True)
        .encode(x='Date:T', y='HR No:Q', color='Player:N')
    )
    st.altair_chart(comparison, use_container_width=True)

st.caption("Data: Statcast (pybaseball) • Rosters: MLB-StatsAPI • Built with Streamlit")
