'''
Transliterate from Buckwalter to IPA transcription of Modern Standard Arabic.

This script takes an input .csv file and outputs an updated .csv file
with IPA transcriptions of Buckwalter words from the input.

Written by Katherine Blake (Cornell) 
with help from Hassan Munshi (UPenn) November 2021.

-------------------------------------------------------------------------------

You may need to pip install pandas.

Usage:
python transliterate.py input_file
python transliterate.py input_file --output ./my_output.csv
'''

import argparse
import pandas as pd
import sys
from ast import literal_eval


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

special_char_dict = {
'A' : ['ʔa', 'a:'], #ʔa is word-initial, a: elsewhere
'p' : ['T','t',''], #surface [t] before vowels only
'w' : ['w','u:'],   #long vowel in the environment u_C, elsewhere: w
'y' : ['j','i:'],   #long vowel in the environment i_C, elsewhere: j
}

vowel_initial = ['a','a:','i','i:','u','u:','e','e:','an','in','un']
coronals = ['d','dˁ','n','r','s','sˁ','t','tˁ','θ','z','ðˁ','ð','ʃ']


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
        # print(pseudo_ipa)
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
    
    return ipa



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
                elif first_pass[i+1] == '~': #geminate
                        second_pass += special_char_dict[char][0]
                else: #before consonant
                    second_pass += special_char_dict[char][1]
        elif char == 'y':
        # long vowel in the environment 'i_C' and word-final, elsewhere: 'j'
            if (second_pass == '') or (second_pass[-1] != 'i'):
                second_pass += special_char_dict[char][0]
            else:
                if i == len(first_pass)-1: #word=final
                    second_pass += special_char_dict[char][1]
                elif first_pass[i+1] == '~': #geminate
                    second_pass += special_char_dict[char][0]
                elif first_pass[i+1] == 'A': #before long vowel
                    second_pass += special_char_dict[char][0]
                else: #before consonant
                    second_pass += special_char_dict[char][1]
        else:
            second_pass += char

    ## THIRD PASS: Buckwalter 'p' character
    third_pass = liaison(second_pass)

    ## FINAL PASS: Sun letters
    ipa = sun_letters(third_pass)

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
    

    trouble = ['ʔannwkj','ʔattqrj','ʔadda:rwjnjT','ʔanna:bħT','ʔarrðlT','ʔaddjna:sˁwr','ʔattwb']

    # iterate over data to add new column with IPA representation(s)
    pform1_col = []
    pform2_col = []
    for index, row in df.iterrows():
        bw = row["target_tokens"] #column name with Buckwalter token/s
        # in my use case, want to transliterate a list of two BW words
        if type(bw) != list:
            bw = literal_eval(bw)
        bw1 = bw[0]
        bw2 = bw[1]
        
        ipa1 = translate(bw1)
        ipa2 = translate(bw2)

        if ipa1 in trouble:
            print(bw1 + '\t' + ipa1)
        elif ipa2 in trouble:
            print(bw2 + '\t' + ipa2)
        
        pform1_col.append(ipa1)
        pform2_col.append(ipa2)

    # update dataframe and write to new file
    df["pform1"] = pform1_col
    df["pform2"] = pform2_col

    df.to_csv(path_or_buf=args.outpath, index=False)