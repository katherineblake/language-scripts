'''
Transliterate from Buckwalter to IPA transcription of Modern Standard Arabic.

This script takes an input .csv file and outputs an updated .csv file
with IPA transcriptions of Buckwalter words from the input.
Buckwalter data is expected to be one word per row, in a column "Buckwalter";
transcription will be added in a new column "IPA". 

Written by Katherine Blake (Cornell) with Hassan Munshi (UPenn) January 2022.
Script developed on Buckwalter MADAMIRA output of Common Voice Arabic corpus.

-------------------------------------------------------------------------------

You may need to pip install pandas.

Usage:
python transliterate.py input_file
python transliterate.py input_file --outpath my_path/my_filename.csv
'''

import argparse
import pandas as pd
import sys
from ast import literal_eval

# 1:1 correspondences
char_dict = {
'a' : 'a',
'b' : 'b',
'c' : 'x',          #loanword: Heinrich
'd' : 'd',
'D' : 'dˁ',
'e' : 'e',
'E' : 'ʕ',
'f' : 'f',
'F' : 'an',
'g' : 'ɣ',
'h' : 'h',
'H' : 'ħ',
'i' : 'i',
'j' : 'ʒ',          # dialectal: ['g','ʤ']
'k' : 'k',
'K' : 'in',
'l' : 'l',
'm' : 'm',
'M' : 'm',          #loanword: "Mar"
'n' : 'n',
'N' : 'un', 
'o' : '',
'q' : 'q',
'r' : 'r',
's' : 's',
'S' : 'sˁ',
't' : 't',
'T' : 'tˁ',
'u' : 'u',
'v' : 'θ',
'V' : 'v',          #loanwords
'x' : 'x',
'Y' : ':',          #lengthens preceding /a/
'z' : 'z',
'Z' : 'ðˁ',         #dialectal: 'zˁ'
'*' : 'ð',
'$' : 'ʃ',
'~' : '~',          #geminate consonant marker
'}' : 'ʔ',          #should be in environment of /i/ or /j/
'>' : 'ʔ',          #should be in environment of /a/
'<' : 'ʔ',          #should be in environment: stem-initial before /i/
'\'' : 'ʔ',
'`' : 'a:',         #something might be weird here -- what about this/that?
'|' : 'ʔa:',
'-' : '',           #loanword: "V-day"
'&' : 'ʔ'           #should be in environment of /u/
}

# 1:many correspondences
special_char_dict = {
'A' : ['ʔa', 'a:', 'a'], #ʔa is word-initial, a after prefixes, a: elsewhere
'p' : ['T','t',''], #surface [t] before vowels only
'w' : ['w',':'],   #long vowel in the environment u_C, elsewhere: w
'y' : ['j',':'],   #long vowel in the environment i_C, elsewhere: j
}

# useful lists for transcription
vowel_initial = ['a','a:','i','i:','u','u:','e','e:','an','in','un']
coronals = ['d','dˁ','n','r','s','sˁ','t','tˁ','θ','z','ðˁ','ð','ʃ','l']
consonants = ['b','x','d','dˁ','ʕ','f','ɣ','h','ħ','ʒ','k','l','m','n',
            'q','r','s','sˁ','t','tˁ','θ','v','z','ðˁ','ð','ʃ','ʔ','ˁ']


############################## HELPER FUNCTIONS ###############################
def liaison(pseudo_ipa):
    '''
    Iterate over pseudo-IPA to replace 'p' Buckwalter character,
    which is realized as [t] before vowels at morpheme- and word-boundaries.
    Changes 'p' to 't' word-internally and 'T' word-finally.
    Returns updated form.
    '''
    ipa = ''
    for i,char in enumerate(pseudo_ipa):
        if char == 'p':
        # surface [t] before vowels
            if i == len(pseudo_ipa)-1:
            # realization of word-final 'p' depends on onset of following word
            # 'T' used as placeholder
                ipa += special_char_dict[char][0]
            else:
                if pseudo_ipa[i+1] in vowel_initial:
                    ipa += special_char_dict[char][1]
                else:
                    ipa += special_char_dict[char][2]
        else:
            ipa += char

    return ipa


def sun_letters(pseudo_ipa):
    '''
    Iterate over pseudo-IPA to assimlate /ʔal-/ definite article to
    [ʔaC] before Sun letters (coronal consonants).
    Returns updated form.
    '''
    if pseudo_ipa[:3] == 'ʔal':
        if pseudo_ipa[3] in coronals:
            # if there is already a geminate Sun letter, delete the /l/
            if pseudo_ipa[3] == pseudo_ipa[4]:
                ipa = pseudo_ipa[:2] + pseudo_ipa[3:]
            else:
                if pseudo_ipa[4] == 'ˁ':
                    ipa = pseudo_ipa[:2] + pseudo_ipa[3:]
                else:
                    ipa = pseudo_ipa[:2] + pseudo_ipa[3] + pseudo_ipa[3:]
        else:
            ipa = pseudo_ipa
    else:
        ipa = pseudo_ipa
    
    # check for CCC sequences, which are not allowed in MSA
    if 'l' in ipa:
        phones = list(ipa)
        l_ixs = [i for i, x in enumerate(phones) if x =='l']
        for l_ix in l_ixs:
            if l_ix <= len(phones) - 3:
                C1 = l_ix+1
                C2 = l_ix+2
                # check for diacritic, if so need to move index
                if phones[C1] == 'ˁ':
                    if C1 < len(phones) - 1:
                        C1 += 1
                        C2 += 1
                    else:
                        break
                if phones[C2] == 'ˁ':
                    if C2 < len(phones) - 1:
                        C2 += 1
                    else:
                        break
                # check if the next two phones after /l/ are also consonants
                if (phones[C1] in consonants) and (phones[C2] in consonants):
                    phones[l_ix] = '%' # replace erroneous /l/ with special char
        # remove erroneous /l/s
        if '%' in phones:
            phones.remove('%')
        ipa = ''.join(phones)

    return ipa


