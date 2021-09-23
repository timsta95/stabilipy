import os
from dataclasses import dataclass
from typing import ClassVar
import pandas as pd
from  stabilipy import stability as stab, evaluation as eval, dam, settings

class Directory:

    @staticmethod
    def verify_directory(directory):
        if not os.path.exists(directory):
            os.makedirs(directory)
        return directory

@dataclass
class Export(Directory, eval.SortedLevels):
    dam: dam.Dam
    levels: list
    level_names: ClassVar[list] = settings.LEVELS

    @staticmethod
    def save_data(directory, level, unique, idx, data):
        path = f'{directory}/{level}_{unique}.xlsx' 
        pd.DataFrame(data[idx]).to_excel(path, index=False, header=False)

    def export(self, directory):
        verified_dir = self.verify_directory(directory)
        segments = [stab.Stability(self.dam, l, i).segments for l, i in zip(
            self.sorted_levels, settings.ICE_LOADS)]
        filtered = [[i for i in segs if i.load > 0] for segs in segments]
        names, axes, weights, widths, x, y = list(zip(*[list(zip(*[(
            i.name, i.axis, i.spec_weight, i.width, i.x_coords,i.y_coords
            ) for i in segs])) for segs in filtered]))
        ext = ('data', 'x', 'y')
        information = [
            list(zip(*i)) for i in list(zip(*(names, axes, weights, widths)))]
        data = (information, x, y)
        for idx, name in enumerate(self.level_names):
            for e, d in zip(ext, data):
                self.save_data(verified_dir, name, e, idx, d)
        print(f'Export finished, files are located in {verified_dir}')      