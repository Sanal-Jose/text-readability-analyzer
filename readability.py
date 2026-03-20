import re

# -----------------------------
# TEXT SPLITTING
# -----------------------------

def split_sentences(text):
    sentences = re.split(r'[.!?]+', text)
    return [s.strip() for s in sentences if s.strip()]

def split_words(text):
    return re.findall(r'\w+', text)

def split_paragraphs(text):
    return [p.strip() for p in text.split("\n") if p.strip()]

# -----------------------------
# EVALUATION METRICS
# -----------------------------

def sentence_length_score(text):
    sentences = split_sentences(text)
    words = split_words(text)

    if not sentences:
        return 0, "No sentences detected"

    avg_len = len(words) / len(sentences)

    if avg_len <= 12:
        return 95, "Excellent sentence length"
    elif avg_len <= 18:
        return 75, "Good sentence length"
    elif avg_len <= 25:
        return 50, "Long sentences"
    else:
        return 25, "Very long sentences"

def word_complexity_score(text):
    words = split_words(text)

    if not words:
        return 0, "No words detected"

    long_words = [w for w in words if len(w) > 7]
    percent = (len(long_words) / len(words)) * 100

    if percent < 10:
        return 95, "Very simple words"
    elif percent < 20:
        return 75, "Mostly simple words"
    elif percent < 35:
        return 50, "Moderate complexity"
    else:
        return 25, "Highly complex vocabulary"

def paragraph_density_score(text):
    paragraphs = split_paragraphs(text)
    words = split_words(text)

    if not paragraphs:
        return 0, "No paragraphs detected"

    avg = len(words) / len(paragraphs)

    # thresholds
    if 40 <= avg <= 80:
        return 90, "Good paragraph size"
    elif 25 <= avg < 40 or 80 < avg <= 120:
        return 60, "Moderate paragraph size"
    else:
        return 30, "Poor paragraph structure"

def passive_voice_score(text):
    sentences = split_sentences(text)

    if not sentences:
        return 0, "No sentences detected", []

    # Common stative adjectives to exclude (as per requirement)
    exclusion_list = {
    "tired", "interested", "worried", "bored", "confused",
    "excited", "pleased", "surprised", "limited", "related",
    "broken", "open", "closed", "ready", "available",
    "possible", "different", "important", "necessary", "clear"
}

    passive_count = int(0)
    flagged_sentences = []

    # Pattern: be-verb + word ending in ed/en
    pattern = r'\b(am|is|are|was|were|be|been|being)\b\s+(\w+(ed|en))\b'

    for sentence in sentences:
        matches = re.findall(pattern, sentence)

        for match in matches:
            word = match[1].lower()  # extracted past participle

            # Skip if it's a stative adjective
            if word in exclusion_list:
                continue

            # Valid passive detected
            passive_count += 1  # type: ignore
            flagged_sentences.append(sentence)
            break  # Avoid duplicate counting per sentence

    percent = (passive_count / len(sentences)) * 100  # type: ignore

    if percent < 10:
        return 95, "Mostly active voice", flagged_sentences
    elif percent < 25:
        return 70, "Some passive voice", flagged_sentences
    elif percent < 40:
        return 50, "Frequent passive voice", flagged_sentences
    else:
        return 25, "Too much passive voice", flagged_sentences

# -----------------------------
# SYLLABLE COUNT
# -----------------------------

def count_syllables(word: str) -> int:
    word = word.lower()
    vowels = "aeiouy"
    count = int(0)
    prev: bool = False

    for char in word:
        if char in vowels:
            if not prev:
                count += 1  # type: ignore
            prev = True
        else:
            prev = False

    if word.endswith("e"):
        count = max(1, count - 1)  # type: ignore

    return count if count > 0 else 1

def flesch_reading_ease(text):
    words = split_words(text)
    sentences = split_sentences(text)

    if not words or not sentences:
        return 0, "Insufficient data"

    syllables = sum(count_syllables(w) for w in words)

    wps = len(words) / len(sentences)
    spw = syllables / len(words)

    score = 206.835 - (1.015 * wps) - (84.6 * spw)

    if score > 80:
        level = "Easy"
    elif score > 60:
        level = "Medium"
    else:
        level = "Hard"

    return round(score, 2), level

# -----------------------------
# SUGGESTIONS
# -----------------------------

def get_suggestions(scores):
    suggestions = []

    if scores["Sentence Length"] < 60:
        suggestions.append("Break long sentences into shorter ones.")

    if scores["Word Complexity"] < 60:
        suggestions.append("Use simpler words where possible.")

    if scores["Paragraph Density"] < 60:
        suggestions.append("Split large paragraphs.")

    if scores["Passive Voice"] < 60:
        suggestions.append("Use active voice more frequently.")

    return suggestions

# -----------------------------
# FINAL ANALYSIS
# -----------------------------

def analyze_text(text):
    s1, m1 = sentence_length_score(text)
    s2, m2 = word_complexity_score(text)
    s3, m3 = paragraph_density_score(text)
    s4, m4, passive_sentences = passive_voice_score(text)

    flesch_score, flesch_level = flesch_reading_ease(text)

    # Weighted scoring 
    overall_score = (
        0.3 * s1 +
        0.25 * s2 +
        0.2 * s3 +
        0.25 * s4
    )

    if overall_score > 80:
        grade = "Easy"
    elif overall_score > 60:
        grade = "Medium"
    else:
        grade = "Hard"

    results = {
        "Sentence Length": (s1, m1),
        "Word Complexity": (s2, m2),
        "Paragraph Density": (s3, m3),
        "Passive Voice": (s4, m4),
        "Flesch Score": (flesch_score, flesch_level)
    }

    suggestions = get_suggestions({
        "Sentence Length": s1,
        "Word Complexity": s2,
        "Paragraph Density": s3,
        "Passive Voice": s4
    })

    return grade, round(overall_score, 2), results, suggestions, passive_sentences