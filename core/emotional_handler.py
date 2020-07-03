import urllib3
import json
import operator
import re
import traceback
import string

import pandas as pd
import numpy as np
from collections import OrderedDict
from collections import Counter

from .emotional_variables_init import init_base
from .emotional_variables_init import init_global_results
from .emotional_variables_init import init_sentence_results
from core.data_preprocessor import TextTransformer

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class EmotionalHandler:

    def __init__(self, verbatim: str,
                 language: str,
                 words_as_df,
                 sentences: list,
                 verbatim_id: int,
                 forced_emotions=False):
        """
        Class Constructor
        :param verbatim: the verbatim to process
        :param language: the language of the verbatim
        :param words_as_df: the words present in the sentence
        :param forced_emotions: the emotions to force
        :param verbatim_id: id of the verbatim
        """
        tt = TextTransformer()
        
        if len(words_as_df) > 0:
            self.original_text = tt.multireplace(verbatim)
            self.text = self.prepare_text(tt.multireplace(verbatim))
            self.verbatim_id = verbatim_id
            self.lang = language
            self.forced_emotions = forced_emotions
            self.words_as_df = words_as_df
            # list of tuples [(sentence, id),...]
            self.sentences = [(tt.multireplace(x),y) for (x,y) in sentences] 
            self.base = init_base(self.text, self.lang,
                                  self.forced_emotions,
                                  self.verbatim_id)
            self.global_results = init_global_results()
            self.compound_words = self.words_as_df[
                (self.words_as_df['is_compound_word'] == True) &
                (self.words_as_df['is_emote'] == False)]
            self.call_functions()
            self.results = self.building_final_results(
                self.base,
                self.global_results
            )
        else:
            self.results = dict()

    @staticmethod
    def prepare_text(text: str):
        text = text.lower()
        return text

    @staticmethod
    def building_final_results(base: dict, global_results: dict):
        """
        Concatenate basic result dict with global results dict
        :param base: basic result dict
        :param global_results: advanced result dict
        :return: concatenation of base and global results
        """
        # Convert global_results' strongest emotions to strings
        global_results['strongest_emotions'] = \
            [list(map(str, x)) for x
             in global_results['strongest_emotions']]
        # Convert sentence results' strongest emotions to strings
        global_results['sentences_results'] = [dict(res) for res in [[
            (key[0], list(map(str, key[1]))) if
            key[0] is 'strongest_emotions' else key for key in
            sent.items()] for sent in global_results
                ['sentences_results']]
        ]
        # Concatenate basic verbatim info with emotional results
        base['global_results'] = global_results
        return base

    @staticmethod
    def do_word_list(sentences: list):
        """
        Split verbatim into word list
        :param sentences: sentences of the verbatim
        :return: a list of words
        """
        word_list = list()
        # Create a list of words from verbatim
        for sent in sentences:
            for word in sent:
                pure_word = word.text.lower()
                pure_word = re.sub('[.,\/#?!$%\^&\*;:{}=\-_`~()]', '',
                                   pure_word)
                word_list.append(pure_word)
        return word_list

    def call_functions(self):
        """
        call the three main functions
        :return:
        """
        # Call the three mains functions
        # TODO: Modifier la facon de faire dans le future
        self.initialize_sentences_results_structures()
        self.search()
        self.set_global_results()
        if self.forced_emotions is not None:
            self.set_forced_emotions()

    def initialize_sentences_results_structures(self):
        """
        Create the sentence result structure for
        each sentence of the verbatim
        :return:
        """
        # Initialize a sentence result structure for each sentence
        for sent in self.sentences:
            self.global_results['sentences_results'].append(
                init_sentence_results(sent[1]))

    def get_word_from_df(self, word: str):
        """
        Return a serie for a word stored in the dataframe
        :param word: the word we want the serie of
        :return: the word as a serie or None if does not exist
        """
        # Delete special char from word
        w = re.sub('[.,\/#?!$%\^&\*;:{}=\-_`~()]', '', word)
        # Get all 'word' words from data (Added try except to
        # bypass errors on Emojis "float" has no uper function)
        try:
            words = self.words_as_df[self.words_as_df['name'] == w]
        except:
            return None
        # Choose the lastest word added if several words with
        # the same spelling
        if len(words) > 1:
            lst_of_ids = list()
            for index, wordd in words.iterrows():
                lst_of_ids.append(int(wordd['id']))
            return words.iloc[lst_of_ids.index(max(lst_of_ids))]
        # Return the word if only one word with the spelling 'word'
        if len(words) == 1:
            return words.iloc[0]
        else:
            return None

    def force_emotions(self, results: dict):
        """
        Force some emotions
        :param results: the forced emotions
        :return:
        """
        # TODO: a tester
        self.global_results = results
        self.get_final_eindex(self.global_results)

    def set_forced_emotions(self):
        """
        Set the forced emotions we passed as parameter
        :return:
        """
        # TODO: a tester
        if self.forced_emotions is not False:
            self.global_results['applied_rules'].append({
                "type": "set_forced_emotions",
                "name": 'rule 1'
            })
            for emotion, value in self.forced_emotions.items():
                self.global_results[emotion] = int(value)
                self.global_results['strongest_emotions'].append(
                    [emotion, int(value)])

    # # # # # # # # # # # # # # # # # # # # #
    #                                       #
    #          SENTENCES FUNCTIONS          #
    #                                       #
    # # # # # # # # # # # # # # # # # # # # #

    def search(self):
        """
        Initialize the words to skip, set the sentence index,
        get sentence results, handle emotional balance
        :return:
        """
        # Compute emotions for each sentence
        for sentence in self.sentences:
            # Initiliaze the words to skip
            skip_words = {"skip_word": [], "skip_superlative": [],
                          "skip_compound": []}
            # Initialize sentence index
            index = sentence[1]
            # Initilize sentence results object
            sentence_results = \
                self.global_results['sentences_results'][
                    index]  # ['{}'.format(index)]
            # Define sentence (string)
            sentence_results['sentence_text'] = sentence[0].lower()
            # Compute emotions for the sentence
            self.get_sentence_results(sentence_results, index,
                                      skip_words)
            # Balance emotions for the sentence
            self.handle_emotions(sentence_results)
            if sentence_results['negative']:
                sentence_results['eindex'] = 18
            # Additional calculations for sentence
            self.set_sentence_results(sentence_results)

    def get_sentence_results(self, sentence_results: dict, index: int,
                             skip_words: dict):
        """
        Get the several type of words, delete and fix sentence string,
        parse simple words and add words to respective lists
        :param sentence_results: the sentence results
        :param index: the index of the sentence
        :param skip_words: the words to skip
        :return:
        """
        sentence_results['order'] = index
        # Get some words from the sentence
        self.look_over_sentence(sentence_results, skip_words)
        # Parse the sentence to avoid any errors
        sentence_text = sentence_results['sentence_text']
        #no_quote_text = re.sub("'", ' ', sentence_text)
        #no_quote_text = re.sub('`', ' ', no_quote_text)
        #no_quote_text = re.sub('’', ' ', no_quote_text)
        no_quote_text = sentence_text 
        no_quote_text = re.sub('(\.\s?\b)', '. ', no_quote_text)
        no_quote_text = re.sub('(\!\b)', '! ', no_quote_text)
        no_quote_text = re.sub('(\,\b)', ', ', no_quote_text)
        no_quote_text = re.sub('(\)\b)', ') ', no_quote_text)
        no_quote_text = re.sub('(\?\b)', '? ', no_quote_text)
        # Transform sentence to list of words
        word_list = self.explode_text_into_word_array(no_quote_text)
        # Define number of words in the sentence
        sentence_results['document_word_count'] += \
            len(sentence_results['sentence_text'].split(' '))
        # Lenght of the sentence
        sentence_results["char_count"] = len(
            sentence_results['sentence_text'])
        words_present_in_compound_words = list()
        # Create a list of words present in the compound words
        for compound_word in sentence_results['compound_words']:
            words_present_in_compound_words.append(compound_word['word']
                                                   .split(' '))
        # TODO: to be reviewd (apparently it slows the operation)
        # Fill unknown words list
        #sentence_results['unknown_words'] = \
        #        self.words_as_df[
        #            (self.words_as_df['name']!=self.words_as_df['name']
        #                 .index
        #                 .str.strip())
        #        ]['name'].tolist()
        # Iterate throught the list of words to
        # add (if necessary) some words
        for i, word in enumerate(word_list):
            word = re.sub('[.,\/#?!$%\^&\*;:{}=\-_`~()]', '', word)
            compute = True
            for c_word in skip_words['skip_compound']:
                for c_w in self.explode_text_into_word_array(c_word):
                    if c_w == word:
                        compute = False
            for index, word_in_cw in enumerate(
                    words_present_in_compound_words):
                if word in word_in_cw:
                    word_in_cw.remove(word)
                    compute = False
                    break
            if word in sentence_results['emotes']:
                compute = False
            if word in skip_words['skip_word']:
                sentence_results['skipped_words'].append({
                    "word": word
                })
                compute = False
                skip_words['skip_word'].remove(word)
            if not compute:
                continue
            is_compound = False
            found_word = self.get_word_from_df(word)
            # TODO: I added the second condition as a tmp workaround
            if found_word is None:
                if (word not in sentence_results['unknown_words']
                    and  word in sentence_results['sentence_text']):
                    sentence_results['unknown_words'].append(word)
                continue
            try:
                # Deal with a comparative word
                if found_word['is_comparative'] == True:
                    self.handle_comparative(sentence_results,
                                            found_word)
                # Deal with a superlative word
                if found_word['is_superlative'] == True:
                    self.handle_superlative(sentence_results, word,
                                            found_word,
                                            i, skip_words)
                # Deal with compound word
                if is_compound is True:
                    self.add_found_compound_emotional_word(
                        sentence_results, word, found_word)
                # Else, deal with simple word
                else:
                    self.add_found_emotional_word(sentence_results,
                                                  word, found_word)
                # Add word emotions to sentence results
                self.primary_emotion_word(sentence_results,
                                          word, found_word)
            except Exception as e:
                print('Erreur sentence results: ', e)
                traceback.print_exc()
                continue
        if len(sentence_results['insistance_words']) > 0:
            self.apply_insistance_words_coeff(sentence_results)

    @staticmethod
    def apply_insistance_words_coeff(sentence_results):
        coeff = sentence_results['insistance_words'][0][
            'insistance_coeff']
        for key in ['eindex', 'happiness', 'surprise', 'calm',
                    'sadness', 'fear', 'anger', 'disgust']:
            if sentence_results[key] is not None:
                sentence_results[key] *= coeff
                sentence_results[key] = round(sentence_results[key])

    def look_over_sentence(self, sentence_results: dict,
                           skip_words: dict):
        """
        Get compound words and emotes from the verbatim
        :param sentence_results: the sentence results
        :param skip_words: the words to skip
        :return:
        """
        # Get all compound words from sentence
        self.find_and_handle_compound_words(sentence_results,
                                            skip_words)
        # Get all emotes from sentence
        self.find_and_handle_emotes(sentence_results)
        self.find_and_handle_insistance_words(sentence_results)

    def set_sentence_results(self, sentence_results: dict):
        """
        Set number of word in the sentence
        Set number of emotional words
        in the sentence and calculate performance rate
        :param sentence_results: the sentence results
        :return:
        """
        # Get number of words in sentence
        sentence_word_count = sentence_results['document_word_count']
        if sentence_word_count == 0:
            sentence_word_count = 1
        nb_words_into_compound_words = 0
        # Iterate through compound words
        for cw in sentence_results['compound_words']:
            nb_words_into_compound_words += len(cw['word'].split(' '))
        emotional_word_count = len(sentence_results['words']) + \
            nb_words_into_compound_words + len(
            sentence_results['skipped_words'])
        # Define number of emotional words in sentence
        sentence_results['emotional_word_count'] = emotional_word_count
        # Calculate performance rate
        sentence_results['performance'] = round(
            (float(emotional_word_count) / sentence_word_count) * 100)
        # Handle emotions of sentence
        self.emotions_ponderation_then_reliability(
            sentence_results,
            {"sentence_index": sentence_results['order'],
             "sentence_text": sentence_results['sentence_text']})

    @staticmethod
    def explode_text_into_word_array(text: str):
        """
        Explode the verbatim into a list of words
        :param text: the verbatim
        :return: a list of words
        """
        array = str(text.lower()).split(' ')
        if len(array) == 0:
            array = [re.sub('[.,\/#?!$%\^&\*;:{}=\-_`~()]', '', text)]
            return array
        lst = list()
        # Delete special chars from words
        for word in array:
            lst.append(re.sub('[.,\/#?!$%\^&\*;:{}=\-_`~()]', '', word))
        return lst

    def apply_punctuaction_coeff(self, sentence_results: dict,
                                 max_emotion):
        """
        Calculate and apply punctuation coeff
        :param sentence_results: the sentence results
        :param max_emotion: the max emotion of the sentence
        :return:
        """
        # Define strong emotions markers
        strong_punctuation_markers = ['??', '?!', '!?', '!!']
        sentence = sentence_results['sentence_text']
        verbatim = self.text
        # Iterate throught punctuation markers
        for punctuation_marker in strong_punctuation_markers:
            # Get all positions of the current punctuation marker
            positions = self.get_positions_for(punctuation_marker)
            # Iterate throught positions
            for position in positions:
                sentence_lenght = len(sentence)
                if sentence_results['order'] == 0:
                    sentence_section = verbatim[0:position]
                else:
                    sentence_section = \
                        verbatim[position:sentence_lenght]
                sentence_section = sentence_section.replace("!", "")\
                    .replace("?", "")
                if sentence_section.lower().strip() in sentence.lower()\
                        and len(sentence_section) > 1:
                    punc_count = 1
                    sub_pos = position
                    while verbatim[sub_pos+1] in ['?', '!']:
                        punc_count += 1
                        sub_pos += 1
                    coeff = 2 + (punc_count - 2) * 0.1
                    max_emotion[1] = float(max_emotion[1] * coeff)
                    sentence_results['punctuation_coeff'] = {
                        "applied": True,
                        "coeff": coeff,
                        "sentence_idx": sentence_results['order']
                    }

    def get_positions_for(self, punctuation_mark):
        """
        Find positions for a given punctuation mark
        :param punctuation_mark: a punctuation mark like '!' or '?'
        :return: all positions of this punctuation mark
        """
        positions = list()
        res = 0
        next_pos = 0
        # Get positions of a punctation mark
        while res != -1:
            # Find a position of the punctuation mark
            res = self.text.find(punctuation_mark, next_pos)
            next_pos += res + 1
            if res != -1:
                next_pos += res + 1
                positions.append(res)
        return positions

    # # # # # # # # # # # # # # # # # # # # #
    #                                       #
    #           COMPOUND WORDS              #
    #                                       #
    # # # # # # # # # # # # # # # # # # # # #

    def find_and_handle_compound_words(self, sentence_results: dict,
                                       skip_words: dict):
        """
        Find all compound words of the sentence and keep only the one
        that have to be kept
        :param sentence_results: the sentence results
        :param skip_words: the words to skip
        :return:
        """
        sentence_str = sentence_results['sentence_text'].lower()
        # Get all compounds words
        compound_words = self.compound_words
        found_compound_words = list()
        cw_already_taken = list()
        # Iterate though compound words
        for index, cw in compound_words.iterrows():
            name = cw['name']
            if len(name.split(' ')) > 1:
                compound_word = name
                if compound_word in sentence_str:
                    # Check if compound words already taken
                    if cw_already_taken.count(compound_word) < \
                            sentence_str.count(compound_word):
                        cw_already_taken.append(compound_word)
                        found_compound_words.append(
                            {
                                "compound_word": compound_word,
                                "id": int(cw['id']),
                                "begin": sentence_str.index(
                                    compound_word),
                                "end": sentence_str.index(
                                    compound_word) + len(compound_word),
                                "lenght": len(compound_word),
                                "is_superlative": cw['is_superlative']
                            }
                        )
        # Function that remove the punctation except apostrophe
        def remove_punct(string_: str):
            # All punct except apostrophe
            punct = string.punctuation.replace("'",'')
            replace_punctuation = str.maketrans(
                punct, ' '*len(punct))
            return string_.translate(replace_punctuation)
        # Parse compound words if some compound words were found
        if len(found_compound_words) != 0:
            new_found_compound_words = list()
            # Sort compound words by lenght (longest to shortest)
            for cw in sorted(found_compound_words, key=lambda l: len(
                    l['compound_word']), reverse=True):
                new_found_compound_words.append(cw)
            # Keep the longest compound word if some
            # compound words have commun words
            new_found_compound_words = self.keep_longest_compound_words(
                found_compound_words, sentence_str)
            sentence = sentence_results['sentence_text']
            for cw in new_found_compound_words:
                nxt = False
                for c_word in cw['compound_word'].split(' '):
                    if c_word in skip_words['skip_word']:
                        nxt = True
                if nxt is True:
                    continue
                next_word = None
                try:
                    sent_index = sentence.index(cw['compound_word'])-1
                    if sentence[0:sent_index]!= \
                            cw['compound_word'] or \
                       remove_punct(sentence).strip() == \
                            cw['compound_word'].strip() :
                        next_word = sentence[sentence.index(
                            cw['compound_word']) +
                                             len(cw['compound_word'])
                                             :].strip().split(' ')[0]
                        if next_word is not None:
                            next_word = re.sub(
                                '[.,\/#?!$%\^&\*;:{}=\-_`~()]', '',
                                next_word)
                    else:
                        return
                except Exception as e:
                    print('Error getting next word: ', e)
                    return
                found_compound_word = None
                # Get detailled compound words info
                words = self.words_as_df[self.words_as_df['name'] ==
                                         cw['compound_word']]
                for index, word in words.iterrows():
                    indexed_word = word
                    if len(indexed_word['name'].split(' ')) > 1:
                        if cw['compound_word'] == indexed_word['name']:
                            if found_compound_word is None:
                                found_compound_word = indexed_word
                            else:
                                if len(indexed_word['name']) > len(
                                        found_compound_word['name']):
                                    found_compound_word = indexed_word
                found_next_word = None
                if len(next_word) != 0:
                    found_next_word = self.get_word_from_df(next_word)
                if found_compound_word is not None and found_next_word \
                        is not None:
                    if found_compound_word['is_superlative'] == True:
                        self.handle_compound_superlative(
                            sentence_results, cw['compound_word'],
                            found_compound_word, found_next_word,
                            skip_words)
                # Prepare to add word if not None
                if found_compound_word is not None:
                    if found_compound_word['is_comparative'] == True:
                        sentence_results['comparative_words'].append(cw)
                        sentence_results['comparative'] = True
                    name = str(found_compound_word['name'])
                    # Add compound words to found words and add
                    # emotions to sentence results
                    if name not in skip_words['skip_word'] and \
                            name not in skip_words['skip_compound']:
                        self.add_found_compound_emotional_word(
                            sentence_results, cw['compound_word'],
                            found_compound_word)
                    self.primary_emotion_compound_word(
                            sentence_results, cw['compound_word'],
                            found_compound_word)
                    continue

    def keep_longest_compound_words(self, found_compound_words: list,
                                    sentence: str):
        """
        Keep the longest compound words in a list of compounds words
        :param found_compound_words: list of compound words
        found in the sentence
        :param sentence: the sentence
        :return: a list of compound words
        """
        cw_to_keep = list()
        list_words=[x['compound_word'] for x in found_compound_words]
        # Iterate through compound words to choose the longest words
        for cw in found_compound_words:
            word = cw['compound_word']
            word_in_another = self.is_in_another(
                list(set(list_words)-set([word])), word)
            if not word_in_another:
                cw_to_keep.append(cw)
        return cw_to_keep

    def is_in_another(self, cw_to_keep: list, word: str):
        """
        Check if a compound word is part of another compound word
        :param cw_to_keep: a list of compound words to keep
        :param word: the word to check
        :return: True if in another, False if not
        """
        for cw in cw_to_keep:
            if word in cw:
                return True
        return False

    def occurence_in_sentence(self, sentence: str, sub_word: str,
                              cw_to_keep: list):
        """
        Check the number of time the word appears in the sentence
        :param sentence: the sentence
        :param sub_word: the word we want to check
        :param cw_to_keep: a list of compound words to keep
        :return: True if word is more present in compound words
        """
        # Return True if the number of occurence of the word in the
        # sentence is inferior to number of occurence in another
        # compound words
        return sentence.count(sub_word) <= self.word_occurence(
            cw_to_keep, sub_word)

    @staticmethod
    def word_occurence(cw_to_keep: list, word: str):
        """
        Check how many times the word is present in other compound words
        :param cw_to_keep: a list of compound words to keep
        :param word: the word we want to check
        :return: the number of occurence of this word
        """
        # Count the number of occurence of a word in another
        # compound words
        count = 0
        for cw in cw_to_keep:
            count += cw['compound_word'].count(word)
        return count

    # # # # # # # # # # # # # # # # # # # # #
    #                                       #
    #           INSISTANCE WORDS            #
    #                                       #
    # # # # # # # # # # # # # # # # # # # # #

    # TODO: PROBABLY NOT WORKING YET
    def find_and_handle_insistance_words(self, sentence_results: dict):
        """
        Find and parse insistance words found in the verbatim
        :param sentence_results: the sentence results
        :return:
        """
        if 'is_insistance_word' not in self.words_as_df.columns:
            return None
        else:
            insistance_words = self.words_as_df[
                self.words_as_df['is_insistance_word'] == True]
            found_insistance_words = list()
            insistance_word_already_taken = list()
            sentence_str = sentence_results['sentence_text']
            for index, iw in insistance_words.iterrows():
                name = iw['name']
                if name in sentence_str:
                    if insistance_word_already_taken.count(name) < \
                            sentence_str.count(name):
                        insistance_word_already_taken.append(name)
                        found_insistance_words.append(
                            {
                                "insistance_word": name,
                                "id": int(iw['id']),
                                "begin": sentence_str.index(name),
                                "end": sentence_str.index(name) + len(
                                    name
                                ),
                                "lenght": len(name),
                                "is_superlative": iw['is_superlative']
                            }
                        )
                        break
            if len(found_insistance_words) != 0:
                for iw in found_insistance_words:
                    detailled_iw = self.get_word_from_df(
                        iw['insistance_word'])
                    if detailled_iw is None:
                        continue
                    self.add_found_insistance_word(
                        sentence_results,
                        iw['insistance_word'],
                        detailled_iw,
                        'insistance_words'
                    )
                    if ' ' in iw['insistance_word']:
                        self.primary_emotion_compound_word(
                            sentence_results,
                            iw['insistance_word'],
                            detailled_iw)
                    else:
                        self.primary_emotion_word(sentence_results,
                                                  iw['insistance_word'],
                                                  detailled_iw)

    # # # # # # # # # # # # # # # # # # # # #
    #                                       #
    #           SUPERLATIVE WORDS           #
    #                                       #
    # # # # # # # # # # # # # # # # # # # # #

    def handle_compound_superlative(self, sentence_results: dict,
                                    compound_word: str,
                                    found_compound_word: dict,
                                    found_superlative_word: dict,
                                    skip_words: dict):
        """
        Handle and apply several rules to superlative compound words
        :param sentence_results: the sentence results
        :param compound_word: the compound word
        :param found_compound_word: the compound word with
        detailled info
        :param found_superlative_word: the superlative word with
        detailled info
        :param skip_words: the words to skip
        :return:
        """
        # Get all emotions and superlative coeff and convert them to
        # avoid errors when indexing data in Elasticsearch
        superlative_coeff = float(
            found_compound_word['superlative_coeff'])
        happiness_score = float(found_superlative_word['happiness']) \
            * superlative_coeff
        surprise_score = float(found_superlative_word['surprise']) \
            * superlative_coeff
        calm_score = float(found_superlative_word['calm']) \
            * superlative_coeff
        fear_score = float(found_superlative_word['fear']) \
            * superlative_coeff
        sadness_score = float(found_superlative_word['sadness']) \
            * superlative_coeff
        anger_score = float(found_superlative_word['anger']) \
            * superlative_coeff
        disgust_score = float(found_superlative_word['disgust']) \
            * superlative_coeff
        already_in = False
        # Check if the word is already in sentence results
        for emotional_word in sentence_results['emotional_words']:
            if found_superlative_word['id'] == emotional_word['id']:
                already_in = True
        # Compute superlative compound word
        if already_in is False:
            self.add_found_compound_emotional_word(sentence_results,
                                                   compound_word,
                                                   found_compound_word)
            if round(happiness_score, 1) > 0:
                sentence_results['happiness'] += round(happiness_score,
                                                       1)
            if round(surprise_score, 1) > 0:
                sentence_results['surprise'] += round(surprise_score, 1)
            if round(calm_score, 1) > 0:
                sentence_results['calm'] += round(calm_score, 1)
            if round(fear_score, 1) > 0:
                sentence_results['fear'] += round(fear_score, 1)
            if round(sadness_score, 1) > 0:
                sentence_results['sadness'] += round(sadness_score, 1)
            if round(anger_score, 1) > 0:
                sentence_results['anger'] += round(anger_score, 1)
            if round(disgust_score, 1) > 0:
                sentence_results['disgust'] += round(disgust_score, 1)
            count = 0
            for emo_word in sentence_results['emotional_words']:
                if found_superlative_word['name'] == emo_word['word']:
                    count += 1
            if count == 0:
                sentence_results['emotional_words'].append({
                    "word": found_superlative_word['name'],
                    "id": int(found_superlative_word['id']),
                    "happiness": round(happiness_score, 1),
                    "surprise": round(surprise_score, 1),
                    "calm": round(calm_score, 1),
                    "fear": round(fear_score, 1),
                    "sadness": round(sadness_score, 1),
                    "anger": round(anger_score, 1),
                    "disgust": round(disgust_score, 1)
            })
            # Add word if not added yet
            if self.superlative_already_taken(
                    sentence_results,
                    found_compound_word['name'],
                    found_superlative_word['name']) is False:
                sentence_results['superlative_words'].append({
                    "word": found_compound_word['name'],
                    "superlative_coeff": float(
                        found_compound_word['superlative_coeff']),
                    "on": found_superlative_word['name'],
                    "happiness": round(happiness_score, 1),
                    "surprise": round(surprise_score, 1),
                    "calm": round(calm_score, 1),
                    "fear": round(fear_score, 1),
                    "sadness": round(sadness_score, 1),
                    "anger": round(anger_score, 1),
                    "disgust": round(disgust_score, 1)
                })
            # Add word to words to skip
            skip_words['skip_word'].append(
                found_superlative_word['name'])
            skip_words['skip_superlative'].append(
                found_compound_word['name'])
            skip_words['skip_compound'].append(
                found_compound_word['name'])

    def handle_superlative(self, sentence_results: dict, word: str,
                           found_word: dict, current_word_index: int,
                           skip_words: dict):
        """
        Handle and parse superlative words
        :param sentence_results: the sentence results as a dict
        :param word: the superlative word
        :param found_word: the superlative word with detailled info
        :param current_word_index: the index of the word in the sentence
        :param skip_words: the words to skip
        :return:
        """
        # Parse sentence to delete special chars
        sentence_text = sentence_results['sentence_text']
        no_quote_text = re.sub("'", ' ', sentence_text)
        no_quote_text = re.sub('`', ' ', no_quote_text)
        no_quote_text = re.sub('’', ' ', no_quote_text)
        no_quote_text = re.sub('(\.\s?\b)', '. ', no_quote_text)
        no_quote_text = re.sub('(\!\b)', '! ', no_quote_text)
        no_quote_text = re.sub('(\,\b)', ', ', no_quote_text)
        no_quote_text = re.sub('(\)\b)', ') ', no_quote_text)
        no_quote_text = re.sub('(\?\b)', '? ', no_quote_text)
        # Explode sentence to list of words
        word_list = self.explode_text_into_word_array(no_quote_text)
        # Get word that the superlative will have effects on
        for rank in [1, 2]:
            n_word = None
            try:
                if word_list[current_word_index + rank] is not None:
                    n_word = word_list[current_word_index + rank]
            except IndexError:
                pass
            if n_word is None:
                continue
            if n_word is not None:
                n_word_index = self.get_word_from_df(n_word)
                if n_word_index is not None:
                    # Get emotions and superlative coeff and convert
                    # those values to float to avoid errors when
                    # indexing data into ES
                    superlative_coeff = \
                        float(found_word['superlative_coeff'])
                    indexed_word = n_word_index
                    happiness_score = float(indexed_word['happiness']) \
                        * superlative_coeff
                    surprise_score = float(indexed_word['surprise']) \
                        * superlative_coeff
                    calm_score = float(indexed_word['calm']) \
                        * superlative_coeff
                    fear_score = float(indexed_word['fear']) \
                        * superlative_coeff
                    sadness_score = float(indexed_word['sadness']) \
                        * superlative_coeff
                    anger_score = float(indexed_word['anger']) \
                        * superlative_coeff
                    disgust_score = float(indexed_word['disgust']) \
                        * superlative_coeff
                    # If word is emotional then add it
                    if happiness_score > 0.0 or surprise_score > 0.0 \
                            or calm_score > 0.0 or \
                            fear_score > 0.0 or sadness_score > 0.0 \
                            or anger_score > 0.0 or disgust_score > 0.0:
                        for emotional_word in \
                                sentence_results['emotional_words']:
                            if emotional_word['id'] == \
                                    indexed_word['id']:
                                sentence_results['emotional_words']\
                                    .remove(emotional_word)
                                if emotional_word in \
                                   sentence_results['words']:
                                    sentence_results['words'].remove(
                                        emotional_word)
                        self.add_found_emotional_word(
                            sentence_results,
                            n_word, n_word_index)
                        if round(happiness_score, 1) > 0:
                            sentence_results['happiness'] += \
                                round(happiness_score, 1)
                        if round(surprise_score, 1) > 0:
                            sentence_results['surprise'] += \
                                round(surprise_score, 1)
                        if round(calm_score, 1) > 0:
                            sentence_results['calm'] += \
                                round(calm_score, 1)
                        if round(fear_score, 1) > 0:
                            sentence_results['fear'] += \
                                round(fear_score, 1)
                        if round(sadness_score, 1) > 0:
                            sentence_results['sadness'] += \
                                round(sadness_score, 1)
                        if round(anger_score, 1) > 0:
                            sentence_results['anger'] += \
                                round(anger_score, 1)
                        if round(disgust_score, 1) > 0:
                            sentence_results['disgust'] += \
                                round(disgust_score, 1)
                        # Add word to emotional words list
                        count = 0
                        for emo_word in sentence_results[
                            'emotional_words']:
                            if n_word == emo_word['word']:
                                count += 1
                        if count == 0:
                            sentence_results['emotional_words'].append({
                                "word": n_word,
                                "id": int(indexed_word['id']),
                                "happiness": round(happiness_score, 1),
                                "surprise": round(surprise_score, 1),
                                "calm": round(calm_score, 1),
                                "fear": round(fear_score, 1),
                                "sadness": round(sadness_score, 1),
                                "anger": round(anger_score, 1),
                                "disgust": round(disgust_score, 1)
                        })
                        # Add words to superlative words if not
                        # already taken
                        if self.superlative_already_taken(
                                sentence_results,
                                word, n_word) is False:
                            sentence_results['superlative_words']\
                                .append({
                                    "word": word,
                                    "superlative_coeff":
                                        float(found_word[
                                            'superlative_coeff']),
                                    "on": n_word,
                                    "happiness": round(happiness_score,
                                                       1),
                                    "surprise": round(surprise_score,
                                                      1),
                                    "calm": round(calm_score, 1),
                                    "fear": round(fear_score, 1),
                                    "sadness": round(sadness_score, 1),
                                    "anger": round(anger_score, 1),
                                    "disgust": round(disgust_score, 1)
                                })
                            skip_words['skip_word'].append(n_word)

    @staticmethod
    def superlative_already_taken(sentence_results: dict, word: str,
                                  n_word: str):
        """
        Check if a superlative word has already been treated
        :param sentence_results: the sentence results as a dict
        :param word: the superlative word
        :param n_word: the word after the superlative
        :return: True if yes, False if not
        """
        # check if the superlative words has already been added
        for sw in sentence_results['superlative_words']:
            if sw['word'] == word and sw['on'] == n_word:
                return True
        return False

    # # # # # # # # # # # # # # # # # # # # #
    #                                       #
    #                EMOTES                 #
    #                                       #
    # # # # # # # # # # # # # # # # # # # # #

    def find_and_handle_emotes(self, sentence_results: dict):
        """
        Find all emotes in the verbatim
        :param sentence_results: the sentence results
        :return:
        """
        # Handle overlap emotes (takes list of pandas series)
        def handle_overlap_(needles):
            count = Counter()
            res =  Counter()
            for element in needles: count[str(element['name'])] += 1
            for needle in count.keys():
                occurence = [0]
                for needle_tmp in count.keys():
                    if needle in needle_tmp and needle != needle_tmp:
                        occurence.append(count[needle_tmp])
                res[needle] = count[needle] - max(occurence)
            return res
        # Transform a counter to list with the same occurence
        def flatten_counter(counter_object):
            res=[]
            for element in counter_object.keys():
                res = res + ([element] * counter_object[element])
            return res
        # Get emotes list
        emotes_list = self.words_as_df[
            self.words_as_df['is_emote'] == True].drop_duplicates(
                subset=['name'])
        emotes_found = list()
        # Iterate through emotes and get those that are in the sentence
        # to avoid multiplying emotes
        for index, emote_obj in emotes_list.iterrows():
            for i in range(sentence_results['sentence_text'].count(
                    str(emote_obj['name']))):
                emotes_found.append(emote_obj)
        #-------------------------------
        # To filter overlapped emotes
        emotes_found_final = list()
        handled_overlap = handle_overlap_(emotes_found)
        # Iterate through emotes and get those that are in the sentence
        for emote_obj in emotes_found:
            if handled_overlap[str(emote_obj['name'])] > 0:
                emotes_found_final.append(emote_obj)
                handled_overlap[str(emote_obj['name'])] -= 1
        emotes_found = emotes_found_final
        # Add emote if emote obj is not None
        for emote in emotes_found:
            if emote is not None and emote['name'] == emote['name']:
                # Add emote to emotional words
                self.add_found_emotional_word(sentence_results,
                                              emote['name'],
                                              emote)
                # Add emote emotions to sentence results
                self.primary_emotion_word(sentence_results,
                                          emote['name'], emote)
                # Initialize emote structure and add it to sentence list
                # of emotes
                sentence_results['emotes'].append({
                    "word": emote['name'],
                    "id": int(emote['id']),
                    "eindex": emote['indice'],
                    "valence": emote['valence'],
                    "arousal": emote['arousal'],
                    "dominance": emote['dominance'],
                    "happiness": emote['happiness'],
                    "surprise": emote['surprise'],
                    "calm": emote['calm'],
                    "fear": emote['fear'],
                    "sadness": emote['sadness'],
                    "anger": emote['anger'],
                    "disgust": emote['disgust'],
                })

    # # # # # # # # # # # # # # # # # # # # #
    #                                       #
    #           COMPARATIVE WORDS           #
    #                                       #
    # # # # # # # # # # # # # # # # # # # # #

    @staticmethod
    def handle_comparative(sentence_results: dict, found_word: dict):
        """
        Add comparative words to sentence results
        :param sentence_results: the sentence results
        :param found_word: the word to add
        :return:
        """
        # Add comparative word to list of comparative words
        sentence_results['comparative_words'].append(found_word['name'])
        # Set sentence as a comparative sentence
        sentence_results['comparative'] = True

    # # # # # # # # # # # # # # # # # # # # #
    #                                       #
    #               ADD WORDS               #
    #                                       #
    # # # # # # # # # # # # # # # # # # # # #

    @staticmethod
    def add_found_emotional_word(sentence_results: dict, word: str,
                                 found_word: dict):
        """
        Add an emotional word to results
        :param sentence_results: the sentence results
        :param word: the word to add
        :param found_word: the word to add with detailled info
        :return:
        """
        # Add eindex, valence, arousal and dominance score to
        # sentence results
        if sentence_results['eindex'] is not None:
            sentence_results['eindex'] += float(found_word['indice'])
        sentence_results['valence'] += float(found_word['valence'])
        sentence_results['arousal'] += float(found_word['arousal'])
        sentence_results['dominance'] += float(found_word['dominance'])
        sensations = dict()
        # Initiliaze emotional word structure
        word_dct = {
            "word": word,
            "id": int(found_word['id']),
            "eindex": float(found_word['indice']),
            "valence": float(found_word['valence']),
            "arousal": float(found_word['arousal']),
            "dominance": float(found_word['dominance']),
            "sensations": sensations
        }
        count = 0
        for word in sentence_results['words']:
            if word['word'] == word_dct['word']:
                count += 1
        # If not already added, we add the word ¯\_(ツ)_/¯
        if count == 0:
            sentence_results['words'].append(word_dct)

    @staticmethod
    def add_found_compound_emotional_word(sentence_results: dict,
                                          word: str, found_word: dict):
        """
        Add an emotional compound word to the results
        :param sentence_results: the sentence results
        :param word: the compound word to add
        :param found_word: the compound word to add with detailled info
        :return:
        """
        # Add the eindex, valence, arousal and dominance score to
        # sentence results
        if sentence_results['eindex'] is not None:
            sentence_results['eindex'] += float(found_word['indice'])
        sentence_results['valence'] += float(found_word['valence'])
        sentence_results['arousal'] += float(found_word['arousal'])
        sentence_results['dominance'] += float(found_word['dominance'])
        # Get word's ID
        word_id = int(found_word['id'])
        # If work is not "broken", we add it to the list of compound
        # words
        if word_id != 0:
            sensations = dict()
            word_dct = {
                "word": word,
                "id": int(word_id),
                "eindex": float(found_word['indice']),
                "valence": float(found_word['valence']),
                "arousal": float(found_word['arousal']),
                "dominance": float(found_word['dominance']),
                "sensations": sensations
            }
            sentence_results['compound_words'].append(word_dct)

    # TODO: WONDERING IF WE WILL USE IT OR NOT ¯\_(ツ)_/¯
    @staticmethod
    def add_found_insistance_word(sentence_results: dict, word: str,
                                  found_word: dict, key: str):
        """
        Add word depending on its type (insistance, lower, ...)
        :param sentence_results: the sentence resutls
        :param word: the word to add
        :param found_word: the word to add with detailled info
        :param key: the type of word to add
        :return:
        """
        if sentence_results['eindex'] is not None:
            sentence_results['eindex'] += float(found_word['indice'])
        sentence_results['valence'] += float(found_word['valence'])
        sentence_results['arousal'] += float(found_word['arousal'])
        sentence_results['dominance'] += float(found_word['dominance'])

        word_dct = {
            "word": word,
            "id": int(found_word['id']),
            "eindex": float(found_word['indice']),
            "valence": float(found_word['valence']),
            "arousal": float(found_word['arousal']),
            "dominance": float(found_word['dominance']),
            "insistance_coeff": float(
                    found_word['insistance_word_coeff'])
        }
        count = 0
        for word_ in sentence_results['words']:
            if word_['word'] == word_dct['word']:
                count += 1
        if count == 0:
            sentence_results[key].append(word_dct)

    def primary_emotion_word(
            self,sentence_results: dict, word: str,
            found_word: dict):
        """
        Add a word to emotional results
        :param sentence_results: the sentence results
        :param word: the word to add
        :param found_word: the word to add with detailled info
        :return:
        """
        uppercase_coeff = 1
        # TODO: IMPOSSIBLE BECAUSE WE LOWER ALL WORDS (TO FIX)
        if self.isupper(word):
            uppercase_coeff = 2
        happiness = 0
        surprise = 0
        calm = 0
        fear = 0
        sadness = 0
        anger = 0
        disgust = 0
        replaced_by = None
        # Calculate all emotional scores
        try:
            if found_word['replaced_by'] is not np.nan:
                replaced_by = found_word['replaced_by']
        except:
            pass
        if float(found_word['happiness']) > 0:
            happiness = float(found_word['happiness']) * uppercase_coeff
            sentence_results['happiness'] += happiness
        if float(found_word['surprise']) > 0:
            surprise = float(found_word['surprise']) * uppercase_coeff
            sentence_results['surprise'] += surprise
        if float(found_word['calm']) > 0:
            calm = float(found_word['calm']) * uppercase_coeff
            sentence_results['calm'] += calm
        if float(found_word['fear']) > 0:
            fear = float(found_word['fear']) * uppercase_coeff
            sentence_results['fear'] += fear
        if float(found_word['sadness']) > 0:
            sadness = float(found_word['sadness']) * uppercase_coeff
            sentence_results['sadness'] += sadness
        if float(found_word['anger']) > 0:
            anger = float(found_word['anger']) * uppercase_coeff
            sentence_results['anger'] += anger
        if float(found_word['disgust']) > 0:
            disgust = float(found_word['disgust']) * uppercase_coeff
            sentence_results['disgust'] += disgust
        if happiness == 0 and surprise == 0 and calm == 0 and \
                fear == 0 and disgust == 0 and anger == 0 \
                and sadness == 0:
            return
        # Initialize emotional word dict
        emotional_word = {
            "word": word,
            'replaced by': replaced_by,
            "id": int(found_word['id']),
            "happiness": float(round(happiness)),
            "surprise": float(round(surprise)),
            "calm": float(round(calm)),
            "fear": float(round(fear)),
            "sadness": float(round(sadness)),
            "anger": float(round(anger)),
            "disgust": float(round(disgust))
        }
        # Add word to emotional word list
        count = 0
        for emo_word in sentence_results['emotional_words']:
            if word == emo_word['word']:
                count += 1
        if count == 0:
            sentence_results['emotional_words'].append(emotional_word)
        # Add word to uppercase words if uppercase (impossible at the
        #  moment)
        if uppercase_coeff > 1:
            sentence_results['uppercase_words'].append({
                "word": word,
                "uppercase_coeff": float(uppercase_coeff)
            })

    def primary_emotion_compound_word(
            self, sentence_results: dict, word: str,
            found_word: dict):
        """
        Add an emotional compound word to the emotional results
        :param sentence_results: the sentence results as a dict
        :param word: the compound word to add
        :param found_word: the compound word to add with detailled info
        :return:
        """
        uppercase_coeff = 1.0
        # Set uppercase coeff is word is uppercased
        if self.isupper(word) is True:
            uppercase_coeff = 2.0
        happiness = 0
        surprise = 0
        calm = 0
        fear = 0
        sadness = 0
        anger = 0
        disgust = 0
        # Calculate emotional scores
        if float(found_word['happiness']) > 0:
            happiness = float(found_word['happiness']) * uppercase_coeff
            sentence_results['happiness'] += happiness
        if float(found_word['surprise']) > 0:
            surprise = float(found_word['surprise']) * uppercase_coeff
            sentence_results['surprise'] += surprise
        if float(found_word['calm']) > 0:
            calm = float(found_word['calm']) * uppercase_coeff
            sentence_results['calm'] += calm
        if float(found_word['fear']) > 0:
            fear = float(found_word['fear']) * uppercase_coeff
            sentence_results['fear'] += fear
        if float(found_word['sadness']) > 0:
            sadness = float(found_word['sadness']) * uppercase_coeff
            sentence_results['sadness'] += sadness
        if float(found_word['anger']) > 0:
            anger = float(found_word['anger']) * uppercase_coeff
            sentence_results['anger'] += anger
        if float(found_word['disgust']) > 0:
            disgust = float(found_word['disgust']) * uppercase_coeff
            sentence_results['disgust'] += disgust
        if happiness == 0 and surprise == 0 and calm == 0 and \
                fear == 0 and disgust == 0 and anger == 0 \
                and sadness == 0:
            return
        # Add compound word to list of emotional words
        count = 0
        for emo_word in sentence_results['emotional_words']:
            if word == emo_word['word']:
                count += 1
        if count == 0:
            sentence_results['emotional_words'].append({
                "word": word,
                "id": int(found_word['id']),
                "happiness": float(round(float(
                    found_word['happiness']) * uppercase_coeff)),
                "surprise": float(round(float(found_word['surprise']) *
                                  uppercase_coeff)),
                "calm": float(round(float(found_word['calm']) *
                              uppercase_coeff)),
                "fear": float(round(float(found_word['fear']) *
                              uppercase_coeff)),
                "sadness": float(round(float(found_word['sadness']) *
                                 uppercase_coeff)),
                "anger": float(round(float(found_word['anger']) *
                               uppercase_coeff)),
                "disgust": float(round(float(found_word['disgust']) *
                                 uppercase_coeff)),
            })
        # Add word to uppercased word if the word is uppercased
        # ¯\_(ツ)_/¯
        if uppercase_coeff > 1:
            sentence_results['uppercase_words'].append({
                "word": word,
                "uppercase_coeff": float(uppercase_coeff)
            })

    # # # # # # # # # # # # # # # # # # # # #
    #                                       #
    #           ADD SENSATIONS              #
    #                                       #
    # # # # # # # # # # # # # # # # # # # # #

    @staticmethod
    def add_sensations(sentence_results: dict, found_word: dict,
                       word: str):
        """
        Add sensations to sentence results and adding sensation word too
        :param sentence_results: the sentence results
        :param found_word: the word to add with detailled info
        :param word: the word to add as a string
        :return:
        """
        if found_word is None or len(found_word) == 0:
            pass
        sensations = json.loads(found_word)
        for sensation in sensations:
            if sensation not in sentence_results['sensations']:
                sentence_results['sensations'][sensation] = 0
            sentence_results['sensations'][sensation] = \
                sensations[sensation]
        if len(sensations) != 0:
            sentence_results['sensations_words'].append(
                {"word": word,
                 "sensations": sensations})

    # # # # # # # # # # # # # # # # # # # # #
    #                                       #
    #           EMOTIONS FUNCTIONS          #
    #                                       #
    # # # # # # # # # # # # # # # # # # # # #

    def handle_emotions(self, sentence_results: dict):
        """
        Check if some results are emotional and if yes, do an emotional
        balance
        :param sentence_results: the sentence results as a dict
        :return:
        """
        # If sentence has emotions, we balance them
        if self.object_has_one_emotion_score_superior_to(
                sentence_results, 0):
            self.emotional_balance(sentence_results)

    def emotional_balance(self, sentence_results: dict):
        """
        Balance emotions and calculate a first eindex
        :param sentence_results: the sentence results
        :return:
        """
        # Set an dict of emotions from sentence emotions
        emotions = {
            "happiness": sentence_results['happiness'],
            "surprise": sentence_results['surprise'],
            "calm": sentence_results['calm'],
            "fear": sentence_results['fear'],
            "sadness": sentence_results['sadness'],
            "anger": sentence_results['anger'],
            "disgust": sentence_results['disgust'],
        }
        # Get the strong emotions of the sentence
        strong_emotions = self.get_strong_emotions(emotions)
        if sentence_results['eindex'] is not None:
            if len(strong_emotions) != 0:
                if len(sentence_results['words']) != 0:
                    eindex_divided_by_nb_words = \
                        sentence_results['eindex'] / \
                        len(sentence_results['words'])
                else:
                    sentence_results['eindex'] = None
                    return
                # Limit the eindex (if eindex > 40 and eindex < -20)
                eindex = self.limit_eindex(eindex_divided_by_nb_words)
                # Rebalance emotions
                self.balance(sentence_results, eindex, strong_emotions)
            else:
                return

    def balance(self, sentence_results: dict, eindex: int,
                strong_emotions: dict):
        """
        Balancing eindex depending on emotions
        :param sentence_results: the sentence results
        :param eindex: the current eindex calculated
        :param strong_emotions: the strong emotions of the sentence
        :return:
        """
        int_balanced_eindex = eindex
        # Get the strongest emotions of the sentence
        strongest_emotions = self.get_strongest_emotions(
            strong_emotions)
        # Balance eindex with the strongest emotions
        int_strong_emotion_eindex = self.balance_with_strong_emotions(
            strongest_emotions)
        if int_strong_emotion_eindex is not None:
            int_balanced_eindex = int_strong_emotion_eindex
        # Get emotion from eindex
        eindex_emotion = self.get_emotion_from_eindex(
            int_balanced_eindex)
        # Balance eindex with all emotions
        int_balanced_emotions_eindex = self.balance_with_emotions(
            int_balanced_eindex,
            eindex_emotion,
            strong_emotions,
            strongest_emotions
        )
        if int_balanced_eindex is not None:
            int_balanced_eindex = int_balanced_emotions_eindex
        # Limit eindex value
        int_balanced_eindex = self.limit_eindex(int_balanced_eindex)
        # Set sentence eindex
        sentence_results['eindex'] = int_balanced_eindex

    @staticmethod
    def balance_with_emotions(int_balanced_eindex: int,
                              eindex_emotion: str,
                              strong_emotions: dict,
                              strongest_emotions: dict):
        """
        Balance eindex with emotions
        :param int_balanced_eindex: current balanced eindex
        :param eindex_emotion: emotion corresponding to calculated einde
        :param strong_emotions: strong emotions of the verbatim
        :param strongest_emotions: the strongest emotions of the verbati
        :return: a balanced eindex
        """
        # Iterate through strong emotions
        for emotion in strong_emotions:
            if len(strongest_emotions) == 0:
                return 18
            if emotion in strongest_emotions:
                continue
            # Balance eindex with emotions
            if eindex_emotion == 'happiness':
                if emotion == 'happiness':
                    int_balanced_eindex = 40
                if emotion == 'surprise':
                    int_balanced_eindex -= 2
                if emotion == 'calm':
                    int_balanced_eindex -= 4
                if emotion == 'fear':
                    int_balanced_eindex -= 6
                if emotion == 'sadness':
                    int_balanced_eindex -= 8
                if emotion == 'anger':
                    int_balanced_eindex -= 10
                if emotion == 'disgust':
                    int_balanced_eindex -= 12
                if int_balanced_eindex < 31:
                    int_balanced_eindex = 31
            if eindex_emotion == 'surprise':
                if emotion == 'surprise':
                    int_balanced_eindex = 30
                if emotion == 'happiness':
                    int_balanced_eindex += 2
                if emotion == 'calm':
                    int_balanced_eindex -= 2
                if emotion == 'fear':
                    int_balanced_eindex -= 4
                if emotion == 'sadness':
                    int_balanced_eindex -= 6
                if emotion == 'anger':
                    int_balanced_eindex -= 8
                if emotion == 'disgust':
                    int_balanced_eindex -= 10
                if int_balanced_eindex < 21:
                    int_balanced_eindex = 21
                if int_balanced_eindex > 30:
                    int_balanced_eindex = 30
            if eindex_emotion == 'calm':
                if emotion == 'calm':
                    int_balanced_eindex = 20
                if emotion == 'happiness':
                    int_balanced_eindex += 4
                if emotion == 'surprise':
                    int_balanced_eindex += 2
                if emotion == 'fear':
                    int_balanced_eindex -= 2
                if emotion == 'sadness':
                    int_balanced_eindex -= 4
                if emotion == 'anger':
                    int_balanced_eindex -= 6
                if emotion == 'disgust':
                    int_balanced_eindex -= 8
                if int_balanced_eindex < 11:
                    int_balanced_eindex = 11
                if int_balanced_eindex > 20:
                    int_balanced_eindex = 20
            if eindex_emotion == 'fear':
                if emotion == 'fear':
                    int_balanced_eindex = 10
                if emotion == 'happiness':
                    int_balanced_eindex += 6
                if emotion == 'surprise':
                    int_balanced_eindex += 4
                if emotion == 'calm':
                    int_balanced_eindex += 2
                if emotion == 'sadness':
                    int_balanced_eindex -= 2
                if emotion == 'anger':
                    int_balanced_eindex -= 4
                if emotion == 'disgust':
                    int_balanced_eindex -= 6
                if int_balanced_eindex < 6:
                    int_balanced_eindex = 6
                if int_balanced_eindex > 10:
                    int_balanced_eindex = 10
            if eindex_emotion == 'sadness':
                if emotion == 'sadness':
                    int_balanced_eindex = 5
                if emotion == 'happiness':
                    int_balanced_eindex += 8
                if emotion == 'surprise':
                    int_balanced_eindex += 6
                if emotion == 'calm':
                    int_balanced_eindex += 4
                if emotion == 'fear':
                    int_balanced_eindex += 2
                if emotion == 'anger':
                    int_balanced_eindex -= 2
                if emotion == 'disgust':
                    int_balanced_eindex -= 4
                if int_balanced_eindex < -4:
                    int_balanced_eindex = -4
                if int_balanced_eindex > 5:
                    int_balanced_eindex = 5
            if eindex_emotion == 'anger':
                if emotion == 'anger':
                    int_balanced_eindex = -14
                if emotion == 'happiness':
                    int_balanced_eindex += 10
                if emotion == 'surprise':
                    int_balanced_eindex += 8
                if emotion == 'calm':
                    int_balanced_eindex += 6
                if emotion == 'fear':
                    int_balanced_eindex += 4
                if emotion == 'sadness':
                    int_balanced_eindex += 2
                if emotion == 'disgust':
                    int_balanced_eindex -= 2
                if int_balanced_eindex < -14:
                    int_balanced_eindex = -14
                if int_balanced_eindex > -5:
                    int_balanced_eindex = -5
            if eindex_emotion == 'disgust':
                if emotion == 'disgust':
                    int_balanced_eindex = -20
                if emotion == 'happiness':
                    int_balanced_eindex += 12
                if emotion == 'surprise':
                    int_balanced_eindex += 10
                if emotion == 'calm':
                    int_balanced_eindex += 8
                if emotion == 'fear':
                    int_balanced_eindex += 6
                if emotion == 'sadness':
                    int_balanced_eindex += 4
                if emotion == 'disgust':
                    int_balanced_eindex += 2
                if int_balanced_eindex > -15:
                    int_balanced_eindex = -15
                if int_balanced_eindex < -20:
                    int_balanced_eindex = -20

        return int_balanced_eindex

    @staticmethod
    def final_balance_with_emotions(int_balanced_eindex: int,
                                    eindex_emotion: str,
                                    strong_emotions: dict,
                                    strongest_emotions: dict):
        """
        Final balanced eindex with emotions
        :param int_balanced_eindex: the current balanced
        calculated eindex
        :param eindex_emotion: the emotion corresponding to the
        calculated eindex
        :param strong_emotions: the strong emotions of the verbatim
        :param strongest_emotions: the strongest emotions
        of the verbatim
        :return: a finally balanced eindex
        """
        # Iterate through emotions
        for emotion, score in strong_emotions.items():
            if len(strongest_emotions) == 0:
                return 18
            if emotion in strongest_emotions and emotion not in \
                    ['happiness', 'sadness', 'calm']:
                continue
            threshold = 7

            strongest_emotion_value = list(
                strongest_emotions.values())[0]
            current_strong_emotion_value = int(score)

            delta = \
                int(strongest_emotion_value) - \
                current_strong_emotion_value

            # Balance eindex with emotions
            if eindex_emotion == 'happiness':
                if strongest_emotion_value > 80:
                    int_balanced_eindex = 40
                if 71 <= strongest_emotion_value <= 80:
                    int_balanced_eindex = 39
                if 61 <= strongest_emotion_value <= 70:
                    int_balanced_eindex = 38
                if 51 <= strongest_emotion_value <= 60:
                    int_balanced_eindex = 37
                if 41 <= strongest_emotion_value <= 50:
                    int_balanced_eindex = 36
                if 31 <= strongest_emotion_value <= 40:
                    int_balanced_eindex = 34
                if 21 <= strongest_emotion_value <= 30:
                    int_balanced_eindex = 33
                if 15 <= strongest_emotion_value <= 20:
                    int_balanced_eindex = 32
                if 7 <= strongest_emotion_value <= 14:
                    int_balanced_eindex = 31
                if 0 <= strongest_emotion_value <= 6:
                    int_balanced_eindex = 30

            if eindex_emotion == 'surprise':
                if emotion == 'surprise':
                    int_balanced_eindex = 30
                if emotion == 'happiness' and delta < threshold:
                    int_balanced_eindex += 5
                if emotion == 'happiness' and delta >= threshold:
                    int_balanced_eindex += 3
                if emotion == 'calm' and delta >= threshold:
                    int_balanced_eindex -= 1
                if emotion == 'calm' and delta > threshold:
                    int_balanced_eindex -= 1
                if emotion == 'fear' and delta >= threshold:
                    int_balanced_eindex -= 1
                if emotion == 'fear' and delta > threshold:
                    int_balanced_eindex -= 1
                if emotion == 'sadness' and delta >= threshold:
                    int_balanced_eindex -= 2
                if emotion == 'sadness' and delta > threshold:
                    int_balanced_eindex -= 2
                if emotion == 'anger' and delta >= threshold:
                    int_balanced_eindex -= 2
                if emotion == 'anger' and delta > threshold:
                    int_balanced_eindex -= 2
                if emotion == 'disgust' and delta >= threshold:
                    int_balanced_eindex -= 2
                if emotion == 'disgust' and delta > threshold:
                    int_balanced_eindex -= 2
                if int_balanced_eindex < 21:
                    int_balanced_eindex = 21
                if int_balanced_eindex > 30:
                    int_balanced_eindex = 30

            if eindex_emotion == 'calm':
                if strongest_emotion_value > 40:
                    int_balanced_eindex = 19
                if 36 <= strongest_emotion_value <= 40:
                    int_balanced_eindex = 18
                if 31 <= strongest_emotion_value <= 35:
                    int_balanced_eindex = 17
                if 26 <= strongest_emotion_value <= 30:
                    int_balanced_eindex = 16
                if 21 <= strongest_emotion_value <= 25:
                    int_balanced_eindex = 15
                if 16 <= strongest_emotion_value <= 20:
                    int_balanced_eindex = 14
                if 11 <= strongest_emotion_value <= 15:
                    int_balanced_eindex = 13
                if 6 <= strongest_emotion_value <= 10:
                    int_balanced_eindex = 12
                if 0 <= strongest_emotion_value <= 5:
                    int_balanced_eindex = 11

            if eindex_emotion == 'fear':
                if emotion == 'fear':
                    int_balanced_eindex = 30
                if emotion == 'happiness' and delta < threshold:
                    int_balanced_eindex += 10
                if emotion == 'happiness' and delta >= threshold:
                    int_balanced_eindex += 10
                if emotion == 'surprise' and delta < threshold:
                    int_balanced_eindex += 9
                if emotion == 'surprise' and delta >= threshold:
                    int_balanced_eindex += 9
                if emotion == 'calm' and delta < threshold:
                    int_balanced_eindex += 8
                if emotion == 'calm' and delta >= threshold:
                    int_balanced_eindex += 8
                if emotion == 'sadness' and delta >= threshold:
                    int_balanced_eindex -= 7
                if emotion == 'sadness' and delta < threshold:
                    int_balanced_eindex -= 6
                if emotion == 'anger' and delta >= threshold:
                    int_balanced_eindex -= 6
                if emotion == 'anger' and delta < threshold:
                    int_balanced_eindex -= 6
                if emotion == 'disgust' and delta >= threshold:
                    int_balanced_eindex -= 6
                if emotion == 'disgust' and delta < threshold:
                    int_balanced_eindex -= 6
                if int_balanced_eindex < 6:
                    int_balanced_eindex = 6
                if int_balanced_eindex > 10:
                    int_balanced_eindex = 10

            if eindex_emotion == 'sadness':
                if strongest_emotion_value > 80:
                    int_balanced_eindex = -4
                if 71 <= strongest_emotion_value <= 80:
                    int_balanced_eindex = -3
                if 61 <= strongest_emotion_value <= 70:
                    int_balanced_eindex = -2
                if 51 <= strongest_emotion_value <= 60:
                    int_balanced_eindex = -1
                if 41 <= strongest_emotion_value <= 50:
                    int_balanced_eindex = 0
                if 31 <= strongest_emotion_value <= 40:
                    int_balanced_eindex = 1
                if 21 <= strongest_emotion_value <= 30:
                    int_balanced_eindex = 2
                if 11 <= strongest_emotion_value <= 20:
                    int_balanced_eindex = 3
                if 0 <= strongest_emotion_value <= 10:
                    int_balanced_eindex = 4

            if eindex_emotion == 'anger':
                if emotion == 'anger':
                    int_balanced_eindex = -14
                if emotion == 'happiness' and delta < threshold:
                    int_balanced_eindex += 7
                if emotion == 'happiness' and delta >= threshold:
                    int_balanced_eindex += 6
                if emotion == 'surprise' and delta < threshold:
                    int_balanced_eindex += 5
                if emotion == 'surprise' and delta >= threshold:
                    int_balanced_eindex += 4
                if emotion == 'calm' and delta < threshold:
                    int_balanced_eindex += 4
                if emotion == 'calm' and delta >= threshold:
                    int_balanced_eindex += 3
                if emotion == 'fear' and delta < threshold:
                    int_balanced_eindex += 3
                if emotion == 'fear' and delta >= threshold:
                    int_balanced_eindex += 2
                if emotion == 'sadness' and delta < threshold:
                    int_balanced_eindex += 2
                if emotion == 'sadness' and delta >= threshold:
                    int_balanced_eindex += 2
                if emotion == 'disgust' and delta >= threshold:
                    int_balanced_eindex -= -1
                if emotion == 'disgust' and delta < threshold:
                    int_balanced_eindex -= -2
                    # TODO CHECK SI C'EST PAS -2 ICI PLUTOT
                if int_balanced_eindex < -14:
                    int_balanced_eindex = -14
                if int_balanced_eindex > -5:
                    int_balanced_eindex = -5

            if eindex_emotion == 'disgust':
                if emotion == 'disgust':
                    int_balanced_eindex = -20
                if emotion == 'happiness' and delta < threshold:
                    int_balanced_eindex += 5
                if emotion == 'happiness' and delta >= threshold:
                    int_balanced_eindex += 5
                if emotion == 'surprise' and delta < threshold:
                    int_balanced_eindex += 4
                if emotion == 'surprise' and delta >= threshold:
                    int_balanced_eindex += 4
                if emotion == 'calm' and delta < threshold:
                    int_balanced_eindex += 3
                if emotion == 'calm' and delta >= threshold:
                    int_balanced_eindex += 3
                if emotion == 'fear' and delta < threshold:
                    int_balanced_eindex += 3
                if emotion == 'fear' and delta >= threshold:
                    int_balanced_eindex += 2
                if emotion == 'sadness' and delta < threshold:
                    int_balanced_eindex += 2
                if emotion == 'sadness' and delta >= threshold:
                    int_balanced_eindex += 2
                if emotion == 'disgust' and delta < threshold:
                    int_balanced_eindex += 1
                if emotion == 'disgust' and delta >= threshold:
                    int_balanced_eindex += 1
                if int_balanced_eindex > -15:
                    int_balanced_eindex = -15
                if int_balanced_eindex < -20:
                    int_balanced_eindex = -20
        return int_balanced_eindex

    @staticmethod
    def balance_with_strong_emotions(strongest_emotions: dict):
        """
        Basic eindex balancing with emotions
        :param strongest_emotions: the strongest emotions
        :return: an eindex
        """
        int_balanced_eindex = None
        # Choose an eindex depending on the strongest emotion
        for emotion in strongest_emotions:
            if len(strongest_emotions) == 1:
                if emotion == 'happiness':
                    int_balanced_eindex = 40
                if emotion == 'surprise':
                    int_balanced_eindex = 23
                if emotion == 'calm':
                    int_balanced_eindex = 12
                if emotion == 'fear':
                    int_balanced_eindex = 7
                if emotion == 'sadness':
                    int_balanced_eindex = 0
                if emotion == 'anger':
                    int_balanced_eindex = -12
                if emotion == 'disgust':
                    int_balanced_eindex = -20
        return int_balanced_eindex

    @staticmethod
    def get_eindex_from_emotion(emotion: str):
        """
        Calculate an eindex depending on the emotion given
        :param emotion: emotion we want the index of
        :return: an eindex
        """
        eindex = 0
        # Choose an eindex depending on the emotion given
        if emotion == 'happiness':
            eindex = 40
        if emotion == 'surprise':
            eindex = 23
        if emotion == 'calm':
            eindex = 12
        if emotion == 'fear':
            eindex = 7
        if emotion == 'sadness':
            eindex = 0
        if emotion == 'anger':
            eindex = -12
        if emotion == 'disgust':
            eindex = -20
        return eindex

    @staticmethod
    def get_emotion_from_eindex(eindex: int):
        """
        Determine the emotion depending on the eindex
        :param eindex: the eindex we want the emotion of
        :return: an emotion
        """
        emotion = ''
        # Choose an emotion depending on the eindex
        if float(eindex) is not None:
            if 31 <= eindex <= 40:
                emotion = 'happiness'
            if 21 <= eindex <= 30:
                emotion = 'surprise'
            if 11 <= eindex <= 20:
                emotion = 'calm'
            if 6 <= eindex <= 10:
                emotion = 'fear'
            if -5 <= eindex <= 5:
                emotion = 'sadness'
            if -14 <= eindex <= -6:
                emotion = 'anger'
            if -20 <= eindex <= -15:
                emotion = 'disgust'
        return emotion

    def get_final_eindex(self, global_results: dict):
        """
        Calculating final eindex and emotional intensity
        :param global_results: verbatim global results
        :return:
        """
        emotions = dict()
        for emotion in global_results['strongest_emotions']:
            if emotion is None:
                continue
            if emotion[0] not in emotions:
                emotions[emotion[0]] = 0
            emotions[emotion[0]] += int(emotion[1])
        # Apply coeff to increase an emotion impact
        for emotion, score in emotions.items():
            if emotion in ['calm']:
                score *= 1
            if emotion in ['happiness', 'surprise', 'sadness', 'fear']:
                score *= 2
            if emotion in ['anger', 'disgust']:
                score *= 3
        # TODO: return score as main emotional intensity
        # (either by socre or the value from get_max_value)
        # Assign main_emotional_intensity in global results
        global_results["main_emotional_intensity"] = score
        # If there are some emotions
        if len(emotions) != 0:
            if self.has_emotional_contradiction(emotions) is False:
                strongest_emotions = self.get_max_values(emotions)
                # Get an eindex depending on the strongest emotion
                if len(strongest_emotions) == 1:
                    final_eindex = self.get_eindex_from_emotion(
                        list(strongest_emotions.keys())[0])
                else:
                    final_eindex = self.get_eindex_from_emotion(
                        self.get_most_emotion(strongest_emotions,
                                              'negative'))
                # Make a last calculation on the eindex
                final_balanced_eindex = \
                    self.final_balance_with_emotions(
                        final_eindex,
                        self.get_emotion_from_eindex(final_eindex),
                        emotions,
                        strongest_emotions
                    )
                # Assign eindex to global results
                global_results['eindex'] = final_balanced_eindex
        if self.object_has_one_emotion_score_superior_to(global_results,
                                                         0) is False:
            global_results['eindex'] = 0

    def has_emotional_contradiction(self, emotions: dict):
        """
        Check if the verbatim has an emotional contradiction
        :param emotions: emotions to check
        :return: True if has emotional contradiction, False if not
        """
        emotions_by_sentences = list()
        count = 0
        positive_total_score = 0
        negative_total_score = 0
        for emotion in emotions:
            if emotion in ['happiness', 'surprise', 'calm']:
                emotions_by_sentences.append('positive')
                positive_total_score += emotions[emotion]
            if emotion in ['fear', 'anger', 'sadness', 'disgust']:
                emotions_by_sentences.append('negative')
                negative_total_score += emotions[emotion]
            count += 1
        emotions = dict(OrderedDict(sorted(emotions.items(),
                                           key = lambda kv: kv[1],
                                           reverse = True)))
        if len(list(set(emotions))) > 1:
            most_positive_emotion = self.get_most_emotion(emotions,
                                                          'positive')
            most_negative_emotion = self.get_most_emotion(emotions,
                                                          'negative')
            if positive_total_score > 1.1 * negative_total_score:
                final_eindex = self.get_eindex_from_emotion(
                    most_positive_emotion)
            else:
                final_eindex = self.get_eindex_from_emotion(
                    most_negative_emotion)
            final_balanced_eindex = self.final_balance_with_emotions(
                final_eindex,
                self.get_emotion_from_eindex(final_eindex),
                emotions,
                self.get_max_values(emotions)
            )
            self.global_results['eindex'] = final_balanced_eindex
            self.global_results['emotional_contradiction'] = True
            return True
        return False

    @staticmethod
    def get_max_values(emotions: dict):
        """
        Create a new dict sorted by highest emotional values
        :param emotions: the emotions to sort
        :return: a newly sorted dict
        """
        new_dict = dict()
        # Sort the emotions to have the "stronger" emotions on top of
        #  other "smaller" emotions
        for emotion, value in emotions.items():
            if len(new_dict) == 0:
                new_dict[emotion] = int(value)
                continue
            insert = False
            replace = False
            for emotion_, value_ in new_dict.items():
                if value == value_ and emotion not in new_dict:
                    insert = True
                elif value > value_ and emotion not in new_dict:
                    replace = True
            if insert:
                new_dict[emotion] = int(value)
            if replace:
                new_dict = dict()
                new_dict[emotion] = int(value)
        return new_dict

    @staticmethod
    def get_most_emotion(emotions: dict, emotion_type: str):
        """
        Get the most negative or positive emotion
        of an emotional dictionary
        :param emotions: emotions as a dict
        :param emotion_type: the type of emotions (negative or positive)
        :return: The most negative or positive emotion
        """
        # Initilize a dict to choose emotions
        emotions_by_values = {
            "happiness": 1,
            "surprise": 2,
            "calm": 3,
            "fear": 4,
            "sadness": 5,
            "anger": 6,
            "disgust": 7,
        }
        emotions_dct = dict()
        for emotion in emotions:
            emotions_dct[emotion] = emotions_by_values[emotion]
        # Return the strongest negative emotion
        if emotion_type == 'negative':
            emotions_dct = max(emotions_dct,
                               key = operator.itemgetter(1))
        # Return the strongest positive emotion
        if emotion_type == 'positive':
            emotions_dct = min(emotions_dct,
                               key = operator.itemgetter(1))
        return emotions_dct

    @staticmethod
    def limit_eindex(eindex: int):
        """
        Set the eindex limits
        :param eindex: current eindex
        :return: a limited-in-value eindex
        """
        # Set eindex maximun value
        if eindex > 40:
            return 40
        # Set eindex minimum value
        if eindex < -20:
            return -20
        return eindex

    @staticmethod
    def get_strong_emotions(emotions: dict):
        """
        Get the strong emotions of a sentence or verbatim
        :param emotions: the emotions to check
        :return: a dict with the strong emotions found
        """
        strong_emotions = dict()
        # For each emotion, get the emotion if it's value is superior
        #  to 5
        for emotion in emotions:
            if emotions[emotion] >= 5:
                strong_emotions['{}'.format(emotion)] = \
                    emotions[emotion]
        return strong_emotions

    @staticmethod
    def get_strongest_emotions(strong_emotions: dict):
        """
        Find strongest emotions in a result dictionary
        :param strong_emotions: the strong emotions
        of a sentence or verbatim
        :return: a dict with the strongest emotions
        """
        strongest_emotions = dict()
        # Iterate through emotions and get the one that has the
        # highest value
        for emotion, score in strong_emotions.items():
            if len(strongest_emotions) == 0:
                strongest_emotions[emotion] = score
                continue
            insert = False
            replace = False
            for str_emotion, str_score in strongest_emotions.items():
                if score == str_score and emotion not in \
                        strongest_emotions:
                    insert = True
                elif score > str_score and emotion not in \
                        strongest_emotions:
                    replace = True
            if insert:
                strongest_emotions[emotion] = int(score)
            if replace:
                strongest_emotions = dict()
                strongest_emotions[emotion] = int(score)
        if len(strongest_emotions) > 1:
            strongest_emotions = dict()
        # print('strong: ', strong_emotions)
        # print('strongest: ', strongest_emotions)
        return strongest_emotions

    def emotions_ponderation_then_reliability(self, results: dict,
                                              sentence_info: dict):
        """
        Ponderate emotions and calculate reliability rate
        :param results: the results of a sentence or verbatim
        :param sentence_info: some information about a sentence
        :return:
        """
        positives = {
            "happiness": results['happiness'],
            "surprise": results['surprise'],
            "calm": results['calm']
        }
        negatives = {
            "fear": results['fear'],
            "sadness": results['sadness'],
            "anger": results['anger'],
            "disgust": results['disgust']
        }
        calm_score = results['calm']
        positive_emotions_sum_score = self.get_emotions_sum_score(
            positives, 'positive')
        negative_emotions_sum_score = self.get_emotions_sum_score(
            negatives, 'negative')
        # If sentence results structure is OK, check for rules that
        # should be applied on the sentence
        if len(sentence_info) != 0:
            results['positives_emotions_sum'] = positives
            results['negatives_emotions_sum'] = negatives
            highest_positive_emotion = max(positives.items(),
                                           key =
                                           operator.itemgetter(1))[0]
            highest_negative_emotion = max(negatives.items(),
                                           key =
                                           operator.itemgetter(1))[0]

            # Emotional Delta
            edelta = abs(positive_emotions_sum_score - \
                         negative_emotions_sum_score)
            # Check if positive emotions are superior to calm and
            # negative emotions
            if calm_score < edelta \
                    and positive_emotions_sum_score > \
                    negative_emotions_sum_score:
                results['applied_rules'].append({
                    "type": "emotions_ponderation_then_reliability",
                    "name": "rule 1"
                })
                max_emotion = [
                    highest_positive_emotion,
                    int(positive_emotions_sum_score -
                        negative_emotions_sum_score)
                ]
            # Check if calm inferior to positive and negative emotions
            elif calm_score < edelta and \
                    positive_emotions_sum_score < \
                    negative_emotions_sum_score:
                results['applied_rules'].append({
                    "type": "emotions_ponderation_then_reliability",
                    "name": "rule 2"
                })
                max_emotion = [
                    highest_negative_emotion,
                    int(negative_emotions_sum_score -
                        positive_emotions_sum_score)
                ]
            else:
                results['applied_rules'].append({
                    "type": "emotions_ponderation_then_reliability",
                    "name": "rule 3"
                })
                max_emotion = [
                    'calm',
                    int(calm_score)
                ]
            # TODO: A TESTER |
            # TODO:          v
            # self.apply_punctuaction_coeff(
            #     sentence_results, max_emotion)
            if max_emotion[1] <= 0 and calm_score <= 0:
                results['strongest_emotions'] = ['calm', 0]
            else:
                results['strongest_emotions'] = max_emotion
        # Set a null eindex if some conditions are reunited
        if self.apply_null_eindex(results, positive_emotions_sum_score,
                                  negative_emotions_sum_score,
                                  calm_score):
            print("main 1: apply null eindex")
            results['applied_rules'].append({
                    "type": "emotions_ponderation_then_reliability",
                    "name": "rule 4"
                })
            results['eindex'] = None
        # Calculate verbatim's reliability rate
        self.calculate_reliability_rate(
            results,
            calm_score,
            positive_emotions_sum_score,
            negative_emotions_sum_score
        )

    # # # # # # # # # # # # # # # # # # # # #
    #                                       #
    #          MARKS CALCULATIONS           #
    #                                       #
    # # # # # # # # # # # # # # # # # # # # #

    @staticmethod
    def compute_confidence_rate(global_results: dict):
        """
        Calculate the confidence rate of a verbatim
        :param global_results: the global results of a verbatim
        :return: a calculated confidence rate
        """
        confidence_rate = 100
        # Lower confidence rate if there is an emotional contradiction
        if global_results['emotional_contradiction']:
            confidence_rate -= 30
        # Calculate confidence rate depending on performace rate
        performance = global_results['performance']
        if 90 <= performance <= 99:
            confidence_rate -= 5
        if 80 <= performance <= 89:
            confidence_rate -= 10
        if 70 <= performance <= 79:
            confidence_rate -= 15
        if 60 <= performance <= 69:
            confidence_rate -= 20
        if 50 <= performance <= 59:
            confidence_rate -= 25
        if 40 <= performance <= 49:
            confidence_rate -= 30
        if 30 <= performance <= 39:
            confidence_rate -= 35
        if 20 <= performance <= 29:
            confidence_rate -= 40
        if 10 <= performance <= 19:
            confidence_rate -= 45
        if 0 <= performance <= 9:
            confidence_rate -= 50
        return confidence_rate

    @staticmethod
    def compute_emotional_intensity(global_results: dict):
        """
        Calculate the emotional intensity of the verbatim
        :param global_results: the global results
        :return: the global results with the
        emotional intensity calculated
        """
        def number_tweets(nb_char: int):
            """
            Return the number of tweets
            :param nb_words: integer, nomber of words
            :return: integer, number of tweets
            """
            return int(nb_char/144)+1
        # Get the number of tweets
        nb_tweets = number_tweets(global_results['char_count'])            
        # Calculate emotional intensity if sentence contains words
        if global_results['document_word_count'] > 0:
            emotion_sum = 0
            emotion_list = ['happiness', 'surprise', 'fear',
                            'sadness', 'anger', 'disgust']
            for key, value in global_results.items():
                if key not in emotion_list:
                    continue
                else:
                    emotion_sum += value
            abs_emotional_value = round(
                float(emotion_sum)/float(nb_tweets), 1)
            # Emotional intensity
            emotional_intensity = int(abs_emotional_value/130*100)
            # Set emotional intensity to 100 if emotional intensity
            # superior to 100
            if emotional_intensity > 100:
                global_results['emotional_intensity'] = 100
            else:
                global_results['emotional_intensity'] = \
                    emotional_intensity
        return global_results

    @staticmethod
    def get_speech_size_mark(verbatim: str):
        """
        Calculate the speech size mark
        :param verbatim: the verbatim
        :return: the speech size mark
        """
        length = len(verbatim)
        # Calculate speech size depending on verbatim lenght
        if length >= 300:
            mark = 1
        else:
            mark = length * 0.1/30
        return round(mark, 2)

    def get_involvement_mark(self, verbatim: str, language: str,
                             global_results: dict):
        """
        Calculate the involvment mark depending on several rules
        :param verbatim: the verbatim
        :param language: the language of the verbatim
        :param global_results: the verbatim global results
        :return: the involvment mark
        """
        mark = 0
        # Check if verbatim contains first person words
        if self.has_first_person(verbatim, language):
            mark += 1
        # Check if verbaitm contains emails
        if self.has_email(verbatim):
            mark += 0.9
        # Check if there are possessive_form in the verbatim
        for possessive_form in global_results['possessive_forms']:
            if possessive_form['personnal'] is True:
                mark += 0.75
            if possessive_form['personnal'] is False:
                mark += 0.50
        # Set mark depending on number of superlative words in verbatim
        if len(global_results['superlative_words']) == 1:
            mark += 0.3
        if len(global_results['superlative_words']) > 1:
            mark += 0.6
        if mark > 1:
            mark = 1
        return mark * 0.4

    @staticmethod
    def get_time_orientation_info(global_results: dict):
        """
        Calculate the time orientation mark
        :param global_results: the verbatim global results
        :return: the time orientation mark and the tenses of the verbati
        """
        mark = 0
        tenses = list()
        # Set a mark depending on the different types of tenses
        # present in the verbatim
        if 'future' in global_results['tenses']:
            mark += 1
            tenses.append('future')
        if 'present' in global_results['tenses']:
            mark += 0.75
            tenses.append('presennt')
        if 'imperative / conditional' in global_results['tenses']:
            mark += 0.5
            tenses.append('imperative / conditional')
        if 'infinite' in global_results['tenses']:
            mark += 0.05
            tenses.append('infinite')
        if 'past' in global_results['tenses'] or \
                'simplepast' in global_results['tenses']:
            mark += 0
            tenses.append('past')
        if mark > 1:
            mark = 1
        tenses = list(set(tenses))
        return {
            "mark": mark * 0.2,
            "tenses": tenses
        }

    def compute_speech_commitment(self):
        """
        Calculate the commitment by concatenating some previously
        calculated marks
        :return: the commitment as a dict
        """
        speech_size_mark = self.get_speech_size_mark(self.text)
        involvement_mark = self.get_involvement_mark(
            self.text.lower(),
            self.lang,
            self.global_results)
        orientation_info = self.get_time_orientation_info(
            self.global_results)
        # Calculate verbatim's commitment
        commitment = (speech_size_mark + involvement_mark + round(
            orientation_info['mark'], 2))
        global_res = self.global_results
        # Calculate emotional intensity of the verbatim
        emotional_intensity = global_res['happiness'] + \
            global_res['surprise'] + \
            global_res['fear'] + \
            global_res['sadness'] + \
            global_res['anger'] + \
            global_res['disgust']
        # Calculate emotional intensity per character
        emotional_intensity_p_char = round(float(emotional_intensity /
                                                 len(self.text)), 2)
        boost = 0
        if emotional_intensity_p_char >= 0.8:
            boost = round((emotional_intensity_p_char - 0.2) * 1.2, 2)
            if boost < 1:
                boost = 1
            if commitment == 0:
                commitment = round(0.1 * boost, 2)
            else:
                commitment = round(commitment * boost, 2)
        if commitment > 1:
            commitment = 1
        # concatenate all previously calculated mark and build a
        # detailled dictionary
        self.global_results['commitment'] = {
            "global_engagement": commitment,
            "details": {
                "speech_size": speech_size_mark,
                "personal_involvement": involvement_mark,
                "time_orientation": orientation_info['tenses'],
                "emotional_boost": {
                    "boost": self.choose_boost(boost),
                    "value": boost
                }
            }
        }

    @staticmethod
    def choose_boost(boost: float):
        """
        Choose if a boost exists or not
        :param boost: current calculated boost
        :return: True if it does, False if not
        """
        # Choose if the boost is supposed to be applied or not
        if boost >= 0.8:
            return True
        return False

    @staticmethod
    def calculate_reliability_rate(results: dict, calm_score: int,
                                   positive_emotions_sum_score: int,
                                   negative_emotions_sum_score: int):
        """
        Calculate the reliability rate depending on couple rules
        :param results: the verbatim global results
        :param calm_score: the verbatim calm score
        :param positive_emotions_sum_score: the sum of
        the verbatim positive emotions
        :param negative_emotions_sum_score: the sum of
        the verbatim negative emotions
        :return: the calculated reliability rate
        """
        reliability_rate = 98
        reliability_rate = round(((reliability_rate
                                   * results['performance']) / 100))
        # Apply rules on reliabilty rate
        if (positive_emotions_sum_score + calm_score
            > negative_emotions_sum_score) \
                and (positive_emotions_sum_score
                     < negative_emotions_sum_score):
            results['applied_rules'].append({
                "type": "reliability_rate",
                "name": "rule 1 [calm make the difference]"
            })
            reliability_rate = reliability_rate / 3
        if calm_score > (positive_emotions_sum_score
                         + negative_emotions_sum_score):
            results['applied_rules'].append({
                "type": "reliability_rate",
                "name": "rule 2 [calm > positive + negative]"
            })
            reliability_rate = reliability_rate / 3
        # Apply questionning rule
        if results['questioning']:
            results['applied_rules'].append({
                "type": "reliability_rate",
                "name": "rule 3 [has question]"
            })
            reliability_rate = reliability_rate / 2
        # Apply document lenght rule
        if results['document_word_count'] <= 3:
            results['applied_rules'].append({
                "type": "reliability_rate",
                "name": "rule 4 [ less then three words]"
            })
            reliability_rate = reliability_rate * 0.8
        # Apply negative document rule
        if results['negative']:
            results['applied_rules'].append({
                "type": "reliability_rate",
                "name": "rule 5 [is negative]"
            })
            reliability_rate = reliability_rate / 2
        results['reliability_rate'] = round(reliability_rate)

    # # # # # # # # # # # # # # # # # # # # #
    #                                       #
    #         MISCELLANEOUS METHODS         #
    #                                       #
    # # # # # # # # # # # # # # # # # # # # #

    def has_emotions(self, found_word: dict):
        """
        Check if a word is emotional or not
        :param found_word: the detailled word
        :return: True if emotional, False if not
        """
        # Return if an object has some emotions
        return self.object_has_one_emotion_score_superior_to(
            sentence_results = found_word, minimal_score = 0,
            is_serie = True)

    @staticmethod
    def has_first_person(verbatim: str, language: str):
        """
        Check if the verbatim has first persons words
        :param verbatim: the verbatim
        :param language: the language of the verbatim
        :return: True if there are first persons words, False if nnot
        """
        has_first_person = False
        first_persons = list()
        if language == 'fr':
            first_persons = [" je ", " j'", " j ", " moi ", " perso ",
                             " personnellement ", " personellement ",
                             " personnellmt ", " m'", "nous", "notre",
                             "nos", "notres"]
        if language == 'en':
            first_persons = [" i ", " i'", " me ", " personally ",
                             " personnally", "our", "we","ours",'my',
                             'mine']
        # Check if the first person words are in the verbatim
        for fp in first_persons:
            if fp in verbatim:
                has_first_person = True
        return has_first_person

    def has_email(self, verbatim: str):
        """
        Check if a verbatim has some email adresses in it
        :param verbatim: the verbatim
        :return: True if has email, False if not
        """
        has_email = False
        emails = self.get_emails(verbatim)
        # Check in the verbatim if there are some emails in it
        for email in emails:
            if '.' in email and '@' in email:
                has_email = True
        return has_email

    @staticmethod
    def get_emails(verbatim: str):
        """
        Get all email adresses in the verbatim
        :param verbatim: the verbatim
        :return: list of email adresses
        """
        emails = list()
        # Get all emails in a verbatim and return the emails as a
        # list of string
        for word in verbatim.split(' '):
            if '@' in word:
                emails.append(word)
        return emails

    def apply_null_eindex(self, results: dict,
                          positive_emotions_sum_score: int,
                          negative_emotions_sum_score: int,
                          calm_score: int):
        """
        Decides if null is supposed to be applied to eindex
        :param results: the sentence or verbatim results
        :param positive_emotions_sum_score: sum of positive emotions
        :param negative_emotions_sum_score: sum of negative emotions
        :param calm_score: verbatim or sentence calm score
        :return: True or False
        """
        minimal_score = 5
        # Set minimal score temporary for the first condition because
        # we have a lot of null on RATP data (cf. Issue
        # https://gitlab.com/qemotion_team/
        # core/processing_components/issues/92)
        minimal_score_tmp = 3
        positive_minus_negative = \
            positive_emotions_sum_score - negative_emotions_sum_score
        negative_minus_negative = \
            negative_emotions_sum_score - positive_emotions_sum_score
        # Choose if the verbatim is supposed to have an eindex set at
        #  NULL
        return not self.object_has_one_emotion_score_superior_to(
            results, minimal_score_tmp) or (
            self.emotions_less_than_minimal_score(
                positive_minus_negative,
                negative_minus_negative,
                calm_score, minimal_score) and
            self.calm_less_than_emotions_sum(
                calm_score,
                positive_emotions_sum_score,
                negative_emotions_sum_score)
        )

    @staticmethod
    def emotions_less_than_minimal_score(pos_minus_neg: int,
                                         neg_minus_pos: int,
                                         calm_score: int,
                                         minimal_score: int):
        """
        Check if some emotions have a score inferior
        to the minimal score
        :param pos_minus_neg: positive - negative score
        :param neg_minus_pos: negative - positive score
        :param calm_score: the calm score
        :param minimal_score: the minimal score
        :return: True or False
        """
        result = pos_minus_neg <= minimal_score and \
            neg_minus_pos <= minimal_score and \
            calm_score <= minimal_score
        return result

    @staticmethod
    def calm_less_than_emotions_sum(calm_score: int,
                                    positive_emotions_sum_score: int,
                                    negative_emotions_sum_score: int):
        """
        Check if calm has an inferior score to positive
        and negative score
        :param calm_score: the calm score
        :param positive_emotions_sum_score: sum of
        positive emotions scores
        :param negative_emotions_sum_score: sum of
        negative emotions scores
        :return: True or False
        """
        result = calm_score < negative_emotions_sum_score \
            and calm_score < positive_emotions_sum_score
        return result

    @staticmethod
    def object_has_one_emotion_score_superior_to(sentence_results,
                                                 minimal_score: int,
                                                 is_serie=False):
        """
        Check if some results have some emotions
        superior to a certain score
        :param sentence_results: the sentence results
        :param minimal_score: the minimal score
        :param is_serie: if the sentence results are a Serie
        :return: True or False
        """
        emotions = [
            'happiness',
            'surprise',
            'calm',
            'fear',
            'sadness',
            'anger',
            'disgust'
        ]
        if is_serie is True:
            for emotion in emotions:
                if sentence_results[emotion] > minimal_score:
                    return True
        else:
            for emotion in emotions:
                if sentence_results[emotion] > minimal_score:
                    return True
        return False

    @staticmethod
    def get_emotions_sum_score(scores: dict, emotion: str):
        """
        Get the score of a type of emotion (negative or positive)
        :param scores: the emotions
        :param emotion: the type of emotion (negative or positive)
        :return: the score of an emotion type
        """
        if emotion == 'positive':
            return int(scores['happiness'] + scores['surprise'])
        if emotion == 'negative':
            return int(scores['fear'] + scores['sadness']
                       + scores['anger'] + scores['disgust'])

    # # # # # # # # # # # # # # # # # # # # #
    #                                       #
    #            GLOBAL RESULTS             #
    #                                       #
    # # # # # # # # # # # # # # # # # # # # #

    def set_global_results(self):
        """
        Preparing the global results of a verbatim
        :return:
        """
        global_results = self.global_results
        # Set if verbatim has a question in it
        if '?' in self.text:
            global_results['questioning'] = True
        # Set if the verbatim has an exclamation in it
        if '!' in self.text:
            global_results['exclamation'] = True
        # For each sentences, add results to verbatim results
        for sentence in self.sentences:
            index = sentence[1]
            sentence_results = \
                self.global_results['sentences_results'][index]  # ['{
            # }'.format(index)]
            self.get_global_results(global_results, sentence_results)
        # Get number of documents in the verbatim
        document_word_count = global_results['document_word_count']
        if document_word_count == 0:
            document_word_count = 1
        sentence_count = len(global_results['sentences'])
        if sentence_count == 0:
            sentence_count = 1
        total_emotional_words_count = len(global_results['words'])
        # Assign some values to global_results
        if global_results['emotional_word_count'] > \
                global_results['document_word_count']:
            global_results['emotional_word_count'] = \
                global_results['document_word_count']
        global_results['performance'] = round((float(
            global_results['emotional_word_count']) /
                                               document_word_count)
                                              * 100)
        # TODO IMPLEMENTER  MUTLIPLICATEURS DE PREMIERE / DERNIERE PHRSE
        if global_results['eindex'] is not None:
            eindex = float(global_results['eindex']) / sentence_count
            if float(eindex) is None:
                global_results['eindex'] = float(
                    global_results['eindex'])
            else:
                global_results['eindex'] = self.limit_eindex(
                    round(eindex))

        if total_emotional_words_count != 0:
            global_results['valence'] = round(float(
                global_results['valence']) /
                float(total_emotional_words_count), 2)
            global_results['arousal'] = round(float(
                global_results['arousal']) /
                float(total_emotional_words_count), 2)
            global_results['dominance'] = round(float(
                global_results['dominance']) /
                float(total_emotional_words_count), 2)
        else:
            global_results['valence'] = 0.00
            global_results['arousal'] = 0.00
            global_results['dominance'] = 0.00
        # Calculate one last time the eindex
        self.get_final_eindex(global_results)
        # Set the confidence rate of the verbatim
        global_results['confidence_rate'] = \
            self.compute_confidence_rate(global_results)
        # Parse some lists in order not to have duplicates
        global_results['unknown_words'] = list(set(
            global_results['unknown_words']))
        global_results['extra_words'] = list(set(
            global_results['extra_words']))
        global_results['corrected_words'] = list(set(
            global_results['corrected_words']))
        # Compute verbatim's speech engagement
        self.compute_speech_commitment()
        # Compute verbatim's emotional intensity
        global_results = self.compute_emotional_intensity(
            global_results)
        # Final verbatim calculation, ponderate emotions and apply
        # reliability rate
        self.emotions_ponderation_then_reliability(global_results, {})
        # Set main emotion
        self.set_main_emotion()

    def set_main_emotion(self):
        """
        Set verbatim_strongest_emotion by providing the main emotion
        and the E-index.
        :param:
        :return:
        """
        strongests = self.global_results['strongest_emotions']
        # Init local results dictionary
        emotions = {
            "happiness": 0, "surprise": 0,
            "calm": 0, "fear": 0, "sadness": 0,
            "anger": 0, "disgust": 0,
        }
        # Get score for each emotion
        for emotion in strongests:
            emotions[str(emotion[0])] += int(emotion[1])
        # Get the main emotion
        main_emotion = max(
            emotions.items(), key = operator.itemgetter(1)
        )[0]
        # set the main emotion in global results
        self.global_results["verbatim_strongest_emotion"] = main_emotion
        # TODO: to be reviewed
        self.global_results["eindex"] = self.rectify_eindex(
            eindex = self.global_results["eindex"],
            emotion = self.global_results["verbatim_strongest_emotion"]
        )
        
    @staticmethod
    def get_global_results(global_results: dict,
                           sentence_results: dict):
        """
        Concatenate all sentences results to make the global resutls
        :param global_results: the current global results
        :param sentence_results: the sentence results
        :return:
        """
        # CONTATENATE ALL SENTENCES RESULTS TO MAKE THE GLOBAL RESULTS
        global_results['sentences'].append(
            sentence_results['sentence_text'])
        global_results['document_word_count'] += \
            sentence_results['document_word_count']
        global_results['char_count'] += \
            sentence_results['char_count']
        global_results['emotional_word_count'] += \
            sentence_results['emotional_word_count']

        if global_results['eindex'] is not None and \
                sentence_results['eindex'] is not None:
            global_results['eindex'] += int(sentence_results['eindex'])

        global_results['valence'] += float(sentence_results['valence'])
        global_results['arousal'] += float(sentence_results['arousal'])
        global_results['dominance'] += float(sentence_results[
            'dominance'])

        global_results['happiness'] += float(sentence_results[
            'happiness'])
        global_results['surprise'] += float(sentence_results[
                                                'surprise'])
        global_results['calm'] += float(sentence_results['calm'])
        global_results['fear'] += float(sentence_results['fear'])
        global_results['sadness'] += float(sentence_results['sadness'])
        global_results['anger'] += float(sentence_results['anger'])
        global_results['disgust'] += float(sentence_results['disgust'])

        global_results['positives_emotions_sum'].append(
            sentence_results['positives_emotions_sum'])
        global_results['negatives_emotions_sum'].append(
            sentence_results['negatives_emotions_sum'])
        global_results['strongest_emotions'].append(
            sentence_results['strongest_emotions'])

        global_results['words'] = \
            global_results['words'] \
            + sentence_results['words']
        global_results['emotional_words'] = \
            global_results['emotional_words'] \
            + sentence_results['emotional_words']
        global_results['compound_words'] = \
            global_results['compound_words'] \
            + sentence_results['compound_words']
        global_results['skipped_words'] = \
            global_results['skipped_words'] \
            + sentence_results['skipped_words']
        global_results['unknown_words'] = \
            global_results['unknown_words'] \
            + sentence_results['unknown_words']
        global_results['extra_words'] = \
            global_results['extra_words'] \
            + sentence_results['extra_words']
        global_results['insistance_words'] = \
            global_results['insistance_words'] \
            + sentence_results['insistance_words']
        global_results['complex_words'] = \
            global_results['complex_words'] \
            + sentence_results['complex_words']
        global_results['inversion_words'] = \
            global_results['inversion_words'] \
            + sentence_results['inversion_words']
        global_results['lower_words'] = \
            global_results['lower_words'] \
            + sentence_results['lower_words']
        global_results['corrected_words'] = \
            global_results['corrected_words'] \
            + sentence_results['corrected_words']
        global_results['idiomatic_expressions'] = \
            global_results['idiomatic_expressions'] \
            + sentence_results['idiomatic_expressions']
        global_results['uppercase_words'] = \
            global_results['uppercase_words'] \
            + sentence_results['uppercase_words']
        global_results['punctuation_coeff'] = \
            global_results['punctuation_coeff'] \
            + sentence_results['punctuation_coeff']
        global_results['emotes'] = \
            global_results['emotes'] \
            + sentence_results['emotes']
        global_results['negative_words'] = \
            global_results['negative_words'] \
            + sentence_results['negative_words']
        global_results['superlative_words'] = \
            global_results['superlative_words'] \
            + sentence_results['superlative_words']

        if sentence_results['negative']:
            global_results['negative'] = True
        if sentence_results['comparative']:
            global_results['comparative'] = True
        global_results['comparative_words'] = \
            global_results['comparative_words'] \
            + sentence_results['comparative_words']
        for sensation in sentence_results['sensations']:
            if sensation not in global_results['sensations']:
                global_results[sensation] = 0
            global_results[sensation] = float(
                sentence_results[sensation])
        global_results['sensations_words'] = \
            global_results['sensations_words'] \
            + sentence_results['sensations_words']

    def rectify_eindex(self, eindex: int, emotion: str):
        """
        This is a temporary function that rectify inconsistency
        between e-index and main emotion. 
        """
        erange = {
        # Positive emotions
            "happiness" : np.arange(31,41,1),
            "surprise"  : np.arange(21,31,1),
        # Neutral emotions
            "calm" : np.arange(11,21,1),
        # Negative emotion
            "fear" : np.arange(5,11,1),
            "sadness" : np.arange(-5,5,1),
            "anger" : np.arange(-14,-5,1),
            "disgust" : np.arange(-20,-14,1),
        }
        try:
            # If eindex is not in the interval (
            # types should be trasnformed from
            # numpy.int64 to int)
            if eindex is None:
                return eindex
            elif eindex not in erange[emotion]:
                return  np.random.randint(
                    np.amin(erange[emotion]),
                    np.amax(erange[emotion]+1)
                )
            else:
                return eindex
        except:
            return eindex

    def isupper(self, word: str):
        """
        Check if the word exist in string in uppercase
        :param word: string, the word
        :return: Boolean
        """
        if (word.upper() in self.original_text and
            word not in self.words_as_df[
                self.words_as_df['is_emote'] == True
            ]['name'].values):
            return True
        else:
            return False
