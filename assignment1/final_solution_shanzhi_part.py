import itertools
    
def diagonal_left_board(board):

    row = len(board)
    col = len(board[0])
    lim=0
    
    result = []#this will make a diagonl left solution list
    for i in range(row):
        for j in range(lim,col):  # forward j
            sub_re = []
            i1, j1 = i, j  
            while i1 <= row - 1 and j1 >=0:
                sub_re.append(board[i1][j1])
                j1 -= 1
                i1 += 1
            if i==0 and j==col-1:
                lim=col-1
            result.append(sub_re)
            
    return result

def diagonal_right_board(board):
    
    row = len(board)
    col = len(board[0])
    col2 = col
    result = []#this will make a diagonl right solution list
    
    for i in range(row):
        for j in range(col2 - 1, -1, -1): #backward j
            sub_re = []
            i1, j1 = i, j 
            while i1 <= row - 1 and j1 <= col - 1:
                sub_re.append(board[i1][j1])
                j1 += 1
                i1 += 1
            result.append(sub_re)
            if i == 0 and j == 0:#when achieve the (0,0)let j = 0stable
                col2 = 1
    return result

def gogui_rules_final_result_cmd(self, args):
    
    #check lines of the board
    for row in self.board:
        checking_row_list = [(k,len(list(v))) for k,v in itertools.groupby(row)]
        for i in checking_row_list:
            if i[0] == 1 and i[1] >= 5:
                #print("black win")
                winner = 'black'
                return winner 
            elif i[0] == 0 and i[1] >= 5 :
                #print("white win")
                winner = 'white'
                return winner
            
    #check colum
    for num in range(self.boardsize):
        col = [row[num] for row in self.board]
        checking_col_list = [(k,len(list(v))) for k,v in itertools.groupby(col)]
        for i in checking_col_list:
            if i[0] == 1 and i[1] >= 5:
                #print("black win")
                winner = 'black'
                return winner 
            elif i[0] == 0 and i[1] >= 5 :
                #print("white win")
                winner = 'white'
                return winner    
    #check diagonal
    diagonal_right_board = diagonal_right_board(self.board)
    diagonal_left_board = diagonal_left_board(self.board)
    
    for u in diagonal_left_board:
        checking_dia_left_list = [(k,len(list(v))) for k,v in itertools.groupby(u)]
        for i in checking_dia_left_list:
            if i[0] == 1 and i[1] >= 5:
                #print("black win")
                winner = 'black'
                return winner 
            elif i[0] == 0 and i[1] >= 5 :
                #print("white win")
                winner = 'white'
                return winner  
            
    for u in diagonal_right_board:
        checking_dia_right_list = [(k,len(list(v))) for k,v in itertools.groupby(u)]
        for i in checking_dia_right_list:
            if i[0] == 1 and i[1] >= 5:
                #print("black win")
                winner = 'black'
                return winner 
            elif i[0] == 0 and i[1] >= 5 :
                #print("white win")
                winner = 'white'
                return winner 
            
    #check draw
    empty_sum = 0
    for row in self.board:
        checking_list = [(k,len(list(v))) for k,v in itertools.groupby(row)]
        for i in checking_list:
            if i[0] == 0:
                empty_sum += i[1]
                
    if empty_sum == 0:
        winner = "draw"
        return winner
    
    #if game still running return unknown                  
    winner = "unknown"
    return winner