import os, time
import selenium
from selenium import webdriver
from pathlib import Path
from string import ascii_lowercase
import pandas as pd

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


# start browser crawler --> Windows users: make sure you know where chromedriver.exe file is
browser = webdriver.Chrome(r'C:\Users\davil\Desktop\NYCDSA_Bootcamp\bootcamp\July_Course\chromedriver_win32\chromedriver.exe')

################## functions to scrape players bios on bballref ##########################
#must loop through alphabet as players are grouped and separated by first letter of last name
def scrapeBbalRefPlayers(page_string: object, 
	id: object, folder_name: object) -> object:
	for letter in ascii_lowercase:
		#note that no player in history of NBA has last name that starts with 'X'
		if letter == 'x':
			continue
		else:
			# navigate to bballref
			url = page_string.replace("*LETTER*", str(letter))
			browser.get(url)

			# setup id strings
			csv_id = "csv_" + id

			# extract values raw_CSV
			raw_csv = browser.execute_script(
				'''var x = document.getElementsByClassName("tooltip");
				x[3].click();
				var content = document.getElementById("'''+ csv_id +'''")		
				return content.textContent
				''')
			#print(raw_csv)		

			# write to CSV in desired folder
			pathstr = Path(folder_name,f"{letter}_{id}.csv")
			f = open(pathstr, "w", encoding="utf-8")
			f.write(raw_csv)

## bring in player_id list for following module

df = pd.read_csv('df_for_model.csv')
x = df.groupby(['Player_ID','Player_Name']).count().reset_index()[['Player_ID','Player_Name']]
x['index'] = x['Player_ID'].str[0]
id_name_dict = dict(zip(x['Player_ID'],x['Player_Name']))
l = []
for i in id_name_dict:
   l.append(i)

############ function to scrape players bio pages (not indexes) bballref ##################
#must loop through alphabet as players are grouped and separated by first letter of last name

def scrapeBbalRefPlayerShooting(page_string: object, 
	id: object, folder_name: object) -> object:
	for letter in ascii_lowercase:
		#note that no player in history of NBA has last name that starts with 'X'
		if letter == 'x':
			continue
		else: 
			# navigate to bballref
			for player_i in l:
				if letter == player_i[:1]:
					try:
						url = page_string.replace("*LETTER*", str(letter))
						url = url.replace("*PLAYER*", str(player_i))
						browser.get(url)

						# setup id strings
						csv_id = "csv_" + id

						raw_csv = browser.execute_script(
							'''
							var x = document.getElementById("all_shooting").getElementsByClassName("tooltip");
							x[3].click();
							var content = document.getElementById("'''+ csv_id +'''")
							return content.textContent
							''')
						print(raw_csv)
						# write to CSV in desired folder
						pathstr = Path(folder_name,f"{player_i}_{id}.csv")
						f = open(pathstr, "w", encoding="utf-8")
						f.write(raw_csv)
					except:
						continue
				else:
					continue

scrapeBbalRefPlayerShooting(
	page_string='https://www.basketball-reference.com/players/*LETTER*/*PLAYER*.html',
	id='shooting',
	folder_name='season_shooting'
)


def scrapeBbalRefPlayerSalaries(page_string: object, 
	id: object, folder_name: object) -> object:
	for letter in ascii_lowercase:
		#note that no player in history of NBA has last name that starts with 'X'
		if letter == 'x':
			continue
		else: 
			# navigate to bballref
			for player_i in l:
				if letter == player_i[:1]:
					try:
						url = page_string.replace("*LETTER*", str(letter))
						url = url.replace("*PLAYER*", str(player_i))
						browser.get(url)

						# setup id strings
						csv_id = "csv_" + id

						raw_csv = browser.execute_script(
							'''
							var x = document.getElementById("all_all_salaries").getElementsByClassName("tooltip");
							x[3].click();
							var content = document.getElementById("'''+ csv_id +'''")
							return content.textContent
							''')
						print(raw_csv)
						# write to CSV in desired folder
						pathstr = Path(folder_name,f"{player_i}_{id}.csv")
						f = open(pathstr, "w", encoding="utf-8")
						f.write(raw_csv)
					except:
						continue
				else:
					continue

scrapeBbalRefPlayerSalaries(
	page_string='https://www.basketball-reference.com/players/*LETTER*/*PLAYER*.html',
	id='all_salaries',
	folder_name='salaries'
)


################ function to scrape NBA and ABA champions ################################
# no need to loop through seasons --> all seasons are included on one page
def scrapeBbalRefChamps(page_string: object, id: object, folder_name: object) -> object:
	# navigate to bballref
	browser.get(page_string)

	# id string for grabbing csv values
	csv_id = "csv_" + id

	# extract values raw_CSV
	raw_csv = browser.execute_script('''var x = document.getElementsByClassName("tooltip");
	x[3].click();
	var content = document.getElementById("'''+ csv_id +'''")
	return content.textContent
	''')
	print(raw_csv)

	# write to CSV
	pathstr = Path(folder_name,f"{id}.csv")

	f = open(pathstr, "w", encoding="utf-8")
	f.write(raw_csv)

	browser.close()

scrapeBbalRefChamps(page_string = "https://www.basketball-reference.com/playoffs/",
	id = 'champions_index',
	folder_name = 'champs')

