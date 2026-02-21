from functions import *

if __name__ == "__main__": # The following code is just executed when this script is run and not imported 
    df = load_data()
    df = data_cleaning(df)

    df = tempo_categorization(df)

    df, prefs = filter_dataset_by_user_preferences(df)

    workout = generate_workout(df, prefs["intensity_level"], prefs["duration"])
    print_workout(workout)