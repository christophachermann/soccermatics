"""
Plotting shots
==============
Skript aus dem Soccermatics erweitert
- Funktionen für die Plots geschrieben
- Shots um Passes erweitert
christoph.achermann@gmail.com
26.11.2025
"""

import matplotlib.pyplot as plt
import numpy as np
import pandas
from mplsoccer import Pitch, Sbopen, VerticalPitch
import pandas as pd


def get_events_from_matchlist(list_match, fbstats_object):
    df_all = []
    related_all = []
    freeze_all = []
    tactics_all = []

    for match in list_match:
        df, related, freeze, tactics = fbstats_object.event(match)
        df_all.append(df)
        related_all.append(related)
        freeze_all.append(freeze)
        tactics_all.append(tactics)

    return (
        pd.concat(df_all, ignore_index=True),
        pd.concat(related_all, ignore_index=True),
        pd.concat(freeze_all, ignore_index=True),
        pd.concat(tactics_all, ignore_index=True)
    )
def plot_player_passes(curr_player_id, df_events):
    player_shots = df_events[df_events["player_id"] == curr_player_id]
    if player_shots.empty:
        print("No events for player", curr_player_id)
        return

    player_name = player_shots["player_name"].unique()[0]

    # Pitch erstellen
    pitch = VerticalPitch(line_color='black', half=True)

    fig, axs = pitch.grid(
        grid_height=0.9,
        title_height=0.06,
        axis=False,
        endnote_height=0.04,
        title_space=0,
        endnote_space=0
    )

    ax_pitch = axs['pitch']  # Das richtige Axes-Objekt holen

    # Daten plotten mit mplsoccer.scatter — hier: auf dem Pitch-Axes
    pitch.scatter(
        player_shots["x"],
        player_shots["y"],
        c="red",
        s=40,
        alpha=player_shots["outcome_name"].eq("Goal").map({True: 1, False: 0.2}),
        ax=ax_pitch
    )

    # Titel setzen
    fig.suptitle(f"{player_name} shots", fontsize=24)

    plt.show()

"""
Definition of Variables
"""
#Competition-Id Euro der Männer
var_competition_id = 55 
#Saison Id für 2024
var_season_id = 282
#alle Spiele der Schweiz; team_id=773
team_id_current = 773
"""
Data from statsbomb
"""
#Statsbomb-service öffnen
parser = Sbopen()
# list of competitions
free_competitions = parser.competition()

# eine _Liste aller Spiele der EM 2024
euro_2024_matches = parser.match(competition_id = var_competition_id, season_id = var_season_id)

euro_2024_matches_current_team = euro_2024_matches[
    (euro_2024_matches["away_team_id"] == team_id_current) |
    (euro_2024_matches["home_team_id"] == team_id_current)
]
# get all events of team switzerland
euro_2024_matches_current_team.match_id
df, related, freeze, tactics = get_events_from_matchlist(
    euro_2024_matches_current_team.match_id, parser)
# nur ein Spiel filtern
df = df[df.match_id == 3940878]
events_alternativ = parser.event(3940878)      # Beispielmatch
frames_alternativ = parser.frame(3940878)      # 360 freeze frames


team_name_current = euro_2024_matches_current_team[
    euro_2024_matches_current_team['home_team_id'] == team_id_current ]["home_team_name"].unique()[0]
team_name_current

df = df.assign(
    dx = df["end_x"] - df["x"],
    dy = df["end_y"] - df["y"])

#A dataframe of shots
shots = df.loc[df['type_name'] == 'Shot'].set_index('id')
# Dataframe of passes
list_event_types = df.type_name.unique()
list_event_types
passes = df.loc[df['type_name'] == 'Pass'].set_index('id')    

##############################################################################

pitch = Pitch(line_color = "black")
fig, ax = pitch.draw(figsize=(10, 7))
#Size of the pitch in yards (!!!)
pitchLengthX = 120
pitchWidthY = 80
#Plot the shots by looping through them.
# 1) Team-Filter
shots_self = shots[shots["team_id"] == team_id_current].copy()
shots_opp  = shots[shots["team_id"] != team_id_current].copy()

