from dataclasses import dataclass
from typing import ClassVar
from functools import cached_property
from shapely.geometry import (
    Point, MultiPoint, LineString, MultiLineString, Polygon)
from shapely.ops import unary_union
from stabilipy import segment, dam, settings

class LoadMethods:

    @property
    def segments(self):
        pass

    @property
    def centroids(self):
        return [i.centroid for i in self.segments]

    @property
    def loads(self):
        return [i.load for i in self.segments]

@dataclass
class BaseLoad:
    dam: dam.Dam

@dataclass
class Load(BaseLoad):
    level: float
    g_water: ClassVar[float] = 9.81

@dataclass
class Vannvekt(Load, LoadMethods):
    @cached_property
    def segments(self):
        vv_list = []
        for p in self.dam.pillars:
            height = min(p.bounding_box['maxy'], self.level)
            box = Polygon([
                (p.left_contact.x, height),
                (p.bounding_box['maxx'] + 1, height),
                (p.bounding_box['maxx'] + 1, p.left_contact.y),
                p.left_contact])
            try:
                poly = box.difference(p.union)[0]
            except:
                poly = Polygon([
                    (p.left_contact.x - 1, p.left_contact.y),
                    p.left_contact,
                    (p.left_contact.x + 1, p.left_contact.y)])
            if self. level > p.bounding_box['maxy'] and poly.area > 0:
                poly2 = Polygon([
                    (p.left_contact.x, p.highest_point.y),
                    (p.left_contact.x, self.level),
                    (p.highest_point.x, self.level),
                    p.highest_point])
                poly = unary_union([poly, poly2])
            vv_list.append(segment.Segment(
                poly, p.max_depth, self.g_water, p.axis, settings.VV))
        return vv_list

@dataclass
class Vanntrykk(Load, LoadMethods):
    @cached_property
    def segments(self):
        vt_list = []
        for p in self.dam.pillars:
            left_pt = Point(
                p.left_contact.x - (self.level - p.left_contact.y),
                p.left_contact.y)
            poly = Polygon([
                (p.left_contact.x, self.level),
                p.left_contact,
                left_pt])
            if self.level > p.bounding_box['maxy']:
                box = Polygon([
                    (left_pt.x, self.level),
                    (p.highest_point.x, self.level),
                    p.highest_point,
                    (left_pt.x, p.highest_point.y)])
                poly = poly.difference(box)
            vt_list.append(segment.Segment(
                poly, p.max_depth, self.g_water, p.axis, settings.VT))
        return vt_list

    @property
    def loads(self):
        return [-i for i in super().loads]

@dataclass
class Opptrykk(Load, LoadMethods):
    @cached_property
    def segments(self):
        increment = settings.INCREMENT
        op_list = []
        for p in self.dam.pillars:
            y = min(p.left_contact.y, p.right_contact.y)
            p0 = (p.left_contact.x, y - (self.level - p.left_contact.y))
            surface = p.cutting_surface
            minx, miny, maxx, maxy = surface.bounds
            line = LineString([(minx, miny), (maxx, miny)])
            new_axis = p.axis - (maxy - miny) / 2 + increment / 2
            count = 0
            segments = []
            while line.intersects(surface):
                count += 1
                intersec = line.intersection(surface)
                if type(intersec) == LineString:
                    intersec = MultiLineString([intersec])
                if type(intersec) not in (Point, MultiPoint):
                    intersec = intersec[0]
                    p1, p2 = intersec.coords
                    p1, p2 = (p1[0], y), (p2[0], y)
                    poly = Polygon([p0, p1, p2])
                    segments.append(segment.Segment(
                        poly, increment, self.g_water, new_axis, settings.OP))
                new_y = miny + count * increment
                line = LineString([(minx, new_y), (maxx, new_y)])
                new_axis += increment
            op_list.append(segments)
        return op_list

    @property
    def centroids(self):
        centr_list = []
        for op, pillar in zip(self.segments, self.dam.pillars):
            area_i = [i.area for i in op]
            x_i = [i.centroid.x for i in op]
            xs = sum([a * b for a, b in zip(area_i, x_i)]) / sum(area_i)
            centr_list.append(Point(xs, pillar.left_contact.y))
        return centr_list

    @property
    def loads(self):
        return [- sum([i.load for i in op]) for op in self.segments]


@dataclass
class Overtopping(Load, LoadMethods):
    @cached_property
    def segments(self):
        ov_list = []
        for p in self.dam.pillars:
            hp = p.highest_point
            cw = p.crest_width
            if self.level > hp.y:
                poly = Polygon([
                    hp,
                    (hp.x, self.level),
                    (hp.x + cw, hp.y)])
            else:
                poly = Polygon([
                    hp,
                    (hp.x + cw / 2, hp.y),
                    (hp.x + cw, hp.y)])
            ov_list.append(segment.Segment(
                poly, p.max_depth, self.g_water, p.axis, settings.OV))
        return ov_list

@dataclass
class Egenvekt(BaseLoad, LoadMethods):
    
    @cached_property
    def segments(self):
        return [p.segments_above_ground for p in self.dam.pillars]

    @property
    def centroids(self):
        centr_list = []
        for segs in self.segments:
            load_i = [seg.load for seg in segs]
            x_i, y_i = zip(*[(seg.centroid.x, seg.centroid.y) for seg in segs])
            xs = sum([l * x for l, x in zip(load_i, x_i)]) / sum(load_i)
            ys = sum([l * y for l, y in zip(load_i, y_i)]) / sum(load_i)
            centr_list.append(Point(xs, ys))
        return centr_list

    @property
    def loads(self):
        return [sum([seg.load for seg in segs]) for segs in self.segments]

@dataclass
class Islast(BaseLoad, LoadMethods):
    level: float
    ice_load: float

    def __post_init__(self):
        if not self.ice_load >= 0:
            raise ValueError('invalid ice load')

    @cached_property
    def segments(self):
        const, length = 0.25, 2
        ice_list = []
        for p in self.dam.pillars:
            y = max(p.bounding_box['miny'], self.level - const)
            x = p.left_contact.x
            poly = Polygon([
                (x, y + const),
                (x, y - const),
                (x - length, y - const),
                (x - length, y + const)])
            ice_list.append(segment.Segment(
                poly, p.max_depth, self.ice_load, p.axis, settings.ICE))
        return ice_list

    @property
    def loads(self):
        return [-i for i in super().loads]