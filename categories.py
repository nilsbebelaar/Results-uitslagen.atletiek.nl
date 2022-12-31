# List of all possible categories in Volta, and their corresponing gender
def category_to_gender(category):
    lookup = {
        'U8J': 'male',
        'U8M': 'female',
        'U9J': 'male',
        'U9M': 'female',
        'U10J': 'male',
        'U10M': 'female',
        'U12J': 'male',
        'U12M': 'female',
        'U12-1J': 'male',
        'U12-1M': 'female',
        'U12-2J': 'male',
        'U12-2M': 'female',
        'U14J': 'male',
        'U14M': 'female',
        'U16J': 'male',
        'U16M': 'female',
        'U18M': 'male',
        'U18V': 'female',
        'U20V': 'female',
        'U20M': 'male',
        'U14-1J': 'male',
        'U14-1M': 'female',
        'U14-2J': 'male',
        'U14-2M': 'female',
        'U16-1J': 'male',
        'U16-1M': 'female',
        'U16-2J': 'male',
        'U16-2M': 'female',
        'SENV': 'female',
        'SENM': 'male',
        'U23M': 'male',
        'U23V': 'female',
        'MASTERSM': 'male',
        'MASTERSV': 'female',
        'M35': 'male',
        'V35': 'female',
        'M40': 'male',
        'V40': 'female',
        'M45': 'male',
        'V45': 'female',
        'M50': 'male',
        'V50': 'female',
        'M55': 'male',
        'V55': 'female',
        'M60': 'male',
        'V60': 'female',
        'V65': 'female',
        'M65': 'male',
        'M70': 'male',
        'V70': 'female',
        'M75': 'male',
        'V75': 'female',
        'M80': 'male',
        'V80': 'female',
        'M85': 'male',
        'V85': 'female',
        'M90': 'male',
        'V90': 'female',
        'M95': 'male',
        'V95': 'female',
        'M100': 'male',
        'V100': 'female',
        'T/F12M': 'male',
        'T/F11M': 'male',
        'T/F11V': 'female',
        'T/F12V': 'female',
        'T/F13M': 'male',
        'T/F13V': 'female',
        'T/F20M': 'male',
        'T/F20V': 'female',
        'T/F31M': 'male',
        'T/F31V': 'female',
        'T/F32M': 'male',
        'T/F32V': 'female',
        'T/F33M': 'male',
        'T/F33V': 'female',
        'T/F35M': 'male',
        'T/F34V': 'female',
        'T/F35M': 'male',
        'T/F35V': 'female',
        'T/F36M': 'male',
        'T/F36V': 'female',
        'T/F37M': 'male',
        'T/F37V': 'female',
        'T/F38M': 'male',
        'T/F38V': 'female',
        'T/F40M': 'male',
        'T/F40V': 'female',
        'T/F4M': 'male',
        'T/F41V': 'female',
        'T/F42M': 'male',
        'T/F42V': 'female',
        'T/F43M': 'male',
        'T/F43V': 'female',
        'T/F44M': 'male',
        'T/F44V': 'female',
        'T/F43M': 'male',
        'T/F45V': 'female',
        'T/F46M': 'male',
        'T/F46V': 'female',
        'T/F47M': 'male',
        'T/F47V': 'female',
        'T/F51M': 'male',
        'T/F51V': 'female',
        'T/F52M': 'male',
        'T/F52V': 'female',
        'T/F53M': 'male',
        'T/F53V': 'female',
        'T/F54M': 'male',
        'T/F54V': 'female',
        'F55M': 'male',
        'F55V': 'female',
        'F56M': 'male',
        'F56V': 'female',
        'F57M': 'male',
        'F57V': 'female',
        'T/F61M': 'male',
        'T/F61V': 'female',
        'T/F62M': 'male',
        'T/F62V': 'female',
        'T/F63M': 'male',
        'T/F63V': 'female',
        'T/F64M': 'male',
        'T/F64V': 'female',
        'GJJ': 'male',
        'GJM': 'female',
        'GPJ': 'male',
        'GPM': 'female',
        'SJJ': 'male',
        'SJM': 'female',
        'SPJ': 'male',
        'SPM': 'female',
        'VBJJ': 'male',
        'VBJM': 'female',
        'VBPJ': 'male',
        'VBPM': 'female',
        'GMM': 'male',
        'GMV': 'female',
        'GSM': 'male',
        'GSV': 'female',
        'SPM': 'male',
        'SPV': 'female',
        'SSM': 'male',
        'SSV': 'female',
        'VBMM': 'male',
        'VBMV': 'female',
        'VBSM': 'male',
        'VBSV': 'female',
        'LBM': 'male',
        'LBV': 'female',
        'RRJJ': 'male',
        'RRJM': 'female',
        'RRPJ': 'male',
        'RRPM': 'female',
        'RRSM': 'male',
        'RRSV': 'female',
        'RecrM': 'male',
        'RecrV': 'female',
        'RecrPJ': 'male',
        'RecrPM': 'female',
        'RecrJJ': 'male',
        'RecrJM': 'female',
        'U8Mix': 'mixed',
        'U9Mix': 'mixed',
        'U10Mix': 'mixed',
        'U12Mix': 'mixed',
        'U14Mix': 'mixed',
        'U16Mix': 'mixed',
        'U18Mix': 'mixed',
        'U20Mix': 'mixed',
        'SenMix': 'mixed',
        'MasMix': 'mixed'
    }
    if category in lookup:
        return lookup[category]
    else:
        return 'Unknown'


