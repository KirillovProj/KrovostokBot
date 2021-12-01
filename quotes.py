"""
Insert your quotes and song data here as listed in example.
Quotes should be turned to dictionary with quotes texts as keys and numbers representing songs from which they originated as values.
Songs should be arranged as a tuple of tuples. Each inner tuple should contain SongName as the first argument and song link as the second. Note that
index of an element in outer tuple should be used as a 'song number' in quotes dict. Indexing starts from 1 for the sake of compatibility with SQL.
"""
songs = (('SongNameA', 'SongLinkA'), ('SongNameB', 'SongLinkB'))
quotes = {'QuoteTextA': 1, 'QuoteTextB': 2}
