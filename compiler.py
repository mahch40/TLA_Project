# region LL1 Grammer class
class LL1Grammar():
    def __init__(self, start, non_terminals, terminals, productions, token_rules):
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

# test file to ll1 grammer
#-------------------------------------
# g = LL1Grammar.file_to_LL1("grammar.ll1")          
# print("Start:", g.start)
# print("Terminals:", g.terminals)
# print("Non-terminals:", g.non_terminals)
# print("Productions:", g.productions)
# print("Token Rules:", g.token_rules)
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