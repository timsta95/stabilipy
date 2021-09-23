from dataclasses import dataclass
from functools import cached_property
from stabilipy import stability as stb, dam, settings

class SortedLevels:
    
    @property
    def sorted_levels(self):
        return sorted(self.levels)

    @staticmethod
    def compare(value, threshold1, threshold2 = None):
        ok, not_ok = settings.OK, settings.NOT_OK
        if threshold2:
            if value >= threshold1 and value <= threshold2:
                return ok
            else:
                return not_ok
        else:
            if value >= threshold1:
                return ok
            else:
                return not_ok

@dataclass
class Evaluation(SortedLevels):
    dam: dam.Dam
    levels: list

    @cached_property
    def stability(self):
        return [stb.Stability(self.dam, level, ice) for level, ice in zip(
            self.sorted_levels, settings.ICE_LOADS)]

    @property
    def glidning(self):
        gl_list = [i.glidning for i in self.stability]
        results = []
        for idx, (gl, name) in enumerate(zip(gl_list, settings.LEVELS)):
            for gl_i, p in zip(gl, self.dam.pillars):
                safety = settings.GL_DICT[p.dam_type][idx]
                result = self.compare(gl_i, safety)
                results.append([
                    settings.GL, name, p.name, round(gl_i, 2), safety, result])
        return results

    @property
    def velting(self):
        vm_list, vr_list = zip(
            *[(i.velting_moment, i.velting_resultant) for i in self.stability])
        results = []
        for idx, (vm, vr, name) in enumerate(
            zip(vm_list, vr_list, settings.LEVELS)):
            for vm_i, vr_i, p in zip(vm, vr, self.dam.pillars):
                safety = settings.VE_DICT[p.dam_type][idx]
                if p.dam_type == settings.GRAVITY:
                    v_i = vr_i
                    dist = p.right_contact.x - p.left_contact.x
                    min_dist = dist * safety
                    max_dist = dist - min_dist
                    result = self.compare(v_i, min_dist, max_dist)
                    safety = f'{round(min_dist, 2)} - {round(max_dist, 2)}'
                elif p.dam_type == settings.BUTTRESS:
                    v_i = vm_i
                    result = self.compare(v_i, safety)
                results.append([
                    settings.VE, name, p.name, round(v_i, 2), safety, result])
        return results     