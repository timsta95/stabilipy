from dataclasses import dataclass

@dataclass
class Dam:
    pillars: list

    # TO DO:
    # class attribute validation:
    # - warning if pillars adjacent
    # - error if pillars overlapping

    def __str__(self) -> str:
        type_set = set([p.dam_type for p in self.pillars])
        type_set_str = ', '.join(type_set)
        return (f'Dam consisting of {len(self.pillars)} pillars; '
                 f'dam type(s): {type_set_str}')