# Import and read data 
import pandas as pd
from plotting import *
from scipy import stats

def load_data() -> pd.DataFrame:
    df = pd.read_csv('dancedata.csv', encoding='latin1')
    print(df.head(10))
    return df

# Data Cleaning
def data_cleaning(df) -> pd.DataFrame:

    # replaces instances of USA with United States -> consitency 
    df['Origin'] = df['Origin'].replace('USA', 'United States')

    # makes all the letters in the "Associated Music Genre" column lowercase to avoid duplicates like "Latin" and "latin"
    df["Associated Music Genre"] = df["Associated Music Genre"].str.lower()

    # remove every music like latin music to latin
    df['Associated Music Genre'] = df['Associated Music Genre'].str.replace(r'\s*music\s*', '', regex=True)
    df['Associated Music Genre'] = df['Associated Music Genre'].str.replace(r'\s*dance\s*', '', regex=True)

    # map associated music genres together like hip-hop and hip hop
    df['Associated Music Genre'] = df['Associated Music Genre'].replace({'hip-hop': 'hip hop'})

    # cleaning end
    return df


def tempo_categorization(df) -> pd.DataFrame:
    
    # t test if speed of bpm is normally distributed
    bpm = df["Tempo (BPM)"]
    k2, p = stats.normaltest(bpm)
    print(f"p-value for normality test: {p}")
    if p < 0.05:
        print("The distribution of BPM is not normal.")

    # used to determine the distrubition of BPM and to determine the categorization of tempos
    plot_histogramm(df, "Tempo (BPM)", "Tempo (BPM)", 200)

    # use descriptive statistics to determine categorization of tempos
    low_cutoff = df['Tempo (BPM)'].quantile(0.33) 
    high_cutoff = df['Tempo (BPM)'].quantile(0.66)

    # categorization of tempos into 3 categories: Slow, Medium, Fast
    df["Tempo Category"] = ""
    df.loc[df["Tempo (BPM)"] < low_cutoff, "Tempo Category"] = "Slow"
    df.loc[(df["Tempo (BPM)"] >= low_cutoff) & (df["Tempo (BPM)"] <= high_cutoff), "Tempo Category"] = "Medium"
    df.loc[df["Tempo (BPM)"] > high_cutoff, "Tempo Category"] = "Fast"

    plot_tempo_distribution_with_categories(df, low_cutoff, high_cutoff)

    print(df["Tempo Category"].value_counts())

    return df

#User input 

def user_numeric_input(prompt, min_value, max_value) -> int:
    num = None
    while True: # loop until a valid input is received
        num_str = input(prompt)
        if num_str.isdigit() and int(num_str) >= min_value and int(num_str) <= max_value: # check if the input is a digit and within the bounds
            num = int(num_str)
            break # exit the loop if a valid input is received
        else:
            print(f"Please enter a valid integer between {min_value} and {max_value}.")

    return num

# menu selection for user input with options, returns the index of the selected option
def user_input_options_menu(choices):
    if len(choices) == 1: # if there is only one option, return option
        print(f"Only one option available: {choices[0]}")
        return 0
    print("Available options:")
    for i in range(len(choices)): # print options with indexes
        print(f"{i + 1}. {choices[i]}") # i + 1 makes so that the outputed list starts counting from 1 instead of 0
    # use input function one to get a valid user choice in the correct interval
    return int(user_numeric_input("Select the number corresponding to your preferred option: ", 1, len(choices))) - 1 # adjusting for 0-based normalization

