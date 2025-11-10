import itertools


CLAUSE = frozenset[int]
SENTENCE = set[CLAUSE]


def create_dnf(spaces: set[int], clue: int) -> SENTENCE:
    """
    Given a set of board spaces (represented as numerical indices) and a clue
    (representing the numbmer of adjacent mines), return a sentence in
    Disjunctive Normal Form (DNF), such that each clause represents one
    possible assignment of `clue` mines to `spaces`.
    """
    dnf = set()
    for combination in itertools.combinations(spaces, clue):
        clause = set(combination)
        for space in spaces:
            if space not in clause:
                clause.add(-space)
        dnf.add(frozenset(clause))
    return dnf


def distribute(dnf: SENTENCE) -> SENTENCE:
    """
    Return the given Disjunctive Normal Form (DNF) sentence as a sentence in
    Conjunctive Normal Form (CNF).
    
    Note that a DNF sentence is a disjunction of conjuncts, whereas a CNF
    sentence is a conjunction of disjuncts.
    """
    cnf = set()
    for clause in itertools.product(*dnf):
        clause = frozenset(clause)
        if not is_tautology(clause):
            cnf.add(clause)
    return remove_supersets(cnf)


def is_tautology(clause: CLAUSE) -> bool:
    """
    Return True if the given clause contains a term in both its positive and
    negative form; otherwise return False.
    """
    for term in clause:
        if -term in clause:
            return True
    return False


def remove_supersets(clauses: SENTENCE) -> SENTENCE:
    """
    Return the given sentence with all supersets removed. A superset is a set
    that contains all the terms of another set in the sentence, plus one or
    more additional terms.
    """
    clause_list = sorted(clauses, key=len)
    supersets = set()
    for i in range(len(clause_list) - 1):
        for j in range(i + 1, len(clause_list)):
            if clause_list[i] < clause_list[j]:
                supersets.add(clause_list[j])
    for superset in supersets:
        clauses.remove(superset)
    return clauses
