# region LL1 Grammer class
class LL1Grammar():
    def __init__(self, start, non_terminals, terminals, productions: dict, token_rules):
        self.start = start
        self.non_terminals = non_terminals
        self.terminals = terminals
        self.productions = productions
        self.token_rules = token_rules

    @staticmethod
    def file_to_LL1(filename):
        with open(filename, 'r') as f:
            line = f.readline()
            start = ""
            non_terminals=[]
            terminals=[]
            productions = {}
            token_rules = {}

            while(line):
                if(line == '\n'):
                    line = f.readline()
                line = line.replace('\n','')
                splitted_line_by_space = line.split()
                splitted_line_by_arrow = line.split("->")
                
                if(splitted_line_by_space[0]=="START"):
                    start = splitted_line_by_space[2]

                if(splitted_line_by_space[0]=="NON_TERMINALS"):
                    temp = line.split('=')
                    temp[1] = temp[1].replace(" " , "")
                    non_terminals = temp[1].split(",")

                if(splitted_line_by_space[0]=="TERMINALS"):
                    temp = line.split('=')
                    temp[1] = temp[1].replace(" " , "")
                    terminals = temp[1].split(",") 

                if(splitted_line_by_arrow[0].strip() in non_terminals):
                    right_side = splitted_line_by_arrow[1].strip().split("|")
                    for i in range(len(right_side)):
                        right_side[i] = right_side[i].strip()
                    productions[splitted_line_by_arrow[0].strip()] = right_side

                if(splitted_line_by_arrow[0].strip() in terminals):
                    token_rules[splitted_line_by_arrow[1].strip()] = splitted_line_by_arrow[0].strip() 

                line =f.readline() 

        return LL1Grammar(start, non_terminals, terminals, productions, token_rules)  
    


def find_first_set_of_beta(ll1, firsts, beta):
    first_beta = []
    
    if not beta: 
        first_beta.append('eps')
        return first_beta

    for i, symbol in enumerate(beta):
        if symbol in firsts:
            current_symbol_first = firsts[symbol]
        elif symbol in ll1.terminals: 
             current_symbol_first = [symbol]
        else:
            return []

        for term in current_symbol_first:
            if term != 'eps':
                if term not in first_beta: 
                    first_beta.append(term)

        if 'eps' not in current_symbol_first:
            break 

        elif i == len(beta) - 1: # If 'eps' was in current and this is the last symbol
            if 'eps' not in first_beta: 
                first_beta.append('eps')
    
    return first_beta

def find_all_firsts(ll1):
    firsts = {}

    # Initialize FIRST lists for terminals
    for terminal in ll1.terminals:
        firsts[terminal] = [terminal] 
    
    # 'eps''s FIRST list is just ['eps']
    firsts['eps'] = ['eps'] 

    # Initialize FIRST lists for non-terminals to empty lists
    for nt in ll1.non_terminals:
        firsts[nt] = [] 

    changed = True
    while changed:
        changed = False
        for nt in ll1.non_terminals: 
            # Production bodies are strings here, e.g., 'T E_prime'
            production_pings = ll1.productions.get(nt, []) 
 
            for p in production_pings:
                # --- NEW: Parse the string into a list of symbols here ---
                parts = p.split(' ')
                production_body_symbols = []
                for s in parts:
                    if s: # Check if the string 's' is not empty
                        production_body_symbols.append(s)
                # --- END NEW ---

                current_production_first = [] 
                produces_epsilon_for_this_production = True 

                for symbol in production_body_symbols: # Iterate over parsed symbols
                    if symbol in firsts: 
                        for term in firsts[symbol]:
                            if term != 'eps':
                                if term not in current_production_first: 
                                    current_production_first.append(term)

                        if 'eps' not in firsts[symbol]:
                            produces_epsilon_for_this_production = False
                            break 
                    else: 
                        produces_epsilon_for_this_production = False # Cannot derive epsilon through this path yet
                        break # Stop processing this production for FIRST calculation this iteration
                
                if produces_epsilon_for_this_production:
                    if 'eps' not in current_production_first: 
                        current_production_first.append('eps')
                
                initial_elements_count = len(firsts[nt])
                for item in current_production_first:
                    if item not in firsts[nt]: 
                        firsts[nt].append(item)
                if len(firsts[nt]) > initial_elements_count:
                    changed = True
    
    return firsts

