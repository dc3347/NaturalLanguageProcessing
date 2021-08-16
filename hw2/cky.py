"""
COMS W4705 - Natural Language Processing - Summer 2021
Homework 2 - Parsing with Probabilistic Context Free Grammars 
Daniel Bauer
"""
import math
import sys
from collections import defaultdict
import itertools
from grammar import Pcfg
from itertools import product

### Use the following two functions to check the format of your data structures in part 3 ###
def check_table_format(table):
    """
    Return true if the backpointer table object is formatted correctly.
    Otherwise return False and print an error.  
    """
    if not isinstance(table, dict): 
        sys.stderr.write("Backpointer table is not a dict.\n")
        return False
    for split in table: 
        if not isinstance(split, tuple) and len(split) ==2 and \
          isinstance(split[0], int)  and isinstance(split[1], int):
            sys.stderr.write("Keys of the backpointer table must be tuples (i,j) representing spans.\n")
            return False
        if not isinstance(table[split], dict):
            sys.stderr.write("Value of backpointer table (for each span) is not a dict.\n")
            return False
        for nt in table[split]:
            if not isinstance(nt, str): 
                sys.stderr.write("Keys of the inner dictionary (for each span) must be strings representing nonterminals.\n")
                return False
            bps = table[split][nt]
            if isinstance(bps, str): # Leaf nodes may be strings
                continue 
            if not isinstance(bps, tuple):
                sys.stderr.write("Values of the inner dictionary (for each span and nonterminal) must be a pair ((i,k,A),(k,j,B)) of backpointers. Incorrect type: {}\n".format(bps))
                return False
            if len(bps) != 2:
                sys.stderr.write("Values of the inner dictionary (for each span and nonterminal) must be a pair ((i,k,A),(k,j,B)) of backpointers. Found more than two backpointers: {}\n".format(bps))
                return False
            for bp in bps: 
                if not isinstance(bp, tuple) or len(bp)!=3:
                    sys.stderr.write("Values of the inner dictionary (for each span and nonterminal) must be a pair ((i,k,A),(k,j,B)) of backpointers. Backpointer has length != 3.\n".format(bp))
                    return False
                if not (isinstance(bp[0], str) and isinstance(bp[1], int) and isinstance(bp[2], int)):
                    print(bp)
                    sys.stderr.write("Values of the inner dictionary (for each span and nonterminal) must be a pair ((i,k,A),(k,j,B)) of backpointers. Backpointer has incorrect type.\n".format(bp))
                    return False
    return True

def check_probs_format(table):
    """
    Return true if the probability table object is formatted correctly.
    Otherwise return False and print an error.  
    """
    if not isinstance(table, dict): 
        sys.stderr.write("Probability table is not a dict.\n")
        return False
    for split in table: 
        if not isinstance(split, tuple) and len(split) ==2 and isinstance(split[0], int) and isinstance(split[1], int):
            sys.stderr.write("Keys of the probability must be tuples (i,j) representing spans.\n")
            return False
        if not isinstance(table[split], dict):
            sys.stderr.write("Value of probability table (for each span) is not a dict.\n")
            return False
        for nt in table[split]:
            if not isinstance(nt, str): 
                sys.stderr.write("Keys of the inner dictionary (for each span) must be strings representing nonterminals.\n")
                return False
            prob = table[split][nt]
            if not isinstance(prob, float):
                sys.stderr.write("Values of the inner dictionary (for each span and nonterminal) must be a float.{}\n".format(prob))
                return False
            if prob > 0:
                sys.stderr.write("Log probability may not be > 0.  {}\n".format(prob))
                return False
    return True



