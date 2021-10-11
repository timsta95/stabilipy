from stabilipy import dam
from example_dam import dam as ex_dam

pillars = ex_dam.pillars
pillar0, pillar1, pillar2 = pillars[:3]

# test __str__()
print(pillar0)

# test __add__()
pillars_added = pillar0 + pillar1 + pillar2
print(pillars_added)
new_dam = dam.Dam(pillars_added)
print(new_dam)