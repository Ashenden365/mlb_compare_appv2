import streamlit as st
import pandas as pd
import altair as alt
from pybaseball import playerid_reverse_lookup, statcast_batter
from datetime import datetime

st.set_page_config(layout="wide")
st.title("MLB Home Run Pace Comparison (2025 Major Players 150+)")

TOKYO_START = datetime(2025, 3, 18)
TOKYO_2 = datetime(2025, 3, 19)
REGULAR_START = datetime(2025, 3, 27)

# MLB2025 全30球団主要スターリスト（各チーム5名）
star_players = [
    # Diamondbacks (ARI)
    ("Corbin Carroll", 677950, "ARI"),
    ("Ketel Marte", 606466, "ARI"),
    ("Christian Walker", 592389, "ARI"),
    ("Lourdes Gurriel Jr.", 666971, "ARI"),
    ("Gabriel Moreno", 672515, "ARI"),

    # Braves (ATL)
    ("Ronald Acuna Jr.", 660670, "ATL"),
    ("Matt Olson", 621566, "ATL"),
    ("Austin Riley", 663586, "ATL"),
    ("Ozzie Albies", 645277, "ATL"),
    ("Michael Harris II", 669127, "ATL"),

    # Orioles (BAL)
    ("Adley Rutschman", 668939, "BAL"),
    ("Gunnar Henderson", 683002, "BAL"),
    ("Cedric Mullins", 663624, "BAL"),
    ("Anthony Santander", 609192, "BAL"),
    ("Ryan Mountcastle", 669222, "BAL"),

    # Red Sox (BOS)
    ("Rafael Devers", 646240, "BOS"),
    ("Triston Casas", 671213, "BOS"),
    ("Trevor Story", 596115, "BOS"),
    ("Masataka Yoshida", 807799, "BOS"),
    ("Jarren Duran", 680776, "BOS"),

    # Cubs (CHC)
    ("Cody Bellinger", 641355, "CHC"),
    ("Seiya Suzuki", 673548, "CHC"),
    ("Dansby Swanson", 663586, "CHC"),
    ("Nico Hoerner", 669357, "CHC"),
    ("Ian Happ", 669709, "CHC"),

    # Reds (CIN)
    ("Elly De La Cruz", 682829, "CIN"),
    ("Spencer Steer", 670242, "CIN"),
    ("Christian Encarnacion-Strand", 680724, "CIN"),
    ("Jonathan India", 663697, "CIN"),
    ("Will Benson", 669197, "CIN"),

    # Guardians (CLE)
    ("José Ramírez", 608070, "CLE"),
    ("Steven Kwan", 680757, "CLE"),
    ("Josh Naylor", 647304, "CLE"),
    ("Andrés Giménez", 666969, "CLE"),
    ("Bo Naylor", 663457, "CLE"),

    # Rockies (COL)
    ("Kris Bryant", 592178, "COL"),
    ("Ryan McMahon", 656713, "COL"),
    ("Ezequiel Tovar", 678662, "COL"),
    ("Nolan Jones", 680695, "COL"),
    ("Elias Díaz", 553869, "COL"),

    # White Sox (CWS)
    ("Luis Robert Jr.", 673357, "CWS"),
    ("Eloy Jiménez", 650391, "CWS"),
    ("Andrew Vaughn", 683734, "CWS"),
    ("Yoán Moncada", 660162, "CWS"),
    ("Gavin Sheets", 657757, "CWS"),

    # Tigers (DET)
    ("Spencer Torkelson", 679529, "DET"),
    ("Riley Greene", 680686, "DET"),
    ("Kerry Carpenter", 681297, "DET"),
    ("Javier Báez", 595879, "DET"),
    ("Mark Canha", 592192, "DET"),

    # Astros (HOU)
    ("Yordan Alvarez", 670541, "HOU"),
    ("Kyle Tucker", 663656, "HOU"),
    ("José Altuve", 514888, "HOU"),
    ("Alex Bregman", 608324, "HOU"),
    ("Jeremy Peña", 665161, "HOU"),

    # Royals (KC)
    ("Bobby Witt Jr.", 677951, "KC"),
    ("Salvador Pérez", 521692, "KC"),
    ("Vinnie Pasquantino", 673931, "KC"),
    ("MJ Melendez", 669004, "KC"),
    ("Michael Massey", 676029, "KC"),

    # Angels (LAA)
    ("Mike Trout", 545361, "LAA"),
    ("Taylor Ward", 670032, "LAA"),
    ("Logan O'Hoppe", 683011, "LAA"),
    ("Zach Neto", 686580, "LAA"),
    ("Jo Adell", 666176, "LAA"),

    # Dodgers (LAD)
    ("Shohei Ohtani", 660271, "LAD"),
    ("Mookie Betts", 605141, "LAD"),
    ("Freddie Freeman", 518692, "LAD"),
    ("Yoshinobu Yamamoto", 808967, "LAD"),
    ("Will Smith", 669257, "LAD"),

    # Marlins (MIA)
    ("Jazz Chisholm Jr.", 665862, "MIA"),
    ("Josh Bell", 605137, "MIA"),
    ("Jake Burger", 669394, "MIA"),
    ("Jesús Sánchez", 660821, "MIA"),
    ("Bryan De La Cruz", 664353, "MIA"),

    # Brewers (MIL)
    ("Christian Yelich", 592885, "MIL"),
    ("William Contreras", 661388, "MIL"),
    ("Willy Adames", 642715, "MIL"),
    ("Rhys Hoskins", 656555, "MIL"),
    ("Sal Frelick", 680776, "MIL"),

    # Twins (MIN)
    ("Carlos Correa", 621043, "MIN"),
    ("Royce Lewis", 668904, "MIN"),
    ("Byron Buxton", 621439, "MIN"),
    ("Max Kepler", 606299, "MIN"),
    ("Edouard Julien", 687146, "MIN"),

    # Mets (NYM)
    ("Pete Alonso", 624413, "NYM"),
    ("Francisco Lindor", 596019, "NYM"),
    ("Brandon Nimmo", 605400, "NYM"),
    ("Juan Soto", 665742, "NYM"),
    ("Brett Baty", 677003, "NYM"),

    # Yankees (NYY)
    ("Aaron Judge", 592450, "NYY"),
    ("Anthony Volpe", 683011, "NYY"),
    ("Giancarlo Stanton", 519317, "NYY"),
    ("Austin Wells", 680694, "NYY"),
    ("Gleyber Torres", 650402, "NYY"),

    # Athletics (OAK)
    ("Brent Rooker", 670043, "OAK"),
    ("Zack Gelof", 686611, "OAK"),
    ("Shea Langeliers", 663624, "OAK"),
    ("Tyler Soderstrom", 680681, "OAK"),
    ("Ryan Noda", 670770, "OAK"),

    # Phillies (PHI)
    ("Bryce Harper", 547180, "PHI"),
    ("Trea Turner", 607208, "PHI"),
    ("Kyle Schwarber", 656941, "PHI"),
    ("Alec Bohm", 666182, "PHI"),
    ("JT Realmuto", 592663, "PHI"),

    # Pirates (PIT)
    ("Bryan Reynolds", 668804, "PIT"),
    ("Ke'Bryan Hayes", 663647, "PIT"),
    ("Oneil Cruz", 665833, "PIT"),
    ("Jack Suwinski", 666704, "PIT"),
    ("Andrew McCutchen", 457705, "PIT"),

    # Padres (SD)
    ("Fernando Tatis Jr.", 665487, "SD"),
    ("Manny Machado", 592518, "SD"),
    ("Xander Bogaerts", 593428, "SD"),
    ("Jake Cronenworth", 664208, "SD"),
    ("Ha-Seong Kim", 673490, "SD"),

    # Giants (SF)
    ("Logan Webb", 657277, "SF"),
    ("Michael Conforto", 624424, "SF"),
    ("Jung Hoo Lee", 808982, "SF"),
    ("Patrick Bailey", 672275, "SF"),
    ("Wilmer Flores", 527038, "SF"),

    # Mariners (SEA)
    ("Julio Rodríguez", 677594, "SEA"),
    ("Ty France", 664034, "SEA"),
    ("J.P. Crawford", 656505, "SEA"),
    ("Cal Raleigh", 663728, "SEA"),
    ("Mitch Haniger", 571745, "SEA"),

    # Cardinals (STL)
    ("Paul Goldschmidt", 502671, "STL"),
    ("Nolan Arenado", 571448, "STL"),
    ("Lars Nootbaar", 676710, "STL"),
    ("Jordan Walker", 691026, "STL"),
    ("Masyn Winn", 691783, "STL"),

    # Rays (TB)
    ("Randy Arozarena", 668227, "TB"),
    ("Isaac Paredes", 664775, "TB"),
    ("Yandy Díaz", 642232, "TB"),
    ("Brandon Lowe", 663993, "TB"),
    ("José Siri", 642350, "TB"),

    # Rangers (TEX)
    ("Corey Seager", 608369, "TEX"),
    ("Marcus Semien", 543760, "TEX"),
    ("Adolis García", 666969, "TEX"),
    ("Josh Jung", 686725, "TEX"),
    ("Nathaniel Lowe", 663993, "TEX"),

    # Blue Jays (TOR)
    ("Vladimir Guerrero Jr.", 665489, "TOR"),
    ("Bo Bichette", 666182, "TOR"),
    ("George Springer", 543877, "TOR"),
    ("Daulton Varsho", 662139, "TOR"),
    ("Davis Schneider", 681297, "TOR"),

    # Nationals (WSH)
    ("CJ Abrams", 670227, "WSH"),
    ("Lane Thomas", 656775, "WSH"),
    ("Keibert Ruiz", 660766, "WSH"),
    ("Joey Meneses", 624641, "WSH"),
    ("Eddie Rosario", 621035, "WSH"),
]


