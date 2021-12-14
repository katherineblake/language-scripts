'''
Automatic stress-assignment rules for Hindi.
Stress is assigned to the heaviest syllable in a word.
In the case of a tie, stress is assigned to the right-most,
non-final syllable of those that are tied.

Kelkar, Ashok R. 1968. Studies in Hindi-Urdu I: Introduction and Word Phonology.
Poona: Deccan College.
(As reproduced in Gordon 2010 Stress systems paper)


'''
import numpy as np
import pandas as pd
import sys


def rewrite_pform(index,pform):
    '''
    Return pform with stress diacritic on stressed syllable.
    '''
    syls = pform.split('.')
    stressed = syls[index].strip()
    stressed = 'ˈ' + stressed
    syls[index] = stressed
    new_pform = '.'.join(syls)

    return new_pform


vowels = ['u','ɛʱ','ɛ' 'ˈə','ɔ', 'ə̯','i','ʊ', 'õ', 'ə̃', 'ɪ̃', 'ə', 'ɪ','a','ʊ̃', 'æ', 'ᵊ']
def get_weight(syl):
    '''
    Weight system of Hindi:
    1. Superheavy: C V: C and C V C C = 3
    2. Heavy: C V: and C V C = 2
    3. Light: C V = 1
    Return 1,2,3 depending on weight of syl.
    '''
    # long vowel
    if 'ː' in syl:
        if syl[-1] == 'ː':
            return 2 #heavy
        else:
            return 3 #superheavy
    #short vowel
    else:
        phones = syl.split(' ')
        for ix,phone in enumerate(phones):
            if phone[-1] == 'ᵊ': #special case
                return 1
            elif phone in vowels:
                coda = phones[ix+1:]
                # complex coda
                if len(coda) == 2:
                    return 3 #superheavy
                # simple coda
                elif len(coda) == 1:
                    return 2 #heavy
                # no coda
                else:
                    return 1 #light


def assign_stress(pform):
    '''
    Find syllable to stress in IPA string dependent on Hindi rules.
    Call get_weight() and rewrite_pform() as helper functions.
    Returns updated pform with stress marked with 'ˈ'.
    '''
    syls = pform.split('.')
    weights = []
    # loop over syllables to assign them a weight
    for syl in syls:
        syl = syl.strip()
        weight = get_weight(syl)
        weights.append(weight)
    heaviest = np.amax(weights) # get heaviest syllables
    indices = list(np.where(weights == heaviest)[0]) # and their indices

    # if there is no tie for heaviest syllable
    if len(indices) == 1:
        # print("stress the " + str(indices[0]))
        new_pform = rewrite_pform(indices[0], pform)
    # otherwise pick the rightmost, non-final
    else:
        #rightmost if non-final
        if indices[-1] != (len(syls)-1):
            # print("stress the " + str(indices[-1]))
            new_pform = rewrite_pform(indices[-1], pform)
        # next rightmost if rightmost is final
        else:
            # print("stress the " + str(indices[-2]))
            new_pform = rewrite_pform(indices[-2], pform)

    return new_pform

        


df = pd.read_csv("pdataset_hi.csv",index_col=False)

new_pf1_col = []
new_pf2_col = []

for index,row in df.iterrows():
    pform1 = row["pform1"]
    pform2 = row["pform2"]

    new_pform1 = assign_stress(pform1)
    new_pform2 = assign_stress(pform2)

    new_pf1_col.append(new_pform1)
    new_pf2_col.append(new_pform2)

df["new_pform1"] = new_pf1_col
df["new_pform2"] = new_pf2_col

df.drop(columns=["pform1","pform2"], inplace=True)

df.to_csv(path_or_buf="pdataset_hi_updated.csv",index=None)
