import sys
import ast
from csp import *
from timeit import default_timer

INPUT_DIR = '../inputs/'

def get_kenken_input(input_file): 
    input_file = INPUT_DIR + input_file

    # parse input kenken puzzle file 
    try:
        with open(input_file) as file:
            n = int(file.readline())
            cliques = [list(map(ast.literal_eval, line.rstrip().split(' '))) for line in file.readlines()]
        file.close()
    except IOError:
        error_exit("Input file not found.")

    return n, cliques


class kenken(CSP):

    def __init__(self, n , cliques):

        self.clqs = cliques
        self.n = n
        variables = [] #empty list
        domains = {} #empty dict
        domain = list(range(1,n+1))  #domain (list) contains values from 1 to n
        for i in range(n):  #create variables' names  (for i=0  to i<=n-1 /rows/)
            for j in range(n):  #(for j=0  to j<=n-1 /columns/)
                var = 'x' + str(i) + str(j) # var type is x00 , x01 , x02 .. (string)
                variables.append(var)  # add var to variables list
                domains[var] = domain  # add var and its possible values in domains dict

        neighbors = {} #empty dict

        for var in variables:  #create neighbors dictionary
            each_var_neighbors = []
            row = var[1]
            col = var[2]
            for j in range(n) :  #get all other variables located in the same row
                neighbor = 'x' + row +str(j)
                if neighbor != var :  # dont include var itself
                    each_var_neighbors.append(neighbor)

            for i in range(n): #get all other variables located in the same column
                neighbor = 'x' + str(i) + col
                if neighbor != var : #dont include var itself
                    each_var_neighbors.append(neighbor)

            neighbors[var] = each_var_neighbors  # add variable's neighbors to dict

        #initialize csp
        CSP.__init__(self, variables, domains, neighbors, self.kenken_constraints)



    def display(self, solution):   # print kenken solution to a easily readable form
        print("\n -----Printing Solution-----\n")
        if solution is None:
            print("-> No solution was found \n")

        for i in range(self.n):
            for j in range(self.n):
                var = 'x' + str(i) + str(j)
                val = solution[var]
                print(val,end=" | ")

            print("\n")


    def kenken_constraints(self, A, a, B, b):

        if A == B:  # if A,B are the same variable
            return False

        if (a not in self.choices(A)) or (b not in self.choices(B)): # a,b must be in the values that aren't currently ruled out
            return False

        A_row = A[1]
        A_col = A[2]
        A_x = int(A_row)
        A_y = int(A_col)
        A_cords = (A_x, A_y)

        B_row = B[1]
        B_col = B[2]
        B_x = int(B_row)
        B_y = int(B_col)
        B_cords = (B_x, B_y)

        if (A_row == B_row) or (A_col == B_col):  # if A and B are located in the same row
            if a == b:  # and have the same value
                return False

        assigned_vars = self.infer_assignment()  # get a dictionary with all assigned variables and their corresponding values

        #checking row and column constraint
        A_neighbors = self.neighbors[A]  # get A's neighbors (it is a list containing variables which are located in the same row or column)
        for neighbor in A_neighbors:
            if neighbor in assigned_vars:  # if a certain A's neighbor has been assigned a value
                if a == assigned_vars[neighbor]:  # and its value is equal to A's value (meaning there are 2 same numbers in one row or column
                    return False

        B_neighbors = self.neighbors[B]  # get B's neighbors (it is a list containing variables which are located in the same row or column)
        for neighbor in B_neighbors:
            if neighbor in assigned_vars:  # if a certain B's neighbor has been assigned a value
                if b == assigned_vars[neighbor]:  # and its value is equal to B's value (meaning there are 2 same numbers in one row or column
                    return False

        # now checking clique's constraints
        A_checked = 0
        B_checked = 0

        for clq in self.clqs:
            if (A_cords in clq[0]) or (B_cords in clq[0]):  # if variable A or B is contained in this clique  (or both of them)
                A_index = -1                #keep A's index inside the clique
                B_index = -1                #keep B's index inside the clique
                operator = clq[1]
                goal_number = clq[2]
                clq_members = clq[0]
                for j, clq_mem in enumerate(clq_members):  # iterate clique's members
                    if clq_mem == A_cords:  # A is in the clique
                        A_index = j
                    elif clq_mem == B_cords:  # B is in the clique
                        B_index = j

                if A_index == -1:  # only B is in the clique
                    clq_var = B
                    clq_var_val = b
                    clq_var_index = B_index

                elif B_index == -1:  # only A is in the clique
                    clq_var = A
                    clq_var_val = a
                    clq_var_index = A_index

                # else: both A and B are in the clique

                if operator == '':  # if operator is none there will be only one variable in the clique (and this variable will be either A or B )
                    if clq_var_val == goal_number:
                        if clq_var == A:
                            A_checked = 1
                        else:
                            B_checked = 1;

                    else:
                        return False

                elif (operator == 'div') or (operator == 'sub'):  # in division and subtraction there are only 2 variables in the clique

                    if (A_index != -1) and (B_index != -1):  # if both A and B are in the same clique (A and B are the only variables in the clique)
                        if operator == 'div':
                            big = max(a, b)
                            small = min(a, b)
                            res = big / small
                        else:  # operator == sub
                            res = abs(a - b)

                        if res == goal_number:
                            return True
                        else:
                            return False

                    else:  # if one of A,B is in this clique - get its neighbor's coordinates from clique
                        if clq_var_index == 0:
                            clq_neighbor_coords = clq[0][1]  # clq_neighbor_coords = (x,y)
                        else:
                            clq_neighbor_coords = clq[0][0]

                        clq_neighbor = 'x' + str(clq_neighbor_coords[0]) + str(clq_neighbor_coords[1])  # covert neighbor's coordinates to variable string type

                        if clq_neighbor in assigned_vars:  # if neighbor has been assigned a value
                            clq_neighbor_val = assigned_vars[clq_neighbor]  # get its value
                            if operator == 'div':
                                big = max(clq_var_val, clq_neighbor_val)
                                small = min(clq_var_val, clq_neighbor_val)
                                res = big / small

                            else:  # operator == sub
                                res = abs(clq_var_val - clq_neighbor_val)

                            if res == goal_number:
                                if clq_var == A:
                                    A_checked = 1;
                                else:
                                    B_checked = 1;

                            else:
                                return False

                        else:  # if neighbor has not been assigned a value

                            clq_neighbor_choices = self.choices(clq_neighbor)  # get all remaining possible values for neighbor

                            return_false = 1
                            for poss_val in clq_neighbor_choices:
                                #poss_val must satisfy row and column constraint with A,B
                                if (A[1] == clq_neighbor[1] or A[2] == clq_neighbor[2] or B[1] == clq_neighbor[1] or B[2] == clq_neighbor[2]) and clq_var_val == poss_val:  # check for row and column neighbors
                                    continue   # poss_val is not good so try another one

                                if operator == 'div':
                                    big = max(poss_val, clq_var_val)
                                    small = min(poss_val, clq_var_val)
                                    res = big / small
                                else:  # operator == sub
                                    res = abs(poss_val - clq_var_val)

                                if res == goal_number:

                                    if clq_var == A:
                                        A_checked = 1;
                                    else:
                                        B_checked = 1;

                                    return_false = 0
                                    break  # we found a good poss_val so break for loop

                            if return_false == 1: # if all possible values have been checked and none of the them is good
                                return False


                elif (operator == 'add') or (operator == 'mult'):
                    if operator == 'add':
                        sum = 0
                    else:
                        sum = 1

                    clq_members = clq[0]
                    all_assigned = 1  # indicates that all neighbors in the clique have been assigned a value

                    for clq_mem in clq_members:
                        clq_neighbor = 'x' + str(clq_mem[0]) + str(clq_mem[1])  # covert neighbor's coordinates to variable string type
                        if clq_mem == A_cords:
                            clq_neighbor_val = a

                        elif clq_mem == B_cords:
                            clq_neighbor_val = b

                        elif clq_neighbor in assigned_vars:
                            clq_neighbor_val = assigned_vars[clq_neighbor]

                        else:
                            all_assigned = 0   #there is at least one neighbor in the clique that has not been assigned a value
                            if operator == 'add':
                                clq_neighbor_val = 0  # so if it is a addition add 0 to sum
                            else:
                                clq_neighbor_val = 1  #or if it is a multiplication multplay 1 to sum

                        if operator == 'add':
                            sum += clq_neighbor_val
                        else:
                            sum *= clq_neighbor_val

                        if sum > goal_number:      #if the goal number has been surpassed
                            return False

                    if all_assigned == 1: # if all neighbors in the clique had been assigned a value
                        if sum != goal_number:
                            return False

                    else:               #if at least one neighbor in the clique has beem assigned a value
                        if operator == 'add':
                            if sum >= goal_number:  #because at least one neighbor's value must be added to the sum at some time and the min value is 1
                                return False         #so the goal number will be surpassed in any case

                        else:
                            if sum > goal_number:  #again at least one neighbor's value must be multiplied to the sum at some time but the min value is 1 which will not change the sum
                                return False

                    if (A_index != -1) and (B_index != -1): # if both A and B are in the same clique and satisfly all the constraints
                        return True
                    else:                                   #one of A,B is in this clique
                        if clq_var == A:
                            A_checked = 1
                        else:
                            B_checked = 1

            if (A_checked == 1) and (B_checked == 1): # if both A and B have been checked and their values satisfy all the constraints
                return True


