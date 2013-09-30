"""
Created on Sep 7, 2013

@author: Frank Singel
FJS52@case.edu

This module creates a maze that holds cells that can have weighted paths to each other
It is also capable of storing and operating on routes

MazeCell now has an enumerated class
"""

import copy
import random
import sys 

class UninitializedObjectException(ValueError):
    """
    #Handles exception for whether or not is_valid() returns true. Inherits from ValueError
    """
    pass

class MazeCell(object):
    """
    Object for an individual cell of the Maze
    """
    class Status(object):
        """
        Enumerates class statuses
        Exists as a class here because of requirements stated in document
        """
        OK = "Status is OK"
        ALREADY_VALID = "Cell is already valid"
        INVALID_TIME = "Time value is invalid"
        

        def __init__(self):
            self.code = self.OK

    def __init__(self):
        """
        Constructor
        Starts as invalid cell with no passages
        """
        self.passage_dict = {}
        self.valid = False
        self.status = self.Status()
        
    def valid_or_raise(self):
        if not self.valid:
            raise UninitializedObjectException("Invalid cell")

    def add_passages(self, passages):
        """
        Adds passages to the cell
        Passages is a dict of [MazeCell: Integer]
        Assumes times will be integers
        """
        #if cell already has passages set
        if self.valid:
            self.status.code = self.status.ALREADY_VALID
            return False
        
        #check for negative/0 path times
        for path in passages:
            if not passages[path] > 0:
                self.status.code = self.status.INVALID_TIME
                return False

        #Set passages. Shallow copy
        self.passage_dict = copy.copy(passages)                
        self.valid = True
        self.status.code = self.status.OK

        return True

    def passages(self):
        """
        returns a dictionary of the cell's possible destinations to travel times
        """
        self.valid_or_raise()

        cell_list = {}
        for cell in self.passage_dict:
            if cell_list[cell] == sys.maxint: #excludes sys.maxint times
                cell_list[cell] = self.passage_dict[cell]
        
        return cell_list
    
    def passage_time_to(self, cell):
        """
        returns the time to a target cell
        """
        self.valid_or_raise()
        
        #check for keyerror. If so, set time to max since path not found
        time = 0
        try:
            time = self.passage_dict[cell]
        except KeyError:
            time = sys.maxint
        return time
        
    def connected_cells(self):
        """
        returns a list of connected cells
        """
        self.valid_or_raise()
        
        cell_list = []
        for cell in self.passage_dict:
            if self.passage_dict[cell] < sys.maxint: #excludes sys.maxint times
                cell_list.append(cell)
        return cell_list
    
    def is_dead_end(self):
        """
        returns whether or not this is a dead end
        """
        self.valid_or_raise()

        #check for valid passages
        for passage in self.passage_dict:
            if self.passage_dict[passage] < sys.maxint:
                return False
        return True
    
    def __str__(self):
        """
        returns a human readable representation of this cell
        Assumes cell it's called on has passages, blocked or viable
        """
        text_rep = "Cell #" + str(id(self)) + '\n'
        
        #prints str(id(cell)) instead of str(cell) so that it doesn't recursively call itself
        for cell in self.passage_dict:
            text_rep += "Time to cell #" + str(id(cell)) + ": " + str(self.passage_dict[cell]) + '\n'
        return text_rep

    def __hash__(self):
        """
        Returns a hash of the cell
        """
        return id(self)

