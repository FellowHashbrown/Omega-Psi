from functools import partial
from requests import post
from json import loads

from cogs.globals import loop

from cogs.game.minigames.chess.pieces import PIECES, COLUMNS, HIGHLIGHT

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

GET_POSSIBLE_MOVES = "https://chess-api-chess.herokuapp.com/api/v1/chess/{}/moves"
CHECK_GAME_OVER = "https://chess-api-chess.herokuapp.com/api/v1/chess/{}/check"

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

class ChessBoard:

    DEFAULT_FEN = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR"

    @staticmethod
    def from_FEN(fen_string: str, selected_piece: tuple=None, *, flip: bool=False) -> str:
        """Creates a ChessBoard object from a FEN string representation
        of the Chess Board.

        The FEN string format can be found here:
            https://en.wikipedia.org/wiki/Forsyth–Edwards_Notation

        :param fen_string: The FEN string to load the Chess Board from
        :param selected_piece: A row-major tuple of the selected piece to "highlight" that piece
        :returns: The string of the Chess Board using emojis
        """

        # Get the rows in the board
        rows = ChessBoard.from_FEN_to_list(fen_string, selected_piece, flip = flip)
    
        # Update the board in the chess board object and return it
        #   Add the rows and columns emojis
        result = ":black_large_square: "
        for emoji in COLUMNS:
            result += emoji + " "
        result += "\n"

        for i in range(len(rows)):
            r = rows[i]
            result += list(COLUMNS.keys())[i]
            for c in r:
                result += c
            result += "\n"
        return result
    
    @staticmethod
    def from_FEN_to_list(fen_string: str, selected_piece: tuple=None, *, flip: bool=False):
        """Converts the chessboard given by the FEN string into a 2-dimensional
        list of board pieces

        :param fen_string: The FEN string to load the Chess Board from
        :param selected_piece: A row-major tuple of the selected piece to "highlight" that piece
        :returns: The string of the Chess Board using emojis
        """

        # Get only the board string from the FEN string
        fen_string = fen_string.split(" ")[0]
        if flip:
            fen_string = fen_string[::-1]

        # Create a Chess Board object from the FEN string
        rows = fen_string.split("/")
        def is_white(row, col) -> bool:
            """Returns whether or not the board space is a white space

            :param row: The row to look at
            :param col: the column to look at
            """
            return (row % 2 == 0) == (col % 2 == 0)

        # Iterate through the split string to generate the chess board
        for i in range(len(rows)):
            cols = []
            new_row = ""

            # Replace the object at rows[i] to keep
            #  the board from having incorrect square colors
            for j in rows[i]:
                if j.isdigit():
                    for _ in range(int(j)):
                        new_row += "-"
                else:
                    new_row += j
            rows[i] = new_row

            # Now iterate through the new row
            for j in range(len(rows[i])):
                piece = rows[i][j]

                # If the piece is a number, add that many empty
                #   columns in the row
                if piece == "-":
                    cols.append(
                        PIECES["WS"] 
                        if is_white(i, j) 
                        else PIECES["BS"])
                    
                # Otherwise, add the piece to the columns
                else:
                    if (i, j) == selected_piece:
                        cols.append(HIGHLIGHT[piece.lower()])
                    else:
                        cols.append(PIECES[piece])
            rows[i] = cols

        return rows
    
    # # # # # # # # # # # # # # # # # # # # # # # # #

    def __init__(self, fen_string: str=DEFAULT_FEN):
        self.board = ChessBoard.from_FEN_to_list(fen_string)

    def __str__(self):
    
        # Update the board in the chess board object and return it
        #   Add the rows and columns emojis
        result = ":black_large_square: "
        for emoji in COLUMNS:
            result += emoji + " "
        result += "\n"

        for i in range(len(self.board)):
            r = self.board[i]
            result += list(COLUMNS.keys())[i]
            for c in r:
                result += c
            result += "\n"
        return result
    
    # # # # # # # # # # # # # # # # # # # # # # # # #

    def get_possible_moves(self, position: tuple, *, flip: bool=False):
        """Returns a list of possible moves for this board
        at the specified position

        :param position: A tuple of the position to look at
        """

        # Get the type of piece at the specified position
        #   and strip it of the emoji data
        piece = str(self.board[position[0]][position[1]])
        print(piece)
    
    # # # # # # # # # # # # # # # # # # # # # # # # #

    @staticmethod
    async def check_for_winner(game):
        """Checks this Board for a winner

        :param game: The ChessGame object that this board is connected to
        """

        result = await loop.run_in_executor(
            None,
            partial(
                post,
                CHECK_GAME_OVER.format("one" if game.opponent.is_ai else "two"),
                data = {
                    "game_id": game.id
                },
                headers = {
                    "Content-Type": "application/x-www-form-urlencoded"
                }
            )
        )
        result = loads(result.text)
        
        if result["status"] == "game continues":
            return None
        return result
        