# List of hurdle heights per category
def category_to_hurdleheight(category, distance='', birthyear=''):
    distance = str(distance)
    birthyear = str(birthyear)
    category = category.replace('-1', '').replace('-2', '')
    if distance == '200' or distance == '300' or distance == '400':
        lookup_value = category + '-' + distance
    else:
        lookup_value = category

    lookup = {
        'U14J': '76cm',  # WR p.289
        'U16J': '84cm',
        'U14J-300': '76cm',
        'U16J-300': '76cm',

        'U14M': '76cm',
        'U16M': '76cm',
        'U14M-300': '76cm',
        'U16M-300': '76cm',


        'U18M': '91cm',  # WR p.124
        'U20M': '99cm',
        'U23M': '107cm',
        'SENM': '107cm',
        'U18M-400': '84cm',
        'U20M-400': '91cm',
        'U23M-400': '91cm',
        'SENM-400': '91cm',

        'U18V': '76cm',
        'U20V': '84cm',
        'U23V': '84cm',
        'SENV': '84cm',
        'U18V-400': '76cm',
        'U20V-400': '76cm',
        'U23V-400': '76cm',
        'SENV-400': '76cm',


        'M35': '99cm',  # WR p.274/275
        'M40': '99cm',
        'M45': '99cm',
        'M50': '91cm',
        'M55': '91cm',
        'M60': '84cm',
        'M65': '84cm',
        'M70': '76cm',
        'M75': '76cm',
        'M80': '69cm',
        'M85': '69cm',
        'M90': '69cm',
        'M95': '69cm',
        'M100': '69cm',
        'M35-400': '91cm',
        'M40-400': '91cm',
        'M45-400': '91cm',
        'M50-400': '84cm',
        'M55-400': '84cm',
        'M60-300': '76cm',
        'M65-300': '76cm',
        'M70-300': '69cm',
        'M75-300': '69cm',
        'M80-200': '69cm',
        'M85-200': '69cm',
        'M90-200': '69cm',
        'M95-200': '69cm',
        'M100-200': '69cm',

        'V35': '84cm',
        'V40': '76cm',
        'V45': '76cm',
        'V50': '76cm',
        'V55': '76cm',
        'V60': '69cm',
        'V65': '69cm',
        'V70': '69cm',
        'V75': '69cm',
        'V80': '69cm',
        'V85': '69cm',
        'V90': '69cm',
        'V95': '69cm',
        'V100': '69cm',
        'V35-400': '76cm',
        'V40-400': '76cm',
        'V45-400': '76cm',
        'V50-300': '76cm',
        'V55-300': '76cm',
        'V60-300': '69cm',
        'V65-300': '69cm',
        'V70-200': '69cm',
        'V75-200': '69cm',
        'V80-200': '69cm',
        'V85-200': '69cm',
        'V90-200': '69cm',
        'V95-200': '69cm',
        'V100-200': '69cm'
    }
    if lookup_value in lookup:
        return ' ' + lookup[lookup_value]
    else:
        return ' ' + category + ' ' + birthyear


