from dataclasses import dataclass

@dataclass
class Dam:

    """Dam class used as a container for pillars"""

    pillars: list

    # implement string representation
    # class attribute validation:
    # - warning if pillars adjacent
    # - error if pillars overlapping