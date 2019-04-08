#!/usr/local/bin/python3
#/usr/bin/python3
# Set the path to your python3 above

from gtp_connection import GtpConnection
from board_util import GoBoardUtil, EMPTY
from simple_board import SimpleGoBoard
from board_util import GoBoardUtil
#from pattern_util import PatternUtil
import numpy as np
import argparse
import sys
from GomokuMCTS import MCTS

def count_at_depth(node, depth, nodesAtDepth):
    if not node._expanded:
        return
    nodesAtDepth[depth] += 1
    for _,child in node._children.items():
        count_at_depth(child, depth+1, nodesAtDepth)

    
def policy_value_fn(actived_features):
    
    return 100000*actived_features[0]+10000*actived_features[1]+5000*actived_features[2]+1000*actived_features[3]+500*actived_features[4]+400*actived_features[5]+100*actived_features[6]+90*actived_features[7]+50*actived_features[8]+10*actived_features[9]+9*actived_features[10]+5*actived_features[11]+2*actived_features[11]+1

def feature1(board,move,color):
    board_copy = board.copy()
    board_copy.play_move_gomoku(move, color)
    

    actived = 1
    return actived    # 0 or 1

def feature2(board,move,color):
    board_copy = board.copy()
    board_copy.play_move_gomoku(move, color)
    

    actived = 1
    return actived    # 0 or 1

def feature3(board,move,color):
    board_copy = board.copy()
    board_copy.play_move_gomoku(move, color)
    

    actived = 1
    return actived    # 0 or 1

def feature4(board,move,color):
    board_copy = board.copy()
    board_copy.play_move_gomoku(move, color)
    

    actived = 1
    return actived    # 0 or 1

def feature5(board,move,color):
    board.play_move_gomoku(move, color)


    undo(board,move)
    actived = 1
    return actived    # 0 or 1

def feature6(board,move,color):
    board.play_move_gomoku(move, color)


    undo(board,move)
    actived = 1
    return actived    # 0 or 1

def feature7(board,move,color):
    board.play_move_gomoku(move, color)


    undo(board,move)
    actived = 1
    return actived    # 0 or 1

def feature8(board,move,color):
    board.play_move_gomoku(move, color)


    undo(board,move)
    actived = 1
    return actived    # 0 or 1

def feature9(board,move,color):
    board.play_move_gomoku(move, color)


    undo(board,move)
    actived = 1
    return actived    # 0 or 1

def feature10(board,move,color):
    board.play_move_gomoku(move, color)


    undo(board,move)
    actived = 1
    return actived    # 0 or 1

def feature11(board,move,color):
    board.play_move_gomoku(move, color)


    undo(board,move)
    actived = 1
    return actived    # 0 or 1

def undo(board,move):
    board.board[move]=EMPTY
    board.current_player=GoBoardUtil.opponent(board.current_player)

def play_move(board, move, color):
    board.play_move_gomoku(move, color)

def game_result(board):
    game_end, winner = board.check_game_end_gomoku()
    moves = board.get_empty_points()
    board_full = (len(moves) == 0)
    if game_end:
        #return 1 if winner == board.current_player else -1
        return winner
    if board_full:
        return 'draw'
    return None

class Gomoku5():

    def __init__(self,num_sim, use_pattern, sim_rule,in_tree_knowledge,size=7,limit=100,exploration=0.4):
        self.name = "Gomoku5"
        self.best_move = None
        self.version = 0.22
        self.MCTS = MCTS()
        self.limit = limit
        self.num_simulation = num_sim
        self.use_pattern = use_pattern
        self.exploration = exploration
        self.sim_rule = sim_rule
        self.in_tree_knowledge = in_tree_knowledge

    def reset(self):
        self.MCTS=MCTS()
    
    def update(self,move):
        self.parent = self.MCTS._root
        self.MCTS.update_with_move(move)
    
    def get_move(self, board, toplay):
        best_move = self.MCTS.get_move(board,toplay,limit=self.limit, use_pattern = self.use_pattern,num_simulation = self.num_simulation,exploration = self.exploration,simulation_policy = self.sim_rule)# in_tree_knowledge = self.in_tree_knowledge)
        self.update(best_move)
        return best_move
    #-----------------------------------------------------
    #in gtp_connection, we need to change gomoku5.get_move to features_get_move to active this function
    def features_get_move(self,board,color_to_play):
        moves = GoBoardUtil.generate_legal_moves_gomoku(board)
        #toplayer = board.current_player
        moves_records = {}
        for move in moves:
            actived_features = []
            actived_features.append(feature1(board,move,color_to_play))
            actived_features.append(feature2(board,move,color_to_play))
            actived_features.append(feature3(board,move,color_to_play))
            actived_features.append(feature4(board,move,color_to_play))
            actived_features.append(feature5(board,move,color_to_play))
            actived_features.append(feature6(board,move,color_to_play))
            actived_features.append(feature7(board,move,color_to_play))
            actived_features.append(feature8(board,move,color_to_play))
            actived_features.append(feature9(board,move,color_to_play))
            actived_features.append(feature10(board,move,color_to_play))
            actived_features.append(feature11(board,move,color_to_play))
            moves_records[move] = policy_value_fn(actived_features)
        best_move = 'pass'
        highest_value = 0
        for move, value in moves_records.items():
            if value>=highest_value:
                best_move = move
        return best_move
    #------------------------------------------------------

    def get_node_depth(self,root):
        MAX_DEPTH = 49
        nodesAtDepth = [0]*MAX_DEPTH
        count_at_depth(root, 0, nodesAtDepth)
        return nodesAtDepth
    
    def get_properties(self):
        return dict(version = self.version, name = self.__class__.__name__)

def run(num_sim, sim_rule, in_tree_knowledge):
    #--------------------------
    use_pattern = None
    #--------------------------
    board = SimpleGoBoard(7)
    con = GtpConnection(Gomoku5(num_sim, use_pattern,sim_rule,in_tree_knowledge),board)
    con.start_connection()

if __name__ == '__main__':
    num_sim = 20
    sim_rule = None
    in_tree_knowledge = None
    run(num_sim,sim_rule,in_tree_knowledge)