class CkyParser(object):
    """
    A CKY parser.
    """

    def __init__(self, grammar): 
        """
        Initialize a new parser instance from a grammar. 
        """
        self.grammar = grammar

    def is_in_language(self,tokens):
        """
        Membership checking. Parse the input tokens and return True if 
        the sentence is in the language described by the grammar. Otherwise
        return False
        """
        # TODO, part 2
        
        # initialization
        pi = [[[] for i in range(len(tokens)+1)] for j in range(len(tokens)+1)]
        for i in range(len(tokens)):
            for rule in grammar.rhs_to_rules[tokens[i],]:
                pi[i][i+1].append(rule[0])
                
        # main loop
        M = []
        for length in range(2,len(tokens)+1):
            for i in range(len(tokens)-length+1):
                j = i+length
                for k in range(i+1,j):
                    A = set(pi[i][k])
                    B = set(pi[k][j])
                    M = product(A,B) # M = {A|A->BC in R and B in pi[i,k] and C in pi[k,j]}
                  
                    for elem in M: # pi[i,j] = pi[i,j]U M 
                        if elem in self.grammar.rhs_to_rules:
                            for non_terminal in grammar.rhs_to_rules[elem]:
                                #print(non_terminal[0])
                                pi[i][j].append(non_terminal[0])
   
        # if S in pi[0,n+1] return true, else false
        if self.grammar.startsymbol in pi[0][len(tokens)]:
            return True
        return False 
     
        
    def parse_with_backpointers(self, tokens):
        """
        Parse the input tokens and return a parse table and a probability table.
        """
    
        # TODO, part 3
        
        # takes list of tokens as input
        
        table= defaultdict(dict) # parse table containing backptrs, keys of dict are spans, value map nonterminial symbols to backpts
        probs = defaultdict(dict) # records log probs instead of backptrs
        
        # initialization
        
        for i in range(len(tokens)):
            for a in self.grammar.rhs_to_rules[(tokens[i]),]:
                table[(i,i+1)][a[0]] = a[1][0] #tokens[i]
                probs[(i,i+1)][a[0]] = math.log(a[2])
            
        # main loop
        for length in range(2, len(tokens)+1):
            for i in range(len(tokens)-length+1):
                j = i + length
               
                for k in range(i+1,j):
                    A = table[(i,k)]
                    B= table[(k,j)]
                
                    M = product(A.keys(),B.keys()) # M = {A|A->BC in R and B in pi[i,k] and C in pi[k,j]}
                    for elem in M: # pi[i,j] = pi[i,j]U M 
                        if elem in self.grammar.rhs_to_rules:
                            for non_terminal in self.grammar.rhs_to_rules[elem]:
                                p=math.log(non_terminal[2]) + probs[(i, k)][elem[0]] + probs[(k, j)][elem[1]]
                                if non_terminal[0] in table[(i,j)]:
                                    if p > probs[(i,j)][non_terminal[0]]:
                                        table[(i,j)][non_terminal[0]] = ((elem[0], i, k), (elem[1],k,j))
                                        probs[(i,j)][non_terminal[0]] = p
                                elif non_terminal not in table[(i,j)]:
                                    table[(i,j)][non_terminal[0]] = ((elem[0], i, k), (elem[1],k,j))
                                    probs[(i,j)][non_terminal[0]] = p
                                else:
                                    continue
                                
        #testing
        #print(table[(0,3)]['NP']) # returns backptrs to the table entries used to create the NP phrase over the span [0,3].
        #print(table[(2,3)]["FLIGHTS"]) # should be "flights"
        #print(probs[(0,3)]['NP']) # should be -12.1324, represents log prob of hte best parse tree for span [0,3]
        
        return table, probs
    
    
def get_tree(chart, i,j,nt): 
    """
    Return the parse-tree rooted in non-terminal nt and covering span i,j.
    """
    # TODO: Part 4
    
    # edge case:
    if nt not in chart[(i,j)]:
        print("Error: sentence not in grammar")
        return None
    
    # hint: recursively traverse the parse chart to assemble tree
    # base case:
    if j - i == 1: # terminals
        terminals = (nt, chart[(i, j)][nt])
        return terminals

    # each tree is represented as tuple where first elem is the parent node and remaining elems are children
    tree1 = get_tree(chart, chart[(i, j)][nt][0][1], chart[(i, j)][nt][0][2], chart[(i, j)][nt][0][0])
    
    # each child is either a tree or a terminal string
    tree2 = get_tree(chart, chart[(i, j)][nt][1][1], chart[(i, j)][nt][1][2], chart[(i, j)][nt][1][0])
    
    output = (nt, tree1, tree2)
    return output
    
  
       
if __name__ == "__main__":
    
    with open('atis3.pcfg','r') as grammar_file: 
        grammar = Pcfg(grammar_file) 
        parser = CkyParser(grammar)
        toks =['flights', 'from','miami', 'to', 'cleveland','.'] 
        #toks = ['miami','flights','cleveland','from','to','.']
        
        print(parser.is_in_language(toks))
        
        table,probs = parser.parse_with_backpointers(toks)
        assert check_table_format(table)
        assert check_probs_format(probs)
        
        print(get_tree(table,0,len(toks),grammar.startsymbol))
