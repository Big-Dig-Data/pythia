def guess_language(text: str) -> str:
    """
    Tries to guess the language from the text
    :param text:
    :return:
    """
    norm_text = text.lower()
    if 'the ' in norm_text:
        return 'eng'
    if 'ee' in norm_text:
        return 'eng'
    for letter in norm_text:
        if ord(letter) > 128:
            return 'cze'
    return ''
