from django import template
import re

register = template.Library()

NAUGHTY_WORDS_LIST = {
    'человек[\\w]*': '(разумный гриб)',
    'балмера[\\w]*': '(Джобса)',
    'закрутил[\\w]*': '(раскрутил)',
}


@register.filter()
def no_naughty_words(char_or_text: str) -> str:
    """Censors strings as per NAUGHTY_WORDS_LIST defined above"""
    for naughty in NAUGHTY_WORDS_LIST.keys():
        char_or_text = re.sub(naughty,
                              NAUGHTY_WORDS_LIST[naughty],
                              char_or_text,
                              flags=re.IGNORECASE)
    return char_or_text
