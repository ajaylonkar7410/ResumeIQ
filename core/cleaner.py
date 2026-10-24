"""
Text preprocessing and NLP cleaning pipeline:
- Tokenization (words & sentences)
- Stopword removal
- Noise cleaning & normalization
- N-gram generation
- Tech token preservation (e.g. C++, C#, .NET, Node.js)
"""

import re
from collections import Counter

# Standard English stopwords list (built-in so no external internet download is required)
STOPWORDS = {
    'a', 'about', 'above', 'after', 'again', 'against', 'all', 'am', 'an', 'and', 'any', 'are',
    'aren\'t', 'as', 'at', 'be', 'because', 'been', 'before', 'being', 'below', 'between', 'both',
    'but', 'by', 'can\'t', 'cannot', 'could', 'couldn\'t', 'did', 'didn\'t', 'do', 'does', 'doesn\'t',
    'doing', 'don\'t', 'down', 'during', 'each', 'few', 'for', 'from', 'further', 'had', 'hadn\'t',
    'has', 'hasn\'t', 'have', 'haven\'t', 'having', 'he', 'he\'d', 'he\'ll', 'he\'s', 'her', 'here',
    'here\'s', 'hers', 'herself', 'him', 'himself', 'his', 'how', 'how\'s', 'i', 'i\'d', 'i\'ll',
    'i\'m', 'i\'ve', 'if', 'in', 'into', 'is', 'isn\'t', 'it', 'it\'s', 'its', 'itself', 'let\'s',
    'me', 'more', 'most', 'mustn\'t', 'my', 'myself', 'no', 'nor', 'not', 'of', 'off', 'on', 'once',
    'only', 'or', 'other', 'ought', 'our', 'ours', 'ourselves', 'out', 'over', 'own', 'same',
    'shan\'t', 'she', 'she\'d', 'she\'ll', 'she\'s', 'should', 'shouldn\'t', 'so', 'some', 'such',
    'than', 'that', 'that\'s', 'the', 'their', 'theirs', 'them', 'themselves', 'then', 'there',
    'there\'s', 'these', 'they', 'they\'d', 'they\'ll', 'they\'re', 'they\'ve', 'this', 'those',
    'through', 'to', 'too', 'under', 'until', 'up', 'very', 'was', 'wasn\'t', 'we', 'we\'d',
    'we\'ll', 'we\'re', 'we\'ve', 'were', 'weren\'t', 'what', 'what\'s', 'when', 'when\'s', 'where',
    'where\'s', 'which', 'while', 'who', 'who\'s', 'whom', 'why', 'why\'s', 'with', 'won\'t', 'would',
    'wouldn\'t', 'you', 'you\'d', 'you\'ll', 'you\'re', 'you\'ve', 'your', 'yours', 'yourself', 'yourselves'
}

def clean_text(text, preserve_newlines=False):
    """
    Cleans raw resume text:
    - Normalizes unicode quotes, bullets, and dashes
    - Normalizes whitespace
    - Preserves technology keywords
    """
    if not text:
        return ""

    # Replace unicode bullets, dashes, non-breaking spaces
    text = text.replace('\xa0', ' ')
    text = text.replace('•', '\n• ')
    text = text.replace('–', '-').replace('—', '-')
    text = text.replace('“', '"').replace('”', '"').replace('’', "'").replace('‘', "'")

    if preserve_newlines:
        # Normalize multiple spaces per line, but keep line breaks
        lines = [re.sub(r'[ \t]+', ' ', line).strip() for line in text.splitlines()]
        # Remove consecutive blank lines
        cleaned_lines = []
        for line in lines:
            if line or (cleaned_lines and cleaned_lines[-1] != ""):
                cleaned_lines.append(line)
        return "\n".join(cleaned_lines).strip()
    else:
        # Collapse all whitespace into single spaces
        text = re.sub(r'\s+', ' ', text)
        return text.strip()


def tokenize_words(text, lowercase=True, remove_stop=False):
    """
    Tokenizes text while preserving technical tokens like C++, C#, .NET, Node.js, CI/CD.
    """
    if not text:
        return []

    if lowercase:
        text = text.lower()

    # Pattern preserves:
    # 1. Words with pluses (c++)
    # 2. Words with sharps (c#)
    # 3. Words with dots (.net, node.js, vue.js)
    # 4. Words with hyphens or slashes (ci/cd, scikit-learn, front-end)
    # 5. Standard alphanumeric words
    pattern = r'[a-zA-Z0-9]+(?:\.[a-zA-Z0-9]+)+|c\+\+|c\#|\.net|[a-zA-Z0-9]+(?:[\/\-][a-zA-Z0-9]+)*'
    tokens = re.findall(pattern, text)

    if remove_stop:
        tokens = [t for t in tokens if t.lower() not in STOPWORDS and len(t) > 1]

    return tokens


def tokenize_sentences(text):
    """
    Splits text into sentences based on punctuation and line boundaries.
    """
    if not text:
        return []

    # Replace newlines with sentence boundaries where appropriate
    text = re.sub(r'[\r\n]+', ' . ', text)
    # Split on sentence terminals . ! ? followed by space or capital
    raw_sentences = re.split(r'(?<=[.!?])\s+', text)
    sentences = []
    for s in raw_sentences:
        s_clean = s.strip(' .•-\t\r\n')
        if len(s_clean) > 3:
            sentences.append(s_clean)
    return sentences


def extract_ngrams(tokens, n=2):
    """Generates n-grams from a list of tokens."""
    if len(tokens) < n:
        return []
    return [" ".join(tokens[i:i+n]) for i in range(len(tokens) - n + 1)]


def compute_word_frequencies(text, top_n=30):
    """
    Returns top frequent keywords, omitting common stopwords.
    """
    tokens = tokenize_words(text, lowercase=True, remove_stop=True)
    # Filter pure digits or single characters
    meaningful = [t for t in tokens if len(t) > 2 and not t.isdigit()]
    counter = Counter(meaningful)
    return counter.most_common(top_n)
