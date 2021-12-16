'''
Given a dataset with strings in IPA of Modern Standard Arabic, add new columns
for the CV-representations of the IPA, which include syllable boundaries
marked with '.' and stress marked with 'ˈ'.

Examples:
ħaqqan ˈCVC.CVC
ħaja:ti CV.ˈGVV.CV
ʔalʔaʕja:n CVC.CVC.ˈGVVC
ʔalmudarrisi CVC.CV.ˈCVC.CV.CV

Stress assignment rules (Watson, 2011):
1. Stress assigned to final superheavy 
(CVVC, CVCC, CVVGG)
2. Stress assigned to heavy penult 
(CVV, CVC)
3. Else stress the antepenult (or initial/penult if disyllabic)

@article{watson2011word,
  title={Word stress in Arabic},
  author={Watson, Janet CE},
  year={2011},
  publisher={Wiley-Blackwell}
}

Usage:
python assign_stress.py input_file
python assign_stress.py input_file --output my_path/my_filename.csv
'''

import argparse
import pandas as pd
import re
import sys

consonants = ['b','x','d','ʕ','f','ɣ','h','ħ','ʒ','k','l',
            'm','n','q','r','s','t','θ','v','z','ð','ʃ','ʔ']
vowels = ['a','i','u','e']
glides = ['w','j']
def generalize(ipa):
    '''
    Replace IPA characters with C, V, or G for consonant, vowel, glide.
    Returns syllabify() of generalized string.
    '''
    if type(ipa) != str:
        return ''

    for char in consonants:
        ipa = ipa.replace(char,'C')
    for char in vowels:
        ipa = ipa.replace(char,'V')
    for char in glides:
        ipa = ipa.replace(char,'G')
    
    ipa = ipa.replace(':','V') #long vowels
    CV_form = ipa.replace('ˁ','') #pharyngealization diacritic

    # add syllable boundaries
    return(syllabify(CV_form))


def syllabify(CV_form):
    '''
    Add syllable boundaries to CVG form.
    Returns add_stress() of CV_form with boundaries (e.g., 'CVC.CV')
    '''
    # get all vowels
    V_ixs = [m.start() for m in re.finditer('V',CV_form)]
    # get nuclei
    try:
        nuclei = [V_ixs[0]]
    except IndexError:
        return CV_form

    for i in range(1,len(V_ixs)):
        if V_ixs[i] != V_ixs[i-1] + 1: # catch VV cases
            nuclei.append(V_ixs[i])
    # insert boundary one to the left of every nuclei (no onsetless syllables)
    boundaries = [ix-1 for ix in nuclei if ix!=0]
    syllables = [CV_form[i:j] for i,j in zip(boundaries, boundaries[1:]+[None])]
    syllabified = '.'.join(syllables)
    
    # add stress diacritic
    return(add_stress(syllabified))


superheavy = ['VVC', 'VCC', 'VVGG']
heavy = ['VV', 'VC', 'VG']
def add_stress(syllabified):
    '''
    Identify which syllable is stressed based on rules hierarchy:
    1. Final if superheavy.
    2. Penult if heavy.
    3. Else antepenult.
    Returns form with primary stress marked.
    '''
    syllables = syllabified.split('.')
    if len(syllables) == 1: #monosyllabic
        return 'ˈ' + syllabified
    else:
        final = syllables[-1]
        penult = syllables[-2]
        # RULE 1
        for rime in superheavy:
            if final.endswith(rime):
                syllables[-1] = 'ˈ' + syllables[-1]
                return '.'.join(syllables)
        # RULE 2
        for rime in heavy:
            if penult.endswith(rime):
                syllables[-2] = 'ˈ' + syllables[-2]
                return '.'.join(syllables)
        # RULE 3
        if len(syllables) > 2:
            syllables[-3] = 'ˈ' + syllables[-3]
            return '.'.join(syllables)
        else: # disyllabic, penult/initial syl stressed even tho it's light
            syllables[-2] = 'ˈ' + syllables[-2]
            return '.'.join(syllables)


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("input_file",  
    help="Give path of the directory with Buckwalter data. Must be .csv. Name of column with Buckwalter assumed to be 'Buckwalter'.")
    parser.add_argument("--outpath", default="./output.csv",
    help="Give output filename and path. Default is ./output.csv")
    args = parser.parse_args()

    # read in data from file as pandas df
    df = pd.read_csv(args.input_file)

    CV_col1 = []
    CV_col2 = []
    for index,row in df.iterrows():
        pform1 = row["pform1"]
        pform2 = row["pform2"]

        # get CV representation with stress and syllable boundaries
        CV_form1 = generalize(pform1)
        CV_form2 = generalize(pform2)

        CV_col1.append(CV_form1)
        CV_col2.append(CV_form2)

    # update dataframe and write to file
    df["CV_form1"] = CV_col1
    df["CV_form2"] = CV_col2

    df.to_csv(path_or_buf=args.outpath, index=False)