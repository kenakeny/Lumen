import random
from panda3d.core import Point3
from config import ROOM_SIZE, DUNGEON_GRID, DUNGEON_ROOMS
from world.room_builder import build_room


DIRECTIONS = {
    "N": (0, 1),
    "S": (0, -1),
    "E": (1, 0),
    "W": (-1, 0),
}
OPPOSITE = {"N": "S", "S": "N", "E": "W", "W": "E"}


class Dungeon:
    def __init__(self, app):
        self.app = app
        self.grid_size = DUNGEON_GRID
        self.cells = set()
        self.room_nodes = {}
        self.root = app.render.attachNewNode("dungeon")

        self._generate_layout()
        self._build_rooms()

    def _generate_layout(self):
        center = self.grid_size // 2
        pos = (center, center)
        self.cells.add(pos)

        for _ in range(DUNGEON_ROOMS - 1):
            for _attempt in range(20):
                dx, dy = random.choice(list(DIRECTIONS.values()))
                nx, ny = pos[0] + dx, pos[1] + dy
                if 0 <= nx < self.grid_size and 0 <= ny < self.grid_size:
                    self.cells.add((nx, ny))
                    pos = (nx, ny)
                    break
            else:
                pos = random.choice(list(self.cells))

    def _build_rooms(self):
        for (gx, gy) in self.cells:
            openings = set()
            for side, (dx, dy) in DIRECTIONS.items():
                if (gx + dx, gy + dy) in self.cells:
                    openings.add(side)
            self.room_nodes[(gx, gy)] = build_room(self.root, gx, gy, openings)

    def get_spawn_pos(self):
        center = self.grid_size // 2
        return Point3(center * ROOM_SIZE, center * ROOM_SIZE, 0)

    def get_room_centers(self):
        positions = []
        for (gx, gy) in self.cells:
            positions.append(Point3(gx * ROOM_SIZE, gy * ROOM_SIZE, 1))
        return positions
