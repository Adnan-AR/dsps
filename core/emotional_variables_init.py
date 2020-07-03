

def init_base(verbatim: str, language: str, forced_emotions: bool,
              verbatim_id: int):
    # TODO: remove verbatim_text in the future
    base = {
        # "verbatim_text": verbatim,
        "verbatim_id": verbatim_id,
        "language": language,
        "forced_emotions": forced_emotions,
        "global_results": {}
    }
    return base


def init_global_results():
    global_results = {
        "confidence_rate":          0,
        "emotional_contradiction":  False,
        "reliability_rate":         99999,
        "performance":              0,
        "document_word_count":      0,
        "emotional_word_count":     0,
        "char_count":               0,
        "negative":                 False,

        "negative_words":           [],
        "superlative_words":        [],
        "emotes":                   [],
        "compound_words":           [],
        "skipped_words":            [],
        "simple_words":             [],
        "unknown_words":            [],
        "extra_words":              [],
        "insistance_words":         [],
        "inversion_words":          [],
        "lower_words":              [],
        "complex_words":            [],
        "corrected_words":          [],
        "idiomatic_expressions":    [],
        "uppercase_words":          [],
        "punctuation_coeff":        [],

        "eindex":                   0,
        "main_emotional_intensity": 0,
        "valence":                  0.0,
        "arousal":                  0.0,
        "dominance":                0.0,

        "happiness":                0.0,
        "surprise":                 0.0,
        "calm":                     0.0,
        "fear":                     0.0,
        "sadness":                  0.0,
        "anger":                    0.0,
        "disgust":                  0.0,

        "emotional_intensity":      0,
        "positives_emotions_sum":   [],
        "negatives_emotions_sum":   [],
        "strongest_emotions":       [],
        "verbatim_strongest_emotion": str,

        "irony":                    False,
        "questioning":              False,
        "exclamation":              False,
        "comparative":              False,

        "comparative_words":        [],
        "emotional_words":          [],
        "words":                    [],

        "tenses":                   [],
        "persons":                  [],
        "moods":                    [],
        "possessive_forms":         [],
        "commitment":               0,

        "sensations_words":         [],
        "sensations":               {},

        "sentences":                [],
        "sentences_results":        [],

        "applied_rules":            []
    }
    return global_results


def init_sentence_results(sentence_index):
    sentence_results = dict()
    # sentence_results['{}'.format(sentence_index)] = {
    sentence_results = {
        "sentence_text":           '',
        "sections":                '',
        "order":                   0,
        "confidence_rate":         0,
        "reliability_rate":        99999,
        "emotional_contradiction": False,
        "performance":             0,
        "document_word_count":     0,
        "char_count":              0,
        "emotional_word_count":    0,
        "negative":                False,

        "negative_words":          [],
        "superlative_words":       [],
        "emotes":                  [],
        "compound_words":          [],
        "words":                   [],
        "word_occurences":         [],
        "emotional_words":         [],
        "simple_words":            [],
        "skipped_words":           [],
        "unknown_words":           [],
        "extra_words":             [],
        "insistance_words":        [],
        "inversion_words":         [],
        "lower_words":             [],
        "complex_words":           [],
        "corrected_words":         [],
        "idiomatic_expressions":   [],
        "uppercase_words":         [],
        "punctuation_coeff":       [],

        "eindex":                  0,
        "valence":                 0.0,
        "arousal":                 0.0,
        "dominance":               0.0,

        "happiness":               0.0,
        "surprise":                0.0,
        "calm":                    0.0,
        "fear":                    0.0,
        "sadness":                 0.0,
        "anger":                   0.0,
        "disgust":                 0.0,

        "positives_emotions_sum":  [],
        "negatives_emotions_sum":  [],
        "strongest_emotions":       [],

        "irony":                   False,
        "questioning":             False,
        "exclamation":             False,
        "comparative":             False,
        "comparative_words":       [],

        "tenses":                  [],
        "persons":                 [],
        "moods":                   [],
        "possessive_forms":        [],
        "commitment":              0,

        "sensations_words":        [],
        "sensations":              {},

        "applied_rules":           []
    }
    return sentence_results
