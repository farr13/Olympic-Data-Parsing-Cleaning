import csv
import itertools as itr
from datetime import datetime
ATHLETE_EVENT_FILE = "olympic_athlete_event_results.csv"
ATHLETE_BIO_FILE = "olympic_athlete_bio.csv"
OLYMPIC_GAMES_FILE = "olympics_games.csv"
OLYMPIC_COUNTRIES = "olympics_country.csv"
MONTHS = {
    "jan": 1, "january": 1,
    "feb": 2, "february": 2,
    "mar": 3, "march": 3,
    "apr": 4, "april": 4,
    "may": 5,
    "jun": 6, "june": 6,
    "jul": 7, "july": 7,
    "aug": 8, "august": 8,
    "sep": 9, "september": 9,
    "oct": 10, "october": 10,
    "nov": 11, "november": 11,
    "dec": 12, "december": 12
}

#Note: You should sort the dictionaries so you can use binary serach on them later to cut down on runtime
#__________________________________________
#ADDING TO OLYMPIC ATHLETE EVEENT CSV START
#__________________________________________
def normalize_game_name(name):
    return name.replace("Olympics", "").replace("Games", "").strip()

def create_age_dict():
    """
    Creates a dictionary containing the athleet id as key, and a list with the atlete date of birth, 
    and all thr games they have participated in

    Args:

    Returns:
        dictionary of athlete info
    """
    athlete_info = {} #will contains index 0 : athlete id, 1 - 3 : mm/dd/yy, 4 - onward : games played in
    with open(ATHLETE_BIO_FILE, 'r', encoding="utf-8") as bioCSV:
        reader = csv.reader(bioCSV) 
        bioCSV.readline() #skips first line
        for row in reader:
            #Adds all the atheltes id and born column into a dictionary
            athlete_info[row[0]] = row[3]

    for id, value in athlete_info.items():
        #splits based on the format of the born column
        if '-' in value:
            year = value.split('-')
        else:
            year = value.split(' ')
        athlete_info[id] = year

    with open(ATHLETE_EVENT_FILE, 'r', encoding="utf-8") as eventCSV:
        eventCSV.readline() #skips first line
        reader = csv.reader(eventCSV)
        for row in reader:
            #Adds the games the athlete participates in after 3rd index
            if row[7] in athlete_info:
                normalized_game = normalize_game_name(row[0]) # fix name
                athlete_info[row[7]].append(normalized_game)

    return athlete_info

def create_games_dict():
    """
    Creates a dictionary containing the game as the key and the date duration of the 
    game corresponding to the key

    Args:

    Returns:
        dict: games info
    """
    games_date = {}#will contains index 0 : game 1 : games date

    with open(OLYMPIC_GAMES_FILE, 'r', encoding="utf-8") as gameCSV:
        reader = csv.reader(gameCSV)
        gameCSV.readline() #skips first line
        for row in reader:
            #Adds all olympic games and there dates
            games_date[normalize_game_name(row[0]) ] = row[9]

    return games_date

def parse_game_duration(s):
    # Normalize dashes and spacing
    s = s.replace("–", "-")
    
    # Split into start and end parts
    start_part, end_part = [p.strip() for p in s.split("-")]

    # Split tokens
    start_tokens = start_part.split()
    end_tokens = end_part.split()

    # CASE 1: Format "6 July – 12 August"
    if len(start_tokens) == 2:  
        start_day = start_tokens[0]
        start_month = start_tokens[1].lower()
        
        end_day = end_tokens[0]
        end_month = end_tokens[1].lower()
    
    # CASE 2: Format "6 – 12 August"
    else:
        # Only a day at the start → month comes from end part
        start_day = start_tokens[0]
        end_day = end_tokens[0]
        end_month = end_tokens[1].lower()
        start_month = end_month   # same month
        
    return [start_day, start_month, end_day, end_month]

def calculate_age(game_duration, athlete_birth, game_year):
    game_duration = parse_game_duration(game_duration)
    game_year = int(game_year.split(' ')[0])
    if athlete_birth[1].lower() in MONTHS:
        start_date = datetime(game_year, MONTHS[game_duration[1].lower()], int(game_duration[0]))
        end_date = datetime(game_year, MONTHS[game_duration[3].lower()], int(game_duration[2]))
        athlete_year = int(athlete_birth[2])
        if athlete_year < 100:
            athlete_year += 1900
        athlete_date = datetime(athlete_year, MONTHS[athlete_birth[1].lower()], int(athlete_birth[0]))
    else:
        return 0 #Failed calculate age due to bad data
    
    age = (((start_date - athlete_date)/ 365).days)

    if start_date <= athlete_date <= end_date:
        age -= 1

    return age

