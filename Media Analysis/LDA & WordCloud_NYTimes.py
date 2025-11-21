'''
Author: Yixin Ding

Summary: This script implements Latent Dirichlet Allocation (LDA) topic modeling for analyzing news articles about China. 
It processes text data through multiple stages: loading articles from CSV, preprocessing text (combining columns, removing special characters),
tokenizing and lemmatizing words, creating a document corpus, finding the optimal number of topics through coherence scores, training the LDA model,
assigning dominant topics to each document, and generating visualizations including topic distribution plots and word clouds. 
The script includes options to manually specify the number of topics and toggle the generation of individual topic wordclouds to improve performance.

Reference: 
https://radimrehurek.com/gensim/models/ldamodel.html;
https://www.nltk.org;
https://amueller.github.io/word_cloud/;
https://seaborn.pydata.org/

AI used only for code comments and modifications.
'''
import pandas as pd
import numpy as np
import re
import matplotlib.pyplot as plt
import seaborn as sns
from wordcloud import WordCloud
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from gensim import corpora, models
from typing import List, Tuple, Dict, Any
import os

def download_nltk_resources():
    """Download required NLTK resources if not already present"""
    nltk.download('stopwords', quiet=True)
    nltk.download('wordnet', quiet=True)

def load_data(file_path: str) -> pd.DataFrame:
    """
    Load data from CSV file
    
    Args:
        file_path: Path to the CSV file
        
    Returns:
        DataFrame containing the news articles
    """
    print(f"Loading data from {file_path}...")
    return pd.read_csv(file_path)

def preprocess_text(df: pd.DataFrame, text_columns: List[str]) -> pd.DataFrame:
    """
    Preprocess text data by combining columns and cleaning text
    
    Args:
        df: DataFrame containing the news articles
        text_columns: List of column names to combine into a single text field
        
    Returns:
        DataFrame with preprocessed text
    """
    print("Preprocessing text data...")
    
    # Combine text columns
    df['text'] = ''
    for col in text_columns:
        df['text'] += ' ' + df[col].fillna('')
    
    # Clean text: convert to lowercase and remove special characters
    df['text'] = df['text'].str.lower()
    df['text'] = df['text'].apply(lambda x: re.sub(r'[^a-z\s]', '', x))
    
    return df

def tokenize_and_lemmatize(df: pd.DataFrame) -> pd.DataFrame:
    """
    Tokenize text, remove stopwords, and apply lemmatization
    
    Args:
        df: DataFrame with 'text' column
        
    Returns:
        DataFrame with added 'tokens' column
    """
    print("Tokenizing and lemmatizing text...")
    
    stop_words = set(stopwords.words('english'))
    lemmatizer = WordNetLemmatizer()
    
    def process_text(text: str) -> List[str]:
        # Replace multi-word terms like "hong kong" with single terms
        text = re.sub(r'\bhong\s+kong\b', 'hongkong', text)
        
        # Tokenize
        tokens = text.split()
        
        # Remove stopwords and short words, then lemmatize
        tokens = [lemmatizer.lemmatize(word) for word in tokens 
                  if word not in stop_words and len(word) > 2]
        
        return tokens
    
    df['tokens'] = df['text'].apply(process_text)
    return df

def create_corpus(tokens_list: List[List[str]]) -> Tuple[corpora.Dictionary, List]:
    """
    Create dictionary and corpus for LDA
    
    Args:
        tokens_list: List of tokenized documents
        
    Returns:
        Tuple of (dictionary, corpus)
    """
    print("Creating dictionary and corpus...")
    
    # Create dictionary
    dictionary = corpora.Dictionary(tokens_list)
    
    # Filter out extremely rare and common words
    dictionary.filter_extremes(no_below=2, no_above=0.9)
    
    # Create corpus
    corpus = [dictionary.doc2bow(text) for text in tokens_list]
    
    return dictionary, corpus

def find_optimal_topics(corpus: List, dictionary: corpora.Dictionary, 
                        texts: List[List[str]], 
                        start: int=2, limit: int=20, step: int=2) -> Tuple[List[float], int]:
    """
    Find the optimal number of topics using coherence scores
    
    Args:
        corpus: Document corpus
        dictionary: Dictionary mapping words to IDs
        texts: List of tokenized texts
        start: Starting number of topics
        limit: Maximum number of topics to test
        step: Step size for the number of topics
        
    Returns:
        Tuple of (coherence_values, best_topic_num)
    """
    print("Computing coherence values to find optimal number of topics...")
    
    coherence_values = []
    models_list = []
    
    for num_topics in range(start, limit, step):
        model = models.LdaModel(
            corpus=corpus,
            id2word=dictionary,
            num_topics=num_topics,
            passes=5,
            alpha='auto',
            random_state=42
        )
        
        models_list.append(model)
        
        coherence_model = models.CoherenceModel(
            model=model, 
            texts=texts, 
            dictionary=dictionary, 
            coherence='c_v'
        )
        
        coherence_values.append(coherence_model.get_coherence())
        print(f"Num topics: {num_topics}, Coherence score: {coherence_values[-1]}")
    
    # Find the best model
    best_index = coherence_values.index(max(coherence_values))
    best_topic_num = range(start, limit, step)[best_index]
    
    return coherence_values, best_topic_num

