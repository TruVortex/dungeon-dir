from blessed import Terminal


class Cell:
    def __init__(self, char: str = " ", color_func=None):
        self.char = char
        self.color_func = color_func


class ScreenBuffer:
    def __init__(self, width: int = 80, height: int = 24):
        self.width = width
        self.height = height
        self.clear()

    def clear(self):
        self.cells = [[Cell() for _ in range(self.width)] for _ in range(self.height)]

    def set_cell(self, x: int, y: int, char: str, color_func=None):
        if 0 <= x < self.width and 0 <= y < self.height:
            self.cells[y][x] = Cell(char[0] if char else " ", color_func)

    def draw(self, term: Terminal, visible: set = None, explored: set = None) -> str:
        """Compiles the buffer into a single string with Fog of War filtering."""
        output = []
        if visible is None:
            visible = {(x, y) for y in range(self.height) for x in range(self.width)}
        if explored is None:
            explored = visible
        for y in range(self.height):
            line = []
            for x in range(self.width):
                cell = self.cells[y][x]
                pos = (x, y)
                if pos in visible:
                    if cell.color_func:
                        line.append(f"{cell.color_func(cell.char)}")
                    else:
                        line.append(cell.char)
                elif pos in explored:
                    if cell.char != " ":
                        line.append(f"{term.bright_black(cell.char)}")
                    else:
                        line.append(" ")
                else:
                    line.append(" ")
            output.append("".join(line))
        return "\n".join(output)
