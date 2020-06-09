# This is the module that serves to handle Unicode code point conversion for
# Proto-Altekhsnan language in case the OpenType lookup doesn't work. Please
# note that this version still disregards characters those do not exist in the
# font file (e.g. numbers)
#
# Currently known issues:
# * The program does not support '<' and '>' character inputs yet (which are used
#   for quotations.
# * When converting certain words, the cluster may sometimes contain five characters
#   instead of the supposed four characters at most.
#   Tested case: "otlium" -> supposed to be "ot-=lium-"
# * Separate clustering between default consonant and vowel (e.g. la=e) is still
#   not possible. -- vertical clustering, cannot be mitigated like below.
#   ...It actually looks normal in CSP, but not the web. Weird.
#   It's also bug in the FONT for different reason. -- horizontal clustering in
#   OpenOffice, can be mitigated using double separator ("==")
#   Tested case: Inputting "c-=la=ee" becomes "c-=lee"

import re
# from timeit import default_timer as timer

# Defines base character groups of Proto-Altekhsnan writing system
characterGroups = {
    "a" : ('a'),
    "non-a" : ('e', '\u00e9', 'i', 'o', 'u', '\ue001' '\ue000', '\ue002',
                '\ue003'),
    "consonants": ('b', 'c', 'd', 'f', 'g', 'h', 'j', 'k', 'l', 'm', 'n',
        'p', 'q', 'r', 's', 't', 'v', 'w', 'x', 'y', 'z', '\ue004', '\ue005'),
    # "non-a" : ('e', '\u00e9', 'ee', 'i', 'o', 'u', '\ue001', 'nn',
        # '\ue000', 'hh', '\ue002', 'th', '\ue003', 'eu'),
    # "consonants": ('b', 'c', 'd', 'f', 'g', 'h', 'j', 'k', 'l', 'm', 'n',
        # 'p', 'q', 'r', 's', 't', 'v', 'w', 'x', 'sy', 'y', 'z', '\ue004', 'ng',
        # '\ue005', 'ny'),
    "vr": ('-'), # wowel removal sign
    "separator": ('='),
    "etc": ('<', '>', ' '),
}

# Dictionary for replacement of certain characters with their single Unicode
# character
single_char_substitute = {
    u'sy' : u'x',
    u'ee' : u'\u00e9',
    u'hh' : u'\ue000',
    u'nn' : u'\ue001',
    u'th' : u'\ue002',
    u'eu' : u'\ue003',
    u'ng' : u'\ue004',
    u'ny' : u'\ue005',
}

# The crude regex pattern required for substitution later
regex_groups = {
    "vowels_all" : "a" + ''.join(characterGroups["non-a"]) + "-",
    "vowels_non_a" : ''.join(characterGroups["non-a"]) + "-",
    "consonants" : ''.join(characterGroups["consonants"])
}

# First, the input is separated into individual words.
def separate_words(sentence):
    words = []
    input2 = str(sentence).lower()

    if input2.find(" ") != -1:
        words = input2.split(" ")
    else:
        words.append(input2)

    return words