def plot_coherence_values(coherence_values: List[float], start: int, limit: int, step: int,
                          output_dir: str=None):
    """
    Plot coherence scores to visualize the optimal number of topics
    
    Args:
        coherence_values: List of coherence scores
        start: Starting number of topics
        limit: Maximum number of topics
        step: Step size for the number of topics
        output_dir: Directory to save the plot (optional)
    """
    print("Plotting coherence values...")
    
    plt.figure(figsize=(12, 6))
    plt.plot(range(start, limit, step), coherence_values, marker='o')
    plt.title('Topic Coherence Score by Number of Topics')
    plt.xlabel('Number of Topics')
    plt.ylabel('Coherence Score')
    plt.grid(True)
    
    if output_dir:
        plt.savefig(os.path.join(output_dir, 'coherence_values.png'), dpi=300, bbox_inches='tight')
    
    plt.close()

def train_lda_model(corpus: List, dictionary: corpora.Dictionary, 
                    num_topics: int, passes: int=5) -> models.LdaModel:
    """
    Train the LDA model
    
    Args:
        corpus: Document corpus
        dictionary: Dictionary mapping words to IDs
        num_topics: Number of topics for the model
        passes: Number of passes through the corpus during training
        
    Returns:
        Trained LDA model
    """
    print(f"Training LDA model with {num_topics} topics...")
    
    lda_model = models.LdaModel(
        corpus=corpus,
        id2word=dictionary,
        num_topics=num_topics,
        passes=passes,
        alpha='auto',
        random_state=42
    )
    
    return lda_model

def display_topics(lda_model: models.LdaModel, num_words: int=10):
    """
    Display the top words for each topic
    
    Args:
        lda_model: Trained LDA model
        num_words: Number of top words to display per topic
    """
    print("\nTopics and their key words:")
    
    for idx, topic in lda_model.print_topics(num_words=num_words):
        print(f"Topic {idx + 1}: {topic}")

def assign_dominant_topics(corpus: List, lda_model: models.LdaModel) -> List[int]:
    """
    Assign the dominant topic to each document
    
    Args:
        corpus: Document corpus
        lda_model: Trained LDA model
        
    Returns:
        List of dominant topic IDs for each document
    """
    print("Assigning dominant topics to documents...")
    
    dominant_topics = []
    
    for bow in corpus:
        topic_probs = lda_model.get_document_topics(bow)
        if topic_probs:  # Check if topic_probs is not empty
            # Add 1 to topic ID for 1-based indexing
            dominant_topic = sorted(topic_probs, key=lambda x: x[1], reverse=True)[0][0] + 1
        else:
            dominant_topic = 0  # Assign 0 if no topics found
        dominant_topics.append(dominant_topic)
    
    return dominant_topics

def plot_topic_distribution(topic_counts: pd.Series, output_dir: str=None):
    """
    Plot the distribution of topics
    
    Args:
        topic_counts: Series with topic counts
        output_dir: Directory to save the plot (optional)
    """
    print("Plotting topic distribution...")
    
    plt.figure(figsize=(14, 7))
    ax = sns.barplot(x=topic_counts.index, y=topic_counts.values, palette='viridis')
    plt.title('Topic Distribution in the Corpus', fontsize=16)
    plt.xlabel('Topic', fontsize=14)
    plt.ylabel('Number of Documents', fontsize=14)
    plt.xticks(rotation=45, ha='right')
    
    # Add count labels on top of bars
    for i, v in enumerate(topic_counts.values):
        ax.text(i, v + 0.5, str(v), ha='center')
    
    plt.tight_layout()
    
    if output_dir:
        plt.savefig(os.path.join(output_dir, 'topic_distribution.png'), dpi=300, bbox_inches='tight')
    
    plt.close()

