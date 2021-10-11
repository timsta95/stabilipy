from dataclasses import dataclass, field
from shapely.geometry import Point, Polygon

@dataclass
class Segment:
    poly: Polygon
    width: float
    spec_weight: float
    axis: float
    name: str
    centroid: Point = field(init=False)
    area: float = field(init=False)
    load: float = field(init=False)

    def __post_init__(self):
        # validate dataclass attributes
        if not isinstance(self.poly, Polygon):
            raise ValueError('poly is not a Polygon')
        if not self.width > 0:
            raise ValueError('width is not greater than zero')
        if not self.spec_weight >= 0:
            raise ValueError('spec_weight is not greater than zero')
        if not (isinstance(self.axis, float) or isinstance(self.axis, int)):
            raise ValueError('axis is not numeric')
        if not isinstance(self.name, str):
            raise ValueError('name is not a string')
        # add attributes
        self.centroid = self.poly.centroid
        self.area = self.poly.area
        self.load = self.area * self.width * self.spec_weight

    def __str__(self) -> str:
        return (f'Segment: name = {self.name}, '
                f'section area = {round(self.area, 3)}, '                
                f'width = {round(self.width, 3)}, '
                f'spec. weight = {round(self.spec_weight, 3)}, '
                f'axis = {round(self.axis, 3)}, '
                f'centroid = ({round(self.centroid.x, 3)}, '
                f'{round(self.centroid.y, 3)}), '
                f'load = {round(self.load, 3)}')

    @property
    def coords(self):
        return self.poly.exterior.coords.xy

    @property
    def x_coords(self):
        return list(self.coords[0])

    @property
    def y_coords(self):
        return list(self.coords[1])