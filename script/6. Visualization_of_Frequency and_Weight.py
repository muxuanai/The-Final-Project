import pandas as pd
import matplotlib.pyplot as plt

def plot_frequency_bargraph(file1, file2):
    df1 = pd.read_csv(file1)
    df2 = pd.read_csv(file2)

    fig, axes = plt.subplots(2, 1, figsize=(10, 8))

    # Plot for Frequency_articles.csv
    colors1 = 'skyblue'
    bars1 = axes[0].bar(df1['Word Translation'].head(15), df1['Frequency'].head(15), color=colors1)

    axes[0].set_title('Top 15 Words Frequency (Articles)')
    axes[0].set_ylabel('Frequency')
    axes[0].tick_params(axis='x', rotation=45)

    # Plot for Frequency_posts.csv
    colors2 = 'skyblue'
    bars2 = axes[1].bar(df2['Word Translation'].head(15), df2['Frequency'].head(15), color=colors2)

    axes[1].set_title('Top 15 Words Frequency (Posts)')
    axes[1].set_ylabel('Frequency')
    axes[1].tick_params(axis='x', rotation=45)

    plt.tight_layout()
    plt.show()


def plot_keywords_bargraph(file1, file2):
    df1 = pd.read_csv(file1)
    df2 = pd.read_csv(file2)

    fig, axes = plt.subplots(2, 1, figsize=(10, 8))

    # Plot for Keywords_Articles.csv
    colors1 = 'skyblue'
    bars1 = axes[0].bar(df1['Keyword Translation'].head(15), df1['Weight'].head(15), color=colors1)

    axes[0].set_title('Top 15 Keywords Weight (Articles)')
    axes[0].set_ylabel('Weight')
    axes[0].tick_params(axis='x', rotation=45)

    # Plot for Keywords_posts.csv
    colors2 = 'skyblue'
    bars2 = axes[1].bar(df2['Keyword Translation'].head(15), df2['Weight'].head(15), color=colors2)

    axes[1].set_title('Top 15 Keywords Weight (Posts)')
    axes[1].set_ylabel('Weight')
    axes[1].tick_params(axis='x', rotation=45)

    plt.tight_layout()
    plt.show()


plot_frequency_bargraph('Frequency_articles.csv', 'Frequency_posts.csv')
plot_keywords_bargraph('Keywords_Articles.csv', 'Keywords_Posts.csv')