teams = sorted({team for _, _, team in star_players})
player_dict = {n: (id, team) for n, id, team in star_players}

def get_id_team(name):
    return player_dict.get(name, (None, "OTHER"))

def get_player_image(mlbam_id):
    return f"https://img.mlbstatic.com/mlb-photos/image/upload/w_180,q_100/v1/people/{mlbam_id}/headshot/67/current.png"

def fetch_data(pid, start, end, team):
    df = statcast_batter(start_dt=start.strftime('%Y-%m-%d'), end_dt=end.strftime('%Y-%m-%d'), player_id=str(pid))
    df["Date"] = pd.to_datetime(df["game_date"])
    # 厳密開幕ロジック
    tokyo_days = [TOKYO_START, TOKYO_2]
    if team in ["LAD", "CHC"]:
        mask = (
            (df["Date"].isin(tokyo_days)) | 
            (df["Date"] >= REGULAR_START)
        )
    else:
        mask = df["Date"] >= REGULAR_START
    df = df[mask]
    df_hr = df[df["events"] == "home_run"].copy()
    df_hr = df_hr.sort_values("Date").reset_index(drop=True)
    df_hr["HR No"] = df_hr.index + 1
    df_hr["MM-DD"] = df_hr["Date"].dt.strftime('%m-%d')
    def pitcher_id_to_name(pid):
        try:
            table = playerid_reverse_lookup([pid], key_type='mlbam')
            return table['name_first'][0] + ' ' + table['name_last'][0]
        except:
            return str(pid)
    df_hr["Pitcher"] = df_hr["pitcher"].apply(lambda pid: pitcher_id_to_name(pid) if pd.notna(pid) else "")
    return df_hr

