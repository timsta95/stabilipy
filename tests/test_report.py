from stabilipy import report
from example_dam import dam as ex_dam, levels as ex_levels
from timeit import default_timer as timer

start = timer()
r = report.Report(ex_dam, ex_levels)
directory = '../test'
r.create_report(directory)
print(f'finished after {round(timer() - start, 5)} seconds')