########### Function to loop through links designated by season and scrape relevant stats ###############
def scrapeBbalRef(year_start: object, year_end: object, page_string: object, id: object, folder_name: object, toggle_partial: object = True) -> object:

	for season in range(year_start, year_end+1):
		# navigate to bballref
		url = page_string.replace("*SEASON*", str(season))
		browser.get(url)

		# setup id strings
		partial_id = id + "_toggle_partial_table"
		csv_id = "csv_" + id

		# toggle to show all teams a player who changed teams during season played for
		if toggle_partial:
			browser.execute_script('document.getElementById("'+ partial_id +'").click();')

		# extract values for raw_CSV
		raw_csv = browser.execute_script('''var x = document.getElementsByClassName("tooltip");
			x[3].click();
			var content = document.getElementById("'''+ csv_id +'''")
			// different element id in some older MVP pages
			if (content==null) {
				var content = document.getElementById("csv_mvp")
				}
			return content.textContent
			''')
		raw_csv		

		# clean csv string
		## get rid of false headers
		if page_string == 'https://www.basketball-reference.com/awards/awards_*SEASON*.html' or \
						page_string == 'https://www.basketball-reference.com/leagues/NBA_*SEASON*_standings.html':
			raw_csv = '\n'.join(raw_csv.split('\n')[2:])
		## remove special characters from standings
		raw_csv=raw_csv.replace("\u2264","")
		raw_csv=raw_csv.replace("\u2265","")


		# write to CSV
		pathstr = Path(folder_name,f"{season}_{id}.csv")
		f = open(pathstr, "w", encoding="utf-8")
		f.write(raw_csv)

### Using function to....
scrape season player stat per game
scrapeBbalRef(year_start=1950, year_end=2019,
	page_string='https://www.basketball-reference.com/leagues/NBA_*SEASON*_per_game.html',
	id='per_game_stats',
	folder_name='season_stats_pergame'
	)
# scrape season player stat totals
scrapeBbalRef(year_start=1950,year_end=2019,
	page_string='https://www.basketball-reference.com/leagues/NBA_*SEASON*_totals.html',
	id='totals_stats',
	folder_name='season_stats_totals'
	)
# scrape season advanced player stats
scrapeBbalRef(year_start=1950,year_end=2019,
	page_string='https://www.basketball-reference.com/leagues/NBA_*SEASON*_advanced.html',
	id='advanced_stats',
	folder_name='season_stats_advanced'
	)
# scrape MVP stats
scrapeBbalRef(year_start=1956,year_end=2019,
	page_string='https://www.basketball-reference.com/awards/awards_*SEASON*.html',
	id='nba_mvp',
	folder_name='award_stats',
	toggle_partial=False
	)
# scrape standings stats
scrapeBbalRef(year_start=1950,year_end=2019,
	page_string='https://www.basketball-reference.com/leagues/NBA_*SEASON*_standings.html',
	id='expanded_standings',
	folder_name='season_standings',
	toggle_partial=False
	)
# scrape playoffs player stats per game
scrapeBbalRef(year_start=1950, year_end=2019,
	page_string='https://www.basketball-reference.com/playoffs/NBA_*SEASON*_per_game.html',
	id='per_game_stats',
	folder_name='playoffs_stats_pergame',
	toggle_partial=False
	)
#scrape playoffs player stats totals
scrapeBbalRef(year_start=1950,year_end=2019,
	page_string='https://www.basketball-reference.com/playoffs/NBA_*SEASON*_totals.html',
	id='totals_stats',
	folder_name='playoffs_stats_totals',
	toggle_partial=False
	)
#scrape playoffs advanced player stats
scrapeBbalRef(year_start=1950,year_end=2019,
	page_string='https://www.basketball-reference.com/playoffs/NBA_*SEASON*_advanced.html',
	id='advanced_stats',
	folder_name='playoffs_stats_advanced',
	toggle_partial=False
	)
scrapeBbalRef(year_start=1974,year_end=2019,
	page_string='https://www.basketball-reference.com/leagues/NBA_*SEASON*_per_poss.html',
	id='per_poss_stats',
	folder_name='season_per100',
	toggle_partial=False
	)

scrape playoffs per 100 poss
scrapeBbalRef(year_start=1974,year_end=2019,
	page_string='https://www.basketball-reference.com/playoffs/NBA_*SEASON*_per_poss.html',
	id='per_poss_stats',
	folder_name='playoffs_per100',
	toggle_partial=False
	)


################ function to scrape NBA and ABA champions ################################
# no need to loop through seasons --> all seasons are included on one page
def scrapeBbalRefChamps(page_string: object, id: object, folder_name: object) -> object:
	# navigate to bballref
	browser.get(page_string)

	# id string for grabbing csv values
	csv_id = "csv_" + id

	# grab raw CSV
	raw_csv = browser.execute_script('''var x = document.getElementsByClassName("tooltip");
		x[3].click();
		var content = document.getElementById("'''+ csv_id +'''")		
		return content.textContent
		''')
	#deleting extra row abover header columns
	raw_csv = '\n'.join(raw_csv.split('\n')[2:])
	print(raw_csv)		

	# write to CSV
	pathstr = Path(folder_name,f"{id}.csv")

	f = open(pathstr, "w", encoding="utf-8")
	f.write(raw_csv)

	browser.close()

scrapeBbalRefChamps(page_string = "https://www.basketball-reference.com/playoffs/",
	id = 'champions_index',
	folder_name = 'champs')