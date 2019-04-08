"""
simple_board.py

Implements a basic Go board with functions to:
- initialize to a given board size
- check if a move is legal
- play a move

The board uses a 1-dimensional representation with padding
"""

import numpy as np
from board_util import GoBoardUtil, BLACK, WHITE, EMPTY, BORDER, \
                       PASS, is_black_white, coord_to_point, where1d, \
                       MAXSIZE, NULLPOINT
import alphabeta
point_list = [[200]]

class SimpleGoBoard(object):

    def get_color(self, point):
        return self.board[point]

    def pt(self, row, col):
        return coord_to_point(row, col, self.size)

    def is_legal(self, point, color):
        """
        Check whether it is legal for color to play on point
        """
        assert is_black_white(color)
        # Special cases
        if point == PASS:
            return True
        elif self.board[point] != EMPTY:
            return False
        if point == self.ko_recapture:
            return False

        # General case: detect captures, suicide
        opp_color = GoBoardUtil.opponent(color)
        self.board[point] = color
        legal = True
        has_capture = self._detect_captures(point, opp_color)
        if not has_capture and not self._stone_has_liberty(point):
            block = self._block_of(point)
            if not self._has_liberty(block): # suicide
                legal = False
        self.board[point] = EMPTY
        return legal

    def _detect_captures(self, point, opp_color):
        """
        Did move on point capture something?
        """
        for nb in self.neighbors_of_color(point, opp_color):
            if self._detect_capture(nb):
                return True
        return False

    def get_empty_points(self):
        """
        Return:
            The empty points on the board
        """
        return where1d(self.board == EMPTY)

    def __init__(self, size):
        """
        Creates a Go board of given size
        """
        assert 2 <= size <= MAXSIZE
        self.reset(size)

    def reset(self, size):
        """
        Creates a start state, an empty board with the given size
        The board is stored as a one-dimensional array
        See GoBoardUtil.coord_to_point for explanations of the array encoding
        """
        self.size = size
        self.NS = size + 1
        self.WE = 1
        self.ko_recapture = None
        self.current_player = BLACK
        self.maxpoint = size * size + 3 * (size + 1)
        self.board = np.full(self.maxpoint, BORDER, dtype = np.int32)
        self.liberty_of = np.full(self.maxpoint, NULLPOINT, dtype = np.int32)
        self._initialize_empty_points(self.board)
        self._initialize_neighbors()
        self.score_black = [-1, -1, -1, -1, -1, -1, -1, -1,
                            -1, 1, 1, 1, 1, 1, 1, 1,
                            -1, 1, 2, 2, 2, 2, 2, 1,
                            -1, 1, 2, 3, 3, 3, 2, 1,
                            -1, 1, 2, 3, 4, 3, 2, 1,
                            -1, 1, 2, 3, 3, 3, 2, 1,
                            -1, 1, 2, 2, 2, 2, 2, 1,
                            -1, 1, 1, 1, 1, 1, 1, 1,
                            -1, -1, -1, -1, -1, -1, -1, -1, -1]
        self.score_white = [-1, -1, -1, -1, -1, -1, -1, -1,
                            -1, 1, 1, 1, 1, 1, 1, 1,
                            -1, 1, 2, 2, 2, 2, 2, 1,
                            -1, 1, 2, 3, 3, 3, 2, 1,
                            -1, 1, 2, 3, 4, 3, 2, 1,
                            -1, 1, 2, 3, 3, 3, 2, 1,
                            -1, 1, 2, 2, 2, 2, 2, 1,
                            -1, 1, 1, 1, 1, 1, 1, 1,
                            -1, -1, -1, -1, -1, -1, -1, -1, -1]

    def _initialize_score_board(self):
        self.score_black = [-1, -1, -1, -1, -1, -1, -1, -1,
                            -1, 1, 1, 1, 1, 1, 1, 1,
                            -1, 1, 2, 2, 2, 2, 2, 1,
                            -1, 1, 2, 3, 3, 3, 2, 1,
                            -1, 1, 2, 3, 4, 3, 2, 1,
                            -1, 1, 2, 3, 3, 3, 2, 1,
                            -1, 1, 2, 2, 2, 2, 2, 1,
                            -1, 1, 1, 1, 1, 1, 1, 1,
                            -1, -1, -1, -1, -1, -1, -1, -1, -1]
        self.score_white = [-1, -1, -1, -1, -1, -1, -1, -1,
                            -1, 1, 1, 1, 1, 1, 1, 1,
                            -1, 1, 2, 2, 2, 2, 2, 1,
                            -1, 1, 2, 3, 3, 3, 2, 1,
                            -1, 1, 2, 3, 4, 3, 2, 1,
                            -1, 1, 2, 3, 3, 3, 2, 1,
                            -1, 1, 2, 2, 2, 2, 2, 1,
                            -1, 1, 1, 1, 1, 1, 1, 1,
                            -1, -1, -1, -1, -1, -1, -1, -1, -1]
        white_points = where1d(self.board == WHITE)
        black_points = where1d(self.board == BLACK)
        non = np.append(white_points, black_points)
        for i in non:
            self.score_black[i] = -2000000
            self.score_white[i] = -2000000

    def copy(self):
        b = SimpleGoBoard(self.size)
        assert b.NS == self.NS
        assert b.WE == self.WE
        b.ko_recapture = self.ko_recapture
        b.current_player = self.current_player
        assert b.maxpoint == self.maxpoint
        b.board = np.copy(self.board)
        return b

    def row_start(self, row):
        assert row >= 1
        assert row <= self.size
        return row * self.NS + 1

    def _initialize_empty_points(self, board):
        """
        Fills points on the board with EMPTY
        Argument
        ---------
        board: numpy array, filled with BORDER
        """
        for row in range(1, self.size + 1):
            start = self.row_start(row)
            board[start : start + self.size] = EMPTY

    def _on_board_neighbors(self, point):
        nbs = []
        for nb in self._neighbors(point):
            if self.board[nb] != BORDER:
                nbs.append(nb)
        return nbs

    def _initialize_neighbors(self):
        """
        precompute neighbor array.
        For each point on the board, store its list of on-the-board neighbors
        """
        self.neighbors = []
        for point in range(self.maxpoint):
            if self.board[point] == BORDER:
                self.neighbors.append([])
            else:
                self.neighbors.append(self._on_board_neighbors(point))

    def is_eye(self, point, color):
        """
        Check if point is a simple eye for color
        """
        if not self._is_surrounded(point, color):
            return False
        # Eye-like shape. Check diagonals to detect false eye
        opp_color = GoBoardUtil.opponent(color)
        false_count = 0
        at_edge = 0
        for d in self._diag_neighbors(point):
            if self.board[d] == BORDER:
                at_edge = 1
            elif self.board[d] == opp_color:
                false_count += 1
        return false_count <= 1 - at_edge # 0 at edge, 1 in center

    def _is_surrounded(self, point, color):
        """
        check whether empty point is surrounded by stones of color.
        """
        for nb in self.neighbors[point]:
            nb_color = self.board[nb]
            if nb_color != color:
                return False
        return True

    def _stone_has_liberty(self, stone):
        lib = self.find_neighbor_of_color(stone, EMPTY)
        return lib != None

    def _get_liberty(self, block):
        """
        Find any liberty of the given block.
        Returns None in case there is no liberty.
        block is a numpy boolean array
        """
        for stone in where1d(block):
            lib = self.find_neighbor_of_color(stone, EMPTY)
            if lib != None:
                return lib
        return None

    def _has_liberty(self, block):
        """
        Check if the given block has any liberty.
        Also updates the liberty_of array.
        block is a numpy boolean array
        """
        lib = self._get_liberty(block)
        if lib != None:
            assert self.get_color(lib) == EMPTY
            for stone in where1d(block):
                self.liberty_of[stone] = lib
            return True
        return False

    def _block_of(self, stone):
        """
        Find the block of given stone
        Returns a board of boolean markers which are set for
        all the points in the block
        """
        marker = np.full(self.maxpoint, False, dtype = bool)
        pointstack = [stone]
        color = self.get_color(stone)
        assert is_black_white(color)
        marker[stone] = True
        while pointstack:
            p = pointstack.pop()
            neighbors = self.neighbors_of_color(p, color)
            for nb in neighbors:
                if not marker[nb]:
                    marker[nb] = True
                    pointstack.append(nb)
        return marker

    def _fast_liberty_check(self, nb_point):
        lib = self.liberty_of[nb_point]
        if lib != NULLPOINT and self.get_color(lib) == EMPTY:
            return True # quick exit, block has a liberty
        if self._stone_has_liberty(nb_point):
            return True # quick exit, no need to look at whole block
        return False

    def _detect_capture(self, nb_point):
        """
        Check whether opponent block on nb_point is captured.
        Returns boolean.
        """
        if self._fast_liberty_check(nb_point):
            return False
        opp_block = self._block_of(nb_point)
        return not self._has_liberty(opp_block)

    def _detect_and_process_capture(self, nb_point):
        """
        Check whether opponent block on nb_point is captured.
        If yes, remove the stones.
        Returns the stone if only a single stone was captured,
            and returns None otherwise.
        This result is used in play_move to check for possible ko
        """
        if self._fast_liberty_check(nb_point):
            return None
        opp_block = self._block_of(nb_point)
        if self._has_liberty(opp_block):
            return None
        captures = list(where1d(opp_block))
        self.board[captures] = EMPTY
        self.liberty_of[captures] = NULLPOINT
        single_capture = None
        if len(captures) == 1:
            single_capture = nb_point
        return single_capture

    def play_move(self, point, color):
        """
        Play a move of color on point
        Returns boolean: whether move was legal
        """
        assert is_black_white(color)
        # Special cases
        if point == PASS:
            self.ko_recapture = None
            self.current_player = GoBoardUtil.opponent(color)
            return True
        elif self.board[point] != EMPTY:
            return False
        if point == self.ko_recapture:
            return False

        # General case: deal with captures, suicide, and next ko point
        opp_color = GoBoardUtil.opponent(color)
        in_enemy_eye = self._is_surrounded(point, opp_color)
        self.board[point] = color
        single_captures = []
        neighbors = self.neighbors[point]
        for nb in neighbors:
            if self.board[nb] == opp_color:
                single_capture = self._detect_and_process_capture(nb)
                if single_capture != None:
                    single_captures.append(single_capture)
        if not self._stone_has_liberty(point):
            # check suicide of whole block
            block = self._block_of(point)
            if not self._has_liberty(block): # undo suicide move
                self.board[point] = EMPTY
                return False
        self.ko_recapture = None
        if in_enemy_eye and len(single_captures) == 1:
            self.ko_recapture = single_captures[0]
        self.current_player = GoBoardUtil.opponent(color)
        return True

    def neighbors_of_color(self, point, color):
        """ List of neighbors of point of given color """
        nbc = []
        for nb in self.neighbors[point]:
            if self.get_color(nb) == color:
                nbc.append(nb)
        return nbc

    def find_neighbor_of_color(self, point, color):
        """ Return one neighbor of point of given color, or None """
        for nb in self.neighbors[point]:
            if self.get_color(nb) == color:
                return nb
        return None

    def _neighbors(self, point):
        """ List of all four neighbors of the point """
        return [point - 1, point + 1, point - self.NS, point + self.NS]

    def _diag_neighbors(self, point):
        """ List of all four diagonal neighbors of point """
        return [point - self.NS - 1,
                point - self.NS + 1,
                point + self.NS - 1,
                point + self.NS + 1]

    def _point_to_coord(self, point):
        """
        Transform point index to row, col.

        Arguments
        ---------
        point

        Returns
        -------
        x , y : int
        coordination of the board  1<= x <=size, 1<= y <=size .
        """
        if point is None:
            return 'pass'
        row, col = divmod(point, self.NS)
        return row, col

    def is_legal_gomoku(self, point, color):
        """
            Check whether it is legal for color to play on point, for the game of gomoku
            """
        return self.board[point] == EMPTY

    def play_move_gomoku(self, point, color):
        """
            Play a move of color on point, for the game of gomoku
            Returns boolean: whether move was legal
            """
        assert is_black_white(color)
        assert point != PASS
        if self.board[point] != EMPTY:
            return False
        self.board[point] = color
        #self.score_black[point] = -2000000
        #self.score_white[point] = -2000000
        self.current_player = GoBoardUtil.opponent(color)
        return True

    def _point_direction_check_connect_gomoko(self, point, shift):
        """
        Check if the point has connect5 condition in a direction
        for the game of Gomoko.
        """
        color = self.board[point]
        count = 1
        d = shift
        p = point
        while True:
            p = p + d
            if self.board[p] == color:
                count = count + 1
                if count == 5:
                    break
            else:
                break
        d = -d
        p = point
        while True:
            p = p + d
            if self.board[p] == color:
                count = count + 1
                if count == 5:
                    break
            else:
                break
        assert count <= 5
        return count == 5

    def point_check_game_end_gomoku(self, point):
        """
            Check if the point causes the game end for the game of Gomoko.
            """
        # check horizontal
        if self._point_direction_check_connect_gomoko(point, 1):
            return True

        # check vertical
        if self._point_direction_check_connect_gomoko(point, self.NS):
            return True

        # check y=x
        if self._point_direction_check_connect_gomoko(point, self.NS + 1):
            return True

        # check y=-x
        if self._point_direction_check_connect_gomoko(point, self.NS - 1):
            return True

        return False

    def check_game_end_gomoku(self):
        """
            Check if the game ends for the game of Gomoku.
            """
        white_points = where1d(self.board == WHITE)
        black_points = where1d(self.board == BLACK)

        for point in white_points:
            if self.point_check_game_end_gomoku(point):
                return True, WHITE

        for point in black_points:
            if self.point_check_game_end_gomoku(point):
                return True, BLACK

        return False, None

    def solve(self):
        result, move, drawMove = alphabeta.solve(self)
        if move=="First":
            if result==0:
                return 'draw',drawMove
            else:
                winner='w' if self.current_player!=WHITE else 'b'
                return winner,'NoMove'
        elif move=="NoMove":
            if result:
                return 'draw', drawMove
            else:
                winner='w' if self.current_player!=WHITE else 'b'
                return winner, move
        else:
            winner='w' if self.current_player==WHITE else 'b'
            return winner, move

    def check_pattern(self,point,have,new,direction_x,direction_y,moveSet,patternList,color,flag):

        for i in range(len(patternList)):
            if have in patternList[i]:
                #print(point_list)
                for j in point_list:
                    token = 0
                    for w in new:
                        if w in j:
                            toekn += 1
                    #print(1)
                    if token < len(new):
                        #print(2)

                        for dis in patternList[i][have]:
                            #moveSet[i].add(point-direction_x*(dis+1)-direction_y*self.NS*(dis+1))
                            moveSet[i].append(point-direction_x*(dis+1)-direction_y*self.NS*(dis+1))
                        #flag[0]=True
                        #print(moveSet)
                        point_list.append(new)
                        break
        if (not (0<= point<len(self.board))) or len(have)==9:
            return
        #if self.get_color(point)==BORDER or len(have)==7:
        #            return
        piece=self.get_color(point)

        if piece==EMPTY:
            piece='.'
        elif piece==color:
            piece='x'
        elif piece == BORDER:
            piece='B'
        else:
            piece='o'

        have+=piece
        new.append(point)
        #print(GoBoardUtil.format_point(self._point_to_coord(point)),have,self.board[point])
        self.check_pattern(point+direction_x+direction_y*self.NS,have,new,direction_x,direction_y,moveSet,patternList,color,flag)

    def get_pattern_moves(self):
        """
        1. direct winning point xxxx. x.xxx xx.xx
        2. urgent blocking point xoooo.
        3. wining in 2 step point
        """
        if len(self.get_empty_points())==0:
            return [None],None
        self._initialize_score_board()
        moveSet=[[], [], [], [], [], [], [], [], [], [], []]
        #moveSet=[set(),set(),set(),set(),set(),set(),set(),set()]
        SL = [1000000, 900000, 500000, 200000, 90000, 40000, 25000, 10000, 4500, 2000, 500]
        color=self.current_player

        patternList=[{'xxxx.':{0},'xxx.x':{1},'xx.xx':{2},'x.xxx':{3},'.xxxx':{4}}, #win - 1 000 000
                     {'oooo.':{0},'ooo.o':{1},'oo.oo':{2},'o.ooo':{3},'.oooo':{4}}, #block win - 900 000
                     {'.xxx..':{1},'..xxx.':{4},'.xx.x.':{2},'.x.xx.':{3}}, #make-open-four - 500 000
                     {'.ooo..':{1,5},'..ooo.':{0,4},'.oo.o.':{0,2,5},'.o.oo.':{0,3,5}, 'B.ooo..':{0}, '..ooo.B':{6}, 'x.ooo..':{0}, '..ooo.x':{6}}, #block-open-four - 200 000
                     {'Bxxx..':{0,1}, 'oxxx..':{0,1}, '..xxxB':{0,1}, '..xxxo':{0,1}, 'Bxx.x.':{0,2}, '.xx.xB':{2,5}, 'oxx.x.':{0,2}, '.xx.xo':{2,5},'ox.xx.':{0,3}, '.x.xxo':{3,5}, 'Bx.xx.':{0,3}, '.x.xxB':{3,5}}, #make-dead-four - 90 000
                     {'..xx...':{2}, '...xx..':{4}, '..x.x..':{3}}, #make-super-open-three - 40 000
                     {'o.xx...':{2},'B.xx...':{2}, '...xx.o':{4}, '...xx.B':{4}, 'o.x.x..':{3}, 'B.x.x..':{3}, '..x.x.o':{3}, '..x.x.B':{3}}, #make-low-open-three - 25 000
                     {'..oo.':{0,3}, '.oo..':{1,4}, '.o.o.':{0,2,4}, '..oo.x':{5}, 'x.oo..': {0}, '..oo.B':{5}, 'B.oo..': {0}}, #block_open_three - 10 000
                     {'.x...':{1,2}, '..x..':{1,3}, '...x.':{2,3}}, #make-open-two - 4500
                     {'oxx...':{1,2}, 'Bxx...':{1,2}, '...xxo':{3,4}, '...xxB':{3,4}, 'o.xx..o':{2}, 'o..xx.o':{4}, 'o.x.x.o':{3}}, #make-dead-three - 2000
                     {'ox....':{3}, 'Bx....':{3}, '....xo':{2}, '....xB':{2}} #make-dead-two - 500
                     ]

        direction_x=[1,0,1,-1]
        direction_y=[0,1,1,1]
        flag=[False]

        for point in range(0, len(self.board)):
            if flag[0]:
                break
            for direction in range(0,4):
                self.check_pattern(point,'',[],direction_x[direction],direction_y[direction],moveSet,patternList,color,flag)
        #print(point_list)
        point_list = [[200]]

        '''
        for i in range(len(moveSet)):
            moveSet[i] = list(set(moveSet[i]))
        '''

        for i in range(len(moveSet)):
            for j in range(len(moveSet[i])):
                #print(moveSet[i][j], SL[i])
                if color == WHITE:
                    self.score_white[moveSet[i][j]] += SL[i]
                elif color == BLACK:
                    self.score_black[moveSet[i][j]] += SL[i]

        best_score = 0
        best_score_moves = []
        for i in range(len(self.score_black)):
            if color == 2:
                if self.score_white[i] > best_score:
                    best_score = self.score_white[i]
                    best_score_moves.clear()
                    best_score_moves.append(i)
                elif self.score_white[i] == best_score:
                    best_score_moves.append(i)
            if color == 1:
                if self.score_black[i] > best_score:
                    best_score = self.score_black[i]
                    best_score_moves.clear()
                    best_score_moves.append(i)
                elif self.score_black[i] == best_score:
                    best_score_moves.append(i)
        return best_score_moves,best_score
    '''       
    print(moveSet)
    print(self.score_black)
    print(self.score_white)
    '''
    '''
    i=0
    while i<4 and not bool(moveSet[i]): i+=1
    if i==4:
        return None
    else:
        #return i, list(moveSet[i])
        return i, moveSet[i]
    '''

    def list_solve_point(self):
        """
        1. direct winning point xxxx. x.xxx xx.xx
        2. urgent blocking point xoooo.
        3. wining in 2 step point
        """
        moveSet=[set(),set(),set(),set()]
        color=self.current_player

        patternList=[{'xxxx.':{0},'xxx.x':{1},'xx.xx':{2},'x.xxx':{3},'.xxxx':{4}},{'oooo.':{0},'ooo.o':{1},'oo.oo':{2},'o.ooo':{3},'.oooo':{4}},{'.xxx..':{1},'..xxx.':{4},'.xx.x.':{2},'.x.xx.':{3}},{'.ooo..':{1,5},'..ooo.':{0,4},'.oo.o.':{2},'.o.oo.':{3}}]

        direction_x=[1,0,1,-1]
        direction_y=[0,1,1,1]
        flag=[False]

        for point in where1d(self.board!=BORDER):
            if flag[0]:
                break
            for direction in range(0,4):
                    self.check_pattern(point,'',direction_x[direction],direction_y[direction],moveSet,patternList,color,flag)

        i=0
        while i<4 and not bool(moveSet[i]):
            i+=1
        if i==4:
            return None
        else:
            return list(moveSet[i])