# dataset is filtered based on user preferences (country, intensity level, duration)
def filter_dataset_by_user_preferences(df) -> pd.DataFrame | dict: # returns the filtered dataset and a dictionary of user preferences for later use
    # simultaneously doing user input and data filtering to avoid printing countries that don't have dances of the selected intensity level 
    
    duration = user_numeric_input("Enter duration of workout in minutes: ", min_value=5, max_value=120)

    print("Select intensity level:")
    intensity_level = user_input_options_menu(["low", "medium", "high"])
    print(f"Selected intensity level: {['low', 'medium', 'high'][intensity_level]}")

    # mapping the intensity level to the corresponding tempo category
    intensity_level_to_tempo = {0: "Slow", 1: "Medium", 2: "Fast"}
    df = df[df["Tempo Category"] == intensity_level_to_tempo[intensity_level]]

    print("Select origin country:")
    countries = df["Origin"].unique() # use unique to print country only once 
    # df[df['Origin'] == country].shape[0] - gives the number of available dances for the country
    country = user_input_options_menu([f"{country} ({df[df['Origin'] == country].shape[0]})" for country in countries])
    
    # remove dances from the dataset that do not match the selected country
    df = df[df["Origin"] == countries[country]]

    return df, {"duration": duration, "intensity_level": intensity_level, "country": countries[country]} # preferences are returned as a dictionary


def generate_workout(df, country, intensity_level, duration) -> pd.DataFrame:    
    
    if df_filtered.empty:
        print("No dances found for the selected country and intensity level.")
        return
    
    selected_dances = [] 
    total_duration = 0
    message_printed = False

    while total_duration < duration: # total duration is the combined duration of the selected dances, duration is the user input

        df_filtered = df_filtered.sample(frac=1, random_state=11)  # Shuffle the filtered dataframe

        for _, row in df_filtered.iterrows(): # go through each row of dataframe 
            if total_duration >= duration: # if workout duration is met, the for loop is broken
                break

            dance_duration = 3 + (2 - intensity_level)  # each dance to last 3 minutes, with an additional 2 minutes for low intensity and 1 minute for medium intensity - less switches for lower intensity
            selected_dances.append((row["Dance style"], dance_duration)) # add tuple of dance style and duration to selected_dances
            total_duration += dance_duration # update total duration of the workout

        if total_duration < duration and not message_printed: # user is notified if their selected duration cannot be met with the available dances from one country
            print("Not enough dances available to fill the desired duration. Filling remaining time with available dances. Duplicates may occur.")
            message_printed = True

    return selected_dances

def connect_consecutive_duplicate_dances(workout):
    if len(workout) <= 1: # No need to connect if there's just 0 or 1 dances
        return workout
    
    # workout is a list of (dance, duration) tuples e.g. [("Zouk", 4), ("Zouk", 4), ("Salsa", 4)]
    connected_workout = [workout[0]] # start with the first (dance, duration) tuple e.g. ("Zouk", 4) -> [("Zouk", 4)]
    for i in range(1, len(workout)): # iterate through the original workout starting from the second dance
        if workout[i][0] == connected_workout[-1][0]: # if the current dance name is the same as the last dance in the connected workout

            # update the last dance in connected_workout by adding the duration of the current dance to it ("Zouk", 4) + ("Zouk", 4) -> ("Zouk", 8)
            connected_workout[-1] = (connected_workout[-1][0], connected_workout[-1][1] + workout[i][1]) 
        else:

            # otherwise add dance to the connected workout ("Salsa", 4) -> [("Zouk", 8), ("Salsa", 4)]
            connected_workout.append(workout[i])
    
    return connected_workout
    
                
def print_workout(workout):
    print("Recommended dances for your workout:")
    if len(workout) == 0:
        print("No dances available for the selected preferences.")
        return
    
    workout = connect_consecutive_duplicate_dances(workout) # the above function is called from here 
    
    for dance, duration in workout:
        print(f"- {dance} ({duration} minutes)")



if __name__ == "__main__": # The following code is just executed when this script is run and not imported 
    df = load_data()
    df = data_cleaning(df)

    # Uses the function from plotting.py to plot the distribution of dance origins, dance types and music genres in the dataset
    plot_counts(df, "Origin", "Country")
    plot_counts(df, "Dance Type", "Dance Type", False)
    plot_counts(df, "Associated Music Genre", "Music Genre", False)

    df = tempo_categorization(df)

    df, prefs = filter_dataset_by_user_preferences(df)

    print(f"User preferences: {prefs}")

    workout = generate_workout(df, prefs["country"], prefs["intensity_level"], prefs["duration"])
    print_workout(workout)