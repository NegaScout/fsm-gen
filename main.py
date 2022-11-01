#https://github.com/caleb531/automata
from automata.fa.dfa import DFA
from automata.fa.nfa import NFA
from random import randrange, sample, choices, choice

# all options supports also weights for discrete prob. distribution
# the range has to match the length of list of probabilities
STATES = {'MIN': 4, 'MAX': 7}
TRANSITIONS = {'MIN': 0, 'MAX': 3, 'WEIGHTS': [0.1, 0.2, 1, 0.1]}
ALPHABET = {'MIN': 2, 'MAX': 3, 'START': 'a'}
EPSILON = {'MIN': 1, 'MAX': 3, 'WEIGHTS': [0.2, 0.7, 0.1]}
STARTS = {'MIN': 1, 'MAX': 2}
FINALS = {'MIN': 1, 'MAX': 2}

def gen_states():
    ret = ['S', 'F']
    num_of_states = choices(range(STATES['MIN'], STATES['MAX'] + 1),
                            k=1,
                            weights=STATES.get('WEIGHTS', None))[0]

    for i in range(num_of_states):
        ret += ['q' + str(i)]
    return set(ret)

def gen_alphabet():
    ret = []

    num_of_alphabet = choices(range(ALPHABET['MIN'], ALPHABET['MAX'] + 1),
                              k=1,
                              weights=ALPHABET.get('WEIGHTS', None))[0]

    for i in range(num_of_alphabet):
        ret += [chr(ord(ALPHABET['START']) + i)]
    return set(ret)

def gen_starts(states):
    states = states - {'S', 'F'}
    num_of_starts = choices(range(STARTS['MIN'], STARTS['MAX'] + 1),
                            k=1,
                            weights=STARTS.get('WEIGHTS', None))[0]
    starts = sample(states, num_of_starts)
    ret = {}
    ret['S'] = {'': set(starts)}

    return ret

def gen_finals(states):
    states = states - {'S', 'F'}
    num_of_finals = choices(range(FINALS['MIN'], FINALS['MAX'] + 1),
                            k=1,
                            weights=FINALS.get('WEIGHTS', None))[0]
    ret = {}
    finals = sample(states, num_of_finals)
    for state in finals:
        ret[state] = {'': {'F'}}
    return ret

def gen_epsilons(states):
    states = states - {'S', 'F'}
    num_of_epsilons = choices(range(EPSILON['MIN'], EPSILON['MAX'] + 1),
                              k=1,
                              weights=EPSILON.get('WEIGHTS', None))[0]

    ret = {}
    for i in range(num_of_epsilons):
        pair = random_pair(states)
        if pair[0] not in ret:
            ret[pair[0]] = {'': {pair[1]}}
        else:
            if '' not in ret[pair[0]]:
                ret[pair[0]][''] = {pair[1]}
            else:
                ret[pair[0]][''] |= {pair[1]}
    return ret

def gen_other_transitions(states, alphabet):
    states = states - {'S', 'F'}
    ret = {}
    for state in states:
        num_of_transitions = choices(range(TRANSITIONS['MIN'], TRANSITIONS['MAX'] + 1),
                                     k=1,
                                     weights=TRANSITIONS.get('WEIGHTS', None))[0]
        for i in range(num_of_transitions):
            transition = choice(list(alphabet))
            target_state = random_state(states)
            if state not in ret:
                ret[state] = {transition: {target_state}}
            else:
                if transition not in ret[state]:
                    ret[state][transition] = {target_state}
                else:
                    ret[state][transition] |= {target_state}
    return ret

def random_pair(states):
    return tuple(sample(list(states), 2))

def random_state(states):
    return sample(list(states), 1)[0]

def transitions_union(transitions):
    ret = {}
    for transition_set in transitions: # for every transition map
        for state in transition_set.keys(): # for every state in the map
            if state not in ret: # check if it is in already
                ret[state] = transition_set[state] # if not just assign
            else: # else we have to merge the dicts
                for transition in transition_set[state].keys(): # for every transition type
                    if transition not in ret[state]: # if not in ret, just assign
                        ret[state][transition] = transition_set[state][transition]
                    else: # else union the sets
                        ret[state][transition] |= transition_set[state][transition]
    return ret

def print_nfa(nfa):
    from tabulate import tabulate
    symbols = list(nfa.input_symbols)
    symbols.sort()
    HEADER = ['', 'ε-nfa', 'ε'] + symbols

    TABLE = []
    states = list(nfa.states)
    states.sort()
    for state in states:
        if state == nfa.initial_state or state in nfa.final_states:
            continue
        ROW = []
        start_s = state in nfa.transitions[nfa.initial_state]['']
        final_s = any([f_state in nfa.transitions.get(state, {}).get('', {}) for f_state in nfa.final_states])
        SPECIAL_STATE = ''
        SPECIAL_STATE += '<' if final_s else ''
        SPECIAL_STATE += '-' if start_s or final_s else ''
        SPECIAL_STATE += '>' if start_s else ''
        ROW += [SPECIAL_STATE]
        ROW += [state]

        for transition in [''] + symbols:
            trans_states = nfa.transitions.get(state, {}).get(transition, {})
            trans_states = set(trans_states) - {'F'}
            trans_states = trans_states if trans_states else {}
            ROW += [trans_states]
        TABLE += [ROW]
    print(tabulate(TABLE, headers=HEADER, tablefmt="rounded_outline")) # exists option tablefmt="latex" for generating latex tables

def print_dfa(dfa):
    from tabulate import tabulate
    symbols = list(dfa.input_symbols)
    symbols.sort()
    HEADER = ['', 'dfa'] + symbols
    TABLE = []

    for state in dfa.states:

        ROW = []
        start_s = state == dfa.initial_state
        final_s = state in dfa.final_states
        SPECIAL_STATE = ''
        SPECIAL_STATE += '<' if final_s else ''
        SPECIAL_STATE += '-' if start_s or final_s else ''
        SPECIAL_STATE += '>' if start_s else ''
        ROW += [SPECIAL_STATE]
        ROW += [state]

        for transition in symbols:
            trans_states = dfa.transitions.get(state, {}).get(transition, {})
            # trans_states = set(trans_states) - {'F'}
            trans_states = trans_states if trans_states else {}
            ROW += [trans_states]
        TABLE += [ROW]
    print(tabulate(TABLE, headers=HEADER, tablefmt="rounded_outline")) # exists option tablefmt="latex" for generating latex tables


if __name__ == '__main__':

    states = gen_states()
    alphabet = gen_alphabet()

    starts = gen_starts(states)
    finals = gen_finals(states)
    epsilons = gen_epsilons(states)
    others = gen_other_transitions(states, alphabet)
    transitions = transitions_union([starts, finals, epsilons, others])
    # https://github.com/caleb531/automata
    nfa = NFA(
        states=states,
        input_symbols=alphabet,
        transitions=transitions,
        initial_state='S', # this is hardcoded so NFA can have multiple start states
        # the real start states have epsilon transitions from S
        final_states={'F'} # this is hardcoded because, I felt like it, its the same like with starting states. all final states have epsilons to F
        # either S or F dont have any other transitions then the epsilons
    )
    print_nfa(nfa)
    dfa = DFA.from_nfa(nfa)
    reduced_dfa = dfa.minify()
    print_dfa(reduced_dfa)

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
