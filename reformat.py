'''
Reformat Phonitalia to add stress diacritic on stressed syllable
and add spaces between phones, similar to WikiPron.

Reformat Polish WikiPron which has stray '/' and missing syllable
boundaries between unstressed.stressed syllables.

Reformat Lexique to replace syllable markers with '.' and add liaison
consonants; and spaces between phones, similar to WikiPron.
'''

import pandas as pd
import sys 

'''
## PHONITALIA
df = pd.read_csv("phonitalia.csv", index_col=False)

pform_col = []
for index,row in df.iterrows():
    # don't mark stress on monosyllabic words
    if len(row["PhoneSyll"]) == 1:
        pform = row["PhoneSyll"]
    else:
        phones = " ".join(row["PhoneSyll"])
        stress_ix = row["StressedSyllable"] - 1
        syls = phones.split('.')
        # primary stress works differently
        if stress_ix == 0:
            syls[stress_ix] = "ˈ" + syls[stress_ix]
        else:
            syls[stress_ix] = " ˈ" + syls[stress_ix][1:]
        pform = ".".join(syl for syl in syls)
    
    pform_col.append(pform)

df["phonological_form"] = pform_col

char_dict = {
    'a\'' : 'à',
    'i\'' : 'ì',
    'u\'' : 'ù',
    'e\'' : 'è', # won't get some é's but good enough for N/A
    'o\'' : 'ò'
}

word_col = []
lemma_col = []
for index,row in df.iterrows():
    word = row["word"]
    lemma = row["lemma"]
    for grapheme in char_dict.keys():
        if grapheme in word:
            word = word.replace(grapheme, char_dict[grapheme])
        if grapheme in lemma:
            lemma = lemma.replace(grapheme, char_dict[grapheme])
    word_col.append(ortho)
    lemma_col.append(lemma)

df["word"] = word_col
df["lemma"] = lemma_col

df.to_csv(path_or_buf="phonitalia_reformat.csv", index=False)
'''

'''
## POLISH WIKIPRON
df = pd.read_csv("lexicon_polish.tsv", sep='\t', index_col=False)

for index,row in df.iterrows():
    pform = row[1].replace('ˈ','. ˈ').strip('.')
    pform = pform.replace('/','').strip(' ')
    row[1] = pform

df.to_csv(path_or_buf="lexicon_polish.csv", index=False)
'''

'''
## LEXIQUE
df = pd.read_csv("lexique.tsv", sep='\t', index_col=False)

pform_col = []
for index,row in df.iterrows():
    # replace syllable marker "-" with "."
    phones = row["syll"]
    phones = phones.replace("-",".")

    # get CV representations of liaison form and regular form
    liaison_cv = row["cvcv"]
    regular_cv = row["p_cvcv"]

    # if there is a liaison consonant, add "T" to the end of the word
    if regular_cv[-1] == "V":
        if liaison_cv[-1] == "C":
            phones += 'T'

    # space-separate phones just like WikiPron
    pform = " ".join(phones)

    pform_col.append(pform)

df["phonological_form"] = pform_col
df.to_csv(path_or_buf="lexique_updated.csv",index=False)
'''