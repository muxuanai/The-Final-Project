import pandas as pd
import jieba
import re
from sklearn.metrics.pairwise import cosine_similarity
import matplotlib.pyplot as plt
import seaborn as sns

# Merge Keywords
df_articles = pd.read_csv('Keywords_Articles.csv')
df_posts = pd.read_csv('Keywords_Posts.csv')

keywords_articles = df_articles['Keyword'].tolist()
keywords_posts = df_posts['Keyword'].tolist()

# Merge and Remove Duplicates
merged_keywords = list(set(keywords_articles + keywords_posts))

# Calculate Relative Frequency
with open('hit_stopwords.txt', 'r', encoding='utf-8') as stopword_file:
    stop_words = set(stopword_file.read().splitlines())

custom_phrases = ['关你屁事', '新京报', '中国青年报', '光明日报', '光明网', '大众日报', '人民论坛', '环球网',
                  '北京日报', '中国新闻周刊']
for phrase in custom_phrases:
    jieba.add_word(phrase)

df_articles = pd.read_csv('Wechat_Articles.csv')
df_posts = pd.read_csv('Weibo_Posts.csv')

# Combine Keyword Lists
keywords = list(set(keywords_articles + keywords_posts))


def calculate_relative_frequency(text, keywords):
    text = '\n'.join(text['Contents'])
    text = re.sub(r'[^\w\s]', '', text)
    text = re.sub(r':\S+:', '', text)

    words = jieba.cut(text, cut_all=False)
    words = [word for word in words if word not in stop_words]

    keyword_count = {keyword: 0 for keyword in keywords}
    total_words = 0

    for word in words:
        total_words += 1
        if word in keyword_count:
            keyword_count[word] += 1

    relative_frequency = {keyword: count / total_words for keyword, count in keyword_count.items()}

    return relative_frequency


relative_frequencies_articles = calculate_relative_frequency(df_articles, keywords)
print(relative_frequencies_articles)
relative_frequencies_posts = calculate_relative_frequency(df_posts, keywords)
print(relative_frequencies_posts)


# Generate Word Vectors Function
def generate_word_vector(relative_frequency, combined_keywords):
    word_vector = []
    for keyword in combined_keywords:
        word_vector.append(relative_frequency.get(keyword, 0))
    return word_vector


vector_posts = generate_word_vector(relative_frequencies_posts, keywords)
vector_articles = generate_word_vector(relative_frequencies_articles, keywords)

# Convert to DataFrame
df_word_vectors = pd.DataFrame([vector_posts, vector_articles], columns=keywords, index=['posts', 'articles'])
print(df_word_vectors)

# Calculate Cosine Similarity
cosine_similarities = cosine_similarity([vector_posts, vector_articles])

# Convert to DataFrame
df_cosine_similarity = pd.DataFrame(cosine_similarities, columns=['posts', 'articles'], index=['posts', 'articles'])
print("cosine similarity matrix")
print(df_cosine_similarity)

# Plot
plt.figure(figsize=(8, 6))
sns.heatmap(df_cosine_similarity, annot=True, cmap='Blues', fmt=".4f", linewidths=.5, vmin=0, vmax=1)
plt.title('Cosine Similarity Matrix')
plt.show()