# 2) Gegner-Koordinaten spiegeln
shots_opp["x_plot"] = pitchLengthX - shots_opp["x"]
shots_opp["y_plot"] = pitchWidthY  - shots_opp["y"]

shots_self["x_plot"] = shots_self["x"]
shots_self["y_plot"] = shots_self["y"]

# 3) Punkte plotten
ax.scatter(
    shots_self["x_plot"], shots_self["y_plot"],
    c="red",
    s=40,                          # circleSize²
    alpha=shots_self["outcome_name"].eq("Goal").map({True:1, False:0.2})
)

ax.scatter(
    shots_opp["x_plot"], shots_opp["y_plot"],
    c="blue",
    s=40,
    alpha=shots_opp["outcome_name"].eq("Goal").map({True:1, False:0.2})
)

# 4) Nur bei Toren Namen plotten
goals_self = shots_self[shots_self["outcome_name"] == "Goal"]
for _, g in goals_self.iterrows():
    ax.text(g["x_plot"]+1, g["y_plot"]-2, g["player_name"])

goals_opp = shots_opp[shots_opp["outcome_name"] == "Goal"]
for _, g in goals_opp.iterrows():
    ax.text(g["x_plot"]+1, g["y_plot"]-2, g["player_name"])
    

#set title
fig.suptitle(f"{team_name_current} (red) and Opponent (blue) shots", fontsize=24)    
fig.set_size_inches(10, 7)
plt.show()



##############################################################################
# Plotting shots on one half
# ----------------------------
#Plot vertical, einmal für jeden Speieler
list_player = shots_self["player_id"].unique()
for player_id in list_player:
    plot_player_passes(player_id , shots)
    
    # Schüsse dieses Spielers
    player_shots = shots_self[shots_self["player_id"] == player_id]
    player_passes = passes[passes["player_id"] == player_id]
    player_name = player_shots["player_name"].unique()[0]

    # Pitch erstellen
    pitch = VerticalPitch(line_color='black', half=True)
    fig, ax = pitch.draw(figsize=(8, 12))

    # Plotten der Shots
    ax.scatter(
        player_shots.y , player_shots.x,
        c="red",
        s=40,
        alpha=player_shots["outcome_name"].eq("Goal").map({True: 1, False: 0.2})
    )
    #ax.arrows(passes.x, passes.y, passes.end.x)

    # Titel setzen
    fig.suptitle(f"{player_name} shots", fontsize=24)

    plt.show()    
    
    
##############################################################################
# Plotting passes and shots on whole pitch
# ----------------------------
#Plot vertical, einmal für jeden Speieler
list_player = shots_self["player_id"].unique()
for player_id in list_player:
    
    # Schüsse dieses Spielers
    player_shots = shots_self[shots_self["player_id"] == player_id]
    player_passes = passes[passes["player_id"] == player_id]
    player_name = player_shots["player_name"].unique()[0]

    # Pitch erstellen
    #pitch = VerticalPitch(line_color='black', half=True)
    #fig, ax = pitch.draw(figsize=(8, 12))
    pitch = Pitch(line_color = "black")
    fig, ax = pitch.draw(figsize=(10, 7))

    # Plotten der Shots
    ax.scatter(
        player_shots.x , player_shots.y,
        c="red",
        s=40,
        alpha=player_shots["outcome_name"].eq("Goal").map({True: 1, False: 0.2})
    )
    #x.arrows(player_passes.x, player_passes.y, player_passes.end.dx, player_passes.end.dy,  color = "blue")
    for _, p in player_passes.iterrows():
        ax.arrow(
            p['x'], p['y'],   # Startpunkt
            p['dx'], p['dy'], # Differenz zum Endpunkt
            width=0.4,
            head_width=2.5,    
            color="blue",
            alpha=0.8,
            length_includes_head=True)
    pitch.scatter(player_passes.x, player_passes.y, alpha = 0.2, s = 500, color = "blue" , ax = ax)

    # Titel setzen
    fig.suptitle(f"{player_name} shots and passes", fontsize=24)
    plt.savefig("pass_plot_" + player_name + ".png")   # speichert im aktuellen Arbeitsverzeichnis 
    plt.show()
    







