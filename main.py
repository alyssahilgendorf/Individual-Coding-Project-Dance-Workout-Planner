# Import and read data 
import pandas as pd
from plotting import *
from scipy import stats

INTENSITY_LEVEL_TO_TEMPO = {0: "Slow", 1: "Medium", 2: "Fast"}

def load_data() -> pd.DataFrame:
    df = pd.read_csv('dancedata.csv', encoding='latin1')
    print(df.head(10))
    return df

def data_cleaning(df) -> pd.DataFrame:

    #Data Cleaning
    df['Origin'] = df['Origin'].replace('USA', 'United States')


    df["Associated Music Genre"] = df["Associated Music Genre"].str.lower()

    #remove every music like latin music to latin
    df['Associated Music Genre'] = df['Associated Music Genre'].str.replace(r'\s*music\s*', '', regex=True)
    df['Associated Music Genre'] = df['Associated Music Genre'].str.replace(r'\s*dance\s*', '', regex=True)

    # map associated music genres together like hip-hop and hip hop
    df['Associated Music Genre'] = df['Associated Music Genre'].replace({'hip-hop': 'hip hop'})

    #cleaning end
    return df

def tempo_categorization(df) -> pd.DataFrame:
    # t test if speed of bpm is normally distributed
    
    bpm = df["Tempo (BPM)"]
    k2, p = stats.normaltest(bpm)
    print(f"p-value for normality test: {p}")
    if p < 0.05:
        print("The distribution of BPM is not normal.")

    #Used to determine the distrubition of BPM and to determine the categorization of tempos
    plot_histogramm(df, "Tempo (BPM)", "Tempo (BPM)", 200)

    # Use descriptive statistics to determine categorization of tempos
    low_cutoff = df['Tempo (BPM)'].quantile(0.33) 
    high_cutoff = df['Tempo (BPM)'].quantile(0.66)

    #Categorization of tempos
    df["Tempo Category"] = ""
    df.loc[df["Tempo (BPM)"] < low_cutoff, "Tempo Category"] = "Slow"
    df.loc[(df["Tempo (BPM)"] >= low_cutoff) & (df["Tempo (BPM)"] <= high_cutoff), "Tempo Category"] = "Medium"
    df.loc[df["Tempo (BPM)"] > high_cutoff, "Tempo Category"] = "Fast"

    plot_tempo_distribution_with_categories(df, low_cutoff, high_cutoff)

    print(df["Tempo Category"].value_counts())

    return df

# Uses the function from plotting.py to plot the distribution of dance origins, dance types and music genres in the dataset
# plot_counts(df, "Origin", "Country")
# plot_counts(df, "Dance Type", "Dance Type", False)
# plot_counts(df, "Associated Music Genre", "Music Genre", False)


#User input

def user_numeric_input(prompt, min_value, max_value) -> int:
    num = None
    while True:
        num_str = input(prompt)
        if num_str.isdigit() and int(num_str) >= min_value and int(num_str) <= max_value:
            num = int(num_str)
            break
        else:
            print(f"Please enter a valid integer between {min_value} and {max_value}.")

    return num

def user_input_options_menu(choices):
    if len(choices) == 1:
        print(f"Only one option available: {choices[0]}")
        return 0
    print("Available options:")
    for i in range(len(choices)):
        print(f"{i + 1}. {choices[i]}") # i + 1 makes so that the outputed list starts counting from 1 instead of 0
    return int(user_numeric_input("Select the number corresponding to your preferred option: ", 1, len(choices))) - 1 # Adjusting for 0-based normalization


def filter_dataset_by_user_preferences(df) -> dict:

    #df = df.copy()  # Create a copy of the dataframe to avoid modifying the original

    duration = user_numeric_input("Enter duration of workout in minutes: ", min_value=5, max_value=120)

    print("Select intensity level:")
    intensity_level = user_input_options_menu(["low", "medium", "high"])
    print(f"Selected intensity level: {['low', 'medium', 'high'][intensity_level]}")

    df = df[df["Tempo Category"] == INTENSITY_LEVEL_TO_TEMPO[intensity_level]] #TODO fix duplicated code

    print("Select origin country:")
    countries = df["Origin"].unique()
    country = user_input_options_menu([f"{country} ({df[df['Origin'] == country].shape[0]})" for country in countries])
    
    # remove dances from the dataset that do not match the selected country
    df = df[df["Origin"] == countries[country]]

    return df, {"duration": duration, "intensity_level": intensity_level, "country": countries[country]}


def generate_workout(df, country, intensity_level, duration) -> pd.DataFrame:
    # Filter the dataset based on the user's country and intensity level
    
    #TODO fix duplicated code
    #df_filtered = df[(df["Origin"] == country) & (df["Tempo Category"] == INTENSITY_LEVEL_TO_TEMPO[intensity_level])]

    if df_filtered.empty:
        print("No dances found for the selected country and intensity level.")
        return
    
    selected_dances = []
    total_duration = 0
    message_printed = False

    while total_duration < duration:

        df_filtered = df_filtered.sample(frac=1, random_state=11)  # Shuffle the filtered dataframe

        for _, row in df_filtered.iterrows():
            if total_duration >= duration:
                break

            dance_duration = 3 + (2 - intensity_level)  # Each dance to last 3 minutes, with an additional 2 minutes for low intensity and 1 minute for medium intensity - less switches for lower intensity
            selected_dances.append((row["Dance style"], dance_duration))
            total_duration += dance_duration

        if total_duration < duration and not message_printed:
            print("Not enough dances available to fill the desired duration. Filling remaining time with available dances. Duplicates may occur.")
            message_printed = True

    return selected_dances

def connect_consecutive_duplicate_dances(workout):
    if len(workout) <= 1: # No need to connect if there's just 0 or 1 dances
        return workout
    
    # workout is a list of (dance, duration) tuples e.g. [("Zouk", 4), ("Zouk", 3), ("Salsa", 5)]
    connected_workout = [workout[0]] # Start with the first (dance, duration) tuple e.g. ("Zouk", 4) -> [("Zouk", 4)]
    for i in range(1, len(workout)): # Iterate through the original workout starting from the second dance
        if workout[i][0] == connected_workout[-1][0]: # If the current dance name is the same as the last dance in the connected workout
            connected_workout[-1] = (connected_workout[-1][0], connected_workout[-1][1] + workout[i][1])
        else:
            connected_workout.append(workout[i])
    
    return connected_workout
    
                
def print_workout(workout):
    print("Recommended dances for your workout:")
    if len(workout) == 0:
        print("No dances available for the selected preferences.")
        return
    
    workout = connect_consecutive_duplicate_dances(workout)
    
    for dance, duration in workout:
        print(f"- {dance} ({duration} minutes)")



if __name__ == "__main__":
    df = load_data()
    df = data_cleaning(df)
    df = tempo_categorization(df)

    df, prefs = filter_dataset_by_user_preferences(df)

    print(f"User preferences: {prefs}")

    workout = generate_workout(df, prefs["country"], prefs["intensity_level"], prefs["duration"])
    print_workout(workout)