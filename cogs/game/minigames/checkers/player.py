from asyncio import wait, FIRST_COMPLETED
from discord import Embed
from random import choice, randint

from cogs.errors import get_error_message
from cogs.globals import PRIMARY_EMBED_COLOR
from cogs.game.minigames.base_game.player import Player
from cogs.game.minigames.checkers.pieces import COLUMNS, UNDO, RESIGN, NUMBERS

from util.functions import get_embed_color

# # # # # # # # # # # # # # # # # # # # # # # # #

def coordinate_to_piece(row, col) -> int:
    """Converts a row, column coordinate to a location
    number in the checkers library used

    :param row: The row to get the location of
    :param col: The column to get the location of
    """
    if (row % 2 == 0) ^ (col % 2 != 0):
        return None
    if row % 2 == 0:
        return (row - 1) * 4 + (col + 1) // 2
    return (row - 1) * 4 + col // 2

# # # # # # # # # # # # # # # # # # # # # # # # #

class CheckersPlayer(Player):
    def __init__(self, member, *, is_smart = False):
        super().__init__(member = member, is_smart = is_smart)

    # # # # # # # # # # # # # # # # # # # # # # # # #

    async def process_turn(self, game):
        """Processes the player's turn in the Checkers game

        :param game: The Game object this Player is connected to
        """

        # Determine the flip value that is used
        #   to rotate the board to make it easier on the
        #   current player's turn
        if game.opponent.is_ai:
            flip = True
        else:
            flip = game.current_player == 0

        # Edit the game message
        # Check if there is a check, checkmate, or stalemate
        #   give the player an option to resign
        title = "Checkers"
        await game.message.edit(
            embed = Embed(
                title = title,
                description = (
                    f"{self.get_name()}'s turn\n" +
                    f"{game.get_board(flip=flip)}\n" +
                    f":brown_circle: {game.opponent.get_name()}\n" +
                    f":red_circle: {game.challenger.get_name()}\n"
                ),
                colour = PRIMARY_EMBED_COLOR if self.is_ai else await get_embed_color(self.member)
            ).set_footer(
                text = "❕❕React with your chosen column first and then the row❕❕"
            )
        )

        # Check if this player is an AI
        if self.is_ai:

            # Choose a random move from the game boards legal moves generator
            legal_moves = game.game.get_possible_moves()

            # Generate a random number of best moves
            best_move = choice(legal_moves)
            for move_try in range(randint(1, len(legal_moves))):
                best_move = choice(legal_moves)
            game.game.move(best_move)
        
        # This player is not an AI
        else:

            # Get the player's desired piece to move
            column_from, row_from = "", ""
            column_to, row_to = "", ""
            col_num, row_num = 0, 0

            while True:  # Ask the player for their move while
                         #  the move they choose is invalid

                # Column_from is 0, Row_from is 1
                # column_to is 2, row_to is 3
                entry = 0
                while entry < 4:
                    while True:

                        # "Highlight" the player's selected piece (when possible)
                        board = game.get_board(None if entry < 2 else (row_num, col_num), flip = flip)
                        await game.message.edit(
                            embed = Embed(
                                title = title,
                                description = (
                                    f"{self.get_name()}'s turn\n" +
                                    f"{board}\n" +
                                    f":brown_circle: {game.opponent.get_name()}\n" +
                                    f":red_circle: {game.challenger.get_name()}\n"
                                ),
                                colour = PRIMARY_EMBED_COLOR if self.is_ai else await get_embed_color(self.member)
                            ).add_field(
                                name = "Current Move: {} -> {}".format(
                                    ":".join([column_from, row_from][:entry]),
                                    ":".join([column_to, row_to][:entry // 2]) if entry >= 2 else ""
                                ),
                                value = (
                                    f"React with {UNDO} to undo your last move\n" +
                                    f"React with {RESIGN} to resign"
                                )
                            ).set_footer(
                                text = "❕❕React with your chosen column first and then the row❕❕"
                            ))

                        def check_reaction(reaction, user):
                            return (
                                reaction.message.id == game.message.id and
                                user.id == self.member.id and
                                (str(reaction) in COLUMNS or
                                 str(reaction) in [UNDO, RESIGN])
                            )
                        done, pending = await wait([
                            game.bot.wait_for("reaction_add", check = check_reaction),
                            game.bot.wait_for("reaction_remove", check = check_reaction)
                        ], return_when = FIRST_COMPLETED)
                        reaction, user = done.pop().result()
                        for future in pending:
                            future.cancel()

                        # Check if the user chose the undo button (remove their last entry)
                        #   and have them input their desired value
                        if str(reaction) == UNDO:
                            if entry == 1:
                                column_from = ""
                                col_num = 0
                            elif entry == 2:
                                row_from = ""
                                row_num = 0
                            elif entry == 3:
                                column_to = ""
                            if entry > 0:
                                entry -= 1
                            continue
                        
                        # Check if the user chose to resign
                        elif str(reaction) == RESIGN:
                            return False
                        
                        # Get the column first, then the row
                        #   but validate the input
                        if entry in [0, 2]:  # Column
                            if str(reaction) not in COLUMNS:
                                await game.ctx.send(
                                    embed = get_error_message(
                                        "That is an invalid column! Try again."
                                    ), delete_after = 10)
                            else:

                                # Shift the reaction if the board is flipped 
                                #   (challenger's turn)
                                if game.current_player == 0:
                                    reaction = NUMBERS[7 - NUMBERS.index(str(reaction))]
                                    if entry < 2:
                                        col_num = 7 - NUMBERS.index(str(reaction))
                                else:
                                    if entry < 2:
                                        col_num = NUMBERS.index(str(reaction))
                                if entry < 2:
                                    column_from = str(NUMBERS.index(str(reaction)) + 1)
                                else:
                                    column_to = str(NUMBERS.index(str(reaction)) + 1)
                                break  # This input was okay
                        else:
                            if str(reaction) not in COLUMNS:
                                await game.ctx.send(
                                    embed = get_error_message(
                                        "That is an invalid row! Try again!"
                                    ), delete_after = 10)
                            else:
                                
                                # Shift the row if the board is not flipped
                                #   (opponent's turn)
                                if game.current_player == 1:
                                    reaction = NUMBERS[7 - NUMBERS.index(str(reaction))]
                                    if entry < 2:
                                        row_num = 7 - NUMBERS.index(str(reaction))
                                else:
                                    if entry < 2:
                                        row_num = NUMBERS.index(str(reaction))
                                if entry < 2:
                                    row_from = str(reaction)[0]  # This will get the number
                                else:
                                    row_to = str(reaction)[0]
                                break  # this input was okay
                    entry += 1

                # Check if the player made a valid move
                valid_moves = game.game.get_possible_moves()
                from_loc = coordinate_to_piece(int(row_from), int(column_from))
                to_loc = coordinate_to_piece(int(row_to), int(column_to))
                if [from_loc, to_loc] in valid_moves:
                    break

                await game.ctx.send(
                    embed = get_error_message(
                        "You can't move that piece like that! Try again."
                    ), delete_after = 10
                )
                row_to, column_to, row_from, column_from = "", "", "", ""
            
            player_move = [
                coordinate_to_piece(int(row_from), int(column_from)),
                coordinate_to_piece(int(row_to), int(column_to))
            ]

            # Check if the game is against an AI or not
            #   and let the player make their move
            game.game.move(player_move)