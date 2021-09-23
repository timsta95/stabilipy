import math
from dataclasses import dataclass
from functools import cached_property
from shapely.geometry import (
    Point, MultiPoint, LineString, MultiLineString, Polygon)
from shapely.ops import unary_union
from stabilipy import segment, settings

@dataclass
class Pillar:
    segments: list
    contact_left: float
    contact_right: float
    crest_width: float
    phi: float
    dam_type: str
    name: str

    def __post_init__(self):
        # validate data class attributes
        for seg in self.segments:
            if not isinstance(seg, segment.Segment):
                raise ValueError('non-Segment in segments')
        bb = self.bounding_box
        for i in (self.contact_left, self.contact_right):
            if i < bb['miny'] or i > bb['maxy']:
                raise ValueError('contact left/right out of range')
        if self.crest_width <= 0:
            raise ValueError('invalid crest width')
        if self.phi < 0 or self.phi > 90:
            raise ValueError('invalid phi')
        if not self.dam_type in (settings.BUTTRESS, settings.GRAVITY):
            raise ValueError('dam type not recognised')
        if not isinstance(self.name, str):
            raise ValueError('invalid name')

    @cached_property
    def union(self):
        return unary_union([i.poly for i in self.segments])

    @cached_property
    def highest_point(self):
        x, y = self.union.exterior.coords.xy
        index = y.index(max(y))
        return Point(x[index], y[index])

    @cached_property
    def left_contact(self):
        x, _ = self.union.exterior.coords.xy
        line = LineString([
            (min(x) - 1, self.contact_left),
            (max(x) + 1, self.contact_left)])
        splits = line.difference(self.union)
        x, y = splits[0].coords.xy
        return Point(x[-1], y[-1])

    @cached_property
    def right_contact(self):
        x, _ = self.union.exterior.coords.xy
        line = LineString([
            (min(x) - 1, self.contact_right),
            (max(x) + 1, self.contact_right)])
        splits = line.difference(self.union)
        x, y = splits[-1].coords.xy
        return Point(x[0], y[0])

    @cached_property
    def bounding_box(self):
        return dict(zip(['minx', 'miny', 'maxx', 'maxy'], self.union.bounds))

    @cached_property
    def cutting_surface(self):
        line = LineString([self.left_contact, self.right_contact])
        polys = []
        for seg in self.segments:
            if seg.poly.intersects(line):
                intersec = seg.poly.intersection(line)
                if type(intersec) == LineString:
                    intersec = MultiLineString([intersec])
                if type(intersec) not in (Point, MultiPoint):
                    axis = seg.axis
                    width = seg.width
                    for i in intersec:
                        coords = list(i.coords)
                        p0 = coords[0][0]
                        p1 = coords[-1][0]
                        polys.append(Polygon([
                            (p0, axis + width / 2),
                            (p1, axis + width / 2),
                            (p1, axis - width / 2),
                            (p0, axis - width / 2)]))
        return unary_union(polys)

    @property
    def max_depth(self):
        _, miny, _, maxy = self.cutting_surface.bounds
        return maxy - miny

    @property
    def axis(self):
        _, miny, _, maxy = self.cutting_surface.bounds
        return (maxy + miny) / 2

    @property
    def segments_above_ground(self):
        box = Polygon([
            self.left_contact,
            self.right_contact,
            (self.bounding_box['maxx'], self.contact_right),
            (self.bounding_box['maxx'], self.bounding_box['maxy']),
            (self.bounding_box['minx'], self.bounding_box['maxy']),
            (self.bounding_box['minx'], self.contact_left)])
        segs_above = []
        for seg in self.segments:
            if seg.poly.intersects(box):
                inters = seg.poly.intersection(box)
                segs_above.append(
                    segment.Segment(
                        inters, seg.width, seg.spec_weight, seg.axis, seg.name
                        )
                    )
        return segs_above

    @property
    def bottom_angle(self):
        ratio = (self.right_contact.y - self.left_contact.y) \
            / (self.right_contact.x - self.left_contact.x)
        return math.degrees(math.atan(ratio))