import sqlite3
import pandas as pd
import numpy as np

#function to make dataframes from sql database

def make_sql_frame(sql):
    """
    Recieves an SQL command to retrieve
    information from our database
    and places the information in
    a pandas dataFrame
    """
    conn = sqlite3.connect("./database.sqlite")
    c = conn.cursor()
    c.execute(sql)
    df = pd.DataFrame(c.fetchall())
    df.columns = [x[0] for x in c.description]
    return df


#function that takes in a dataFrame and sample size and returns the means
def sample_mean(dataFrame, sample_size):
    sample = np.random.choice(dataFrame, size=sample_size, replace=True)
    return sample.mean()


#funcion that adds a binary value for Home Wins, Losses, Draws 
#given a soccer match with no result but with goals for each side

def add_results(dataFrame):
    dataFrame['HomeWin'] = 0
    dataFrame['AwayWin'] = 0
    dataFrame['Draw'] = 0
    dataFrame.loc[dataFrame['home_team_goal'] > dataFrame['away_team_goal'], "HomeWin"] = 1
    dataFrame.loc[dataFrame['home_team_goal'] < dataFrame['away_team_goal'], "AwayWin"] = 1
    dataFrame.loc[dataFrame['home_team_goal'] == dataFrame['away_team_goal'], "Draw"] = 1
    return dataFrame

#Calculates Team Win Percantages, Home, Away and Total
def calc_wins(dataFrame):   
    #Calculating Wins as Home Team and Win Percentage as Home Team
    HomeTeamWins = dataFrame.groupby(['home_team'])['HomeWin', 'AwayWin', 'Draw'].sum()
    HomeTeamWins['HomeWinPct'] = HomeTeamWins['HomeWin'] / (HomeTeamWins['HomeWin'] + HomeTeamWins['AwayWin'] + HomeTeamWins['Draw'])
    HomeTeamWins.rename(columns = {"AwayWin" : "HomeLoss", "Draw": "HomeDraw"}, inplace = True)
    
    #Calculating Wins as Away Team and Win Percentage as Away Team
    AwayTeamWins = dataFrame.groupby(['away_team'])['HomeWin', 'AwayWin', 'Draw'].sum()
    AwayTeamWins['AwayWinPct'] = AwayTeamWins['AwayWin'] / (AwayTeamWins['HomeWin'] + AwayTeamWins['AwayWin'] + AwayTeamWins['Draw'])
    AwayTeamWins.rename(columns = {"HomeWin" : "AwayLoss", "Draw" : "AwayDraw"}, inplace = True) 

    #Adding Both Wins DataFrames into a single DataFrame
    TeamWinFrame = pd.concat([HomeTeamWins,AwayTeamWins], axis =1)

    #Calculating Total Wins and Win Percentage for Each Team
    TeamWinFrame['TotalWins'] = TeamWinFrame['HomeWin'] + TeamWinFrame['AwayWin']
    TeamWinFrame['TotalLosses'] = TeamWinFrame['HomeLoss'] + TeamWinFrame['AwayLoss']
    TeamWinFrame['TotalDraws'] = TeamWinFrame['HomeDraw'] + TeamWinFrame['AwayDraw']
    TeamWinFrame['GamesPlayed'] = TeamWinFrame['TotalWins'] + TeamWinFrame['TotalLosses'] + TeamWinFrame['TotalDraws']
    TeamWinFrame['TotalWinPct'] = TeamWinFrame['TotalWins'] / TeamWinFrame['GamesPlayed']
    TeamWinFrame.reset_index(inplace = True)
    TeamWinFrame.rename(columns = {"index": "TeamName"}, inplace = True)
    
    return TeamWinFrame


#function to add wins, losses, draws to team objects

def get_results(teamDict, dataFrame, result):
    """
    Checks a dataFrame for the desired result
    Iterates through the dataFrame and populates
    the dictionary of Team objects with the
    information in the dataFrame
    """
    
    df_adjusted = dataFrame.loc[dataFrame['Match_Result'] == result]
    for index, row in df_adjusted.iterrows():
        away_name = row['AwayTeam']
        home_name = row['HomeTeam']
        away_goals = row['Away_Goals']
        home_goals = row['Home_Goals']
        for team in teamDict:
            if team == away_name:
                teamDict[team].add_goals(away_goals)
                if(result == 'A'):
                    teamDict[team].add_win()
                elif(result == 'H'):
                    teamDict[team].add_loss()
                else:
                    teamDict[team].add_draw()
            elif team == home_name:
                teamDict[team].add_goals(home_goals)
                if(result == 'A'):
                    teamDict[team].add_loss()
                elif(result == 'H'):
                    teamDict[team].add_win()
                else:
                    teamDict[team].add_draw()

