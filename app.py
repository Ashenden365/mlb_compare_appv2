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


# MLB2025全30球団主要スターリスト（各チーム5名以上、150名超）
star_players = [
    # Dodgers (LAD)
    ("Shohei Ohtani",660271,"LAD"), ("Mookie Betts",605141,"LAD"), ("Freddie Freeman",518692,"LAD"), ("Yoshinobu Yamamoto",808967,"LAD"), ("Will Smith",669257,"LAD"),
    # Yankees (NYY)
    ("Aaron Judge",592450,"NYY"), ("Anthony Rizzo",519203,"NYY"), ("DJ LeMahieu",518934,"NYY"), ("Anthony Volpe",683011,"NYY"), ("Ben Rice",687608,"NYY"),
    ("Austin Wells",680694,"NYY"), ("Everson Pereira",677956,"NYY"), ("Gleyber Torres",650402,"NYY"), ("Giancarlo Stanton",519317,"NYY"),
    ("Cody Bellinger",641355,"NYY"), ("Paul Goldschmidt",502671,"NYY"), ("Jazz Chisholm Jr.",665862,"NYY"),
    # Mets (NYM)
    ("Juan Soto",665742,"NYM"), ("Francisco Lindor",596019,"NYM"), ("Brandon Nimmo",605400,"NYM"), ("Pete Alonso",624413,"NYM"), ("Jeff McNeil",643446,"NYM"),
    ("Starling Marte",516782,"NYM"), ("Mark Vientos",672351,"NYM"), ("Francisco Alvarez",672284,"NYM"), ("Brett Baty",677003,"NYM"), ("Harrison Bader",669222,"NYM"),
    # Cubs (CHC)
    ("Seiya Suzuki",673548,"CHC"), ("Cody Bellinger",641355,"CHC"), ("Dansby Swanson",663586,"CHC"), ("Christopher Morel",666624,"CHC"), ("Nico Hoerner",669357,"CHC"),
    ("Ian Happ",669709,"CHC"), ("Michael Busch",686580,"CHC"), ("Yan Gomes",553993,"CHC"), ("Patrick Wisdom",605218,"CHC"), ("Mike Tauchman",641509,"CHC"),
    # Braves (ATL)
    ("Ronald Acuna Jr.",660670,"ATL"), ("Matt Olson",621566,"ATL"), ("Ozzie Albies",645277,"ATL"), ("Austin Riley",663586,"ATL"), ("Michael Harris II",669127,"ATL"),
    ("Marcell Ozuna",542303,"ATL"), ("Orlando Arcia",606213,"ATL"), ("Travis d'Arnaud",543228,"ATL"), ("Jarred Kelenic",666134,"ATL"), ("Sean Murphy",669221,"ATL"),
    # Phillies (PHI)
    ("Bryce Harper",547180,"PHI"), ("Trea Turner",607208,"PHI"), ("Kyle Schwarber",656941,"PHI"), ("Alec Bohm",666182,"PHI"), ("Nick Castellanos",592206,"PHI"),
    ("Bryson Stott",669222,"PHI"), ("Brandon Marsh",669457,"PHI"), ("JT Realmuto",592663,"PHI"), ("Edmundo Sosa",642082,"PHI"), ("Cristian Pache",665724,"PHI"),
    # Cardinals (STL)
    ("Paul Goldschmidt",502671,"STL"), ("Nolan Arenado",571448,"STL"), ("Lars Nootbaar",676710,"STL"), ("Jordan Walker",691026,"STL"), ("Willson Contreras",544369,"STL"),
    ("Tommy Edman",669242,"STL"), ("Brendan Donovan",680977,"STL"), ("Nolan Gorman",677551,"STL"), ("Masyn Winn",691783,"STL"), ("Dylan Carlson",666185,"STL"),
    # Blue Jays (TOR)
    ("Vladimir Guerrero Jr.",665489,"TOR"), ("Bo Bichette",666182,"TOR"), ("George Springer",543877,"TOR"), ("Daulton Varsho",662139,"TOR"), ("Justin Turner",457759,"TOR"),
    ("Davis Schneider",681297,"TOR"), ("Cavan Biggio",624415,"TOR"), ("Alejandro Kirk",672515,"TOR"), ("Isiah Kiner-Falefa",643395,"TOR"), ("Kevin Kiermaier",571662,"TOR"),
    # Astros (HOU)
    ("Yordan Alvarez",670541,"HOU"), ("Jose Altuve",514888,"HOU"), ("Alex Bregman",608324,"HOU"), ("Kyle Tucker",663656,"HOU"), ("Jeremy Pena",665161,"HOU"),
    ("Chas McCormick",676801,"HOU"), ("Yainer Diaz",676667,"HOU"), ("Jake Meyers",680686,"HOU"), ("Mauricio Dubon",670487,"HOU"), ("Jon Singleton",592716,"HOU"),
    # Padres (SD)
    ("Fernando Tatis Jr.",665487,"SD"), ("Manny Machado",592518,"SD"), ("Xander Bogaerts",593428,"SD"), ("Jake Cronenworth",664208,"SD"), ("Ha-Seong Kim",673490,"SD"),
    ("Jackson Merrill",695117,"SD"), ("Luis Campusano",668942,"SD"), ("Jurickson Profar",595777,"SD"), ("David Peralta",606715,"SD"), ("Garrett Cooper",656941,"SD"),
    # Rays (TB)
    ("Randy Arozarena",668227,"TB"), ("Isaac Paredes",664775,"TB"), ("Yandy Diaz",642232,"TB"), ("Brandon Lowe",663993,"TB"), ("Jose Siri",642350,"TB"),
    ("Richie Palacios",678771,"TB"), ("Jonathan Aranda",677617,"TB"), ("Harold Ramirez",642732,"TB"), ("Ben Rortvedt",670025,"TB"), ("Amed Rosario",642515,"TB"),
    # Rangers (TEX)
    ("Adolis Garcia",666969,"TEX"), ("Corey Seager",608369,"TEX"), ("Marcus Semien",543760,"TEX"), ("Josh Jung",686725,"TEX"), ("Nathaniel Lowe",663993,"TEX"),
    ("Leody Taveras",666801,"TEX"), ("Ezequiel Duran",670090,"TEX"), ("Jonah Heim",656555,"TEX"), ("Travis Jankowski",543272,"TEX"), ("Andrew Knizner",669003,"TEX"),
    # Mariners (SEA)
    ("Julio Rodriguez",677594,"SEA"), ("Ty France",664034,"SEA"), ("J.P. Crawford",656505,"SEA"), ("Eugenio Suarez",553993,"SEA"), ("Cal Raleigh",663728,"SEA"),
    ("Josh Rojas",670661,"SEA"), ("Dylan Moore",670109,"SEA"), ("Mitch Haniger",571745,"SEA"), ("Dominic Canzone",680886,"SEA"), ("Luke Raley",670042,"SEA"),
    # Angels (LAA)
    ("Mike Trout",545361,"LAA"), ("Taylor Ward",670032,"LAA"), ("Logan O'Hoppe",683011,"LAA"), ("Nolan Schanuel",694364,"LAA"), ("Brandon Drury",608668,"LAA"),
    ("Luis Rengifo",650859,"LAA"), ("Jo Adell",666176,"LAA"), ("Zach Neto",686580,"LAA"), ("Miguel Sano",596146,"LAA"), ("Kevin Pillar",607680,"LAA"),
    # Orioles (BAL)
    ("Adley Rutschman",668939,"BAL"), ("Gunnar Henderson",683002,"BAL"), ("Anthony Santander",609192,"BAL"), ("Ryan Mountcastle",669222,"BAL"), ("Cedric Mullins",663624,"BAL"),
    ("Jordan Westburg",669487,"BAL"), ("Colton Cowser",682998,"BAL"), ("Austin Hays",669016,"BAL"), ("Jorge Mateo",622761,"BAL"), ("James McCann",571740,"BAL"),
    # Brewers (MIL)
    ("Christian Yelich",592885,"MIL"), ("William Contreras",661388,"MIL"), ("Willy Adames",642715,"MIL"), ("Rhys Hoskins",656555,"MIL"), ("Sal Frelick",680776,"MIL"),
    ("Brice Turang",677587,"MIL"), ("Joey Ortiz",680913,"MIL"), ("Blake Perkins",677958,"MIL"), ("Jake Bauers",657046,"MIL"), ("Jackson Chourio",694390,"MIL"),
    # Twins (MIN)
    ("Carlos Correa",621043,"MIN"), ("Royce Lewis",669257,"MIN"), ("Byron Buxton",621439,"MIN"), ("Max Kepler",606299,"MIN"), ("Edouard Julien",687146,"MIN"),
    ("Ryan Jeffers",669222,"MIN"), ("Alex Kirilloff",666135,"MIN"), ("Jose Miranda",663330,"MIN"), ("Trevor Larnach",666165,"MIN"), ("Willi Castro",650489,"MIN"),
    # Marlins (MIA)
    ("Jazz Chisholm Jr.",665862,"MIA"), ("Josh Bell",605137,"MIA"), ("Jake Burger",669394,"MIA"), ("Bryan De La Cruz",664353,"MIA"), ("Jesus Sanchez",660821,"MIA"),
    ("Tim Anderson",650895,"MIA"), ("Nick Fortes",680510,"MIA"), ("Vidal Brujan",661563,"MIA"), ("Otto Lopez",673676,"MIA"), ("Jon Berti",595909,"MIA"),
    # Tigers (DET)
    ("Riley Greene",680686,"DET"), ("Spencer Torkelson",679529,"DET"), ("Kerry Carpenter",681297,"DET"), ("Javier Baez",595879,"DET"), ("Mark Canha",592192,"DET"),
    ("Matt Vierling",669557,"DET"), ("Akil Baddoo",668731,"DET"), ("Gio Urshela",570482,"DET"), ("Zach McKinstry",669743,"DET"), ("Jake Rogers",668709,"DET"),
    # Guardians (CLE)
    ("Jose Ramirez",608070,"CLE"), ("Steven Kwan",680757,"CLE"), ("Josh Naylor",647304,"CLE"), ("Bo Naylor",663457,"CLE"), ("Andres Gimenez",666969,"CLE"),
    ("Tyler Freeman",669334,"CLE"), ("David Fry",672430,"CLE"), ("Gabriel Arias",672274,"CLE"), ("Will Brennan",676810,"CLE"), ("Austin Hedges",571771,"CLE"),
    # Athletics (OAK)
    ("Brent Rooker",670043,"OAK"), ("Zack Gelof",686611,"OAK"), ("Seth Brown",664913,"OAK"), ("Ryan Noda",670770,"OAK"), ("Shea Langeliers",663624,"OAK"),
    ("Tyler Soderstrom",680681,"OAK"), ("J.J. Bleday",666664,"OAK"), ("Esteury Ruiz",670397,"OAK"), ("Nick Allen",666149,"OAK"), ("Abraham Toro",647351,"OAK"),
    # Pirates (PIT)
    ("Bryan Reynolds",668804,"PIT"), ("Ke'Bryan Hayes",663647,"PIT"), ("Jack Suwinski",666704,"PIT"), ("Oneil Cruz",665833,"PIT"), ("Rowdy Tellez",642133,"PIT"),
    ("Connor Joe",623963,"PIT"), ("Andrew McCutchen",457705,"PIT"), ("Jared Triolo",680473,"PIT"), ("Joey Bart",670221,"PIT"), ("Alika Williams",669220,"PIT"),
    # Nationals (WSH)
    ("CJ Abrams",670227,"WSH"), ("Lane Thomas",656775,"WSH"), ("Joey Meneses",624641,"WSH"), ("Jesse Winker",605400,"WSH"), ("Keibert Ruiz",660766,"WSH"),
    ("Luis Garcia",666930,"WSH"), ("Eddie Rosario",621035,"WSH"), ("Nick Senzel",669222,"WSH"), ("Harold Ramirez",642732,"WSH"), ("Drew Millas",686668,"WSH"),
    # Rockies (COL)
    ("Kris Bryant",592178,"COL"), ("Elias Diaz",553869,"COL"), ("Ryan McMahon",656713,"COL"), ("Ezequiel Tovar",678662,"COL"), ("Nolan Jones",680695,"COL"),
    ("Brenton Doyle",680937,"COL"), ("Charlie Blackmon",502671,"COL"), ("Jacob Stallings",592663,"COL"), ("Sean Bouchard",680790,"COL"), ("Michael Toglia",669357,"COL"),
    # Royals (KC)
    ("Bobby Witt Jr.",677951,"KC"), ("Salvador Perez",521692,"KC"), ("Vinnie Pasquantino",673931,"KC"), ("Michael Massey",676029,"KC"), ("MJ Melendez",669004,"KC"),
    ("Nelson Velazquez",678226,"KC"), ("Maikel Garcia",672567,"KC"), ("Hunter Renfroe",592669,"KC"), ("Garrett Hampson",669222,"KC"), ("Adam Frazier",608365,"KC"),
    # Diamondbacks (ARI)
    ("Corbin Carroll",677950,"ARI"), ("Ketel Marte",606466,"ARI"), ("Christian Walker",592389,"ARI"), ("Gabriel Moreno",672515,"ARI"), ("Lourdes Gurriel Jr.",666971,"ARI"),
    ("Joc Pederson",592626,"ARI"), ("Jake McCarthy",677950,"ARI"), ("Eugenio Suarez",553993,"ARI"), ("Alek Thomas",677950,"ARI"), ("Pavin Smith",669329,"ARI"),
    # Reds (CIN)
    ("Elly De La Cruz",682829,"CIN"), ("Spencer Steer",670242,"CIN"), ("Christian Encarnacion-Strand",680724,"CIN"), ("Jonathan India",663697,"CIN"), ("Will Benson",669197,"CIN"),
    ("TJ Friedl",670280,"CIN"), ("Jake Fraley",656448,"CIN"), ("Jeimer Candelario",642715,"CIN"), ("Santiago Espinal",642397,"CIN"), ("Nick Martini",592666,"CIN"),
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