def find_all_follows(ll1, all_firsts):
    follows = {}
    end_of_input_marker = '$' 

    # 1. Initialization
    for nt in ll1.non_terminals:
        follows[nt] = []
    
    # Add '$' to FOLLOW(start_symbol)
    follows[ll1.start].append(end_of_input_marker)

    changed = True
    while changed:
        changed = False
        # Iterate through each production A -> body
        for nt_A in ll1.non_terminals:
            # Production bodies are strings here, e.g., 'T E_prime'
            production_pings = ll1.productions.get(nt_A, [])

            for p in production_pings:
                # --- NEW: Parse the string into a list of symbols here ---
                production_body_symbols = [s for s in p.split(' ') if s]
                # --- END NEW ---

                # Iterate through symbols in the production body to find non-terminals
                for i, symbol_B in enumerate(production_body_symbols):
                    if symbol_B in ll1.non_terminals: # We are interested in non-terminals B
                        # The 'beta' part are symbols following B
                        beta = production_body_symbols[i+1:]

                        # Rule 1: A -> alpha B beta
                        if beta:
                            first_of_beta = find_first_set_of_beta(ll1, all_firsts, beta)

                            # Add all non-'eps' terminals from FIRST(beta) to FOLLOW(B)
                            for term in first_of_beta:
                                if term != 'eps':
                                    if term not in follows[symbol_B]:
                                        follows[symbol_B].append(term)
                                        changed = True
                            
                            # Rule 2: If 'eps' is in FIRST(beta), then FOLLOW(A) also contributes to FOLLOW(B)
                            if 'eps' in first_of_beta:
                                for term_in_follow_A in follows[nt_A]:
                                    if term_in_follow_A not in follows[symbol_B]:
                                        follows[symbol_B].append(term_in_follow_A)
                                        changed = True
                        
                        # Rule 3: If B is the last symbol in the production (beta is empty)
                        # Then FOLLOW(A) is added to FOLLOW(B)
                        else: # beta is empty
                             for term_in_follow_A in follows[nt_A]:
                                if term_in_follow_A not in follows[symbol_B]:
                                    follows[symbol_B].append(term_in_follow_A)
                                    changed = True

    return follows




# test file to ll1 grammer
#-------------------------------------
g = LL1Grammar.file_to_LL1("grammar.ll1")          
# print("Start:", g.start)
# print("Terminals:", g.terminals)
# print("Non-terminals:", g.non_terminals)
# print("Productions:", g.productions)
# print("Token Rules:", g.token_rules)
# print(find_all_firsts(g))
print(find_all_follows(g , find_all_firsts(g)))
# print(return_follows(g , LL1Grammar.return_firsts(g)))
#-------------------------------------
# endtest

# endregion

# region DPDA class
class DPDA():
    def __init__(self, states, input_alphabet, stack_alphabet, transition_function, final_states, initial_state='q0', stack_start_symbol='$'):
        self.states = states
        self.input_alphabet = input_alphabet
        self.stack_alphabet = stack_alphabet
        self.transition_function = transition_function
        self.stack_start_symbol = stack_start_symbol
        self.final_states = final_states
        self.initial_state = initial_state

    @staticmethod
    def process_string(dpda , string):
        stack = [dpda.stack_start_symbol]   
        current_state = dpda.initial_state
        top = stack[-1]
        j = 0
        s = ''
        while j <= len(string):
            if(j != len(string)):
                s = string[j]
            if (current_state, s, top) in dpda.transition_function:
                next = dpda.transition_function[(current_state, s, top)]
                current_state = next[0]
                stack.pop()
                for i in range(len(next[1]) - 1, -1, -1):
                    stack.append(next[1][i])
                top = stack[-1]
                j += 1
            elif (current_state, '', top) in dpda.transition_function:
                next = dpda.transition_function[(current_state, '', top)]
                current_state = next[0]
                stack.pop()
                for i in range(len(next[1]) - 1, -1, -1):
                    stack.append(next[1][i])
                top = stack[-1]
                if(j == len(string)):
                    j += 1
            else:
                return False
            
        if current_state in dpda.final_states and len(stack) == 1:
            return True
        
        return False
    
    
# test dpda
#-------------------------------------
# states_anbn = {'q0', 'q1', 'qf'}
# input_alphabet_anbn = {'a', 'b'}
# stack_alphabet_anbn = {'A', '$'}

# transition_function_anbn = {
#     ('q0', '', '$'): ('q0', '$'),
#     ('q0', 'a', '$'): ('q0', 'A$'),
#     ('q0', 'a', 'A'): ('q0', 'AA'),
#     ('q0', 'b', 'A'): ('q1', ''),
#     ('q1', 'b', 'A'): ('q1', ''),
#     ('q1', '', '$'): ('qf', '$')
# }

# final_states_anbn = ['qf', 'q0']
# initial_state_anbn = 'q0'
# stack_start_symbol_anbn = '$'

# dpda_anbn = DPDA(
#     states=states_anbn,
#     input_alphabet=input_alphabet_anbn,
#     stack_alphabet=stack_alphabet_anbn,
#     transition_function=transition_function_anbn,
#     final_states=final_states_anbn,
#     initial_state=initial_state_anbn,
#     stack_start_symbol=stack_start_symbol_anbn
# )

# result = DPDA.process_string(dpda_anbn, 'aabb')
# print(result)
#-------------------------------------
# endtest

# endregion