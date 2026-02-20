import matplotlib.pyplot as plt


# Plotting the distribution of one of the columns
def plot_histogramm(df, column, column_name, bins=20):
    plt.figure(figsize=(10, 6))
    plt.hist(df[column], bins=bins, color='lavender', edgecolor='purple')
    plt.title(f"Distribution of Dance {column_name}")
    plt.xlabel(column_name)
    plt.ylabel("Frequency")
    plt.show()


# Bar chart of number of dances per country - change later
def plot_counts(df, column, column_name, log_scale=True):
    country_counts = df[column].value_counts()
    country_counts.plot(kind='bar', color = 'skyblue', edgecolor='blue')
    if log_scale:
        plt.yscale('log')
    plt.title(f"Number of Dances per {column_name}")
    plt.xlabel(column_name)
    plt.ylabel("Number of Dances")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

#visualize the categorization of tempos with histogramm plot with colored background
def plot_tempo_distribution_with_categories(df, low_cutoff, high_cutoff):
    plt.figure(figsize=(10, 6))
    plt.axvspan(0, low_cutoff, color='cornflowerblue', alpha=0.5, label='Low Tempo')
    plt.axvspan(low_cutoff, high_cutoff, color='mediumseagreen', alpha=0.5, label='Medium Tempo')
    plt.axvspan(high_cutoff, df["Tempo (BPM)"].max(), color='red', alpha=0.5, label='High Tempo')
    plt.hist(df["Tempo (BPM)"], bins=200, color='black')
    plt.title(f"Distribution of Dance Tempos with Tempo Categories")
    plt.xlabel("Tempo (BPM)")
    plt.ylabel("Frequency")
    plt.legend()
    plt.show()


