


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