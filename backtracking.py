from csp import Constraint, Variable, CSP
from constraints import *
import random

class UnassignedVars:
    '''class for holding the unassigned variables of a CSP. We can extract
       from, re-initialize it, and return variables to it.  Object is
       initialized by passing a select_criteria (to determine the
       order variables are extracted) and the CSP object.

       select_criteria = ['random', 'fixed', 'mrv'] with
       'random' == select a random unassigned variable
       'fixed'  == follow the ordering of the CSP variables (i.e.,
                   csp.variables()[0] before csp.variables()[1]
       'mrv'    == select the variable with minimum values in its current domain
                   break ties by the ordering in the CSP variables.
    '''
    def __init__(self, select_criteria, csp):
        if select_criteria not in ['random', 'fixed', 'mrv']:
            pass #print "Error UnassignedVars given an illegal selection criteria {}. Must be one of 'random', 'stack', 'queue', or 'mrv'".format(select_criteria)
        self.unassigned = list(csp.variables())
        self.csp = csp
        self._select = select_criteria
        if select_criteria == 'fixed':
            #reverse unassigned list so that we can add and extract from the back
            self.unassigned.reverse()

    def extract(self):
        if not self.unassigned:
            pass #print "Warning, extracting from empty unassigned list"
            return None
        if self._select == 'random':
            i = random.randint(0,len(self.unassigned)-1)
            nxtvar = self.unassigned[i]
            self.unassigned[i] = self.unassigned[-1]
            self.unassigned.pop()
            return nxtvar
        if self._select == 'fixed':
            return self.unassigned.pop()
        if self._select == 'mrv':
            nxtvar = min(self.unassigned, key=lambda v: (v.curDomainSize(), -len(self.csp.constraintsOf(v))))
            self.unassigned.remove(nxtvar)
            return nxtvar


    def empty(self):
        return len(self.unassigned) == 0

    def insert(self, var):
        if not var in self.csp.variables():
            pass #print "Error, trying to insert variable {} in unassigned that is not in the CSP problem".format(var.name())
        else:
            self.unassigned.append(var)

def bt_search(algo, csp, variableHeuristic, allSolutions, trace):
    '''Main interface routine for calling different forms of backtracking search
       algorithm is one of ['BT', 'FC', 'GAC']
       csp is a CSP object specifying the csp problem to solve
       variableHeuristic is one of ['random', 'fixed', 'mrv']
       allSolutions True or False. True means we want to find all solutions.
       trace True of False. True means turn on tracing of the algorithm

       bt_search returns a list of solutions. Each solution is itself a list
       of pairs (var, value). Where var is a Variable object, and value is
       a value from its domain.
    '''
    solutions = []
    varHeuristics = ['random', 'fixed', 'mrv']
    algorithms = ['BT', 'FC', 'GAC']

    #statistics
    bt_search.nodesExplored = 0

    if variableHeuristic not in varHeuristics:
        pass #print "Error. Unknown variable heursitics {}. Must be one of {}.".format(
        #variableHeuristic, varHeuristics)
    if algo not in algorithms:
        pass #print "Error. Unknown algorithm heursitics {}. Must be one of {}.".format(
        #algo, algorithms)

    uv = UnassignedVars(variableHeuristic,csp)
    Variable.clearUndoDict()
    for v in csp.variables():
        v.reset()
    if algo == 'BT':
        AC3(csp)  # Perform initial AC-3 propagation
        solutions = BT(uv, csp, allSolutions, trace)
    elif algo == 'FC':
        for cnstr in csp.constraints():
            if cnstr.arity() == 1:
                FCCheck(cnstr, None, None)
        solutions = FC(uv, csp, allSolutions, trace)
    elif algo == 'GAC':
        GacEnforce(csp.constraints(), csp, None, None)
        solutions = GAC(uv, csp, allSolutions, trace)

    return solutions, bt_search.nodesExplored

def FCCheck(cnstr, var, val):
    """
    Forward Checking: Enforce consistency for a single variable-value assignment.
    """
    pruned = []
    for v in cnstr.unAssignedVars():
        for d in v.curDomain():
            if not cnstr.hasSupport(v, d):
                v.pruneValue(d, var, val)  # Pass the variable and value causing the pruning
                pruned.append((v, d))
                if v.curDomainSize() == 0:  # Domain wipe-out
                    # Restore pruned values on failure
                    for pvar, pval in pruned:
                        pvar.restoreValue(pval)
                    return False
    return True


def AC3(csp,var1=None, val1=None):
    """
    AC-3 Algorithm for constraint propagation.
    """
    queue = list(csp.constraints())
    while queue:
        cnstr = queue.pop(0)
        for var in cnstr.scope():
            for val in var.curDomain():
                if not cnstr.hasSupport(var, val):
                    var.pruneValue(val,var1,val1)
                    if var.curDomainSize() == 0:
                        return False
                    for c in csp.constraintsOf(var):
                        if c != cnstr:
                            queue.append(c)
    return True


