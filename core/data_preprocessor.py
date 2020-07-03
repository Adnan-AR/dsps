import time
import re
import uuid
import string

import pandas as pd
import nltk
from nltk.tokenize import sent_tokenize
from urlextract import URLExtract

class TextTransformer:

    def __init__(self):
        # Add extra abbreviation to the tokenizer
        extra_abbreviations = ['ex', 'eg']
        punkt_data = nltk.data.load('tokenizers/punkt/english.pickle')
        punkt_data._params.abbrev_types.update(extra_abbreviations)
        # URL extractor initialized here to avoid multiple
        # initialization, hence faster text transforming
        self.url_extractor = URLExtract()
        # Dictionary to replace bad apostrophe
        self.apostrophes_rep = {"’":" ", "'":" "}
        

    def amend_text(self, text: str):
        """
        Replace urls, hashtags and mentions from text
        :param text: text to amend
        :return: an amended text
        """
        mention_pattern = r'(?<=^|(?<=[^a-zA-Z0-9-_\.]))' \
                          r'@([A-Za-z]+[A-Za-z0-9-_]+)'
        hashtag_pattern = r'#(\w+)'
        amended_text = self.replace_urls(text)[0]
        amended_text = re.sub(mention_pattern, '{{{tag}}}',
                              amended_text)
        amended_text = re.sub(hashtag_pattern, '{{{hashtag}}}',
                              amended_text)
        return amended_text

    @staticmethod
    def get_list_from_regex(text: str,
                            pattern: str):
        """
        Get a list of matching objects from regex pattern
        :param text: text to search in
        :param pattern: regex pattern to use
        :return: a list of matching objects
        """
        results = re.finditer(pattern, text)
        url_list = list()
        for result in results:
            url_list.append(str(result.group()))
        return url_list

    def text_tokenize(self, text: str):
        """
        TODO
        :param text: text to split
        :return: a list of subtexts
        """
        # --1-- Add a white space between final [.?!]
        # and the next char
        text = re.sub(
            r"(?<![0-9a-zA-ZÀ-ÿ ])(\.)(?=[a-zA-Z0-9À-ÿ ])",
            " . ",text)
        # --2--
        text = re.sub(
            r"([\?\!])(?=[a-zA-Z0-9À-ÿ])",r" \1 ",text)
        # period with no white space after
        # --3--
        text = re.sub(
            r"(?<=[a-zA-ZÀ-ÿ])(\.)(?![ .!?])",r"\1 ",text)
        # --4-- (specific to banque Casino Chat)
        text = text.replace("|*|","|*|. ")
        return sent_tokenize(text, "english")

    def get_subtexts(self, text: str):
        """
        Get subtexts from text
        :param text: the text to split
        :return: a list of subtexts
        """
        # Remove the urls before tokenize
        text = self.replace_urls(text)[0]
        # Tokenize qfter replacing url
        subtexts = self.text_tokenize(text)
        return [
            {
                'id': index,
                'subtext_id': str(uuid.uuid4()),
                'subtext': subtext
            } for index, subtext in enumerate(subtexts)
        ]

    # TODO: Warning this function is duplicated for
    # API (c.f. process_string)
    def process(self,dataframe,column_name = 'text'):
        """
        Process a structural analysis on dataframe
        :param dataframe: dataframe to process
        :param column_name: name of the column where texts are stored
        :return: "structurally" processed dataframe
        """
        mention_pattern = r'(?<=^|(?<=[^a-zA-Z0-9-_\.]))' \
                          r'@([A-Za-z]+[A-Za-z0-9-_]+)'
        hashtag_pattern = r'#(\w+)'
        dataframe[column_name] = dataframe[column_name].apply(
            lambda text: str(text)
        )
        dataframe['amended_text'] = dataframe[column_name].apply(
            lambda text: self.amend_text(text)
        )
        dataframe['urls'] = dataframe[column_name].apply(
            lambda text: self.replace_urls(text)[1]
        )
        dataframe['tags'] = dataframe[column_name].apply(
            lambda text: self.get_list_from_regex(text, mention_pattern)
        )
        dataframe['hashtags'] = dataframe[column_name].apply(
            lambda text: self.get_list_from_regex(text, hashtag_pattern)
        )
        dataframe['subtexts'] = dataframe.apply(
            lambda x: self.get_subtexts(x[column_name]), axis = 1)
        dataframe['is_preprocessed'] = dataframe[column_name].apply(
            lambda value: True)
        return dataframe
    
    # TODO: Warning this function is duplicated for
    # endpoint (c.f. process)
    def process_string(self, string: str):
        """
        Structural analysis on string
        :param string: string to process
        :return: string
        """
        mention_pattern = r'(?<=^|(?<=[^a-zA-Z0-9-_\.]))' \
                          r'@([A-Za-z]+[A-Za-z0-9-_]+)'
        hashtag_pattern = r'#(\w+)'
        string = string
        return {
            'amended_text' : self.amend_text(string),
            'urls' : self.replace_urls(string)[1],
            'tags' : self.get_list_from_regex(string, mention_pattern),
            'hashtags' : self.get_list_from_regex(
                string, hashtag_pattern),
            'subtexts' : self.get_subtexts(string),
            'is_preprocessed' : True
        }

    # TODO voir si on peut loop sur une chaine de charactères spéciaux
    @staticmethod
    def restructure_verbatim(text: str):
        text = re.sub('(\.\s?\b)', '. ', text)
        text = re.sub('(\b\.)', ' .', text)
        text = re.sub('(\b\!\b)', ' ! ', text)
        text = re.sub('(\!\b)', '! ', text)
        text = re.sub('(\b\!)', ' !', text)
        text = re.sub('(\b\,\b)', ' , ', text)
        text = re.sub('(\,\b)', ', ', text)
        text = re.sub('(\b\,)', ' ,', text)
        text = re.sub('(\b\)\b)', ' ) ', text)
        text = re.sub('(\)\b)', ') ', text)
        text = re.sub('(\b\))', ' )', text)
        text = re.sub('(\b\?\b)', ' ? ', text)
        text = re.sub('(\?\b)', '? ', text)
        text = re.sub('(\b\?)', ' ?', text)
        text = re.sub('(\b\'\b)', ' \' ', text)
        text = re.sub('(\'\b)', '\' ', text)
        text = re.sub('(\b\')', ' \'', text)
        text = re.sub('(\b\"\b)', ' \" ', text)
        text = re.sub('(\"\b)', '\" ', text)
        text = re.sub('(\b\")', ' \"', text)
        text = re.sub('(\b\\\b)', ' \\ ', text)
        text = re.sub('(\\\b)', '\\ ', text)
        text = re.sub('(\b\\)', ' \\', text)
        text = re.sub('(\b\/\b)', ' / ', text)
        text = re.sub('(\/\b)', '/ ', text)
        text = re.sub('(\b\/)', ' /', text)
        text = re.sub('(\b\-\b)', ' - ', text)
        text = re.sub('(\-\b)', '- ', text)
        text = re.sub('(\b\-)', ' -', text)
        return text

    def restructure_verbatims(self,
                              dataframe,
                              column_name = 'text'):
        dataframe['restructured_verbatim'] = dataframe[
            column_name].apply(
            lambda text: self.restructure_verbatim(text))

    def separate_words(self, string: str):
        """
        Put space around words and compound words, 
        including apostrophes, degree or dash.
        :param string: input string
        :return: string
        """
        string = re.sub(
            r"((?=\S*['-°])([a-zA-Z°'À-ÿ-]+)|([a-zA-Z0-9À-ÿ]+))",
            r" \1 ", string
        )
        # Reduce the excessive number of spaces
        string = re.sub(" +"," ", string)
        # Return the string (lowercase)
        return string.lower()

    def replace_urls(self, string: str):
        """
        Replace URLs in a string.
        :param string: string
        :return: tuple of string and urls
        """
        # Get all urls in the string
        urls = self.url_extractor.find_urls(string)
        # Replace the urls by {{{url}}}
        if urls:
            for url in urls:
                string = string.replace(url, ' ', 1)
        return (string, urls)

    def multireplace(
            self, string, replacements = None, ignore_case=False):
        """
        Given a string and a replacement map, it returns the 
        replaced string.
        :param str string: string to execute replacements on
        :param dict replacements: replacement dictionary {value to 
        find: value to replace}
        :param bool ignore_case: whether the match should be case 
        insensitive
        :rtype: str
        """
        # if replacements are not defined wez take the ascii letters
        # as default
        if replacements is None:
            replacements = self.apostrophes_rep
        # If case insensitive, we need to normalize the old string so
        # that later a replacement
        # can be found. For instance with {"HEY": "lol"} we should
        # match and find a replacement for "hey",
        # "HEY", "hEy", etc.
        if ignore_case:
            def normalize_old(s):
                return s.lower()
            re_mode = re.IGNORECASE
        else:
            def normalize_old(s):
                return s
            re_mode = 0
        replacements = {
            normalize_old(key): val for key, val in
            replacements.items()}
        # Place longer ones first to keep shorter substrings from
        # matching where the longer ones should take place
        # For instance given the replacements {'ab': 'AB',
        # 'abc': 'ABC'}
        # against the string 'hey abc', it should produce
        # 'hey ABC' and not 'hey ABc'
        rep_sorted = sorted(replacements, key=len, reverse=True)
        rep_escaped = map(re.escape, rep_sorted)
        # Create a big OR regex that matches any of the substrings to
        # replace
        pattern = re.compile("|".join(rep_escaped), re_mode)
        # For each match, look up the new string in the replacements,
        # being the key the normalized old string
        return pattern.sub(
            lambda match: replacements[normalize_old(match.group(0))],
            string)
