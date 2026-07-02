# DungeonDir

DungeonDir is a terminal-based, roguelike-inspired file explorer. It procedurally generates your local directory structures into dungeons complete with real-time sightlines. 

## Quickstart
Ensure Python 3.10+ and [`uv`](https://docs.astral.sh/uv/) are installed. Then, run the application:

```bash
uv run main.py
```

## Controls

* **`WASD` / `HJKL` / `Arrow Keys`**: Move your character (`@`) through the tunnels.
* **`Space` or `Enter`**: Interact with the item you are standing on:
  * **Folders (`+`)**: Enter the directory (regenerates a new procedural map level).
  * **Files (`?`)**: Open the file in your operating system's default handler.
  * **Stairs (`<`)**: Go up to the parent directory.
* **`Q` or `Esc`**: Exit the application.