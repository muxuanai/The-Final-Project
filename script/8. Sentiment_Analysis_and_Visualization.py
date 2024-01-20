import pandas as pd
import os
from snownlp import SnowNLP
import matplotlib.pyplot as plt

def get_sentiment(input_file, output_file):
    """Get sentiment scores using SnowNLP model."""
    df = pd.read_csv(input_file)
    sentiments, pos_scores, neg_scores, unknown_scores = [], 0, 0, 0

    for text in df['Contents']:
        s = SnowNLP(text)
        sentiment_score = s.sentiments
        sentiments.append(sentiment_score)

        # Define positive, negative and unknown score
        if sentiment_score < 0.5:
            label = 'Negative'
            neg_scores += 1
        elif sentiment_score > 0.5:
            label = 'Positive'
            pos_scores += 1
        else:
            label = 'Unknown'
            unknown_scores += 1

        df.loc[df['Contents'] == text, 'Sentiment Label'] = label

    df['Sentiments'] = sentiments

    if os.path.exists(output_file):
        os.remove(output_file)
        print(f'Deleting existing file: {output_file}')

    df[['Sentiments', 'Sentiment Label', 'Posting Time','Contents']].to_csv(output_file, index=False, encoding='utf_8_sig')

    return df['Sentiments'], pos_scores, neg_scores, unknown_scores


def calculate_negative_ratio(pos_scores, neg_scores, unknown_scores):
    total_scores = pos_scores + neg_scores + unknown_scores
    return neg_scores / total_scores if total_scores != 0 else 0


def print_scores_and_ratios(pos_scores, neg_scores, unknown_scores, ratio_prefix=''):
    print(f'{ratio_prefix}Positive Scores:', pos_scores)
    print(f'{ratio_prefix}Negative Scores:', neg_scores)
    print(f'{ratio_prefix}Unknown Scores:', unknown_scores)
    ratio = calculate_negative_ratio(pos_scores, neg_scores, unknown_scores)
    print(f'{ratio_prefix}Negative Ratio:', ratio)


def plot_pie_charts(positive_list, negative_list, unknown_list, titles):
    labels = ['Positive', 'Negative', 'Unknown']
    colors = ['lightgreen', 'lightcoral', 'lightskyblue']

    fig, axes = plt.subplots(1, 3, figsize=(18, 6))

    for i, (pos, neg, unknown, title) in enumerate(zip(positive_list, negative_list, unknown_list, titles)):
        sizes = [pos, neg, unknown]
        wedges, texts, autotexts = axes[i].pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90, textprops={'fontsize': 12})
        axes[i].set_title(title)

        for text, autotext in zip(texts, autotexts):
            text.set(size=10)
            autotext.set(size=10)

    plt.legend(wedges, labels, title="Sentiments", loc="center left", bbox_to_anchor=(1, 0, 0.5, 1))
    plt.show()


# Call the function for sentiment analysis
sentiments_comments, pos_scores_comments, neg_scores_comments, unknown_scores_comments = get_sentiment('Weibo_comments.csv', 'Sentiment_Comments.csv')
sentiments_posts, pos_scores_posts, neg_scores_posts, unknown_scores_posts = get_sentiment('Weibo_posts.csv', 'Sentiment_Posts.csv')
sentiments_articles, pos_scores_articles, neg_scores_articles, unknown_scores_articles = get_sentiment('Wechat_Articles.csv', 'Sentiment_Articles.csv')

# Print scores and ratios for each score table
print_scores_and_ratios(pos_scores_comments, neg_scores_comments, unknown_scores_comments, 'Comments ')
print_scores_and_ratios(pos_scores_posts, neg_scores_posts, unknown_scores_posts, 'Posts ')
print_scores_and_ratios(pos_scores_articles, neg_scores_articles, unknown_scores_articles, 'Articles ')

print('\nThe process is accomplished.')

# Plot pie charts
plot_pie_charts([pos_scores_comments, pos_scores_posts, pos_scores_articles],
                [neg_scores_comments, neg_scores_posts, neg_scores_articles],
                [unknown_scores_comments, unknown_scores_posts, unknown_scores_articles],
                ['Distribution of Sentiment in News Reviews', 'Distribution of Sentiment in Posts', 'Distribution of Sentiments in News Reports'])
