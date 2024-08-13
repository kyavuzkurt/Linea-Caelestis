Here's a short and professional GitHub README for the codebase:

# Linea Caelestis Chess Engine

Linea Caelestis is a UCI-compatible chess engine implemented in Python. It features advanced search and evaluation techniques for strong chess play.

## Features

- UCI protocol support
- Alpha-beta pruning with aspiration windows
- Transposition table
- Piece-square tables for different game phases
- Advanced evaluation functions
- Opening book and endgame tablebase support

## To Do

- [ ] Implement lichess API. It is working buggy.
- [ ] Improvements on the evaluation function.
- [ ] Docker image for this to be run on any machine.
- [ ] GUI on uci wrapper.
## Installation

1. Clone the repository
2. Install the required dependencies:

```
pip install -r requirements.txt
```

## Usage

Run the engine using:

```
python src/uciwrapper.py
```

## Configuration

Adjust the following parameters in `src/searchAndEvaluation.py` to fine-tune the engine:

```
CHECKMATE = 1000
DRAW = 0
DEPTH = 3  # Change the depth parameter. Max 5 is recommended.
POLYGLOT_FILE = "Titans.bin"  #Using the Titans opening book
SYZYGY_PATH = "/syzygy"  #Using the Syzygy tablebases
FUTILITY_MARGIN = 200
FULL_DEPTH_MOVES = 4
REDUCTION_LIMIT = 3
ASPIRATION_WINDOW = 50
FUTILITY_MARGIN = 200
HISTORY_MAX = 10000
MAX_TIME = 60
```


## Contributing

Contributions are welcome. Please open an issue to discuss proposed changes or submit a pull request.

## License

[MIT License](LICENSE)
