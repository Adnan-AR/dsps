dummy_words = {"c'est la classe!":
    {"mood": "",
     "is_emote": True,
     "is_compound_word": False,
     "name": "c'est la classe!",
     "updated_by": "5"},
 "not enough barnyard":
     {"is_emote": False,
      "is_compound_word": True,
      "name": "not enough barnyard"},
 "familiarisations" : 
     {"is_emote": False,
      "created_at": "2016-03-23T22:21:05.396Z",
      "is_compound_word": False,
      "name": "familiarisations"}
}

# Expected results after transformatrion
dummy_words_expected = {"c'est la classe!":
    {"mood": "",
     "is_emote": True,
     "is_compound_word": True,
     "name": "c'est la classe!",
     "updated_by": "5"},
 " not enough barnyard ":
     {"is_emote": False,
      "is_compound_word": True,
      "name": "not enough barnyard"},
 " familiarisations " : 
     {"is_emote": False,
      "created_at": "2016-03-23T22:21:05.396Z",
      "is_compound_word": False,
      "name": "familiarisations"}
}