ROYAL_BLUE = "#1E90FF"
ORANGE = "#FF8000"

st.sidebar.header("Select Players and Date Range")
team1 = st.sidebar.selectbox("First Player's Team", teams, index=teams.index("LAD"))
team2 = st.sidebar.selectbox("Second Player's Team", teams, index=teams.index("NYY"))
team1_players = [n for n, _, t in star_players if t == team1]
team2_players = [n for n, _, t in star_players if t == team2]
pl1 = st.sidebar.selectbox("First Player", team1_players, index=0)
pl2 = st.sidebar.selectbox("Second Player", team2_players, index=0)
user_start = st.sidebar.date_input("Start date", REGULAR_START)
end_date = st.sidebar.date_input("End date", datetime(2025, 6, 27))

p1_id, team1_code = get_id_team(pl1)
p2_id, team2_code = get_id_team(pl2)
s1 = datetime.combine(user_start, datetime.min.time()) if p1_id else None
s2 = datetime.combine(user_start, datetime.min.time()) if p2_id else None

if p1_id and team1_code not in ["LAD", "CHC"] and s1 < REGULAR_START:
    st.sidebar.warning(f"No official MLB games for {pl1} ({team1_code}) during this period. Opening Day is March 27 except for Dodgers/Cubs (Tokyo Series: March 18).")
