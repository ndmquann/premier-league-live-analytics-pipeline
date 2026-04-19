from app.db.database import (
    get_today_matches_and_scores,
    get_standings,
    get_liverpool_points,
)
import pandas as pd
import streamlit as st

standings = pd.DataFrame(
                data=get_standings(),
                columns=[
                    "position",
                    "team_name",
                    "played_games",
                    "won",
                    "draw",
                    "lost",
                    "points",
                    "goals_for",
                    "goals_against",
                    "goal_difference"
                ]
)

matches = pd.DataFrame(
                data=get_today_matches_and_scores(),
                columns=[
                    "utc_date",
                    "status",
                    "matchday",
                    "home_team_name",
                    "away_team_name",
                    "home_team_score",
                    "away_team_score"
                ]
)

st.title("Premier League Dashboard")

st.header("Liverpool FC")
liverpool = get_liverpool_points()
col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("Position", f"#{liverpool['position']}")
col2.metric("Points", liverpool['points'])
col3.metric("Played Games", liverpool['played_games'])
col4.metric("Won", liverpool['won'], delta=liverpool['won'])
col5.metric("Lost", liverpool['lost'], delta=-liverpool['lost'])

st.header("Today's Matches")
st.dataframe(matches, use_container_width=True)

st.header("Standings")
st.dataframe(standings, use_container_width=True)