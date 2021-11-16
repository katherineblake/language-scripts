import pandas as pd
import sys

vowels = ['a','e','i','u']
consonants = ['f','h','ħ','k','q','s','sˁ','t','tˁ','θ','ʃ','ʔ','x',
'b','v','d','dˁ','ʕ','ɣ','ʒ','l','r','v','z','ð','ðˁ','w','j','n','m']

def find_vowels(pform):
    '''
    Put '.' syllable boundary after every vowel, short and long,
    except for the final one.
    '''
    try:
        pform = pform.split('a')
        pform = "a.".join(pform)

        pform = pform.split('e')
        pform = "e.".join(pform)

        pform = pform.split('i')
        pform = "i.".join(pform)

        pform = pform.split('u')
        pform = "u.".join(pform)

        pform = pform.replace(".:",":.")

        last_ix = pform.rfind(".")
        pform = pform[:last_ix] + pform[last_ix+1:]

    # got a float type ?
    except AttributeError:
        pform = pform

    return pform


def find_consonants(pform):



    return pform
    

df = pd.read_csv("dataset_ar.csv",index_col=False)

new_p1 = []
new_pf2 = []
for index,row in df.iterrows():
    pform1 = row["pform1"]
    pform2 = row["pform2"]

    # add '.' after every long/short vowel (syllable count)
    pform1 = find_vowels(pform1)
    pform2 = find_vowels(pform2)

    # add move '.' to reflect accurate onset/coda assingment of Cs
    pform1 = find_consonants(pform1)
    pform2 = find_consonants(pform2)

    new_p1.append(pform1)
    new_p2.append(pform2)

