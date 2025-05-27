#     def return_firsts(ll1):
#         first = {}
#         ll1.non_terminals.reverse()
#         for nt in ll1.non_terminals:
#             right_side = ll1.productions[nt]
#             l = []
#             for r in right_side:
#                 beta = r.split()
#                 l += find_first(ll1 , beta , first)
#             first[nt] = l
#         return first 
     
# def find_first(ll1 : LL1Grammar , beta , first):
#     l = []
#     if not beta:
#         return beta
#     if beta[0] in ll1.terminals or beta[0] == 'eps':
#         l.append(beta[0])
#     else:
#         j = 0
#         var = beta[0]
#         while 'eps' in first[var] and j < len(beta):
#             for e in first[var]:
#                 if e != 'eps':
#                     l.append(e)
#             j += 1
#             if(j < len(beta)):
#                 var = beta[j]
#         if j == len(beta):
#             l.append('eps')
#         for e in first[var]:
#             l.append(e)   
#     return l

# def return_follows(ll1 : LL1Grammar, firsts):
#     follow = {}
#     for nt in ll1.non_terminals:
#         follow[nt] = []
#     ll1.non_terminals.reverse()
#     follow[ll1.start] += ['$']
#     for k , v_list in ll1.productions.items():
#         for v in v_list:
#             v = v.split()
#             for i in range(len(v)) :
#               if v[i] in ll1.non_terminals:
#                 beta = v[i + 1:]
#                 beta_firsts = find_first(ll1 , beta , firsts)
#                 if 'eps' in beta_firsts:
#                     follow[v[i]] += follow[k]
#                     beta_firsts.remove('eps')
#                 follow[v[i]] += beta_firsts 
#     return follow 



