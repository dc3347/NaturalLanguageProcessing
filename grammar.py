"""
COMS W4705 - Natural Language Processing - Summer 2021 
Homework 2 - Parsing with Context Free Grammars 
Daniel Bauer
"""

import sys
from collections import defaultdict
from math import fsum, isclose
import string

class Pcfg(object): 
    """
    Represent a probabilistic context free grammar. 
    """

    def __init__(self, grammar_file): 
        self.rhs_to_rules = defaultdict(list)
        self.lhs_to_rules = defaultdict(list)
        self.startsymbol = None 
        self.read_rules(grammar_file)      
 
    def read_rules(self,grammar_file):
        
        for line in grammar_file: 
            line = line.strip()
            if line and not line.startswith("#"):
                if "->" in line: 
                    rule = self.parse_rule(line.strip())
                    lhs, rhs, prob = rule
                    self.rhs_to_rules[rhs].append(rule)
                    self.lhs_to_rules[lhs].append(rule)
                else: 
                    startsymbol, prob = line.rsplit(";")
                    self.startsymbol = startsymbol.strip()
                    
     
    def parse_rule(self,rule_s):
        lhs, other = rule_s.split("->")
        lhs = lhs.strip()
        rhs_s, prob_s = other.rsplit(";",1) 
        prob = float(prob_s)
        rhs = tuple(rhs_s.strip().split())
        return (lhs, rhs, prob)

    def verify_grammar(self):
        """
        Return True if the grammar is a valid PCFG in CNF.
        Otherwise return False. 
        """
        # TODO, Part 1
        
        for key, lhs_rule in self.lhs_to_rules.items():
            prob_lhs = 0
        
            for rule in lhs_rule:
                lhs = rule[0]
                rhs = rule[1]
                prob = rule[2]
                prob_lhs+=prob
                
                # check that rules are in CNF
                # A->BC or A->b
                if len(rhs)==1:
                    if rhs[0].islower() or rhs[0].isdigit() or rhs[0] in string.punctuation: # 
                        continue # terminal is lowercase
                    else:
                        #print(rhs)
                        print("Grammar is not valid. Error: Terminals must be lowercase (A->b)")
                        return False
                
                if len(rhs)==2:
                    if rhs[0].isupper() and rhs[1].isupper():
                        continue # terminals are both uppercase
                    else: 
                        print("Grammar is not valid. Error: Non-terminals must be uppercase (A->BC)")
                        return False
                
            # check that all probs for the same lhs symbol sum to 1.0
            if not isclose(1,prob_lhs):
                print("Grammar is not valid. Error: LHS probabilities do not sum to 1.")
                return False
        
        print("Grammar is valid.")
        return True
            


if __name__ == "__main__":
    #with open(sys.argv[1],'r') as grammar_file:
        #grammar = Pcfg(grammar_file)
    
    with open('atis3.pcfg','r') as grammar_file:
        grammar = Pcfg(grammar_file)

    grammar.verify_grammar()
    
    #print(grammar.startsymbol)
    #print(grammar.lhs_to_rules['PP'])
    #print(grammar.rhs_to_rules[('ABOUT','NP')])
    #print(grammar.rhs_to_rules[('NP','VP')])
    
    
    
        
