import os
from dotenv import load_dotenv
import time
from copy import deepcopy
from PIL import Image
import numpy as np
from wordcloud import WordCloud, ImageColorGenerator
from pathlib import Path
from gather_data import process_reviews_in_batches, WordCountEnum, load_prepared_data


COMMON_WORDS = {
    'the', 'be', 'to', 'of', 'and', 'a', 'in', 'that', 'have', 'i', 'it', 'for', 'not', 'are', 'was', 'were', '\'re',
    'on', 'with', 'he', 'as', 'you', 'do', 'at', 'this', 'but', 'his', 'by', 'from', 'they', 'we', 'say', 'her',
    'she', 'or', 'an', 'will', 'my', 'one', 'all', 'would', 'there', 'their', 'what', 'so', 'up', 'out', 'if',
    'about', 'who', 'get', 'which', 'go', 'me', 'when', 'make', 'can', 'like', 'time', 'no', 'just', 'him', '\'ll',
    'know', 'take', 'people', 'into', 'year', 'your', 'good', 'some', 'could', 'them', 'see', 'other', 'than',
    'then', 'now', 'look', 'only', 'come', 'its', 'over', 'think', 'also', 'back', 'after', 'use', 'two', 'how',
    'our', 'work', 'first', 'well', 'way', 'even', 'new', 'want', 'because', 'any', 'these', 'give', 'day', 'most',
    'us', ',', '.', '!', '?', ':', ';', '[', ']', '(', ')', 'n\'t', '...', '....', '\'ve', '\'d', 'did', 'should',
    'does', 'has', 'had', 'very', 'much', 'more'
}

MIN_WORD_LENGTH = 3

MASKS = {
    WordCountEnum.TITLE_POSITIVE: Path('masks/like.jpg'),
    WordCountEnum.TEXT_POSITIVE: Path('masks/like.jpg'),
    WordCountEnum.TITLE_NEGATIVE: Path('masks/dislike.jpg'),
    WordCountEnum.TEXT_NEGATIVE: Path('masks/dislike.jpg')
}


def prepare_dictionary(d: dict, freq_threshold=0.0004):
    dictionary = deepcopy(d)

    # Remove common/short words from the set
    for key in d.keys():
        if key in COMMON_WORDS or len(key) < MIN_WORD_LENGTH:
            dictionary.pop(key, None)

    # Calculate threshold count
    total_count = sum(dictionary.values())
    min_count = total_count * freq_threshold

    # Remove values not fitting threshold
    for key, val in d.items():
        if val < min_count:
            dictionary.pop(key, None)

    return dictionary


def make_wordclouds(database_url: str, from_result=False):
    # Prepare output folder
    output_folder = Path('./output') / str(int(time.time()))
    output_folder.mkdir(exist_ok=True, parents=True)

    # Get the word-count from DB
    word_count = load_prepared_data() if from_result else process_reviews_in_batches(database_url)

    for wc_key in [
        WordCountEnum.TITLE_POSITIVE,
        WordCountEnum.TEXT_POSITIVE,
        WordCountEnum.TITLE_NEGATIVE,
        WordCountEnum.TEXT_NEGATIVE
    ]:
        cur_dict = prepare_dictionary(word_count.get(wc_key))

        # Generate a mask
        mask_path = MASKS.get(wc_key)
        # noinspection PyTypeChecker
        mask = np.asarray(Image.open(mask_path))
        mask = mask[::3, ::3]  # Subsample by factor of 3. Lossy, but does not matter with Word Clouds

        # Generate WordCloud
        wc = WordCloud(background_color='white', mask=mask)
        wc.generate_from_frequencies(cur_dict)
        wc.recolor(color_func=ImageColorGenerator(mask))

        svg_string = wc.to_svg()
        with open(output_folder / f'{wc_key}.svg', 'w') as f:
            f.write(svg_string)

    return output_folder


if __name__ == '__main__':
    load_dotenv()
    make_wordclouds(os.getenv('DATABASE_URL'), from_result=True)
