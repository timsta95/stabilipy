from dataclasses import dataclass

@dataclass
class Dam:
    pillars: list

    # implement string representation
    # class attribute validation:
    # - warning if pillars adjacent
    # - error if pillars overlapping