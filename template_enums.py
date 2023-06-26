enums_numbers_to_str = {
    1: 'ONE',
    2: 'TWO',
    3: 'THREE',
    4: 'FOUR',
    5: 'FIVE',
    6: 'SIX',
    7: 'SEVEN',
    8: 'EIGHT',
    9: 'NINE',
    26: 'TWENTY_SIX'
}

templates_enums_body = {
    'ColorsEnum': "class ColorsEnum(str, Enum):\n"
                  "    RED = 'red'\n"
                  "    GREEN = 'green'\n"
                  "    BLUE = 'blue'\n"
                  "    BLACK = 'black'\n"
                  "    WHITE = 'white'\n"
                  "    YELLOW = 'yellow'\n"
                  "    MAGENTA = 'magenta'\n"
                  "    CYAN = 'cyan'\n"
                  "    PINK = 'pink'\n"
                  "    BROWN = 'brown'\n\n\n",
    'StatisticEnum': "class StatisticEnum(str, Enum):\n"
                     "    MEAN = 'mean'\n"
                     "    MEDIAN = 'median'\n"
                     "    SUM = 'muc'\n"
                     "    MAX = 'max'\n"
                     "    MIN = 'min'\n"
                     "    STDEV = 'stdev'\n"
                     "    VAR = 'var'\n"
                     "    AREA = 'area'\n"
                     "    VARBC = 'varbc'\n\n\n",
    'ShapeEnum': "class ShapeEnum(str, Enum):\n"
                 "    DISK = 'disk'\n"
                 "    SQUARE = 'square'\n\n\n",
    'PSFTypeEnum': "class PSFTypeEnum(str, Enum):\n"
                   "    BESSEL = 'bessel'\n"
                   "    GAUSS = 'gauss'\n"
                   "    EXP = 'exp'\n"
                   "    CONFOCAL_BESSEL = 'confocal_bessel'\n"
                   "    ONES = 'ones'\n\n\n",
    'Connectivity3dEnum': "class Connectivity3dEnum(str, Enum):\n"
                          "    SIX = '6'\n"
                          "    TWENTY_SIX = '26'\n\n\n",
    'ConnectivityEnum': "class ConnectivityEnum(str, Enum):\n"
                        "    FOUR = '4'\n"
                        "    EIGHT = '8'\n\n\n",
    'DistanceTransformEnum': "class DistanceTransformEnum(str, Enum):\n"
                             "    THREE = '3'\n"
                             "    FIVE = '5'\n"
                             "    SEVEN = '7'\n\n\n",
    'SoloEnum': "class SoloEnum(str, Enum):\n"
                "    NUCLEAR = 'nuclear'\n"
                "    ENERGRID = 'energid'\n"
                "    OUTNUC = 'outnuc'\n\n\n",
    'APEnum': "class APEnum(str, Enum):\n"
              "    A = 'A'\n"
              "    P = 'P'\n\n\n"
}

templates_enums = {
    ('red', 'green', 'blue', 'black', 'white', 'yellow', 'magenta', 'cyan', 'pink', 'brown'):
        {
            'name': 'ColorsEnum',
            'default_value': 'RED',
            'body': templates_enums_body['ColorsEnum']
         },
    ('mean', 'median', 'muc', 'max', 'min', 'stdev', 'var', 'area', 'varbc'):
        {
            'name': 'StatisticEnum',
            'default_value': 'MEAN',
            'body': templates_enums_body['StatisticEnum']
         },
    ('disk', 'square'):
        {
            'name': 'ShapeEnum',
            'default_value': 'DISK',
            'body': templates_enums_body['ShapeEnum']
         },
    ('bessel', 'gauss', 'exp', 'confocal_bessel', 'ones'):
        {
            'name': 'PSFTypeEnum',
            'default_value': 'BESSEL',
            'body': templates_enums_body['PSFTypeEnum']
        },
    ('6', '26'):
        {
            'name': 'Connectivity3dEnum',
            'default_value': 'SIX',
            'body': templates_enums_body['Connectivity3dEnum']
        },
    ('4', '8'):
        {
            'name': 'ConnectivityEnum',
            'default_value': 'FOUR',
            'body': templates_enums_body['ConnectivityEnum']
        },
    ('3', '5', '7'):
        {
            'name': 'DistanceTransformEnum',
            'default_value': 'THREE',
            'body': templates_enums_body['DistanceTransformEnum']
        },
    ('nuclear', 'energid', 'outnuc'):
        {
            'name': 'SoloEnum',
            'default_value': 'NUCLEAR',
            'body': templates_enums_body['SoloEnum']
        },
    ('A', 'P'):
        {
            'name': 'APEnum',
            'default_value': 'A',
            'body': templates_enums_body['APEnum']
        }
}