if p2_id and team2_code not in ["LAD", "CHC"] and s2 < REGULAR_START:
    st.sidebar.warning(f"No official MLB games for {pl2} ({team2_code}) during this period. Opening Day is March 27 except for Dodgers/Cubs (Tokyo Series: March 18).")

col1, col2 = st.columns(2)
dfs = {}

player_colors = {
    pl1: ROYAL_BLUE,
    pl2: ORANGE
}

for col, pid, name, start, team in [(col1, p1_id, pl1, s1, team1_code), (col2, p2_id, pl2, s2, team2_code)]:
    with col:
        st.subheader(name)
        if pid:
            st.image(get_player_image(pid), width=100)
        if pid:
            df = fetch_data(pid, start, end_date, team)
            dfs[name] = df
            if not df.empty:
                st.dataframe(df[["HR No", "MM-DD", "home_team", "away_team", "Pitcher"]], use_container_width=True)
                color = player_colors.get(name, "#222")
                # x軸: カレンダー日付（MM-DDで表示）
                line = alt.Chart(df).mark_line(point=False, color=color).encode(
                    x=alt.X('Date:T', title='Date (MM-DD)', axis=alt.Axis(format='%m-%d')),
                    y=alt.Y('HR No:Q', title='Cumulative HRs', axis=alt.Axis(format='d'))
                )
                points = alt.Chart(df).mark_point(filled=True, size=60, color=color).encode(
                    x=alt.X('Date:T', axis=alt.Axis(format='%m-%d')),
                    y='HR No:Q'
                )
                chart = (line + points).properties(title=f"{name} HR Pace")
                st.altair_chart(chart, use_container_width=True)
            else:
                st.info(f"No home run data found for {name} in the selected period. This player has not hit a HR in the MLB 2025 season.")
        else:
            st.warning(f"Can't find MLBAM ID for {name}")

if all(n in dfs for n in [pl1, pl2]):
    d1, d2 = dfs[pl1], dfs[pl2]
    if not d1.empty and not d2.empty:
        st.subheader("Head-to-Head Comparison (Interactive)")
        compare_df = pd.concat([
            d1.assign(Player=pl1),
            d2.assign(Player=pl2)
        ])
        color_scale = alt.Scale(domain=[pl1, pl2], range=[ROYAL_BLUE, ORANGE])
        base = alt.Chart(compare_df).encode(
            x=alt.X('Date:T', title='Date (MM-DD)', axis=alt.Axis(format='%m-%d')),
            y=alt.Y('HR No:Q', title='Cumulative HRs', axis=alt.Axis(format='d')),
            color=alt.Color('Player:N', scale=color_scale),
            tooltip=['Player', 'Date', 'HR No', 'Pitcher']
        )
        line = base.mark_line(point=False)
        points = base.mark_point(filled=True, size=60)
        chart2 = (line + points).properties(title="Cumulative HRs Comparison")
        st.altair_chart(chart2, use_container_width=True)
