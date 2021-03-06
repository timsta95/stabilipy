BUTTRESS, GRAVITY = 'Platedam', 'Gravitasjonsdam'
ICE = 'Islast'
VT = 'Vanntrykk'
VV = 'Vannvekt'
OV = 'Overtopping'
OP = 'Opptrykk'
EV = 'Egenvekt'
LOADS = (ICE, VT, VV, OV, OP, EV)
INCREMENT = 0.05
GL, VE, SI = 'Glidning', 'Velting', 'Sikkerhet'
LEVELS = ('HRV + is', 'DFV', 'MFV')
OK, NOT_OK = 'ok', 'ikke ok'
GL_DICT = {GRAVITY: (1.5, 1.5, 1.1), BUTTRESS: (1.4, 1.4, 1.1)}
VE_DICT = {GRAVITY: (1/12, 1/12, 1/6), BUTTRESS: (1.4, 1.4, 1.3)}
ICE_LOADS = (100, 0, 0)
SYMBOL_DICT = dict(zip(LOADS, ('>', '>', 'v', 'v', '^')))
COLOR_DICT = dict(zip(LOADS, ['blue'] * 5))
Y_LABEL = 'Høyde over havet [m]'
IN = 'i'
CALC = 'er beregnet som'
ANALYSIS = 'Stabilitetsberegning'