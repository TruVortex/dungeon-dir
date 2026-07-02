import random

from src.terminal_ui import ScreenBuffer


class MapGenerator:
    def __init__(self, width: int, height: int):
        self.width = width if width % 2 != 0 else width - 1
        self.height = height if height % 2 != 0 else height - 1

    def _is_carvability_zone(self, x, y):
        """Defines an elliptical boundary inside our grid where paths can be carved."""
        if not (0 < x < self.width - 1 and 0 < y < self.height - 1):
            return False
        cx, cy = self.width // 2, self.height // 2
        rx = (self.width - 6) / 2
        ry = (self.height - 6) / 2
        if rx <= 0 or ry <= 0:
            return True
        dx = x - cx
        dy = y - cy
        return (dx / rx) ** 2 + (dy / ry) ** 2 <= 1.0

    def _generate_base_maze(self):
        """Generates an organic elliptical cave system with loops and corridors."""
        grid = [["void" for _ in range(self.width)] for _ in range(self.height)]
        for y in range(self.height):
            for x in range(self.width):
                if self._is_carvability_zone(x, y):
                    grid[y][x] = "#"
        start_x = (self.width // 2) | 1
        start_y = (self.height // 2) | 1
        if grid[start_y][start_x] != "#":
            start_x, start_y = 1, 1
            grid[start_y][start_x] = "#"
        visited = set()
        stack = []
        grid[start_y][start_x] = " "
        visited.add((start_x, start_y))
        stack.append((start_x, start_y))
        while stack:
            cx, cy = stack[-1]
            neighbors = []
            for dx, dy in [(-2, 0), (2, 0), (0, -2), (0, 2)]:
                nx, ny = cx + dx, cy + dy
                if 0 <= nx < self.width and 0 <= ny < self.height:
                    if grid[ny][nx] == "#" and (nx, ny) not in visited:
                        neighbors.append((nx, ny))

            if neighbors:
                nx, ny = random.choice(neighbors)
                grid[cy + (ny - cy) // 2][cx + (nx - cx) // 2] = " "
                grid[ny][nx] = " "
                visited.add((nx, ny))
                stack.append((nx, ny))
            else:
                stack.pop()
        for y in range(1, self.height - 1):
            for x in range(1, self.width - 1):
                if grid[y][x] == "#":
                    open_neighbors = 0
                    for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                        if grid[y + dy][x + dx] == " ":
                            open_neighbors += 1
                    if open_neighbors >= 2 and random.random() < 0.15:
                        grid[y][x] = " "
        for y in range(self.height):
            for x in range(self.width):
                if grid[y][x] == "void":
                    has_path_neighbor = False
                    for dy in [-1, 0, 1]:
                        for dx in [-1, 0, 1]:
                            nx, ny = x + dx, y + dy
                            if 0 <= nx < self.width and 0 <= ny < self.height:
                                if grid[ny][nx] == " ":
                                    has_path_neighbor = True
                                    break
                        if has_path_neighbor:
                            break
                    if has_path_neighbor:
                        grid[y][x] = "#"
        return grid

    def build_map(self, explorer, buffer: ScreenBuffer, term):
        buffer.clear()
        folders, files = explorer.get_contents()
        grid = self._generate_base_maze()
        open_cells = []
        dead_ends = []
        start_x = (self.width // 2) | 1
        start_y = (self.height // 2) | 1
        for y in range(1, self.height - 1):
            for x in range(1, self.width - 1):
                if grid[y][x] == " ":
                    open_cells.append((x, y))
                    open_neighbors = 0
                    for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                        if grid[y + dy][x + dx] == " ":
                            open_neighbors += 1
                    if open_neighbors == 1:
                        dead_ends.append((x, y))
        if (start_x, start_y) in dead_ends:
            dead_ends.remove((start_x, start_y))
        if (start_x, start_y) in open_cells:
            open_cells.remove((start_x, start_y))
        random.shuffle(dead_ends)
        random.shuffle(open_cells)
        for y in range(self.height):
            for x in range(self.width):
                if grid[y][x] == "#":
                    buffer.set_cell(x, y, "#", term.gray)
                elif grid[y][x] == " ":
                    buffer.set_cell(x, y, " ")
                else:
                    buffer.set_cell(x, y, " ")
        door_coords = {}
        file_coords = {}
        stair_pos = None
        items_to_place = []
        if explorer.current_path.parent != explorer.current_path:
            items_to_place.append(('<', explorer.current_path.parent))
        for folder in folders:
            items_to_place.append(('+', folder))
        for file in files:
            items_to_place.append(('?', file))
        placement_pool = dead_ends + open_cells
        for item_type, path_obj in items_to_place:
            if not placement_pool:
                break
            x, y = placement_pool.pop(0)
            if item_type == '<':
                buffer.set_cell(x, y, "<", term.bold_yellow)
                stair_pos = (x, y)
            elif item_type == '+':
                buffer.set_cell(x, y, "+", term.bold_blue)
                door_coords[(x, y)] = path_obj
            elif item_type == '?':
                buffer.set_cell(x, y, "?", term.bold_cyan)
                file_coords[(x, y)] = path_obj
        return door_coords, file_coords, stair_pos
