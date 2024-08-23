Here's a short and professional GitHub README for the codebase:

# Linea Caelestis Chess Engine

Linea Caelestis is a UCI-compatible chess engine implemented in Python. It features advanced search and evaluation techniques for strong chess play.

## Features

- UCI protocol support
- Alpha-beta pruning with aspiration windows
- Transposition table
- Opening book and endgame tablebase support

## To Do
- [ ] Docker image for this to be run on any machine.
- [ ] GUI on uci wrapper to choose player color and depth of the search.
## Installation

1. Clone the repository
2. Install the required dependencies:

```
pip install -r requirements.txt
```

## Usage

Run the engine on your computer using:

```
python src/uciwrapper.py
```

## Configuration
Change isWhite parameter in the 'src/chessgame.py' file to change the color of the engine.
If you want to change the depth of the search, you can change the depth parameter in the 'src/chessgame.py' file.
Press r to undo the last move.
Press z to reset the board.

## Contributing

Contributions are welcome. Please open an issue to discuss proposed changes or submit a pull request.

## License

[MIT License](LICENSE)
