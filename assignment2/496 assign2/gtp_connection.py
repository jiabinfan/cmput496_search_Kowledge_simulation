"""
gtp_connection.py
Module for playing games of Go using GoTextProtocol
Parts of this code were originally based on the gtp module 
in the Deep-Go project by Isaac Henrion and Amos Storkey 
at the University of Edinburgh.
"""
import traceback
from sys import stdin, stdout, stderr
from board_util import GoBoardUtil, BLACK, WHITE, EMPTY, BORDER, PASS, \
                       MAXSIZE, coord_to_point
import numpy as np
import re
import time

INFINITY = 10000000


class GtpConnection():

    def __init__(self, go_engine, board, debug_mode = False, time = 1):
        """
        Manage a GTP connection for a Go-playing engine
        Parameters
        ----------
        go_engine:
            a program that can reply to a set of GTP commandsbelow
        board: 
            Represents the current board state.
        """
        self._debug_mode = debug_mode
        self.go_engine = go_engine
        self.board = board
        self.time = time
        self.commands = {
            "protocol_version": self.protocol_version_cmd,
            "quit": self.quit_cmd,
            "name": self.name_cmd,
            "boardsize": self.boardsize_cmd,
            "timelimit":self.timelimit_cmd,
            #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            "showboard": self.showboard_cmd,
            "clear_board": self.clear_board_cmd,
            "komi": self.komi_cmd,
            "version": self.version_cmd,
            "known_command": self.known_command_cmd,
            "genmove": self.genmove_cmd,
            "list_commands": self.list_commands_cmd,
            "play": self.play_cmd,
            "solve": self.solve_cmd,
            #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            "legal_moves": self.legal_moves_cmd,
            "gogui-rules_game_id": self.gogui_rules_game_id_cmd,
            "gogui-rules_board_size": self.gogui_rules_board_size_cmd,
            "gogui-rules_legal_moves": self.gogui_rules_legal_moves_cmd,
            "gogui-rules_side_to_move": self.gogui_rules_side_to_move_cmd,
            "gogui-rules_board": self.gogui_rules_board_cmd,
            "gogui-rules_final_result": self.gogui_rules_final_result_cmd,
            "gogui-analyze_commands": self.gogui_analyze_cmd
        }

        # used for argument checking
        # values: (required number of arguments, 
        #          error message on argnum failure)
        self.argmap = {
            "boardsize": (1, 'Usage: boardsize INT'),
            "komi": (1, 'Usage: komi FLOAT'),
            "known_command": (1, 'Usage: known_command CMD_NAME'),
            "genmove": (1, 'Usage: genmove {w,b}'),
            "play": (2, 'Usage: play {b,w} MOVE'),
            "legal_moves": (1, 'Usage: legal_moves {w,b}'),
            "timelimit": (1, 'Usage: timelimit INT')
            #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        }
    
    def write(self, data):
        stdout.write(data) 

    def flush(self):
        stdout.flush()

    def start_connection(self):
        """
        Start a GTP connection. 
        This function continuously monitors standard input for commands.
        """
        line = stdin.readline()
        while line:
            self.get_cmd(line)
            line = stdin.readline()

    def get_cmd(self, command):
        """
        Parse command string and execute it
        """
        if len(command.strip(' \r\t')) == 0:
            return
        if command[0] == '#':
            return
        # Strip leading numbers from regression tests
        if command[0].isdigit():
            command = re.sub("^\d+", "", command).lstrip()

        elements = command.split()
        if not elements:
            return
        command_name = elements[0]; args = elements[1:]
        if self.has_arg_error(command_name, len(args)):
            return
        if command_name in self.commands:
            try:
                self.commands[command_name](args)
            except Exception as e:
                self.debug_msg("Error executing command {}\n".format(str(e)))
                self.debug_msg("Stack Trace:\n{}\n".
                               format(traceback.format_exc()))
                raise e
        else:
            self.debug_msg("Unknown command: {}\n".format(command_name))
            self.error('Unknown command')
            stdout.flush()

    def has_arg_error(self, cmd, argnum):
        """
        Verify the number of arguments of cmd.
        argnum is the number of parsed arguments
        """
        if cmd in self.argmap and self.argmap[cmd][0] != argnum:
            self.error(self.argmap[cmd][1])
            return True
        return False

    def debug_msg(self, msg):
        """ Write msg to the debug stream """
        if self._debug_mode:
            stderr.write(msg)
            stderr.flush()

    def error(self, error_msg):
        """ Send error msg to stdout """
        stdout.write('? {}\n\n'.format(error_msg))
        stdout.flush()

    def respond(self, response=''):
        """ Send response to stdout """
        stdout.write('= {}\n\n'.format(response))
        stdout.flush()

    def reset(self, size):
        """
        Reset the board to empty board of given size
        """
        self.board.reset(size)

    def board2d(self):
        return str(GoBoardUtil.get_twoD_board(self.board))
        
    def protocol_version_cmd(self, args):
        """ Return the GTP protocol version being used (always 2) """
        self.respond('2')

    def quit_cmd(self, args):
        """ Quit game and exit the GTP interface """
        self.respond()
        exit()

    def name_cmd(self, args):
        """ Return the name of the Go engine """
        self.respond(self.go_engine.name)

    def version_cmd(self, args):
        """ Return the version of the  Go engine """
        self.respond(self.go_engine.version)

    def clear_board_cmd(self, args):
        """ clear the board """
        self.reset(self.board.size)
        self.respond()

    def boardsize_cmd(self, args):
        """
        Reset the game with new boardsize args[0]
        """
        self.reset(int(args[0]))
        self.respond()

    def showboard_cmd(self, args):
        self.respond('\n' + self.board2d())    
        
   #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~   
        
    #given the timelimit
    def timelimit_cmd(self, args):
        
        assert 1 <= int(args[0]) <= 100
        self.reset_time(int(args[0])) 
        #self.respond(self.time)
        self.respond()

    def reset_time(self, new_time):

        self.time = new_time
        

    def solve_cmd(self, args):
        
        #alphabeta_limited_search
        #evaluation function, heuristic function
        
        start = time.clock()
        result = self.callAlphabetaDL(4)
        end = time.clock() - start

        if end > self.time:
            self.respond("unknown")
            return
        else:
                
            resulting_list = result[1]
            
            if resulting_list == []:
                if result[0] == 0:
                    self.respond("draw")
                    return
                elif result[0] == 1:
                    if self.board.current_player == 1:
                        self.respond("b")
                        return
                    if self.board.current_player == 2:
                        self.respond("w")
                        return
                elif result[0] == -1:
                    if GoBoardUtil.opponent(self.board.current_player) == 1:
                        self.respond("b")
                        return
                    if GoBoardUtil.opponent(self.board.current_player) == 2:
                        self.respond("w")
                        return
                    
            if result[0] == 0: # draw
                for i in resulting_list:
                    coords = point_to_coord(i, self.board.size)
                    ans = format_point(coords)
                    self.respond("draw  " + ans)
            elif result[0] == 1: # our win
                if self.board.current_player == 1:
                    coords = point_to_coord(resulting_list[0], self.board.size)
                    ans = format_point(coords)
                    self.respond("b " + ans)
                    return
                if self.board.current_player == 2:
                    coords = point_to_coord(resulting_list[0], self.board.size)
                    ans = format_point(coords)
                    self.respond("w " + ans)
                    return
            elif result[0] == -1: # opponent wins
                if GoBoardUtil.opponent(self.board.current_player) == 1:
                    coords = point_to_coord(resulting_list[0], self.board.size)
                    ans = format_point(coords)
                    self.respond("b")
                    return  
                elif GoBoardUtil.opponent(self.board.current_player) == 2:
                    coords = point_to_coord(resulting_list[0], self.board.size)
                    ans = format_point(coords)
                    self.respond("w")
                    return  
            return
        
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
               
    def alphabetaDL(self, alpha, beta, depth):
        
        moves = self.board.get_empty_points()
        board_full = (len(moves) == 0)   #board full check 
        win_step = []  
        if self.board.check_game_end_gomoku()[0] or depth == 0 or board_full: #checking end game, no depth, draw
            return self.staticallyEvaluateForToPlay() 
        for move in GoBoardUtil.generate_legal_moves_gomoku(self.board): #moves inlegal move
            self.board.play_move_gomoku(move, self.board.current_player) #play a stone
            value = -self.alphabetaDL(-beta, -alpha, depth - 1)[0] #alphabeta search
            if value > alpha:
                alpha = value
                win_step.clear()
                win_step.append(move)
                '''
            if value == alpha:
                win_step.append(move)'''
            self.board.undo(move)
            if value >= beta: 
                return beta,win_step # or value in failsoft (later)
                
        return alpha,win_step
    
    # initial call with full window
    
    def callAlphabetaDL(self, depth):
        
        return self.alphabetaDL(-INFINITY, INFINITY, depth)
    
    def staticallyEvaluateForToPlay(self):
        
        game_end, winner = self.board.check_game_end_gomoku()
        assert winner != self.board.current_player
        if winner == None:
            return 0,[]
        
        else: return -1,[]
        
     #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~   
        
    def komi_cmd(self, args):
        """
        Set the engine's komi to args[0]
        """
        self.go_engine.komi = float(args[0])
        self.respond()

    def known_command_cmd(self, args):
        """
        Check if command args[0] is known to the GTP interface
        """
        if args[0] in self.commands:
            self.respond("true")
        else:
            self.respond("false")

    def list_commands_cmd(self, args):
        """ list all supported GTP commands """
        self.respond(' '.join(list(self.commands.keys())))

    def legal_moves_cmd(self, args):
        """
        List legal moves for color args[0] in {'b','w'}
        """
        board_color = args[0].lower()
        color = color_to_int(board_color)
        moves = GoBoardUtil.generate_legal_moves(self.board, color)
        gtp_moves = []
        for move in moves:
            coords = point_to_coord(move, self.board.size)
            gtp_moves.append(format_point(coords))
        sorted_moves = ' '.join(sorted(gtp_moves))
        self.respond(sorted_moves)

    def play_cmd(self, args):
        """
        play a move args[1] for given color args[0] in {'b','w'}
        """
        try:
            board_color = args[0].lower()
            board_move = args[1]
            if board_color != "b" and board_color !="w":
                self.respond("illegal move: \"{}\" wrong color".format(board_color))
                return
            color = color_to_int(board_color)
            if args[1].lower() == 'pass':
                self.board.play_move(PASS, color)
                self.board.current_player = GoBoardUtil.opponent(color)
                self.respond()
                return
            coord = move_to_coord(args[1], self.board.size)
            if coord:
                move = coord_to_point(coord[0],coord[1], self.board.size)
            else:
                self.error("Error executing move {} converted from {}"
                           .format(move, args[1]))
                return
            if not self.board.play_move_gomoku(move, color):
                self.respond("illegal move: \"{}\" occupied".format(board_move))
                return
            else:
                self.debug_msg("Move: {}\nBoard:\n{}\n".
                                format(board_move, self.board2d()))
            self.respond()
        except Exception as e:
            self.respond('{}'.format(str(e)))

    def genmove_cmd(self, args):
        """
        Generate a move for the color args[0] in {'b', 'w'}, for the game of gomoku.
        """
        board_color = args[0].lower()
        color = color_to_int(board_color)
        game_end, winner = self.board.check_game_end_gomoku()
        start = time.clock()
        result = self.callAlphabetaDL(4)
        end = time.clock() - start
        if game_end:
            if winner == color:
                self.respond("pass")
            else:
                self.respond("resign")
            return
        else:
            #win_moves is a list. If toplayer is losing or draw, it only has None, else is has moves that lead him to win
            #win_moves = self.solve_cmd(args)
            win_moves = result[1]
            if end > self.time or result[0] == -1:
                move = GoBoardUtil.generate_random_move_gomoku(self.board)
            if move == PASS:
                self.respond("pass")
                return
        move = win_moves[0]
        '''
        if result[0] == -1:
            #move = self.go_engine.get_move(self.board, color)
            move = GoBoardUtil.generate_random_move_gomoku(self.board)
            if move == PASS:
                self.respond("pass")
                return
        '''
        move_coord = point_to_coord(move, self.board.size)
        move_as_string = format_point(move_coord)
        if self.board.is_legal_gomoku(move, color):
            self.board.play_move_gomoku(move, color)
            self.respond(move_as_string)
        else:
            self.respond("illegal move: {}".format(move_as_string))
        #~~
    def final_result_helper(self):
        # check lines of the board
        board_cc = self.board.board[:-1]
        board_aa = np.array(board_cc).reshape(self.board.size + 2, self.board.size + 1)
        for row in board_aa:
            checking_row_list = [(k, len(list(v))) for k, v in itertools.groupby(row)]
            for i in range(len(checking_row_list)):
                
                if i + 1 < len(checking_row_list):
                    if i + 2 > len(checking_row_list):
                        if checking_row_list[i][1] >= 4 and checking_row_list[i+1][0] == 0:
                            return checking_row_list[i][0]
                    else:
                        if checking_row_list[i][0] == checking_row_list[i+2][0] and checking_row_list[i][1] + checking_row_list[i+2][1] >= 4 and checking_row_list[i+1][0] == 0 and checking_row_list[i+1][1] == 1:
                            return checking_row_list[i][0]
        # check column
        for num in range(self.board.size):
            col = [row[num] for row in board_aa]
            checking_col_list = [(k, len(list(v))) for k, v in itertools.groupby(col)]
            for i in checking_col_list:

                if i + 1 < len(checking_row_list):
                    if i + 2 > len(checking_row_list):
                        if checking_row_list[i][1] >= 4 and checking_row_list[i+1][0] == 0:
                            return checking_row_list[i][0]
                    else:
                        if checking_row_list[i][0] == checking_row_list[i+2][0] and checking_row_list[i][1] + checking_row_list[i+2][1] >= 4 and checking_row_list[i+1][0] == 0 and checking_row_list[i+1][1] == 1:
                            return checking_row_list[i][0]

        # check diagonal
        row_left = len(board_aa)
        col_left = len(board_aa[0])
        lim = 0

        result_left = []  # this will make a diagonal left solution list
        for i in range(row_left):
            for j in range(lim, col_left):  # forward j
                sub_re = []
                i1, j1 = i, j
                while i1 <= row_left - 1 and j1 >= 0:
                    sub_re.append(board_aa[i1][j1])
                    j1 -= 1
                    i1 += 1
                if i == 0 and j == col_left - 1:
                    lim = col_left - 1
                result_left.append(sub_re)

        for u in result_left:
            checking_dia_left_list = [(k, len(list(v))) for k, v in itertools.groupby(u)]
            for i in checking_dia_left_list:

                if i + 1 < len(checking_row_list):
                    if i + 2 > len(checking_row_list):
                        if checking_row_list[i][1] >= 4 and checking_row_list[i+1][0] == 0:
                            return checking_row_list[i][0]
                    else:
                        if checking_row_list[i][0] == checking_row_list[i+2][0] and checking_row_list[i][1] + checking_row_list[i+2][1] >= 4 and checking_row_list[i+1][0] == 0 and checking_row_list[i+1][1] == 1:
                            return checking_row_list[i][0]

        row_right = len(board_aa)
        col_right = len(board_aa[0])
        col2_right = col_right
        result_right = []  # this will make a diagonl right solution list

        for i in range(row_right):
            for j in range(col2_right - 1, -1, -1):  # backward j
                sub_re = []
                i1, j1 = i, j
                while i1 <= row_right - 1 and j1 <= col_right - 1:
                    sub_re.append(board_aa[i1][j1])
                    j1 += 1
                    i1 += 1
                result_right.append(sub_re)
                if i == 0 and j == 0:  # when achieve the (0,0)let j = 0stable
                    col2_right = 1

        for u in result_right:
            checking_dia_right_list = [(k, len(list(v))) for k, v in itertools.groupby(u)]
            for i in checking_dia_right_list:

                if i + 1 < len(checking_row_list):
                    if i + 2 > len(checking_row_list):
                        if checking_row_list[i][1] >= 4 and checking_row_list[i+1][0] == 0:
                            return checking_row_list[i][0]
                    else:
                        if checking_row_list[i][0] == checking_row_list[i+2][0] and checking_row_list[i][1] + checking_row_list[i+2][1] >= 4 and checking_row_list[i+1][0] == 0 and checking_row_list[i+1][1] == 1:
                            return checking_row_list[i][0]

        # if game still running return unknown
        return 'unknown'

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~        
    def gogui_rules_game_id_cmd(self, args):
        self.respond("Gomoku")
    
    def gogui_rules_board_size_cmd(self, args):
        self.respond(str(self.board.size))
    
    def legal_moves_cmd(self, args):
        """
            List legal moves for color args[0] in {'b','w'}
            """
        board_color = args[0].lower()
        color = color_to_int(board_color)
        moves = GoBoardUtil.generate_legal_moves(self.board, color)
        gtp_moves = []
        for move in moves:
            coords = point_to_coord(move, self.board.size)
            gtp_moves.append(format_point(coords))
        sorted_moves = ' '.join(sorted(gtp_moves))
        self.respond(sorted_moves)

    def gogui_rules_legal_moves_cmd(self, args):
        game_end,_ = self.board.check_game_end_gomoku()
        if game_end:
            self.respond()
            return
        moves = GoBoardUtil.generate_legal_moves_gomoku(self.board)
        gtp_moves = []
        for move in moves:
            coords = point_to_coord(move, self.board.size)
            gtp_moves.append(format_point(coords))
        sorted_moves = ' '.join(sorted(gtp_moves))
        self.respond(sorted_moves)
    
    def gogui_rules_side_to_move_cmd(self, args):
        color = "black" if self.board.current_player == BLACK else "white"
        self.respond(color)
    
    def gogui_rules_board_cmd(self, args):
        size = self.board.size
        str = ''
        for row in range(size-1, -1, -1):
            start = self.board.row_start(row + 1)
            for i in range(size):
                point = self.board.board[start + i]
                if point == BLACK:
                    str += 'X'
                elif point == WHITE:
                    str += 'O'
                elif point == EMPTY:
                    str += '.'
                else:
                    assert False
            str += '\n'
        self.respond(str)
    
    def gogui_rules_final_result_cmd(self, args):
        game_end, winner = self.board.check_game_end_gomoku()
        moves = self.board.get_empty_points()
        board_full = (len(moves) == 0)
        if board_full and not game_end:
            self.respond("draw")
            return
        if game_end:
            color = "black" if winner == BLACK else "white"
            self.respond(color)
        else:
            self.respond("unknown")

    def gogui_analyze_cmd(self, args):
        self.respond("pstring/Legal Moves For ToPlay/gogui-rules_legal_moves\n"
                     "pstring/Side to Play/gogui-rules_side_to_move\n"
                     "pstring/Final Result/gogui-rules_final_result\n"
                     "pstring/Board Size/gogui-rules_board_size\n"
                     "pstring/Rules GameID/gogui-rules_game_id\n"
                     "pstring/Show Board/gogui-rules_board\n"
                     )

def point_to_coord(point, boardsize):
    """
    Transform point given as board array index 
    to (row, col) coordinate representation.
    Special case: PASS is not transformed
    """
    if point == PASS:
        return PASS
    else:
        NS = boardsize + 1
        return divmod(point, NS)

def format_point(move):
    """
    Return move coordinates as a string such as 'a1', or 'pass'.
    """
    column_letters = "ABCDEFGHJKLMNOPQRSTUVWXYZ"
    #column_letters = "abcdefghjklmnopqrstuvwxyz"
    if move == PASS:
        return "pass"
    row, col = move
    if not 0 <= row < MAXSIZE or not 0 <= col < MAXSIZE:
        raise ValueError
    return column_letters[col - 1]+ str(row) 
    
def move_to_coord(point_str, board_size):
    """
    Convert a string point_str representing a point, as specified by GTP,
    to a pair of coordinates (row, col) in range 1 .. board_size.
    Raises ValueError if point_str is invalid
    """
    if not 2 <= board_size <= MAXSIZE:
        raise ValueError("board_size out of range")
    s = point_str.lower()
    if s == "pass":
        return PASS
    try:
        col_c = s[0]
        if (not "a" <= col_c <= "z") or col_c == "i":
            raise ValueError
        col = ord(col_c) - ord("a")
        if col_c < "i":
            col += 1
        row = int(s[1:])
        if row < 1:
            raise ValueError
    except (IndexError, ValueError):
        raise ValueError("illegal move: \"{}\" wrong coordinate".format(s))
    if not (col <= board_size and row <= board_size):
        raise ValueError("illegal move: \"{}\" wrong coordinate".format(s))
    return row, col

def color_to_int(c):
    """convert character to the appropriate integer code"""
    color_to_int = {"b": BLACK , "w": WHITE, "e": EMPTY, 
                    "BORDER": BORDER}
    return color_to_int[c] 

def overtime(total_time, time):
        
    assert int(total_time) <= int(time)
