from stabilipy import export
from example_dam import dam as ex_dam, levels as ex_levels
from timeit import default_timer as timer

start = timer()
e = export.Export(ex_dam, ex_levels)
directory = '../test'
e.export(directory)
print(f'finished after {round(timer() - start, 5)} seconds')