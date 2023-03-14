import math
from dataclasses import dataclass
from functools import cached_property
from stabilipy import load, dam

@dataclass
class Stability:
    dam: dam.Dam
    level: float
    ice: float

    @cached_property
    def basic(self):
        return [load.Islast(self.dam, self.level, self.ice),
            load.Vanntrykk(self.dam, self.level),
            load.Vannvekt(self.dam, self.level),
            load.Overtopping(self.dam, self.level),
            load.Opptrykk(self.dam, self.level),
            load.Egenvekt(self.dam)]

    @cached_property
    def basic_segments(self):
        return [i.segments for i in self.basic]

    @property
    def segments(self):
        ice, vt, vv, ov, op, ev = self.basic_segments
        loads = [ice, vt, vv, ov] + op + ev
        return [s for l in loads for s in l]

    @property
    def segments_per_pillar(self):
        return [[ice, vt, vv, ov] + op + ev for ice, vt, vv, ov, op, ev in zip(
            *self.basic_segments)]

    @cached_property
    def loads(self):
        return [i.loads for i in self.basic]

    @property
    def horizontal_loads(self):
        ice, vt, _, _, _, _ = self.loads
        return [a + b for a, b in zip(ice, vt)]

    @property
    def vertical_loads(self):
        _, _, vv, ov, op, ev = self.loads
        return [a + b + c + d for a, b, c, d in zip(vv, ov, op, ev)]

    @cached_property
    def moment(self):
        pts = [p.right_contact for p in self.dam.pillars]
        ice, vt, vv, ov, op, ev = self.loads
        ice_c, vt_c, vv_c, ov_c, op_c, ev_c = [i.centroids for i in self.basic]
        moments = []
        for idx, pt in enumerate(pts):
            ice_m = ice[idx] * (ice_c[idx].y - pt.y)
            vt_m = vt[idx] * (vt_c[idx].y - pt.y)
            vv_m = vv[idx] * (pt.x - vv_c[idx].x)
            ov_m = ov[idx] * (pt.x - ov_c[idx].x)
            op_m = op[idx] * (pt.x - op_c[idx].x)
            ev_m = ev[idx] * (pt.x - ev_c[idx].x)
            moments.append([ice_m, vt_m, vv_m, ov_m, op_m, ev_m])
        return moments

    @property
    def glidning(self):
        alphas, phis = zip(*[(p.bottom_angle, p.phi) for p in self.dam.pillars])
        ice_load, vt_load, vv_load, ov_load, op_load, ev_load = self.loads
        glidning = []
        for (alpha, phi, ice, vt, vv, ov, op, ev) in zip(
                alphas, phis, ice_load, vt_load,
                vv_load, ov_load, op_load, ev_load):
            fh = ice + vt
            fv = vv + ov + op + ev
            glidning.append(
                abs((fv * math.tan(math.radians(phi + alpha))) / fh))
        return glidning

    @property
    def velting_resultant(self):
        return [sum(m) / fv for m, fv in zip(
            self.moment, self.vertical_loads)]

    @property
    def velting_moment(self):
        s_list = []
        for m_list in self.moment:
            m_pos = sum([m for m in m_list if m >= 0])
            m_neg = sum([m for m in m_list if m < 0])
            s_list.append(abs(m_pos / m_neg)) 
        return s_list  