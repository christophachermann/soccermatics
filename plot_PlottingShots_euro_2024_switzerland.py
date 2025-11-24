"""
Plotting shots
==============

Start by watching the video below, then learn how to plot shot positions.

..  youtube:: GWsK_KWKCas
   :width: 640
   :height: 349

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


parser = Sbopen()
# list of competitions
free_competitions = parser.competition()
# eine _Liste aller Spiele der EM 2024
euro_2024_matches = parser.match(competition_id = 55, season_id = 282)
#alle Spiele der Schweiz; team_id=773
team_id_current = 773
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
# Making the shot map using iterative solution
# ----------------------------
# First let's draw the pitch using the `MPL Soccer class <https://mplsoccer.readthedocs.io/en/latest/gallery/pitch_setup/plot_pitches.html>`_,
#
# In this example, we set variables for pitch length and width to the Statsbomb coordinate system (they use yards).
# You can read more about `different coordinate systems here <https://mplsoccer.readthedocs.io/en/latest/gallery/pitch_setup/plot_compare_pitches.html>`_
#
# Now, we iterate through all the shots in the match. We take *x* and *y* coordinates, the team name and information
# if goal was scored. If It was scored, we plot a solid circle with a name of the player, if not, we plot a
# transculent circle (parameter alpha tunes the transcluency).
# To have England's shots on one half and Sweden shots on the other half,
# we subtract *x* and *y* from the pitch length and height.
#
# Football data tends to be attacking left to right, and we will use this as default in the course.

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