# List of weights per category
def category_to_weight(event, category, birthyear=''):
    birthyear = str(birthyear)
    category = category.replace('-1', '').replace('-2', '')

    if event == 'kogelstoten':
        event = 'kogel'
    elif event == 'kogelslingeren':
        event = 'kogel'
    elif event == 'discuswerpen':
        event = 'discus'
    elif event == 'speerwerpen':
        event = 'speer'
    elif event == 'gewichtwerpen':
        event = 'gewicht'

    lookup = {
        'U8J': {'kogel': '1 kg'},  # WR p.297/298
        'U9J': {'kogel': '1 kg'},
        'U10J': {'kogel': '2 kg'},
        'U12J': {'kogel': '2 kg'},

        'U8M': {'kogel': '1 kg'},
        'U9M': {'kogel': '1 kg'},
        'U10M': {'kogel': '2 kg'},
        'U12M': {'kogel': '2 kg'},


        'U14J': {'kogel': '3 kg', 'discus': '1 kg', 'speer': '400 g'},  # WR p.290/291
        'U16J': {'kogel': '4 kg', 'discus': '1 kg', 'speer': '600 g'},

        'U14M': {'kogel': '2 kg', 'discus': '0,75 kg', 'speer': '400 g'},
        'U16M': {'kogel': '3 kg', 'discus': '1 kg', 'speer': '500 g'},


        'U18M': {'kogel': '5 kg', 'discus': '1,5 kg', 'speer': '700 g'},  # WR p.168
        'U20M': {'kogel': '6 kg', 'discus': '1,75 kg', 'speer': '800 g'},
        'U23M': {'kogel': '7,26 kg', 'discus': '2 kg', 'speer': '800 g'},
        'SENM': {'kogel': '7,26 kg', 'discus': '2 kg', 'speer': '800 g'},

        'U18V': {'kogel': '3 kg', 'discus': '1 kg', 'speer': '500 g'},
        'U20V': {'kogel': '4 kg', 'discus': '1 kg', 'speer': '600 g'},
        'U23V': {'kogel': '4 kg', 'discus': '1 kg', 'speer': '600 g'},
        'SENV': {'kogel': '4 kg', 'discus': '1 kg', 'speer': '600 g'},


        'M35':  {'kogel': '7,26 kg', 'discus': '2 kg', 'speer': '800 g', 'gewicht': '15,88 kg'},  # WR p.277
        'M40':  {'kogel': '7,26 kg', 'discus': '2 kg', 'speer': '800 g', 'gewicht': '15,88 kg'},
        'M45':  {'kogel': '7,26 kg', 'discus': '2 kg', 'speer': '800 g', 'gewicht': '15,88 kg'},
        'M50':  {'kogel': '6 kg', 'discus': '1,5 kg', 'speer': '700 g', 'gewicht': '11,34 kg'},
        'M55':  {'kogel': '6 kg', 'discus': '1,5 kg', 'speer': '700 g', 'gewicht': '11,34 kg'},
        'M60':  {'kogel': '5 kg', 'discus': '1 kg', 'speer': '600 g', 'gewicht': '9,08 kg'},
        'M65':  {'kogel': '5 kg', 'discus': '1 kg', 'speer': '600 g', 'gewicht': '9,08 kg'},
        'M70':  {'kogel': '4 kg', 'discus': '1 kg', 'speer': '500 g', 'gewicht': '7,26 kg'},
        'M75':  {'kogel': '4 kg', 'discus': '1 kg', 'speer': '500 g', 'gewicht': '7,26 kg'},
        'M80':  {'kogel': '3 kg', 'discus': '1 kg', 'speer': '400 g', 'gewicht': '5,45 kg'},
        'M85':  {'kogel': '3 kg', 'discus': '1 kg', 'speer': '400 g', 'gewicht': '5,45 kg'},
        'M90':  {'kogel': '3 kg', 'discus': '1 kg', 'speer': '400 g', 'gewicht': '5,45 kg'},
        'M95':  {'kogel': '3 kg', 'discus': '1 kg', 'speer': '400 g', 'gewicht': '5,45 kg'},
        'M100': {'kogel': '3 kg', 'discus': '1 kg', 'speer': '400 g', 'gewicht': '5,45 kg'},

        'V35':  {'kogel': '4 kg', 'discus': '1 kg', 'speer': '600 g', 'gewicht': '9,08 kg'},
        'V40':  {'kogel': '4 kg', 'discus': '1 kg', 'speer': '600 g', 'gewicht': '9,08 kg'},
        'V45':  {'kogel': '4 kg', 'discus': '1 kg', 'speer': '600 g', 'gewicht': '9,08 kg'},
        'V50':  {'kogel': '3 kg', 'discus': '1 kg', 'speer': '500 g', 'gewicht': '7,26 kg'},
        'V55':  {'kogel': '3 kg', 'discus': '1 kg', 'speer': '500 g', 'gewicht': '7,26 kg'},
        'V60':  {'kogel': '3 kg', 'discus': '1 kg', 'speer': '500 g', 'gewicht': '5,45 kg'},
        'V65':  {'kogel': '3 kg', 'discus': '1 kg', 'speer': '500 g', 'gewicht': '5,45 kg'},
        'V70':  {'kogel': '3 kg', 'discus': '1 kg', 'speer': '500 g', 'gewicht': '5,45 kg'},
        'V75':  {'kogel': '2 kg', 'discus': '0,75 kg', 'speer': '400 g', 'gewicht': '4 kg'},
        'V80':  {'kogel': '2 kg', 'discus': '0,75 kg', 'speer': '400 g', 'gewicht': '4 kg'},
        'V85':  {'kogel': '2 kg', 'discus': '0,75 kg', 'speer': '400 g', 'gewicht': '4 kg'},
        'V90':  {'kogel': '2 kg', 'discus': '0,75 kg', 'speer': '400 g', 'gewicht': '4 kg'},
        'V95':  {'kogel': '2 kg', 'discus': '0,75 kg', 'speer': '400 g', 'gewicht': '4 kg'},
        'V100': {'kogel': '2 kg', 'discus': '0,75 kg', 'speer': '400 g', 'gewicht': '4 kg'}
    }
    if category in lookup:
        if event in lookup[category]:
            return ' ' + lookup[category][event]

    return ' ' + category + ' ' + birthyear
