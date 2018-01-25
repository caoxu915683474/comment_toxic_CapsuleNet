import os
import re
import numpy as np
import pandas as pd
from keras.preprocessing import text, sequence
import config

def get_raw_data():
    data_path = 'data'
    train = 'train.csv'
    test = 'test.csv'
    train_path = os.path.join(data_path, train)
    test_path = os.path.join(data_path, test)
    train_data = pd.read_csv(train_path)
    test_data = pd.read_csv(test_path)
    return train_data, test_data

def get_data(raw_data):
     raw_value = raw_data['comment_text'].fillna("_na_").values
     processed_data = []
     for v in raw_value:
         processed_data.append(text_to_wordlist(v))
     return processed_data 
     '''
     return list(raw_value)
     '''


def text_to_wordlist(text, remove_stopwords=False, stem_words=False):
    # Clean the text, with the option to remove stopwords and to stem words.
    # Convert words to lower case and split them

    # Regex to remove all Non-Alpha Numeric and space
    special_character_removal = re.compile(r'[^a-z\d ]', re.IGNORECASE)
    # regex to replace all numerics
    replace_numbers = re.compile(r'\d+', re.IGNORECASE)

    text = text.lower().split()
    # Optionally, remove stop words
    if remove_stopwords:
        stops = set(stopwords.words("english"))
        text = [w for w in text if not w in stops]

    text = " ".join(text)
    # Remove Special Characters
    text = special_character_removal.sub('', text)
    # Replace Numbers
    text = replace_numbers.sub('n', text)
    # Optionally, shorten words to their stems
    if stem_words:
        text = text.split()
        stemmer = SnowballStemmer('english')
        stemmed_words = [stemmer.stem(word) for word in text]
        text = " ".join(stemmed_words)
    # Return a list of words
    return (text)


def get_label(raw_data):
    labels = ['toxic', 'severe_toxic',
              'obscene', 'threat',
              'insult', 'identity_hate']
    return raw_data[labels].values

def get_id(raw_data):
    return raw_data['id'].values

def process_data(train_data, test_data):
    tokenizer = text.Tokenizer(num_words=config.MAX_WORDS)
    tokenizer.fit_on_texts(train_data+test_data)
    train_tokenized = tokenizer.texts_to_sequences(train_data)
    test_tokenized = tokenizer.texts_to_sequences(test_data)
    train_data = sequence.pad_sequences(train_tokenized, maxlen = config.MAX_LENGTH)
    test_data = sequence.pad_sequences(test_tokenized, maxlen = config.MAX_LENGTH)
    return train_data, test_data, tokenizer.word_index

def get_word_embedding():
    data_path = 'data'
    EMBEDDING_FILE = os.path.join(data_path, 'glove.840B.300d.txt')
    embeddings_index = {}
    for line in open(EMBEDDING_FILE, "rb"):
        values = line.split()
        word = values[0]
        coefs = np.asarray(values[1:], dtype='float32')
        embeddings_index[word] = coefs
    return embeddings_index

def get_embed_matrix(embeddings_index, word_index):
    nb_words = min(config.MAX_WORDS, len(word_index))
    embedding_matrix = np.zeros((nb_words, config.EMBEDDING_DIM))
    for word, i in word_index.items():
        if i >= config.MAX_WORDS:
            continue
        # embedding_vector = embeddings_index.get(str.encode(word))
        embedding_vector = embeddings_index.get(word)
        if embedding_vector is not None:
            # words not found in embedding index will be all-zeros.
            embedding_matrix[i] = embedding_vector
    return embedding_matrix

def fetch_data():
    train_raw, test_raw = get_raw_data()
    train_data = get_data(train_raw)
    test_data = get_data(test_raw)
    train_label = get_label(train_raw)
    train_data, test_data, word_index = process_data(train_data, test_data)
    return train_data, train_label, word_index

def fetch_test_data():
    train_raw, test_raw = get_raw_data()
    train_data = get_data(train_raw)
    test_data = get_data(test_raw)
    train_label = get_label(train_raw)
    train_data, test_data, word_index = process_data(train_data, test_data)
    test_id = get_id(test_raw)
    return test_data, test_id

if __name__ == '__main__':
    # embedding_dict = get_word_embedding()
    data, label, word_index = fetch_data()
    print np.sum(label, axis=0).astype(float) / label.shape[0]
    # em = get_embed_matrix(embedding_dict, word_index)
    # print(em.shape)