def error_exit(msg):
    print("-> ERROR: " + msg)
    sys.exit(1)
    

def main(argv):
    
    print("--> KenKen Solver <--")

    if len(sys.argv) != 3:
        error_exit("Wrong number of command line parameters was given.") 

    input_file = sys.argv[1]
    n, cliques = get_kenken_input(input_file)
    if n == None or cliques == None:
        error_exit("Wrong input file format.")

    kenken_puzzle = kenken(n, cliques) #create a kenken puzzle

    start = default_timer()
    if sys.argv[2] == "BT":
        print("-> Using 'BT' algorithm to solve the puzzle")
        solution = backtracking_search(kenken_puzzle)
    elif sys.argv[2] == "BT+MRV":
        print("-> Using 'BT and MRV' algorithms to solve the puzzle")
        solution = backtracking_search(kenken_puzzle, select_unassigned_variable=mrv)
    elif sys.argv[2] == "FC":
        print("-> Using 'FC' algorithm to solve the puzzle")
        solution = backtracking_search(kenken_puzzle, inference=forward_checking)
    elif sys.argv[2] == "FC+MRV":        
        print("-> Using 'FC and MRV' algorithms to solve the puzzle")
        solution = backtracking_search(kenken_puzzle, select_unassigned_variable=mrv, inference=forward_checking)
    elif sys.argv[2] == "MAC":        
        print("-> Using 'MAC' algorithm to solve the puzzle")
        solution = backtracking_search(kenken_puzzle, inference=mac)
    else:
	    error_exit("Wrong type of algorithm was given.")

    duration = default_timer() - start


    #BT:
    # start = default_timer()
    # x = backtracking_search(test)
    # duration = default_timer() - start

    #BT + MRV:
    #start = default_timer()
    #x = backtracking_search(test, select_unassigned_variable=mrv)
    #duration = default_timer() - start

    #FC:
    #start = default_timer()
    #x = backtracking_search(test, inference=forward_checking)
    #duration = default_timer() - start

    #FC + MRV:
    #start = default_timer()
    #x = backtracking_search(test, select_unassigned_variable=mrv, inference=forward_checking)
    #duration = default_timer() - start

    #MAC:
    #start = default_timer()
    #x = backtracking_search(test, inference=mac)
    #duration = default_timer() - start

    #max_conflict
    #start = default_timer()
    #x = min_conflicts(test)
    #duration = default_timer() - start

    print("-> Duration:", duration)
    print("-> Number of assignments:", kenken_puzzle.nassigns)

    kenken_puzzle.display(solution)


if __name__ == "__main__":
    main(sys.argv)
