This project is being made to be used by my another project. My final goal is to make an open sourced robotic arm model, MeArm, to play chess with RasperryPi controller. 



To Do:

- Adding 50 move and 3 move repeat rules
- Promoting to other pieces rather than only promoting to Queen
- Lichess.com bot account
- Early Game/Mid Game/End Game evaluation tables
- Overall better evaluation system
- More pruning on search algorithm


I made this project thanks to chessprogramming.org and the guides of Eddie Sharick on youtube. His channel is: https://www.youtube.com/channel/UCaEohRz5bPHywGBwmR18Qww


How to Open:
- Run chessgame.py on python.
- Press z to undo moves.
- Press r to reset to board
- Change whitePlayer or blackPlayer parameters to True depending on which side you are playing
- Change the DEPTH parameter in searchAndEvaluation to your desired depth. Code is not optimized, so it works well up to 5 depth.

