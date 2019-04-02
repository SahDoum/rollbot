import random
import re

from zalgo_text import zalgo


def zalgo_filter(text):
    return zalgo.zalgo().zalgofy(text)


def uppercase_filter(text):
    return "".join( random.choice([k.upper(), k ]) for k in text )


def anti_vowel_filter(text):
    vowels = ['а', 'е', 'ё', 'и', 'о', 'у', 'ы', 'э', 'ю', 'я', 'a', 'e', 'y', 'u', 'i', 'o']
    return "".join([l for l in text if l.lower() not in vowels])


def revert_filter(text):
    return text[::-1]


def shuffle_string(string):
    chars = list(string)
    random.shuffle(chars)
    return ''.join(chars)


def garble_word(word):
    # No operation needed on sufficiently small words
    # (Also, main algorithm requires word length >= 2)
    if len(word) <= 3:
        return word

    # Split word into first & last letter, and middle letters
    first, mids, last = word[0], word[1:-1], word[-1]

    return first + shuffle_string(mids) + last


def garble_filter(sentence):
    words = sentence.split(' ')
    return ' '.join(map(garble_word, words))


def tarabarsky_filter(text):
    return re.sub(r'([аеёиоуыэюя])', r'\1с\1', text, flags=re.IGNORECASE)


def igor_filter(text):
    return text.replace('с', 'ш').replace('х', 'ф')


FILTERS = [zalgo_filter, uppercase_filter, anti_vowel_filter, revert_filter, garble_filter, tarabarsky_filter, igor_filter]


def get_filter():
    return random.choice(FILTERS)
