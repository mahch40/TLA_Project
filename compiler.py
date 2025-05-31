import re
from graphviz import Digraph
from builtins import id as uniq_id
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
                                        if(var in self.terminals):
                                            beta_first.add(var)
                                            break
                                    if var not in self.terminals:
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

    def turn_string_to_tokens(self, string):
        tokend_str = ""
        splitted_str = string.split()
        for char in splitted_str:
            found = False
            for reg, token in self.token_rules.items():
                if re.fullmatch(reg, char):
                    found = True
                    tokend_str += token + ' '
                    break
            if not found:
                raise Exception("input is not tokenizable !")
        return tokend_str

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
    def turn_LL1_to_DPDA(ll1: LL1Grammar):
        first = ll1.find_first_set()
        follow = ll1.find_follow_set(first)
        parsing_table = ll1.construct_parsing_table(first, follow)

        states = ['q0', 'qf']
        final_states = ['qf']

        input_alphabet = set(ll1.terminals + [ll1.stack_bottom_symbol])

        stack_alphabet = set(ll1.non_terminals + ll1.terminals + [ll1.start] + [ll1.stack_bottom_symbol])
        
        transition_function = {}

        for (non_terminal, terminal), right_side in parsing_table.items():
            rs_str = right_side if right_side != 'eps' else 'eps'
            transition_function[('q0', terminal, non_terminal)] = ('q0', rs_str)

        for terminal in ll1.terminals:
            transition_function[('q0', terminal, terminal)] = ('q0', 'eps')

        transition_function[('q0', ll1.stack_bottom_symbol, ll1.stack_bottom_symbol)] = ('qf', ll1.stack_bottom_symbol)

        dpda_stack_start_symbol = [ll1.stack_bottom_symbol, ll1.start]

        return DPDA(states=states,
                    input_alphabet=input_alphabet,
                    stack_alphabet=stack_alphabet,
                    transition_function=transition_function,
                    final_states=final_states,
                    initial_state='q0', 
                    stack_start_symbol=dpda_stack_start_symbol)        

    def process_string(self , tokened_string, string):
        derivations = []
        tokened_string = tokened_string.split()
        tokened_string.append(self.stack_start_symbol[0])
        stack = []
        string = string.split()
        for s in self.stack_start_symbol:
            stack.append(s)   
        current_state = self.initial_state
        top = stack[-1]
        j = 0
        s = ''
        while j <= len(tokened_string):
            if(j != len(tokened_string)):
                s = tokened_string[j]

            if (current_state, s, top) in self.transition_function:
                next = self.transition_function[(current_state, s, top)]
                current_state = next[0]
                should_derive = True
                if(top == s):
                    should_derive = False
                    if j < len(tokened_string) - 1:
                        derivations.append(string[j])
                    j+=1
                stack.pop()
                temp = next[1].split()
                derivation = top + " -> "
                n = len(temp)
                for i in range(len(temp) - 1, -1, -1):
                    derivation += temp[n - i - 1] + ' '
                    if(temp[i] != 'eps'):
                        stack.append(temp[i])
                if should_derive:
                    derivations.append(derivation)
                top = stack[-1]
            elif (current_state, 'eps', top) in self.transition_function:
                next = self.transition_function[(current_state, 'eps', top)]
                current_state = next[0]
                stack.pop()
                temp = next[1].split()
                n = len(temp)
                derivation = top + " -> "
                for i in range(len(temp) - 1, -1, -1):
                    derivation += temp[n - i - 1] + ' '
                    if(temp[i] != 'eps'):
                        stack.append(temp[i])
                derivations.append(derivation)
                top = stack[-1]
                if(j == len(tokened_string) and len(stack) == 1):
                    j += 1
            elif j == len(tokened_string) and len(stack) == 1:
                j += 1
            else:
                return False, derivations
            
        if current_state in self.final_states and len(stack) == 1:
            return True, derivations
        
        return False, derivations
    
    def make_nodes_from_derivations(self, derivations: list, id):
        der = derivations[0]
        root = None
        if '->' in der:
            temp = der.split('->')
            root = Node(temp[0].strip(), id, "node")
            derivations.pop(0)
            children = temp[1].strip().split()
            for child in children:
                id += 1
                if child == 'eps':
                    root.add_child(Node('eps', id, "leaf"))
                    break
                node, derivations = self.make_nodes_from_derivations(derivations, id)
                root.add_child(node)
            new_derivations = derivations.copy()
        else:
            new_derivations = derivations.copy()
            new_derivations.pop(0)
            root = Node(der, id, "leaf")
        return root, new_derivations


class Node:
    def __init__(self, label, id, type):
        self.label = label
        self.id = id
        self.children = []
        self.type = type

    def add_child(self, child):
        self.children.append(child)

    def add_childrens(self, children):
        self.children.extend(children)

# test ll1 to dpda
#-------------------------------------
def visualize_tree(tree, graph=None, parent_name=None, edge_label=""):
    if graph is None:
        graph = Digraph()

    # assign unique ID to prevent merging if node is repeated
    unique_node_name = f"{tree.label}_{uniq_id(tree)}"  
   
    # check whether it's a leaf (has no children) if is put rectangle else put oval
    if not tree.children:
        graph.node(unique_node_name, label=str(tree.label), shape="box") 

    else:
        graph.node(unique_node_name, label=str(tree.label), shape="oval") 

    if parent_name is not None:
        graph.edge(parent_name, unique_node_name)  

    for node in tree.children:
        visualize_tree(node, graph, unique_node_name, node.label) 

    return graph

g = LL1Grammar.file_to_LL1("grammar2.ll1")        
m = DPDA.turn_LL1_to_DPDA(g)
s = "function main ( ) { x = 42 ; y = 3.14 ; z = ( x + y ) * 2 ; if ( z ) { result = z / 1.5 ; } while ( x = 0 ) { x = x - 1 ; } return result ; }"
tokens = g.turn_string_to_tokens(s)
result, derivations = m.process_string(tokens, s)
print(result)
print(derivations)
id = 0
if result:
    tree, derivations = m.make_nodes_from_derivations(derivations, id)
    h = visualize_tree(tree)
    h.render('wt', format='pdf', view=True)

    