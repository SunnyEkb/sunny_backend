import os
from functools import lru_cache
from typing import List

from django.conf import settings


@lru_cache
def get_bad_words_list() -> List:
    with open(
        os.path.join(settings.BASE_DIR, "media", "bad_words.txt"),
        encoding="utf-8",
    ) as file:
        return [line.rstrip() for line in file]


@lru_cache
def get_good_words_list() -> List:
    with open(
        os.path.join(settings.BASE_DIR, "media", "white_list_words.txt"),
        encoding="utf-8",
    ) as file:
        return [line.rstrip() for line in file]


def bad_words_filter(text: str) -> List[str]:
    bad_words = get_bad_words_list()
    good_words = get_good_words_list()

    text = text.lower().replace(" ", "")

    for item in good_words:
        if item in text:
            text = text.replace(item, "")

    multiple_letter_subst = {
        "ж": ["zh"],
        "к": ["i{", "|{"],
        "л": ["ji"],
        "х": ["}{"],
        "ч": ["ч", "ch"],
        "ш": ["ш", "sh"],
        "щ": ["щ", "sch"],
        "ы": ["ы", "bi"],
        "ю": ["ю", "io"],
        "я": ["я", "ya"],
    }
    for key, value in multiple_letter_subst.items():
        for letter in value:
            if letter in text:
                text = text.replace(letter, key)

    one_letter_subst = {
        "а": ["а", "a", "@"],
        "б": ["б", "6", "b"],
        "в": ["в", "b", "v"],
        "г": ["г", "r", "g"],
        "д": ["д", "d"],
        "е": ["е", "e"],
        "ё": ["ё", "e"],
        "ж": ["ж", "*"],
        "з": ["з", "3", "z"],
        "и": ["и", "u", "i"],
        "й": ["й", "u", "i"],
        "к": ["к", "k"],
        "л": ["л", "l"],
        "м": ["м", "m"],
        "н": ["н", "h", "n"],
        "о": ["о", "o", "0"],
        "п": ["п", "n", "p"],
        "р": ["р", "r", "p"],
        "с": ["с", "c", "s"],
        "т": ["т", "m", "t"],
        "у": ["у", "y", "u"],
        "ф": ["ф", "f"],
        "х": ["х", "x", "h"],
        "ц": ["ц", "c", "u,"],
        "ч": ["ч"],
        "ш": ["ш"],
        "щ": ["щ"],
        "ь": ["ь", "b"],
        "ы": ["ы"],
        "ъ": ["ъ"],
        "э": ["э", "e"],
        "ю": ["ю"],
        "я": ["я"],
    }
    for key, value in one_letter_subst.items():
        for letter in value:
            for phr in text:
                if letter == phr:
                    text = text.replace(phr, key)
    result = []
    for word in bad_words:
        for part in range(len(text)):
            fragment = text[part : part + len(word)]  # noqa
            if fragment == word:
                result.append(fragment)
    return result
