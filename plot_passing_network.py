# -*- coding: utf-8 -*-
"""
Created on Sun Nov 30 21:26:31 2025

@author: christoph.achermann@gmail.com
Plot passing network for games until first substitution

1st calculate mean passing positione for every player
2nd plot graph, with mean passing positions as verteces
and lines between them as edges.
size of edges represent the number of passes in the game
"""


import matplotlib.pyplot as plt
import numpy as np
import pandas
from mplsoccer import Pitch, Sbopen, VerticalPitch
import pandas as pd
import datetime

def get_mean_passing_positions (indata):
    return(0)

def get_earliest_substitution (indata):
    df_subs = indata[indata["type_name"] == "Substitution"]
    earliest_sub = df_subs.minute.min()
    return(earliest_sub)
    
def get_passnetwork_before_sub (indata):
    teams = indata["team_id"].unique()
    
    team_list = []
    for current_team in teams:
        df_current_team = indata[indata["team_id"] == current_team]
        earliest_sub = df_current_team.pipe(get_earliest_substitution)
        df_before_substitution  = df_current_team[df_current_team["minute"] <= earliest_sub]
        df_pass_events = df_before_substitution[(df_before_substitution["type_name"] == "Pass") ]
        
        df_player_pos = df_pass_events.groupby(["player_id", "player_name"]).agg({
            "x" : "mean",
            "y" : "mean"
            }).reset_index() 
        
        df_pass_list = df_pass_events.groupby(["player_id", "player_name", "pass_recipient_id", "pass_recipient_name"]).size().reset_index(name = "anzahl_paesse")
        df_pass_network = df_pass_list.merge(df_player_pos, how="left", left_on=["player_id","player_name"], right_on = ["player_id","player_name"])
        df_pass_network = df_pass_network.merge(df_player_pos, how="left", left_on=["pass_recipient_id", "pass_recipient_name"], right_on = ["player_id","player_name"], suffixes = ["_player", "_recipient"])
        df_pass_network["team_id"] = current_team
        df_pass_network["match_id"] = indata["match_id"].unique()[0]
        df_pass_network["paesse_zeit_normiert"] = df_pass_network["anzahl_paesse"] / earliest_sub * 90
        df_pass_network["first_sub_minute"] = earliest_sub
        df_pass_network["dx"] = df_pass_network["x_recipient"] - df_pass_network["x_player"]
        df_pass_network["dy"] = df_pass_network["y_recipient"] - df_pass_network["y_player"]
        df_pass_network["team_name"] = df_current_team["team_name"].unique()[0]
        team_list.append(df_pass_network) 
    
    outdata = pd.concat([team_list[0], team_list[1]], ignore_index=True)
    
    return outdata

df_game_pass_network = get_passnetwork_before_sub(df)

for team_id in df_game_pass_network["team_id"].unique():
    df_network_map_current_team = df_game_pass_network[df_game_pass_network["team_id"]==team_id]
    current_team_name = df_network_map_current_team["team_name"].unique()[0]
    # draw player on pitch
    pitch = Pitch(line_color = "black")
    fig, ax = pitch.draw(figsize=(10, 7))
    #Size of the pitch in yards (!!!)
    pitchLengthX = 120
    pitchWidthY = 80
    df_player_pos = df_network_map_current_team[["player_id_player", "player_name_player", "x_player", "y_player"]].drop_duplicates()
    ax.scatter(
        df_player_pos["x_player"], df_player_pos["y_player"],
        c="red",
        s=40,                          # circleSize²
        alpha=1)
    
    # Spielerlabels hinzufügen
    dx = np.random.uniform(-1, 1)
    dy = np.random.uniform(0.5, 1.5)
    for _, row in df_player_pos.iterrows():
        ax.text(
            row["x_player"] + dx,
            row["y_player"] + dy,
            row["player_name_player"],
            fontsize=9,
            color="black",
            ha="center",
            va="center"
        )
    #fig.suptitle(f"{team_} (red) and Opponent (blue) shots", fontsize=24)    
    #fig.set_size_inches(10, 7)
    
    # Jetzt die Passpfeile zeichnen
    var_mindest_pass_zahl = 8
    df_network_map_current_team_draw =  df_network_map_current_team[df_network_map_current_team["paesse_zeit_normiert"] >= var_mindest_pass_zahl ]
    for _, row in df_network_map_current_team_draw.iterrows():

        x0 = row["x_player"]
        y0 = row["y_player"]
        dx = row["dx"]
        dy = row["dy"]
        width = row["paesse_zeit_normiert"] * 0.2   # Faktor anpassen für Dicke

        ax.arrow(
            x0, y0,
            dx, dy,
            head_width=1.5,        # Größe der Pfeilspitze
            length_includes_head=True,
            color="red",
            alpha=0.7,
            linewidth=0,
            width=.1             # Linienbreite = Pass-Stärke
        )
    plt.savefig("pass_network_" + current_team_name + ".png")
    plt.show()