def add_athlete_to_games_dict(games_date, athlete_info):
    """
    Creates a dictionary containt olympic games as the key and a dictionary of athletes ids and 
    there age corresponsgin to that game as the items

    Args:
        str: Game date duration
        lst[str]: athlete birthday
        str: olympic game containing year
    Returns:
        dict: olypmic games and coressponding athlete ages
    """
    #A dict containing all games during olympics and empty dicts that will contain athlete id and age
    athlete_age_during_game = {key: {} for key in games_date.keys()}

    for athlete_id in athlete_info:
        athletes_birth_and_games = athlete_info[athlete_id]

        for i in range(3, len(athletes_birth_and_games)): #Games begin at index 3
            if athletes_birth_and_games[i] not in games_date:
                #print(f"WARNING: Game '{athletes_birth_and_games[i]}' not found in games_date.")
                pass
            else:
                game_duration = games_date[athletes_birth_and_games[i]]
                athlete_birth = athletes_birth_and_games[:3] #Athlete birth from index 0 - 2
                game_year = athletes_birth_and_games[i]
                athlete_age = calculate_age(game_duration, athlete_birth, game_year)
                if athlete_age == 0:
                    athlete_age_during_game[athletes_birth_and_games[i]][athlete_id] = "N/A"
                else:
                    athlete_age_during_game[athletes_birth_and_games[i]][athlete_id] = athlete_age   
    return athlete_age_during_game

def add_age_to_athelete(athlete_ages):
    """This function parses througth the olympic_athlete_event_results.csv and 
    adds an age column to every athelte"""

    old_file = "olympic_athlete_event_results.csv"
    new_file = "new_olympic_athlete_event_results.csv"

    with open(old_file, newline='', encoding='utf-8') as infile, \
        open(new_file, "w", newline='', encoding='utf-8') as outfile:

        reader = csv.DictReader(infile)
        fieldnames = reader.fieldnames + ["age"]

        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()

        for row in reader:

            game = row["\ufeffedition"].replace("Olympics", "").strip()
            id = row["athlete_id"]
            if (game in athlete_ages):
                if(id in athlete_ages[game]):
                    row["age"] = athlete_ages[game][id]
            else:
                row["age"] = "N/A"

            writer.writerow(row)
    print(f"CSV file '{new_file}' created successfully.")
#________________________________________
#ADDING TO OLYMPIC ATHLETE EVEENT CSV END
#________________________________________

#___________________________
#CREATING SUMMARY FILE START
#___________________________

def parse_olympics_country():
    noc_to_country = {}
    with open(OLYMPIC_COUNTRIES, 'r', newline='', encoding='utf-8') as countries_csv:
        reader = csv.reader(countries_csv) 
        for row in reader:
            noc_to_country[row[0]] = row[1]
    return noc_to_country

def tally_event_info(countries):
    event_tally = {}
    with open(ATHLETE_EVENT_FILE, 'r', newline='', encoding='utf-8') as event_csv:
        reader = csv.DictReader(event_csv)
        for row in reader:
            if row["edition_id"] not in event_tally:
                event_tally[row["edition_id"]] = {
                    "edition": row["\ufeffedition"],
                    "country": countries[row["country_noc"]],
                    "country_noc": row["country_noc"],
                    "number_of_athletes": 0,
                    "gold_medal_count": 0,
                    "silver_medal_count": 0,
                    "bronze_medal_count": 0,
                    "total_medals": 0
                }
            event_tally[row["edition_id"]]["number_of_athletes"] += 1
            if row["medal"] == "Gold":
                event_tally[row["edition_id"]]["gold_medal_count"] += 1
                event_tally[row["edition_id"]]["total_medals"] += 1

            elif row["medal"] == "Silver":
                event_tally[row["edition_id"]]["silver_medal_count"] += 1
                event_tally[row["edition_id"]]["total_medals"] += 1

            elif row["medal"] == "Bronze":
                event_tally[row["edition_id"]]["bronze_medal_count"] += 1
                event_tally[row["edition_id"]]["total_medals"] += 1

    return event_tally

def add_results_to_summary(tally):
    filename = "new_medal_tally.csv"
    headers = ["edition", "edition_id", "Country", "NOC", "number_of_athletes", 
               "gold_medal_count", "silver_medal_count", "bronze_medal_count", "total_medals"]
    with open(filename, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(headers)
        for id in tally:
            summary_info = tally[id]
            writer.writerow([summary_info["edition"], 
                                id, summary_info["country"], 
                                summary_info["country_noc"], 
                                summary_info["number_of_athletes"], 
                                summary_info["gold_medal_count"], 
                                summary_info["silver_medal_count"], 
                                summary_info["bronze_medal_count"],
                                summary_info["total_medals"]])


    print(f"CSV file '{filename}' created successfully.")
#_________________________
#CREATING SUMMARY FILE END
#_________________________

def task3_main():

#Fucntions used to add age
    athlete = create_age_dict()
    games = create_games_dict()
    athlete_ages = add_athlete_to_games_dict(games, athlete)
    add_age_to_athelete(athlete_ages)

#Functions used to summarize tallies
    countries = parse_olympics_country()
    tally = tally_event_info(countries)
    add_results_to_summary(tally)

task3_main()
