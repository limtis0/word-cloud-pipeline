import time
import os
from dotenv import load_dotenv
import pickle
import psycopg2
from nltk.tokenize import word_tokenize
from collections import defaultdict
from psycopg2 import sql
from enum import Enum

# Ensure the necessary NLTK data is downloaded, 'punkt' is needed for tokenization
import nltk

nltk.download('punkt')
POSITIVE_ENUM = 2


class WordCountEnum(str, Enum):
    TITLE_POSITIVE = 'title_word_counts_pos'
    TITLE_NEGATIVE = 'title_word_counts_neg'
    TEXT_POSITIVE = 'text_word_counts_pos'
    TEXT_NEGATIVE = 'text_word_counts_neg'

    def __repr__(self):
        return self.value


def process_reviews_in_batches(conn_str, batch_size=1000, delay=1, output_file='word_counts.pkl',
                               state_file='state.pkl'):
    """
    Process reviews from the database in batches, tokenize the title and text,
    count their occurrences for each polarity, and save the results in a pickle file.

    Args:
        conn_str (str): Database connection string.
        batch_size (int): Number of reviews to process in each batch.
        delay (int): Delay (in seconds) between processing batches.
        output_file (str): Name of the output pickle file.
        state_file (str): Name of the state file to store the last processed ID.
    """

    # Load state if exists
    try:
        with open(state_file, 'rb') as f:
            state = pickle.load(f)
            last_id = state.get('last_id', 0)
            title_word_counts_pos = state.get(WordCountEnum.TITLE_POSITIVE, defaultdict(int))
            title_word_counts_neg = state.get(WordCountEnum.TITLE_NEGATIVE, defaultdict(int))
            text_word_counts_pos = state.get(WordCountEnum.TEXT_POSITIVE, defaultdict(int))
            text_word_counts_neg = state.get(WordCountEnum.TEXT_NEGATIVE, defaultdict(int))
    except FileNotFoundError:
        last_id = 0
        title_word_counts_pos = defaultdict(int)
        title_word_counts_neg = defaultdict(int)
        text_word_counts_pos = defaultdict(int)
        text_word_counts_neg = defaultdict(int)

    # Connect to the database
    conn = psycopg2.connect(conn_str)
    cur = conn.cursor()

    print('Fetching the database...')
    while True:
        try:
            # Fetch a batch of reviews
            query = sql.SQL(
                "SELECT id, title, text, polarity FROM reviews WHERE id > {last_id} ORDER BY id LIMIT {limit}").format(
                last_id=sql.Literal(last_id),
                limit=sql.Literal(batch_size)
            )
            cur.execute(query)
            reviews = cur.fetchall()

            # Break the loop if there are no more reviews
            if not reviews:
                break

            # Process each review in the batch, count only one mention of a word
            for review in reviews:
                review_id, title, text, polarity = review

                title_words = set(word_tokenize(title.lower()))
                text_words = set(word_tokenize(text.lower()))

                if polarity == POSITIVE_ENUM:
                    for word in title_words:
                        title_word_counts_pos[word] += 1
                    for word in text_words:
                        text_word_counts_pos[word] += 1
                else:
                    for word in title_words:
                        title_word_counts_neg[word] += 1
                    for word in text_words:
                        text_word_counts_neg[word] += 1

                last_id = review_id

            # Save the state after processing each batch
            with open(state_file, 'wb') as f:
                pickle.dump({
                    'last_id': last_id,
                    WordCountEnum.TITLE_POSITIVE: title_word_counts_pos,
                    WordCountEnum.TITLE_NEGATIVE: title_word_counts_neg,
                    WordCountEnum.TEXT_POSITIVE: text_word_counts_pos,
                    WordCountEnum.TEXT_NEGATIVE: text_word_counts_neg
                }, f)

            # Delay to avoid overwhelming the database
            print(f'Fetched {last_id} entries')
            time.sleep(delay)

        except psycopg2.Error as e:
            print('Error while polling data:', e)
            time.sleep(5)

    # Close the database connection
    cur.close()
    conn.close()

    # Save the final word counts dictionary to a pickle file
    final = {
        WordCountEnum.TITLE_POSITIVE: title_word_counts_pos,
        WordCountEnum.TITLE_NEGATIVE: title_word_counts_neg,
        WordCountEnum.TEXT_POSITIVE: text_word_counts_pos,
        WordCountEnum.TEXT_NEGATIVE: text_word_counts_neg
    }

    with open(output_file, 'wb') as f:
        pickle.dump(final, f)

    print(f'Processing complete. Word counts saved to {output_file}.')
    return final


# Used for debug to not to spend 3 hours each load :)
def load_prepared_data(output_file='word_counts.pkl'):
    with open(output_file, 'rb') as f:
        data = pickle.load(f)
        return {
            WordCountEnum.TITLE_POSITIVE: data[WordCountEnum.TITLE_POSITIVE],
            WordCountEnum.TITLE_NEGATIVE: data.get(WordCountEnum.TITLE_NEGATIVE),
            WordCountEnum.TEXT_POSITIVE: data.get(WordCountEnum.TEXT_POSITIVE),
            WordCountEnum.TEXT_NEGATIVE: data.get(WordCountEnum.TEXT_NEGATIVE)
        }


if __name__ == '__main__':
    load_dotenv()
    process_reviews_in_batches(os.getenv('DATABASE_URL'))
