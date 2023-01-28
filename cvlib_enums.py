from enum import Enum


class ColorsEnum(str, Enum):
    RED = 'red'
    GREEN = 'green'
    BLUE = 'blue'
    BLACK = 'black'
    WHITE = 'white'
    YELLOW = 'yellow'
    MAGENTA = 'magenta'
    CYAN = 'cyan'
    PINK = 'pink'
    BROWN = 'brown'


class StatisticEnum(str, Enum):
    MEAN = 'mean'
    MEDIAN = 'median'
    SUM = 'muc'
    MAX = 'max'
    MIN = 'min'
    STDEV = 'stdev'
    VAR = 'var'
    AREA = 'area'
    VARBC = 'varbc'


class ShapeEnum(str, Enum):
    DISK = 'disk'
    SQUARE = 'square'


class PSFTypeEnum(str, Enum):
    BESSEL = 'bessel'
    GAUSS = 'gauss'
    EXP = 'exp'
    CONFOCAL_BESSEL = 'confocal_bessel'
    ONES = 'ones'


class Connectivity3dEnum(str, Enum):
    SIX = '6'
    TWENTY_SIX = '26'


class ConnectivityEnum(str, Enum):
    FOUR = '4'
    EIGHT = '8'


class DistanceTransformEnum(str, Enum):
    THREE = '3'
    FIVE = '5'
    SEVEN = '7'


class SoloEnum(str, Enum):
    NUCLEAR = 'nuclear'
    ENERGRID = 'energid'
    OUTNUC = 'outnuc'


class APEnum(str, Enum):
    A = 'A'
    P = 'P'


class AndifFunction_typeEnum(str, Enum):
    exp = 'exp'
    frac = 'frac'


class Plot_spFunctionEnum(str, Enum):
    log = 'log'
    eqn = 'eqn'


class SselectRuleEnum(str, Enum):
    accept = 'accept'
    reject = 'reject'


class ThresholdMethodEnum(str, Enum):
    plain = 'plain'
    otsu = 'otsu'


class VtxtFormatEnum(str, Enum):
    xyz = 'xyz'
    vrml_sphere = 'vrml_sphere'


class Surf3dFormatEnum(str, Enum):
    vtk = 'vtk'
    oogl = 'oogl'
    ooglb = 'ooglb'
    gts = 'gts'


class Grid3d_iTypeEnum(str, Enum):
    cartesian = 'cartesian'
    elliptical = 'elliptical'


class Surf3dfullFunctionEnum(str, Enum):
    cartesian = 'cartesian'
    tetra = 'tetra'
    tetra_bounded = 'tetra_bounded'
    tetra_bcl = 'tetra_bcl'


class MlsregTypeEnum(str, Enum):
    affine = 'affine'
    similar = 'similar'
    rigid = 'rigid'


