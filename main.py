import sys
from blessed import Terminal
from src.terminal_ui import ScreenBuffer
from src.explorer import FilesystemExplorer
from src.map_generator import MapGenerator


def get_line(x0, y0, x1, y1):
    """Bresenham's Line Algorithm to calculate steps between two coordinates."""
    points = []
    dx = abs(x1 - x0)
    dy = abs(y1 - y0)
    x, y = x0, y0
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    if dx > dy:
        err = dx / 2.0
        while x != x1:
            points.append((x, y))
            err -= dy
            if err < 0:
                y += sy
                err += dx
            x += sx
    else:
        err = dy / 2.0
        while y != y1:
            points.append((x, y))
            err -= dx
            if err < 0:
                x += sx
                err += dy
            y += sy
    points.append((x1, y1))
    return points


def has_los(px, py, tx, ty, buffer):
    """Checks if there is a clear line-of-sight between player and target coordinates."""
    if px == tx and py == ty:
        return True
    line = get_line(px, py, tx, ty)
    for lx, ly in line[1:-1]:
        if buffer.cells[ly][lx].char == "#":
            return False
    return True


def calculate_visibility(px, py, buffer, radius=5):
    """Finds all coordinates within vision radius that have clear line-of-sight."""
    visible = set()
    visible.add((px, py))
    min_x = max(0, px - radius)
    max_x = min(buffer.width - 1, px + radius)
    min_y = max(0, py - radius)
    max_y = min(buffer.height - 1, py + radius)
    for y in range(min_y, max_y + 1):
        for x in range(min_x, max_x + 1):
            if (x - px) ** 2 + (y - py) ** 2 <= radius ** 2:
                if has_los(px, py, x, y, buffer):
                    visible.add((x, y))
    return visible


def main():
    term = Terminal()
    explorer = FilesystemExplorer()
    view_width = 79
    view_height = 21
    buffer = ScreenBuffer(view_width, view_height)
    generator = MapGenerator(view_width, view_height)
    player_x = (view_width // 2) | 1
    player_y = (view_height // 2) | 1
    current_selected_item = None
    selected_type = None
    error_message = None
    explored_cells = set()
    map_dirty = True
    door_coords = {}
    file_coords = {}
    stair_pos = None
    with term.fullscreen(), term.cbreak(), term.hidden_cursor():
        print(term.clear)
        while True:
            if map_dirty:
                door_coords, file_coords, stair_pos = generator.build_map(explorer, buffer, term)
                player_x = (view_width // 2) | 1
                player_y = (view_height // 2) | 1
                current_selected_item = None
                selected_type = None
                error_message = None
                explored_cells.clear()
                map_dirty = False
            visible_cells = calculate_visibility(player_x, player_y, buffer, radius=5)
            explored_cells.update(visible_cells)
            original_cell_char = buffer.cells[player_y][player_x].char
            original_cell_color = buffer.cells[player_y][player_x].color_func
            buffer.set_cell(player_x, player_y, "@", term.bold_green)
            sys.stdout.write(term.home + buffer.draw(term, visible=visible_cells, explored=explored_cells))
            buffer.set_cell(player_x, player_y, original_cell_char, original_cell_color)
            location_line = f"\n{term.bold('Location:')} {explorer.current_path}" + term.clear_eol
            sys.stdout.write(location_line)
            hud_action_line = "\n"
            if error_message:
                hud_action_line += f"{term.bold_red('System Error:')} {error_message}"
            elif current_selected_item:
                if selected_type == "folder":
                    hud_action_line += f"{term.bold_blue('Folder:')} {current_selected_item.name} | {term.yellow('[Press Space/Enter to enter]')}"
                elif selected_type == "file":
                    hud_action_line += f"{term.bold_cyan('File:')} {current_selected_item.name} | {term.yellow('[Press Space/Enter to open]')}"
                elif selected_type == "parent":
                    hud_action_line += f"{term.bold_yellow('Stairs Up')} (to Parent Directory) | {term.yellow('[Press Space/Enter to climb]')}"
            else:
                hud_action_line += f"{term.gray('WASD/HJKL/Arrows to move. Stand on items to inspect.')}"
            hud_action_line += term.clear_eol
            sys.stdout.write(hud_action_line)
            sys.stdout.flush()
            key = term.inkey(timeout=0.1)
            if not key:
                continue
            error_message = None
            if key.code == term.KEY_ESCAPE or key == 'q':
                break
            if key == " " or key.name == "KEY_ENTER" or key == "\n" or key == "\r":
                if current_selected_item:
                    if selected_type == "folder":
                        explorer.change_directory(current_selected_item)
                        map_dirty = True
                    elif selected_type == "parent":
                        explorer.change_directory(explorer.current_path.parent)
                        map_dirty = True
                    elif selected_type == "file":
                        err = explorer.open_file(current_selected_item)
                        if err:
                            error_message = err
                continue
            next_x, next_y = player_x, player_y
            if key.name == 'KEY_UP' or key == 'w' or key == 'k':
                next_y = max(0, player_y - 1)
            elif key.name == 'KEY_DOWN' or key == 's' or key == 'j':
                next_y = min(view_height - 1, player_y + 1)
            elif key.name == 'KEY_LEFT' or key == 'a' or key == 'h':
                next_x = max(0, player_x - 1)
            elif key.name == 'KEY_RIGHT' or key == 'd' or key == 'l':
                next_x = min(view_width - 1, player_x + 1)
            if buffer.cells[next_y][next_x].char == "#":
                continue
            player_x, player_y = next_x, next_y
            pos = (player_x, player_y)
            if pos in door_coords:
                current_selected_item = door_coords[pos]
                selected_type = "folder"
            elif pos in file_coords:
                current_selected_item = file_coords[pos]
                selected_type = "file"
            elif pos == stair_pos:
                current_selected_item = explorer.current_path.parent
                selected_type = "parent"
            else:
                current_selected_item = None
                selected_type = None


if __name__ == "__main__":
    main()