def vocalize(ipa,ignore=True):
    '''
    Iterate over IPA to vocalize inter-consonantal glides, which should be
    vocalized. E.g., /twb/ --> /tawb/
    Vowel identity may be incorrect, but syllable structure should be more
    accurate. Should affect only a small subset of the data (~1%)

    If ignore, return empty string; else apply less-than-perfect rule.

    Returns updated form.
    '''
    for i in range(1,len(ipa)-1):
        if ipa[i] == 'j':
            if (ipa[i-1] in consonants) and (ipa[i+1] in consonants):
                if ignore:
                    return ''
                else:
                    ipa = ipa[:i] + 'ij' + ipa[i+1:]
        elif ipa[i] == 'w':
            if (ipa[i-1] in consonants) and (ipa[i+1] in consonants):
                if ignore:
                    return ''
                else:
                    ipa = ipa[:i] + 'aw' + ipa[i+1:]
    
    if (len(ipa) > 1) and (ipa[-1] == 'T') and (ipa[-2] in consonants):
        ipa = ipa[:-1] + 'aT'

    return ipa

###############################################################################

def translate(bw):
    '''Iterate over characters in a word in Buckwalter and 
    look up their IPA character. Some special cases where 
    BW:IPA is not a 1:1 correspondence. Returns IPA string.
    '''
    
    ## FIRST PASS: replace all 1:1 Buckwalter:IPA correspondences
    first_pass = ''
    for i,char in enumerate(bw):
        try:
            first_pass += char_dict[char]
        except KeyError:
            first_pass += char

    ## SECOND PASS: 1:many correspondances
    second_pass = ''
    for i,char in enumerate(first_pass):
        if char == 'A':
        # 'ʔa' word-initial, delete before 'an' morpheme, 'a:' elsewhere
            if i == 0:
                second_pass += special_char_dict[char][0]
            elif first_pass[i-1] == 'i':
                second_pass += special_char_dict[char][2]
            elif first_pass[i-1] == 'a':
                second_pass += ':'
            elif len(first_pass) >= 3:
                if first_pass[i+1:] == 'an':
                    second_pass += ''
                else:
                    second_pass += special_char_dict[char][1]
            else:
                second_pass += special_char_dict[char][1]
        elif char == '~':
        # geminate previous consonant
            if second_pass[-1] == 'ˁ':
                second_pass += second_pass[-2:]
            else:
                second_pass += second_pass[-1]
        elif char == 'w':
        # long vowel in the environment 'u_C' and word-final, elsewhere: 'w'
            if 'ww' in first_pass:
            # there is an issue with Buckwalter transcription
                second_pass = '' 
                break
            elif (second_pass == '') or (second_pass[-1] != 'u'):
                second_pass += special_char_dict[char][0]
            else:
                if i == len(first_pass)-1: #word-final
                    second_pass += special_char_dict[char][1]
                elif (first_pass[i+1] == '~') or (first_pass[i+1] in vowel_initial): #geminate or before vowel
                        second_pass += special_char_dict[char][0]
                else: #before consonant
                    second_pass += special_char_dict[char][1]
        elif char == 'y':
        # long vowel in the environment 'i_C' and word-final, elsewhere: 'j'
            if (second_pass == '') or (second_pass[-1] != 'i'):
                second_pass += special_char_dict[char][0]
            else:
                if i == len(first_pass)-1: #word-final
                    second_pass += special_char_dict[char][1]
                elif first_pass[i+1] == '~': #geminate
                    second_pass += special_char_dict[char][0]
                elif (first_pass[i+1] == 'A') or (first_pass[i+1] in vowel_initial): #before vowel
                    second_pass += special_char_dict[char][0]
                else: #before consonant
                    second_pass += special_char_dict[char][1]
        else:
            second_pass += char

    ## THIRD PASS: Buckwalter 'p' character
    third_pass = liaison(second_pass)

    ## FOURTH PASS: Sun letters
    fourth_pass = sun_letters(third_pass)

    ## FINAL PASS: Glide nuclei
    ipa = vocalize(fourth_pass,ignore=False)

    return ipa


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("input_file",  
    help="Give path of the directory with Buckwalter data. Must be .csv. Name of column with Buckwalter assumed to be 'Buckwalter'.")
    parser.add_argument("--outpath", default="./output.csv",
    help="Give output filename and path. Default is ./output.csv")
    args = parser.parse_args()

    # read in data from file as pandas df
    df = pd.read_csv(args.input_file)
    
    # iterate over data to add new column with IPA representation(s)
    ipa_col = []
    for index, row in df.iterrows():
        bw = row["Buckwalter"] #column name with Buckwalter token

        # get IPA transcription of Buckwalter
        ipa = translate(bw)
        ipa_col.append(ipa)

    # update dataframe and write to new file
    df["IPA"] = ipa_col

    df.to_csv(path_or_buf=args.outpath, index=False)