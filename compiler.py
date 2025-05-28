# region LL1 Grammer class
class LL1Grammar():
    def __init__(self, start, non_terminals, terminals, productions, token_rules, stack_bottom_symbol='$'):
        self.start = start
        self.non_terminals = non_terminals
        self.terminals = terminals
        self.productions = productions
        self.token_rules = token_rules
        self.stack_bottom_symbol = stack_bottom_symbol

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
    
    def find_first_set(self):
        first = {}
        for nt in self.non_terminals:
            first[nt] = set()
        done = False
        while not done:
            changed = False
            for nt in self.non_terminals:
                productions = self.productions[nt]
                size_before_change = len(first[nt])
                size_after_change = len(first[nt])
                for production in productions:
                    terms = production.split()
                    if terms[0] in self.terminals or terms[0] == 'eps':
                        first[nt].add(terms[0])
                        size_after_change = len(first[nt])
                    else:
                        idx = 0
                        var = terms[0]
                        while 'eps' in first[var] and idx < len(terms):
                            temp_copy = first[var].copy()
                            temp_copy.remove('eps')
                            first[nt].update(temp_copy)
                            idx += 1
                            if idx == len(terms):
                                break
                            var = terms[idx]
                        first[nt].update(first[var])
                        size_after_change = len(first[nt])
                if(size_after_change > size_before_change):
                    changed = True
            if(not changed):
                done = True

        return first
    
    def find_follow_set(self , first):
        follow = {}
        for nt in self.non_terminals:
            follow[nt] = set()
            if nt == self.start:
                follow[nt].add(self.stack_bottom_symbol)
        done = False
        while not done:
            changed = False
            for left_side , productions in self.productions.items():
                for right_side in productions:
                    terms = right_side.split()
                    for i, term in enumerate(terms):
                        if term in self.non_terminals:
                            size_before_change = len(follow[term])
                            size_after_change = len(follow[term])
                            if i == len(terms) - 1:
                                follow[term].update(follow[left_side])
                                size_after_change = len(follow[term])
                            else:
                                beta = terms[i+1 :]
                                beta_first = set()
                                if beta[0] in self.terminals or beta[0] == 'eps':
                                    beta_first.add(beta[0])
                                else:
                                    idx = 0
                                    var = beta[0]
                                    while 'eps' in first[var] and idx < len(beta):
                                        temp_copy = first[var].copy()
                                        temp_copy.remove('eps')
                                        beta_first.update(temp_copy)
                                        idx += 1
                                        if idx == len(beta):
                                            break
                                        var = beta[idx]
                                    beta_first.update(first[var])
                                if 'eps' in beta_first:
                                    beta_first.remove('eps')
                                    follow[term].update(follow[left_side])
                                follow[term].update(beta_first)
                                size_after_change = len(follow[term])
                            if(size_after_change > size_before_change):
                                changed = True
            if not changed:
                done = True
        
        return follow
    
    def construct_parsing_table(self, first, follow):
        parsing_table = {}
        for left_side , productions in self.productions.items():
            for right_side in productions:
                    terms = right_side.split()
                    if terms[0] in self.terminals:
                        parsing_table[(left_side, terms[0])] = right_side
                    elif terms[0] == 'eps' and len(terms) == 1:
                        for term in (follow[left_side]):
                            parsing_table[(left_side, term)] = 'eps'
                    else:    
                        all_have_eps = True
                        for i, term in enumerate(terms):
                            alpha_first = set()
                            if 'eps' not in first[term]:
                                alpha_first.update(first[term]) 
                                all_have_eps = False
                                break
                            copy_term = first[term].copy()
                            copy_term.remove('eps')
                            alpha_first.update(copy_term)
                        for f in alpha_first:    
                            parsing_table[(left_side, f)] = right_side
                        if all_have_eps:
                            for term in (follow[left_side]):
                                parsing_table[(left_side, term)] = right_side
        return parsing_table                        

            
# test file to ll1 grammer
#-------------------------------------
g = LL1Grammar.file_to_LL1("grammar.ll1")          
# print("Start:", g.start)
# print("Terminals:", g.terminals)
# print("Non-terminals:", g.non_terminals)
# print("Productions:", g.productions)
# print("Token Rules:", g.token_rules)
# print(g.find_first_set())
# print(g.find_follow_set(g.find_first_set()))
# first = g.find_first_set()
# print(g.construct_parsing_table(first, g.find_follow_set(first)))
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
        string = string.split()
        stack = []
        for s in dpda.stack_start_symbol:
            stack.append(s)   
        current_state = dpda.initial_state
        top = stack[-1]
        j = 0
        s = ''
        while j <= len(string):
            if(j != len(string)):
                s = string[j]
            if (current_state, s, top) in dpda.transition_function:
                if(s == top):
                    j += 1
                next = dpda.transition_function[(current_state, s, top)]
                current_state = next[0]
                stack.pop()
                temp = next[1].split()
                for i in range(len(temp) - 1, -1, -1):
                    stack.append(temp[i])
                top = stack[-1]
            elif (current_state, 'eps', top) in dpda.transition_function:
                next = dpda.transition_function[(current_state, 'eps', top)]
                current_state = next[0]
                stack.pop()
                temp = next[1].split()
                for i in range(len(temp) - 1, -1, -1):
                    if(temp[j] != 'eps'):
                        stack.append(temp[i])
                top = stack[-1]
                if(j == len(string) and len(stack) == 1):
                    j += 1
            else:
                return False
            
        if current_state in dpda.final_states and len(stack) == 1:
            return True
        
        return False
    
    @staticmethod
    def turn_LL1_to_DPDA(ll1: LL1Grammar):
        first = ll1.find_first_set()
        follow = ll1.find_follow_set(first)
        parsing_table = ll1.construct_parsing_table(first, follow)

        states = ['q0', 'qf']
        final_states = ['qf']
        input_alphabet = ll1.terminals
        stack_alphabet = ll1.non_terminals 
        stack_alphabet.append('$')
        transition_function = {('q0', '$', '$'): ('qf', '$'), ('q0', 'eps', 'eps'): ('q0', 'eps')}
        for key, value in parsing_table.items():
            transition_function[('q0', key[1], key[0])] = ('q0', value)
        for terminal in ll1.terminals:
            transition_function[('q0', terminal, terminal)] = ('q0', 'eps')
        # print(transition_function)
        return DPDA(states, input_alphabet, stack_alphabet, transition_function, final_states, stack_start_symbol=f"${ll1.start}")
        
        
    
    
# test dpda
#-------------------------------------
# states_anbn = {'q0', 'q1', 'qf'}
# input_alphabet_anbn = {'a', 'b'}
# stack_alphabet_anbn = {'A', '$'}

# transition_function_anbn = {
#     ('q0', 'eps', '$'): ('q0', '$'),
#     ('q0', 'a', '$'): ('q0', 'A$'),
#     ('q0', 'a', 'A'): ('q0', 'AA'),
#     ('q0', 'b', 'A'): ('q1', 'eps'),
#     ('q1', 'b', 'A'): ('q1', 'eps'),
#     ('q1', 'eps', '$'): ('qf', '$')
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



g = LL1Grammar.file_to_LL1("grammar.ll1")          

m = DPDA.turn_LL1_to_DPDA(g)
print(DPDA.process_string(m, 'I'))