def generate_wordcloud(lda_model: models.LdaModel, topic_id: int=None, 
                       title: str='Word Cloud', top_n: int=50, output_dir: str=None):
    """
    Generate and display word cloud for a specific topic or all topics combined
    
    Args:
        lda_model: Trained LDA model
        topic_id: Specific topic ID (0-based) or None for all topics
        title: Title for the wordcloud plot
        top_n: Number of top words to include from each topic
        output_dir: Directory to save the wordcloud (optional)
    """
    if topic_id is not None:
        print(f"Generating word cloud for Topic {topic_id + 1}...")
        # Get words and weights for the specific topic
        words = lda_model.show_topic(topic_id, top_n)
        filename = f'wordcloud_topic_{topic_id + 1}.png'
    else:
        print("Generating word cloud for all topics combined...")
        # Get words and weights for all topics
        all_topics_words = []
        for i in range(lda_model.num_topics):
            words = lda_model.show_topic(i, top_n)
            all_topics_words.extend(words)
        words = all_topics_words
        filename = 'wordcloud_all_topics.png'
    
    # Convert to format for WordCloud
    word_freq = {word: int(weight * 1000) for word, weight in words}
    
    # Generate wordcloud
    wordcloud = WordCloud(
        width=800, 
        height=400, 
        background_color='white',
        max_words=100,
        colormap='viridis',
    ).generate_from_frequencies(word_freq)
    
    # Display wordcloud
    plt.figure(figsize=(10, 6))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.title(title, fontsize=16)
    plt.axis('off')
    
    if output_dir:
        plt.savefig(os.path.join(output_dir, filename), dpi=300, bbox_inches='tight')
    
    plt.close()

def save_results(df: pd.DataFrame, output_file: str):
    """
    Save DataFrame with dominant topics to CSV
    
    Args:
        df: DataFrame with dominant_topic column
        output_file: Path to save the output CSV
    """
    print(f"Saving results to {output_file}...")
    df.to_csv(output_file, index=False)
    print(f"Results saved to {output_file}")

def main(file_path: str, text_columns: List[str], output_dir: str=None, 
         manual_best_topic: int=None, generate_topic_wordclouds: bool=True):
    """
    Main function to run the LDA topic modeling pipeline
    
    Args:
        file_path: Path to input CSV file
        text_columns: List of column names to use for text analysis
        output_dir: Directory to save output files (created if doesn't exist)
        manual_best_topic: Manually specified number of topics (overrides coherence analysis)
        generate_topic_wordclouds: Whether to generate wordclouds for each topic
    """
    # Create output directory if specified
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"Created output directory: {output_dir}")
    
    # Download NLTK resources
    download_nltk_resources()
    
    # Load data
    df = load_data(file_path)
    
    # Preprocess text
    df = preprocess_text(df, text_columns)
    
    # Tokenize and lemmatize
    df = tokenize_and_lemmatize(df)
    
    # Create corpus
    dictionary, corpus = create_corpus(df['tokens'].tolist())
    
    # Find optimal number of topics or use manual specification
    if manual_best_topic is None:
        coherence_values, best_topic_num = find_optimal_topics(
            corpus, dictionary, df['tokens'].tolist()
        )
        
        # Plot coherence values
        plot_coherence_values(coherence_values, 2, 20, 2, output_dir)
    else:
        best_topic_num = manual_best_topic
        print(f"Using manually specified number of topics: {best_topic_num}")
    
    # Train LDA model
    lda_model = train_lda_model(corpus, dictionary, best_topic_num)
    
    # Display topics
    display_topics(lda_model)
    
    # Assign dominant topics
    df['dominant_topic'] = assign_dominant_topics(corpus, lda_model)
    
    # Plot topic distribution
    topic_counts = df['dominant_topic'].value_counts().sort_index()
    topic_counts.index = [f"Topic {i}" for i in topic_counts.index]
    plot_topic_distribution(topic_counts, output_dir)
    
    # Generate wordcloud for all topics combined
    generate_wordcloud(
        lda_model, 
        title='Fox News: Word Cloud for China-related News 2024',
        output_dir=output_dir
    )
    
    # Generate wordcloud for each topic
    if generate_topic_wordclouds:
        for i in range(best_topic_num):
            generate_wordcloud(
                lda_model, 
                topic_id=i, 
                title=f'Topic {i + 1} Keywords',
                output_dir=output_dir
            )
    
    # Save results
    output_file = os.path.join(output_dir, 'news_with_topics.csv') if output_dir else 'news_with_topics.csv'
    save_results(df, output_file)
    
    return df, lda_model, dictionary, corpus

if __name__ == "__main__":
    file_path = '/Users/yixin/MACSS/2025 winter quarter/MACS 30112 Data Analysis for Computational Social Scientists/final project/final-project-super-legend-decoders-1/NY Times Scraper & Filter/China_article_nyt2024.csv'
    text_columns = ['headline', 'abstract', 'full_text']
    output_dir = 'lda_results'
    
    # Run with reduced complexity
    df, lda_model, dictionary, corpus = main(
        file_path=file_path,
        text_columns=text_columns,
        output_dir=output_dir,
        manual_best_topic=None,  
        generate_topic_wordclouds=False  # Skip individual wordclouds
    )
