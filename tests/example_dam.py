from context import stabilipy

from stabilipy import segment, pillar, dam
from shapely.geometry import Polygon

"""
This script is used to define the dam construction.
The script expects a list of pillars to be passed to a Dam instance and a list
of water levels (HRV, DFV, MFV). See pillar.py for definition of pillars.
"""

#help functions and variables
y_new = 273 #faelt fyllda ned till {y_new} m oever havet
x_left = -((274.85 - y_new) / 1.3188 - 0.168) #help function (polygon vertex)
x_right = (273.833 - y_new) * 0.35113 + 1.28 #help function (polygon vertex)
    
start = 0 #first axis starts at 0 m
start_fl = -2.025 #help variable for axis definition
start_fr = 2.025 #help variable for axis definition
axis = 6.1 #axis length [m]
concrete = 23.54 #specific weight concrete [kn/m3]
half_f = 2.05 #width of stoept betong (= 0.5 * clear width between pillars)
width_p = 2. #pillar width
phi = 50 #friction angle [deg]
width_cr = 1.4 #width of dam crest
    
#define dam geometries
plate_poly = Polygon(((-16.688, 254), (0, 275.062),
                      (0, 275.870),
                      (0, 276.070), (0.2, 276.070),
                      (0.2, 275.05), (1.4, 275.05),
                      (1.4, 274.85), (0.168, 274.85),
                      (-16.226, 254)))
pilar_poly = Polygon(((-16.226, 254), (0.168, 274.85),
                      (1.28, 274.85), (1.28, 273.833),
                      (5.852, 260.812), (5.852, 254)))
filled_drain = Polygon(((x_left, y_new), (0.168, 274.85),
                       (1.28, 274.85), (1.28, 273.833),
                       (x_right, y_new)))
    
#contact points dam - rock (left = upstream, right =  downstream)
left = [261.768, 258.346, 256.309, 255.312, 254.543,
        254.776, 255.947, 257.125, 258.310, 259.497,
        260.676, 261.844, 263.014, 264.172, 265.326,
        266.484, 267.683, 268.703, 270.342, 272.929]
right = [265.996, 261.150, 261.000, 260.812, 260.871,
         260.839, 260.726, 261.132, 262.089, 263.811,
         265.370, 267.479, 267.785, 267.835, 268.052,
         268.100, 268.168, 269.409, 270.850, 273.085]

#build pillars
pillars = []
for i in range(0, 20):
    
    #contact points dam - rock
    l, r = left[i], right[i]
    
    #axes
    start_i = start + i * axis
    start_fl_i = start_fl + i * axis
    start_fr_i = start_fr + i * axis
    
    #name
    name = str(i + 1)
    
    #segments
    plate = segment.Segment(
        plate_poly, axis, concrete, start_i, f'Plate{name}'
        )
    pilar = segment.Segment(
        pilar_poly, width_p, concrete, start_i, f'Pilar{name}'
        )
    
    if i < 19:
        fill_l = segment.Segment(
            filled_drain, half_f, concrete, start_fl_i, f'Fill{name}_l'
            )
        fill_r = segment.Segment(
            filled_drain, half_f, concrete, start_fr_i, f'Fill{name}_r'
            )
        dam_type = 'Platedam'
    else:
        fill_l = segment.Segment(
            pilar_poly, half_f, concrete, start_fl_i, f'Fill{name}_l'
            )
        fill_r = segment.Segment(
            pilar_poly, half_f, concrete, start_fr_i, f'Fill{name}_r'
            )
        dam_type = 'Gravitasjonsdam'
    
    #combine segments
    p = pillar.Pillar(
        [plate, pilar, fill_l, fill_r],
        l, r, width_cr, phi, dam_type, f'Pilar {name}'
    )
    
    pillars.append(p)

#build dam
dam = dam.Dam(pillars)

#define water levels
levels = [275, 275.81, 276.33]