# The next step is to break down each word into syllables in Proto-Altekhsnan
def separate_syllables_regex(word):
    syllables = []

    syllable = ''

    # The priority is as follows:
    # 1 - Special consonants - nga, nya, sya - vowels a, e, i, o, u, eu, n, h, e-acute
    #       For s* (s and sy), this means s does not need to be included in regular consonants
    #       Ditto for t, since it's possible for it to be 'th' (becoming vowel)
    # 2 - Regular consonants followed by vowel (minus 'nnn' and 'hhh')
    # 3 - Special vowels - h, n, th, e-acute, eu
    # 4 - Regular vowels
    rgx_pattern_vowels = 'e[eu]*|(?<!n)(nn)|(?<!h)(hh)|[aiou\u00e9-]' # th cannot be put here due to its complicated position
    rgx_pattern_sp_consonants = 'n[gy]*|sy*' # ng*, ny*, n*, sy*, s*
    rgx_pattern_t = 't(e[eu]*|nn|[ahiou\u00e9-])' # tee* (with e-acute), teu*, tn, t*
    rgx_pattern_consonants = '[^aeinostu\u00e9-]'

    # =|((n[gy]*|sy*|[^aeinostu\u00e9 =-])(e[eu]*|(?<!n)(nn)|(?<!h)(hh)|[aiou\u00e9-]))|(t(e[eu]*|nn|[ahiou\u00e9-]))|(e[eu]*|(?<!n)(nn)|(?<!h)(hh)|[aiou\u00e9-])
    rgx_pattern_full = str('=' + '|' + '(' + '(({0}|{1})({2}))' + '|' + '({3})'
                            + '|' + '({4})' + ')') \
        .format(rgx_pattern_sp_consonants, rgx_pattern_consonants,
            rgx_pattern_vowels, rgx_pattern_t, rgx_pattern_vowels)

    for syl in re.finditer(rgx_pattern_full, word):
        syllable = syl.group(0)

        print("Possible syllable groups found: ", syl.groups())

        # To make clustering easier, substitute several characters such as "th" with their
        # Unicode variant
        # Must be done in this way because Python is a huge jerk
        ch = [i for i in list(single_char_substitute.keys()) if i in syllable]
        if ch:
            syllable = syllable.replace(ch[0], single_char_substitute[ch[0]])


        # If the syllable is not in modified form (e.g. 'ha'), remove the 'a' to make
        # conversion easier
        if len(syllable) > 1 and any(cons in syllable for cons in characterGroups['consonants']) and syllable[-1] == 'a':
            syllable = syllable[:-1]

        syllables.append(syllable)

    # for consonant followed by vowels h, n, and th, join the separated consonant with the vowel.
    for index in range(len(syllables)):
        # To handle accidentally choosing the last item because of the -1 thing
        prevIndex = index-1 if (index - 1 >= 0) else 0

        if (len(syllables[prevIndex]) == 1 and syllables[prevIndex]
            in characterGroups["consonants"]) and (syllables[index] in
            ("\ue000", "\ue001", "\ue002")):
            syllables[prevIndex] = ''.join(syllables[prevIndex:index+1])
            syllables[index] = ''
            syllables.remove('')

    return syllables


# The next step is to break down each word into syllables in Proto-Altekhsnan
# def separate_syllables(word):
    # syllables = []

    # latin_vowel = u'aeiou\u00e9'
    # vowel_eraser = u'-'

    # # 't' -> th
    # # 's' -> sy
    # # 'n' -> nn, ng, ny
    # # 'h' -> hh
    # t_connectors = latin_vowel + vowel_eraser + u'h'
    # s_connectors = latin_vowel + vowel_eraser + u'y'
    # h_connectors = latin_vowel + vowel_eraser + u'h'
    # n_connectors = latin_vowel + vowel_eraser + u'g' + u'y' + u'n'

    # # break down into individual chars and reverse it
    # chars_list = list(word)
    # chars_list.reverse()

    # syllable = u''

    # # We will use character indexing because we need to predict the next character
    # for ch in chars_list[::-1]:

        # # Add the front-most character in the word to the syllable
        # syllable += chars_list.pop()

        # # Handle only as long as chars_list is not empty
        # if chars_list:

            # # By default, assume the character is a consonant
            # if ch not in (latin_vowel + vowel_eraser + u'='):

                # # Handle special cases.
                # if syllable[-1] == u'n':
                    # if (len(syllable) > 1 and syllable[-2] not in (u'n')) or len(syllable) == 1:
                        # if chars_list[-1] in n_connectors:
                            # continue
                # elif syllable[-1] == u't':
                    # if chars_list[-1] in t_connectors:
                        # continue
                # elif syllable[-1] == u'h':
                    # if (len(syllable) > 1 and syllable[-2] not in (u't', u'h')) or len(syllable) == 1:
                        # if chars_list[-1] in h_connectors:
                            # continue
                # elif syllable[-1] == u's':
                    # if chars_list[-1] in s_connectors:
                        # continue
                # else:
                    # continue

            # else: # Otherwise, assume it's a vowel
                # # Handle special case for 'e' because it can be 'ee' or 'eu'
                # if syllable[-1] == u'e':
                    # if (len(syllable) > 1 and syllable[-2] != u'e') or len(syllable) == 1:
                        # if chars_list[-1] in (u'e', u'u'):
                            # continue

        # # To make clustering easier, substitute several characters such as "th" with their
        # # Unicode variant
        # if 'sy' in syllable:
            # syllable = syllable.replace(u'sy', u'x')
        # if 'ee' in syllable:
            # syllable = syllable.replace(u'ee', u'\u00e9')
        # if 'hh' in syllable:
            # syllable = syllable.replace(u'hh', u'\ue000')
        # if 'nn' in syllable:
            # syllable = syllable.replace(u'nn', u'\ue001')
        # if 'th' in syllable:
            # syllable = syllable.replace(u'th', u'\ue002')
        # if 'eu' in syllable:
            # syllable = syllable.replace(u'eu', u'\ue003')
        # if 'ng' in syllable:
            # syllable = syllable.replace(u'ng', u'\ue004')
        # if 'ny' in syllable:
            # syllable = syllable.replace(u'ny', u'\ue005')

        # # If the syllable is not in modified form (e.g. 'ha'), remove the 'a' to make
        # # conversion easier
        # if len(syllable) > 1 and syllable[-1] == 'a':
            # syllable = syllable[:-1]


        # # Append the syllable to the syllables list, then reset
        # syllables.append(syllable)
        # syllable = u''

    # # for consonant followed by vowels h, n, and th, join the separated consonant with the vowel.
    # for index in range(len(syllables)):
        # # To handle accidentally choosing the last item because of the -1 thing
        # prevIndex = index-1 if (index - 1 >= 0) else 0

        # if (len(syllables[prevIndex]) == 1 and syllables[prevIndex]
            # in characterGroups["consonants"]) and (syllables[index] in
            # ("\ue000", "\ue001", "\ue002")):
            # syllables[prevIndex] = ''.join(syllables[prevIndex:index+1])
            # syllables[index] = ''
            # syllables.remove('')


    # return syllables

