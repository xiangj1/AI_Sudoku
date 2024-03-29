import SudokuBoard
import Variable
import Domain
import Trail
import Constraint
import ConstraintNetwork
import time

class BTSolver:

    # ==================================================================
    # Constructors
    # ==================================================================

    def __init__ ( self, gb, trail, val_sh, var_sh, cc ):
        self.network = ConstraintNetwork.ConstraintNetwork(gb)
        self.hassolution = False
        self.gameboard = gb
        self.trail = trail

        self.varHeuristics = var_sh
        self.valHeuristics = val_sh
        self.cChecks = cc

    # ==================================================================
    # Consistency Checks
    # ==================================================================

    # Basic consistency check, no propagation done
    def assignmentsCheck ( self ):
        for c in self.network.getConstraints():
            if not c.isConsistent():
                return False
        return True

    """
        Part 1 TODO: Implement the Forward Checking Heuristic

        This function will do both Constraint Propagation and check
        the consistency of the network

        (1) If a variable is assigned then eliminate that value from
            the square's neighbors.

        Note: remember to trail.push variables before you change their domain
        Return: true is assignment is consistent, false otherwise
    """
    def forwardChecking ( self ):
        lastAssignment = self.trail.trailStack[-1][0]
        neighbors = self.network.getNeighborsOfVariable(lastAssignment)

        for v in neighbors:
            if v.isChangeable():
                self.trail.push(v)
                v.removeValueFromDomain(lastAssignment.domain.values[0])
        return self.assignmentsCheck()

    """
        Part 2 TODO: Implement both of Norvig's Heuristics

        This function will do both Constraint Propagation and check
        the consistency of the network

        (1) If a variable is assigned then eliminate that value from
            the square's neighbors.

        (2) If a constraint has only one possible place for a value
            then put the value there.

        Note: remember to trail.push variables before you change their domain
        Return: true is assignment is consistent, false otherwise
    """
    def norvigCheck ( self ):
        lastAssignment = self.trail.trailStack[-1][0]
        neighbors = self.network.getNeighborsOfVariable(lastAssignment)

        for v in neighbors:
            if v.isChangeable():
                self.trail.push(v)
                v.removeValueFromDomain(lastAssignment.domain.values[0])
                if v.domain.size() == 1:
                    v.assignValue(v.domain.values[0])
                    for c in self.network.getConstraintsContainingVariable(v):
                        if not c.isConsistent():
                            return False
        return True

    """
         Optional TODO: Implement your own advanced Constraint Propagation

         Completing the three tourn heuristic will automatically enter
         your program into a tournament.
     """
    def getTournCC ( self ):
        return None

    # ==================================================================
    # Variable Selectors
    # ==================================================================

    # Basic variable selector, returns first unassigned variable
    def getfirstUnassignedVariable ( self ):
        for v in self.network.variables:
            if not v.isAssigned():
                return v

        # Everything is assigned
        return None

    """
        Part 1 TODO: Implement the Minimum Remaining Value Heuristic

        Return: The unassigned variable with the smallest domain
    """
    def getMRV ( self ):
        mrv = self.getfirstUnassignedVariable()
        for v in self.network.variables:
            if (not v.isAssigned()) and (v.domain.size() < mrv.domain.size()):
                mrv = v
        return mrv

    """
        Part 2 TODO: Implement the Degree Heuristic

        Return: The unassigned variable with the most unassigned neighbors
    """
    def getDegree ( self ):
        var = self.getfirstUnassignedVariable() # The unassigned variable with the most unassigned neighbors
        if var == None:
            return None
        var_neighbors = self.network.getNeighborsOfVariable(var)
        var_assigned_neighbors = 0
        # max_neighbors = len(var_neighbors) #initial the value to the number of neighbors

        # Get the assigned_neighbor of the first node
        for var_nei in var_neighbors:
            if var_nei.isAssigned():
                var_assigned_neighbors += 1

        for v in self.network.variables:
            if not v.isAssigned():
                neighbors = self.network.getNeighborsOfVariable(v)  # get v's neighbors
                assigned_neighbor_size = 0

                for neighbor in neighbors:
                    if neighbor.isAssigned():
                        assigned_neighbor_size += 1
                        if assigned_neighbor_size > var_assigned_neighbors:
                            break

                if assigned_neighbor_size == 0:
                    return v

                if assigned_neighbor_size < var_assigned_neighbors:
                    var = v
                    var_assigned_neighbors = assigned_neighbor_size
        return var



    """
        Part 2 TODO: Implement the Minimum Remaining Value Heuristic
                       with Degree Heuristic as a Tie Breaker

        Return: The unassigned variable with, first, the smallest domain
                and, second, the most unassigned neighbors
    """
    def MRVwithTieBreaker ( self ):
        var = self.getfirstUnassignedVariable()

        if var == None:
            return None

        var_list = []
        for v in self.network.variables:
            if (not v.isAssigned()) and (v.domain.size() <= var.domain.size()):
                if v.domain.size() < var.domain.size():
                    var = v
                    var_list.clear()
                else:
                    var_list.append(v)

        var_list.append(var)

        most_unassigned_neighbor = 0
        for v in var_list:
            v_neighbors = self.network.getNeighborsOfVariable(v)
            v_unassigned_neighbor = 0
            for neighbor in v_neighbors:
                if not neighbor.isAssigned():
                    v_unassigned_neighbor += 1

            if v_unassigned_neighbor > most_unassigned_neighbor:
                var = v
                most_unassigned_neighbor = v_unassigned_neighbor

        return var

    """
         Optional TODO: Implement your own advanced Variable Heuristic

         Completing the three tourn heuristic will automatically enter
         your program into a tournament.
     """
    def getTournVar ( self ):
        return None

    # ==================================================================
    # Value Selectors
    # ==================================================================

    # Default Value Ordering
    def getValuesInOrder ( self, v ):
        values = v.domain.values
        return sorted( values )

    """
        Part 1 TODO: Implement the Least Constraining Value Heuristic

        The Least constraining value is the one that will knock the least
        values out of it's neighbors domain.

        Return: A list of v's domain sorted by the LCV heuristic
                The LCV is first and the MCV is last
    """
    def getValuesLCVOrder ( self, v ):

        if not v:
            return None

        if v.isAssigned():
            return v.getValues()

        v_domains = dict()
        v_neighbors = self.network.getNeighborsOfVariable(v)
        for value in v.getValues():
            value_count = 0
            for neighbor in v_neighbors:
                if neighbor.domain.contains(value):
                    value_count += 1
            v_domains.update({value: value_count})

        return sorted(v_domains)
        """
        vDomain = dict()
        for d in v.domain.values:
            vDomain[d] = 0

        neighbors = self.network.getNeighborsOfVariable(v)
        for n in neighbors:
            for k in vDomain.keys():
                if k in n.domain.values:
                    vDomain[k] += 1

        #print("vdomain: ",vDomain)
        LCV = sorted(vDomain, key = vDomain.__getitem__)

        return LCV
        """
    """
         Optional TODO: Implement your own advanced Value Heuristic

         Completing the three tourn heuristic will automatically enter
         your program into a tournament.
     """
    def getTournVal ( self, v ):
        return None

    # ==================================================================
    # Engine Functions
    # ==================================================================

    def solve ( self ):
        if self.hassolution:
            return

        # Variable Selection
        v = self.selectNextVariable()

        # check if the assigment is complete
        if ( v == None ):
            for var in self.network.variables:

                # If all variables haven't been assigned
                if not var.isAssigned():
                    print ( "Error" )

            # Success
            self.hassolution = True
            return

        # Attempt to assign a value
        for i in self.getNextValues( v ):

            # Store place in trail and push variable's state on trail
            self.trail.placeTrailMarker()
            self.trail.push( v )

            # Assign the value
            v.assignValue( i )

            # Propagate constraints, check consistency, recurse
            if self.checkConsistency():
                self.solve()

            # If this assignment succeeded, return
            if self.hassolution:
                return

            # Otherwise backtrack
            self.trail.undo()

    def checkConsistency ( self ):
        if self.cChecks == "forwardChecking":
            return self.forwardChecking()

        if self.cChecks == "norvigCheck":
            return self.norvigCheck()

        if self.cChecks == "tournCC":
            return self.getTournCC()

        else:
            return self.assignmentsCheck()

    def selectNextVariable ( self ):
        if self.varHeuristics == "MinimumRemainingValue":
            return self.getMRV()

        if self.varHeuristics == "Degree":
            return self.getDegree()

        if self.varHeuristics == "MRVwithTieBreaker":
            return self.MRVwithTieBreaker()

        if self.varHeuristics == "tournVar":
            return self.getTournVar()

        else:
            return self.getfirstUnassignedVariable()

    def getNextValues ( self, v ):
        if self.valHeuristics == "LeastConstrainingValue":
            return self.getValuesLCVOrder( v )

        if self.valHeuristics == "tournVal":
            return self.getTournVal( v )

        else:
            return self.getValuesInOrder( v )

    def getSolution ( self ):
        return self.network.toSudokuBoard(self.gameboard.p, self.gameboard.q)
