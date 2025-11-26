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
team_name_current = euro_2024_matches_current_team[
    euro_2024_matches_current_team['home_team_id'] == team_id_current ]["home_team_name"].unique()[0]
team_name_current

#A dataframe of shots
shots = df.loc[df['type_name'] == 'Shot'].set_index('id')
    
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
    """
    # Schüsse dieses Spielers
    player_shots = shots_self[shots_self["player_id"] == player_id]
    player_name = player_shots["player_name"].unique()[0]

    # Pitch erstellen
    pitch = VerticalPitch(line_color='black', half=True)
    fig, ax = pitch.grid(grid_height=0.9, title_height=0.06, axis=False,
                         endnote_height=0.04, title_space=0, endnote_space=0)

    # Plotten der Shots
    ax.scatter(
        player_shots["x_plot"], player_shots["y_plot"],
        c="red",
        s=40,
        alpha=player_shots["outcome_name"].eq("Goal").map({True: 1, False: 0.2})
    )

    # Titel setzen
    fig.suptitle(f"{player_name} shots", fontsize=24)

    plt.show()    
    """
"""
pitch = VerticalPitch(line_color='black', half = True)
fig, ax = pitch.grid(grid_height=0.9, title_height=0.06, axis=False,
                     endnote_height=0.04, title_space=0, endnote_space=0)
#plotting all shots
pitch.scatter(df_england.x, df_england.y, alpha = 1, s = 500, color = "red", ax=ax['pitch'], edgecolors="black") 
fig.suptitle("England shots against Sweden", fontsize = 30)           
plt.show()

##############################################################################
# Challenge - try it before looking at the next page
# ----------------------------
# 1) Create a dataframe of passes which contains all the passes in the match
# 2) Plot the start point of every Sweden pass. Attacking left to right.
# 3) Plot only passes made by Caroline Seger (she is Sara Caroline Seger in the database)
# 4) Plot arrows to show where the passes went to.

"""