# Group the syllables into clusters to be converted. The general rule of thumb for Proto-
# Altekhsnan is that a cluster consists either four characters OR three syllables at most.
def cluster_syllables(syllables):
    clusters = []

    # Prioritize clustering based on availability of separators
    if u'=' in syllables:
        clusters = [syl.split(',') for syl in (','.join(syllables)).split('=')]

    # Otherwise, we have to do manual clustering
    else:
        while len(syllables) > 0:
            # If the first three syllables has four or less characters, immediately
            # cluster them.
            if len(''.join(syllables[:3])) <= 4:
                clusters.append(syllables[:3])
                syllables = syllables[3:]
            else:
                clusters.append(syllables[:2])
                syllables = syllables[2:]


    # Delete empty members from the split
    for cluster in clusters:
        while '' in cluster:
            cluster.remove('')

    print("Final syllable clusters: ", clusters)

    return clusters

# This function is intended to perform the actual conversion of the syllables
def convert_cluster(cluster, forScrivener=False):

    # Define dictionaries for glyph replacement
    halfSizeSubstitution = {
        'horizontal' : {
            'a' : '\ue006',
            'e' : '\ue007',
            'i' : '\ue008',
            'o' : '\ue009',
            'u' : '\ue00a',
            'ee' : '\ue00b', '\u00e9' : '\ue00b',
            'hh' : '\ue00c', '\ue000' : '\ue00c',
            'nn' : '\ue00d', '\ue001' : '\ue00d',
            'th' : '\ue00e', '\ue002' : '\ue00e',
            'eu' : '\ue00f', '\ue003' : '\ue00f',

            'b' : '\ue016',
            'c' : '\ue017',
            'd' : '\ue018',
            'f' : '\ue019', 'h' : '\ue019',
            'g' : '\ue01a',
            'j' : '\ue01b',
            'k' : '\ue01c', 'q' : '\ue01c',
            'l' : '\ue01d', 'r' : '\ue01d',
            'm' : '\ue01e',
            'n' : '\ue01f',
            'p' : '\ue020',
            's' : '\ue021',
            'x' : '\ue022', 'sy' : '\ue022',
            't' : '\ue023',
            'v' : '\ue024', 'w' : '\ue024',
            'y' : '\ue025',
            'ng' : '\ue026', '\ue004' : '\ue026',
            'ny' : '\ue027', '\ue005' : '\ue027',
        },

        'vertical' : {
            'e' : '\ue010',
            'i' : '\ue011',
            'o' : '\ue012',
            'u' : '\ue013',
            '-' : '\ue015',
            'ee' : '\ue014', '\u00e9' : '\ue014',
            'hh' : '\ue03a', '\ue000' : '\ue03a',
            'nn' : '\ue03b', '\ue001' : '\ue03b',
            'th' : '\ue03c', '\ue002' : '\ue03c',
            'eu' : '\ue03d', '\ue003' : '\ue03d',

            'b' : '\ue028',
            'c' : '\ue029',
            'd' : '\ue02a',
            'f' : '\ue02b', 'h' : '\ue02b',
            'g' : '\ue02c',
            'j' : '\ue02d',
            'k' : '\ue02e', 'q' : '\ue02e',
            'l' : '\ue02f', 'r' : '\ue02f',
            'm' : '\ue030',
            'n' : '\ue031',
            'p' : '\ue032',
            's' : '\ue033',
            'x' : '\ue034', 'sy' : '\ue034',
            't' : '\ue035',
            'v' : '\ue036', 'w' : '\ue036',
            'y' : '\ue037',
            'ng' : '\ue038', '\ue004' : '\ue038',
            'ny' : '\ue039', '\ue005' : '\ue039',
        },
    }

    thirdSizeSubstitution = {
        'horizontal' : {
            'a' : '\ue05a',
            'e' : '\ue05b',
            'i' : '\ue05c',
            'o' : '\ue05d',
            'u' : '\ue05e',
            'ee' : '\ue05f', '\u00e9' : '\ue05f',
            'hh' : '\ue060', '\ue000' : '\ue060',
            'nn' : '\ue061', '\ue001' : '\ue061',
            'th' : '\ue062', '\ue002' : '\ue062',
            'eu' : '\ue063', '\ue003' : '\ue063',

            'b' : '\ue064',
            'c' : '\ue065',
            'd' : '\ue066',
            'f' : '\ue067', 'h' : '\ue067',
            'g' : '\ue068',
            'j' : '\ue069',
            'k' : '\ue06a', 'q' : '\ue06a',
            'l' : '\ue06b', 'r' : '\ue06b',
            'm' : '\ue06c',
            'n' : '\ue06d',
            'p' : '\ue06e',
            's' : '\ue06f',
            'x' : '\ue072', 'sy' : '\ue072',
            't' : '\ue070',
            'v' : '\ue071', 'w' : '\ue071',
            'y' : '\ue073',
            'ng' : '\ue074', '\ue004' : '\ue074',
            'ny' : '\ue075', '\ue005' : '\ue075',
        },

        'vertical' : {
            'e' : '\ue076',
            'i' : '\ue077',
            'o' : '\ue078',
            'u' : '\ue079',
            '-' : '\ue091',
            'ee' : '\ue07a', '\u00e9' : '\ue07a',
            'hh' : '\ue07b', '\ue000' : '\ue07b',
            'nn' : '\ue07c', '\ue001' : '\ue07c',
            'th' : '\ue07d', '\ue002' : '\ue07d',
            'eu' : '\ue07e', '\ue003' : '\ue07e',

            'b' : '\ue07f',
            'c' : '\ue080',
            'd' : '\ue081',
            'f' : '\ue082', 'h' : '\ue082',
            'g' : '\ue083',
            'j' : '\ue084',
            'k' : '\ue085', 'q' : '\ue085',
            'l' : '\ue086', 'r' : '\ue086',
            'm' : '\ue087',
            'n' : '\ue088',
            'p' : '\ue089',
            's' : '\ue08a',
            'x' : '\ue08c', 'sy' : '\ue08c',
            't' : '\ue08b',
            'v' : '\ue08d', 'w' : '\ue08d',
            'y' : '\ue08e',
            'ng' : '\ue08f', '\ue004' : '\ue08f',
            'ny' : '\ue090', '\ue005' : '\ue090',
        },
    }

    quarterSizeSubstitution = {
        'e' : '\ue03e',
        'i' : '\ue03f',
        'o' : '\ue040',
        'u' : '\ue041',
        '-' : '\ue059',
        'ee' : '\ue042', '\u00e9' : '\ue042',
        'hh' : '\ue043', '\ue000' : '\ue043',
        'nn' : '\ue044', '\ue001' : '\ue044',
        'th' : '\ue045', '\ue002' : '\ue045',
        'eu' : '\ue046', '\ue003' : '\ue046',

        'b' : '\ue047',
        'c' : '\ue048',
        'd' : '\ue049',
        'f' : '\ue04a', 'h' : '\ue04a',
        'g' : '\ue04b',
        'j' : '\ue04c',
        'k' : '\ue04d', 'q' : '\ue04d',
        'l' : '\ue04e', 'r' : '\ue04e',
        'm' : '\ue04f',
        'n' : '\ue050',
        'p' : '\ue051',
        's' : '\ue052',
        'x' : '\ue053', 'sy' : '\ue053',
        't' : '\ue054',
        'v' : '\ue055', 'w' : '\ue055',
        'y' : '\ue056',
        'ng' : '\ue057', '\ue004' : '\ue057',
        'ny' : '\ue058', '\ue005' : '\ue058',
    }

    joined = ''.join(cluster)
    character_count = len(joined)
    syllable_count = len(cluster)
    print("Syllable count in cluster ", cluster, ": ", syllable_count)

    new_syllables = []

    # Check the length of the cluster. Four-character cluster takes priority.
    for syllable in cluster:
        if syllable_count == 3: # Use the third-size
            if bool(re.match('^[' + regex_groups["consonants"] + regex_groups["vowels_all"] + '](?![' + regex_groups["vowels_non_a"] +'])', syllable)):
                new_syllables.append(thirdSizeSubstitution['horizontal'][syllable])
            elif bool(re.match('^[' + regex_groups["consonants"] + '](?=[' + regex_groups["vowels_non_a"] +'])', syllable)):
                new_syllables.append(thirdSizeSubstitution['vertical'][syllable[0]] + thirdSizeSubstitution['vertical'][syllable[1]])
            else:
                pass
        elif syllable_count == 2: # Use either the quarter-size or horizontal half-size
            if bool(re.match('^[' + regex_groups["consonants"] + regex_groups["vowels_all"] + '](?![' + regex_groups["vowels_non_a"] +'])', syllable)):
                new_syllables.append(halfSizeSubstitution['horizontal'][syllable])
            elif bool(re.match('^[' + regex_groups["consonants"] + '](?=[' + regex_groups["vowels_non_a"] +'])', syllable)):
                new_syllables.append(quarterSizeSubstitution[syllable[0]] + quarterSizeSubstitution[syllable[1]])
            else:
                pass
        elif syllable_count == 1:
            if bool(re.match('^[' + regex_groups["consonants"] + regex_groups["vowels_all"] + '](?![' + regex_groups["vowels_non_a"] +'])', syllable)):
                if forScrivener and (syllable in ('\ue000', '\ue001', '\ue002')):
                    if syllable == '\ue000':
                        new_syllables.append('\ue092')
                    elif syllable == '\ue001':
                        new_syllables.append('\ue093')
                    elif syllable == '\ue002':
                        new_syllables.append('\ue094')
                else:
                    new_syllables.append(syllable)
            elif bool(re.match('^[' + regex_groups["consonants"] + '](?=[' + regex_groups["vowels_non_a"] +'])', syllable)):
                new_syllables.append(halfSizeSubstitution['vertical'][syllable[0]] + halfSizeSubstitution['vertical'][syllable[1]])
            else:
                pass


    unicode_code_points = []

    # For the Unicode representation
    for ch in "".join(new_syllables):
        unicode_code_points.append(
            str(
                hex(ord(ch))
            ).replace('0x', '\\u')
        )

    return ("".join(new_syllables), "".join(unicode_code_points))


# The actual system
def converter(sentence, forScrivener=False):
    # start = timer()
    words = []
    syllables = []
    clusters = []

    final_string = u''
    unicode_code_points = u''

    # Separate the sentence into words.
    words = separate_words(sentence)

    # For each word, separate into syllables, then group into clusters
    for word in words:
        syllables = separate_syllables_regex(word)
        clusters = cluster_syllables(syllables)

        # Finally, generate the converted word along with their Unicode code points
        for cluster in clusters:
            tmp = convert_cluster(cluster, forScrivener)
            final_string += tmp[0]
            final_string += "==" # FIXME: dirty fix for the text display due to the font bug
            unicode_code_points += tmp[1]

        # Add space if it's not the end of the sentence
        if word != words[-1]:
            final_string += u" "
            # unicode_code_points += "\\u0020"
            unicode_code_points += "\u0020"

    # stop = timer()
    # print("Time elapsed: " + str(stop-start))

    return final_string, unicode_code_points

if __name__ == '__main__':
    while True:
        a = input("Enter a word: ")
        b = converter(a)
        print(b)
        print("\n")