def FC(unAssignedVars, csp, allSolutions, trace):
    """
    Forward Checking with Backtracking.
    """
    if unAssignedVars.empty():
        if trace:
            print("Solution Found!")
        return [[(v, v.getValue()) for v in csp.variables()]]

    bt_search.nodesExplored += 1
    solutions = []
    nxtvar = unAssignedVars.extract()

    if trace:
        print(f"Trying {nxtvar.name()}...")

    for val in nxtvar.curDomain():
        nxtvar.setValue(val)
        consistent = True

        for cnstr in csp.constraintsOf(nxtvar):
            if cnstr.numUnassigned() == 0 and not cnstr.check():
                consistent = False
                break
            if cnstr.numUnassigned() == 1:
                FCCheck(cnstr, nxtvar, val)

        if consistent:
            new_solutions = FC(unAssignedVars, csp, allSolutions, trace)
            if new_solutions:
                solutions.extend(new_solutions)
            if len(solutions) > 0 and not allSolutions:
                break

        nxtvar.unAssign()

    unAssignedVars.insert(nxtvar)
    return solutions


def GacEnforce(constraints, csp, var=None, val=None):
    """
    Generalized Arc Consistency (GAC): Enforces consistency for all constraints.
    """
    queue = list(constraints)
    while queue:
        cnstr = queue.pop(0)
        for v in cnstr.scope():
            for d in v.curDomain():
                if not cnstr.hasSupport(v, d):
                    v.pruneValue(d, var, val)  # Pass the variable and value causing the pruning
                    if v.curDomainSize() == 0:  # Domain wipe-out
                        return False  # Failure
                    for c in csp.constraintsOf(v):
                        if c != cnstr and c not in queue:
                            queue.append(c)
    return True



def GAC(unAssignedVars, csp, allSolutions, trace):
    """
    Generalized Arc Consistency with Backtracking.
    """
    if unAssignedVars.empty():
        if trace:
            print("Solution Found!")
        return [[(v, v.getValue()) for v in csp.variables()]]

    bt_search.nodesExplored += 1
    solutions = []
    nxtvar = unAssignedVars.extract()


    for val in nxtvar.curDomain():
        nxtvar.setValue(val)
        if GacEnforce(csp.constraints(), csp, nxtvar, val):
            new_solutions = GAC(unAssignedVars, csp, allSolutions, trace)
            if new_solutions:
                solutions.extend(new_solutions)
            if len(solutions) > 0 and not allSolutions:
                break

        nxtvar.unAssign()

    unAssignedVars.insert(nxtvar)
    return solutions

def BT(unAssignedVars, csp, allSolutions, trace):
    '''Backtracking Search. unAssignedVars is the current set of
       unassigned variables.  csp is the csp problem, allSolutions is
       True if you want all solutionss trace if you want some tracing
       of variable assignments tried and constraints failed. Returns
       the set of solutions found.

      To handle finding 'allSolutions', at every stage we collect
      up the solutions returned by the recursive  calls, and
      then return a list of all of them.

      If we are only looking for one solution we stop trying
      further values of the variable currently being tried as
      soon as one of the recursive calls returns some solutions.
    '''
    if unAssignedVars.empty():
        if trace:
            print("Solution Found!")
        soln = [(v, v.getValue()) for v in csp.variables()]
        return [soln]

    bt_search.nodesExplored += 1
    solns = []

    # Extract next variable using heuristics
    nxtvar = unAssignedVars.extract()
    if trace:
        print(f"==> Trying {nxtvar.name()} with domain {nxtvar.curDomain()}")

    # Sort values using Least-Constraining-Value heuristic
    values = sorted(nxtvar.curDomain(), key=lambda val: count_constraint_violations(nxtvar, val, csp))

    for val in values:
        nxtvar.setValue(val)
        if trace:
            print(f"==> {nxtvar.name()} = {val}")

        # Check constraints for the current assignment
        consistent = True
        for cnstr in csp.constraintsOf(nxtvar):
            if cnstr.numUnassigned() == 0 and not cnstr.check():
                consistent = False
                if trace:
                    print(f"<== Constraint {cnstr.name()} violated!")
                break

        if consistent:
            # Recursive call for the next variable
            new_solns = BT(unAssignedVars, csp, allSolutions, trace)
            if new_solns:
                solns.extend(new_solns)
                if len(solns) > 0 and not allSolutions:
                    break  # Stop if only one solution is needed

        nxtvar.unAssign()  # Undo assignment

    # Reinsert the variable for backtracking
    unAssignedVars.insert(nxtvar)
    return solns

def count_constraint_violations(var, val, csp):
    """
    Count the number of constraint violations caused by assigning val to var.
    Lower values indicate less constraining assignments.
    """
    var.setValue(val)
    violations = 0

    for cnstr in csp.constraintsOf(var):
        for neighbor in cnstr.unAssignedVars():
            if not any(cnstr.hasSupport(neighbor, d) for d in neighbor.curDomain()):
                violations += 1

    var.unAssign()
    return violations