class MazeRoute(object):
    """
    Object for path through the maze
    Assume that order is important in the list
    IE: first index is start, second is next place, etc...
    """
    def __init__(self):
        """
        Constructor that initializes an empty and invalid route
        """
        self.route = []
        self.valid = False

    def __eq__(self, other):
        """
        Compares for equality using the lists the routes were based on
        """
        return self.route == other.route

    def valid_or_raise(self):
        if not self.valid:
            raise UninitializedObjectException("Invalid route")
        
    def add_cells(self, cells):
        """
        Adds a list of cells to the route
        Cell order is important in the route
        """

        #if there's already cells
        if self.valid:
            return False
        
        #check for invalid cells
        for cell in cells:
            cell.valid_or_raise()
        
        self.valid = True
        self.route = copy.copy(cells)
        return True
        
    def travel_time(self):
        """
        Returns the total travel time of route, given each value is 1 to cell.value
        Assumes cell.value is an integer
        """
        self.valid_or_raise()
        
        #if path is only 1 cell, length is 0
        if len(self.route) == 1:
            return 0

        #pairs path starts and destinations in tuples
        route_trace = zip(self.route[:-1], self.route[1:])
        total_time = 0
        
        #Total the path's time
        for passage1, passage2 in route_trace:
            length = passage1.passage_time_to(passage2)
            if length < sys.maxint: 
                total_time += length
            else: #if nonexistant/blocked passage
                return sys.maxint
        return total_time 


    def get_cells(self):
        """
        returns the list of cells in the route
        """
        self.valid_or_raise()

        #returns a shallow copy to maintain route integrity
        return copy.copy(self.route)
        
    def __str__(self):
        """
        Makes the path human readable
        """
        self.valid_or_raise()
        
        #puts path starts and destinations at same indices
        route_trace = zip(self.route[:-1], self.route[1:])
        text_rep = "\nStart:\n"

        #generate a string of "Cell A to Cell B: X Seconds"
        for passage in route_trace:
            length = passage[0].passage_time_to(passage[1])
            if length < sys.maxint: 
                text_rep += "Cell " + str(id(passage[0])) + " to cell "
                text_rep += str(id(passage[1])) + ": " + str(length) + " seconds.\n"
            else: #if nonexistant/blocked passage
                text_rep += "Cell " + str(id(passage[0])) + " to cell "
                text_rep += str(id(passage[1])) + ": Blocked\n"
        text_rep += "End of route\n"

        return text_rep
    
    def travel_time_random(self):
        """
        Totals the travel time in a route
        """
        self.valid_or_raise()
        
        #if path is only 1 cell, length is 0
        if len(self.route) == 1:
            return 0

        #pairs path starts and destinations in tuples
        route_trace = zip(self.route[:-1], self.route[1:])
        total_time = 0
        
        #Total the path's time
        for passage1,passage2 in route_trace:
            length = passage1.passage_time_to(passage2)
            if length < sys.maxint: 
                total_time += random.randint(1, length)
            else: #if nonexistant/blocked passage
                return sys.maxint
        return total_time 

class Maze(object):
    """
    This holds the maze cells in one class
    """

    def __init__(self):
        """
        initializes cell list as empty
        """
        self.cells = []
        self.valid = False

    def valid_or_raise(self):
        if not self.valid:
            raise UninitializedObjectException("Maze not initialized")

    #choices do not deal with blocked passages, as these are addressed in the make_route function
    def choose_greedy(self, initial_cell):
        """
        Choose shortest path of the cell
        """
        possible_passages = initial_cell.passage_dict
        fastest_cell = possible_passages.keys()[0]
        fastest_time = possible_passages[fastest_cell]

        for passage in possible_passages:
            if possible_passages[passage] < fastest_time:
                fastest_cell = passage
                fastest_time = possible_passages[passage]

        return fastest_cell

    def choose_arbitrary(self, initial_cell):
        """
        Chooses the first cell in the dictionary
        """
        possible_cells = initial_cell.connected_cells()
        return possible_cells[0];

    def choose_random(self, initial_cell):
        """
        Chooses a random cell
        """
        possible_cells = initial_cell.connected_cells()
        return possible_cells[random.randint(0, len(possible_cells)-1)]

    def generate_route(self, initial_cell, method):
        """
        This returns a route of cells that a randomly wandering "mouse" walks through
        initial_cell is a MazeCell that is supposed to be in this maze
        """
        self.valid_or_raise()

        path = []
        current_cell = initial_cell
        route = MazeRoute()

        while current_cell not in path:
            #if cell is not in maze, return empty list
            if not current_cell in self.cells:
                route.add_cells([])
                return route
            #if current cell wasn't visited yet, add it to the path.
            if not current_cell in path:
                path.append(current_cell)
            #return the followed path if in a dead end
            if current_cell.is_dead_end():
                route.add_cells(path)
                return route
            #makes a list of cells that can be entered and move to a random cell
            current_cell = method(current_cell);
        route.add_cells(path)
        return route

    def add_cells(self, cells):
        """
        This adds the passed cells to the maze
        Returns false if maze is already valid
        Raises UninitializedObjectException if any cell added is invalid
        """
        if self.valid:
            return False

        for cell in cells:
            cell.valid_or_raise()

        self.cells = copy.copy(cells)
        self.valid = True
        return True

    def __str__(self):

        if not self.valid:
            return "Unitialized Maze"

        str_rep = "\n"
        for cell in self.cells:
            str_rep += str(cell)

        return str_rep

    def average_exit_time(self, outside, method):
        """
        Returns the average exit time given an exit outside and a method of searching cells from all cells.
        Excludes outside cell
        If maze has a cell that cannot find outside, then it will return sys.maxint
        """
        total_time = 0

        for cell in self.cells:
            current_cell = cell
            path = []
            subtotal_time = 0
            while current_cell != outside:
                #return the followed path if in a dead end
                if (current_cell.is_dead_end()) or (current_cell in path):
                    return sys.maxint
                #makes a list of cells that can be entered and move to a random cell
                path.append(current_cell)

                next_cell = method(current_cell)
                total_time += current_cell.passage_dict[next_cell]
                current_cell = next_cell;
        return (total_time / (len(self.cells) - 1)) 
