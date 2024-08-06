import chess
import chess.engine
from searchAndEvaluation import bestMove, scoreBoard
from multiprocessing import Queue, Process
import threading
import time
import sys

class UCIWrapper:
    def __init__(self):
        self.board = chess.Board()
        self.return_queue = Queue()
        self.ponder_process = None
        self.is_pondering = False
        self.syzygy_path = None
        self.show_wdl = False
        self.threads = 1
        self.hash_size = 16
        self.running = True

    def uci(self):
        print("id name Linea Caelestis")
        print("id author Kadir Yavuz Kurt")
        print("option name Hash type spin default 16 min 1 max 1024")
        print("option name Threads type spin default 1 min 1 max 128")
        print("option name Ponder type check default false")
        print("option name Move Overhead type spin default 10 min 0 max 5000")
        print("option name SyzygyPath type string default <empty>")
        print("option name UCI_ShowWDL type check default false")
        print("uciok")

    def isready(self):
        print("readyok")

    def ucinewgame(self):
        self.board.reset()

    def position(self, command):
        parts = command.split()
        if parts[1] == "startpos":
            self.board.reset()
            moves_start = 3 if len(parts) > 2 and parts[2] == "moves" else 0
        else:
            fen = " ".join(parts[1:7])
            self.board.set_fen(fen)
            moves_start = 8 if len(parts) > 8 and parts[7] == "moves" else 0

        if moves_start:
            for move in parts[moves_start:]:
                self.board.push(chess.Move.from_uci(move))

    def go(self, command):
        parts = command.split()
        time_control = {}
        ponder = False
        for i in range(1, len(parts)):
            if parts[i] in ["wtime", "btime", "winc", "binc", "movestogo", "depth", "nodes", "movetime"]:
                time_control[parts[i]] = int(parts[i+1])
            elif parts[i] == "ponder":
                ponder = True

        if self.is_pondering:
            self.stop_pondering()

        try:
            bestMove(self.board, list(self.board.legal_moves), self.return_queue, time_control)
            
            # Wait for a maximum of 30 seconds for a response
            start_time = time.time()
            while time.time() - start_time < 60:
                try:
                    move = self.return_queue.get(timeout=1)
                    print(f"bestmove {move}")
                    
                    if ponder:
                        self.start_pondering(move)
                    
                    return
                except Queue.Empty:
                    continue
            
            # If no move is received, find the highest scored move
            highest_scored_move = self.get_highest_scored_move()
            print(f"bestmove {highest_scored_move}")
        except Exception as e:
            print(f"info string Error in go command: {str(e)}")
            highest_scored_move = self.get_highest_scored_move()
            print(f"bestmove {highest_scored_move}")

    def get_highest_scored_move(self):
        legal_moves = list(self.board.legal_moves)
        if not legal_moves:
            return "0000"  # No legal moves available
        
        best_move = None
        best_score = float('-inf')
        
        for move in legal_moves:
            self.board.push(move)
            score = -scoreBoard(self.board)
            self.board.pop()
            
            if score > best_score:
                best_score = score
                best_move = move
        
        return best_move.uci() if best_move else "0000"

    def start_pondering(self, move):
        ponder_board = self.board.copy()
        ponder_board.push(chess.Move.from_uci(move))
        self.is_pondering = True
        self.ponder_process = Process(target=bestMove, args=(ponder_board, list(ponder_board.legal_moves), self.return_queue, {}))
        self.ponder_process.start()

    def stop_pondering(self):
        if self.is_pondering:
            self.ponder_process.terminate()
            self.ponder_process.join()
            self.is_pondering = False

    def set_option(self, command):
        parts = command.split()
        if len(parts) >= 5 and parts[1] == "name" and parts[3] == "value":
            option_name = parts[2]
            option_value = " ".join(parts[4:])
            if option_name == "SyzygyPath":
                self.syzygy_path = option_value
                print(f"info string Set SyzygyPath to {option_value}")
            elif option_name == "UCI_ShowWDL":
                self.show_wdl = option_value.lower() == "true"
                print(f"info string Set UCI_ShowWDL to {self.show_wdl}")
            elif option_name == "Threads":
                self.threads = int(option_value)
                print(f"info string Set Threads to {self.threads}")
            elif option_name == "Hash":
                self.hash_size = int(option_value)
                print(f"info string Set Hash to {self.hash_size} MB")
            elif option_name == "Move Overhead":
                print(f"info string Set Move Overhead to {option_value}")
            else:
                print(f"info string Unknown option: {option_name}")
        else:
            print("info string Invalid setoption command")

    def quit(self):
        print("info string Entering quit method", flush=True)
        self.running = False
        self.stop_pondering()
        if hasattr(self, 'return_queue'):
            self.return_queue.close()
            self.return_queue.join_thread()
        print("info string Engine quit successfully", flush=True)
        print("readyok", flush=True)
        sys.stdout.flush()
        sys.exit(0)  # Force exit the process

    def run(self):
        while self.running:
            try:
                command = input().strip()
                if not command:
                    continue

                if command == "uci":
                    self.uci()
                elif command == "isready":
                    print("readyok", flush=True)
                elif command == "ucinewgame":
                    self.ucinewgame()
                elif command.startswith("position"):
                    self.position(command)
                elif command.startswith("go"):
                    self.go(command)
                elif command == "quit":
                    self.quit()
                elif command == "stop":
                    self.stop_pondering()
                elif command.startswith("setoption"):
                    self.set_option(command)
                else:
                    print(f"info string Unknown command: {command}", flush=True)
            except EOFError:
                break
            except Exception as e:
                print(f"info string Error in command execution: {str(e)}", flush=True)

        self.quit()  # Ensure quit is called if we break out of the loop

if __name__ == "__main__":
    uci_wrapper = UCIWrapper()
    uci_wrapper.run()