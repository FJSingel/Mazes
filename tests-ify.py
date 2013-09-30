'''
Created on Sep 8, 2013

@author: Frank
'''
import random #for random.randint
import sys #for sys.maxint

import mock
from testify import *

import Mazes #the mazes class I made



class Test(TestCase):

    __cells = []
    __route = ""
    __maze = ""

    @class_setup
    def setUp(self):

        """
        Default maze looks like this ascii picture
        Cell 4 is not validated yet
        There is a blocked route from 1 to 3

            cell 0     <-4    cell 3     5->  cell 4
                | 1             ^ 3
                v       2       |
            cell 1     ->   cell 2
        """

        #generate 5 cells
        for cell in range(0,5):
            self.__cells.append(Mazes.MazeCell())

        #make an empty route
        self.__route = Mazes.MazeRoute()
        self.__empty_route = Mazes.MazeRoute()
        self.__empty_route.add_cells([])
        
        assert_equals(False, self.__route.valid)

        #Connects each cell in a loop, except for cell [4]
        self.__cells[0].add_passages({self.__cells[1]: 1})
        self.__cells[1].add_passages({self.__cells[2]: 2, self.__cells[3]: sys.maxint})
        self.__cells[2].add_passages({self.__cells[3]: 3})
        self.__cells[3].add_passages({self.__cells[0]: 4, self.__cells[4]: 3})

        #makes an empty maze
        self.__maze = Mazes.Maze()

    def test_dead_end(self):

        assert_equals(False, self.__cells[4].valid)

        self.__cells[4].add_passages({self.__cells[0]: sys.maxint})

        assert_equals(True, self.__cells[4].valid)

        #Test the dead end method
        assert_equals(False, self.__cells[3].is_dead_end())
        assert_equals(True, self.__cells[4].is_dead_end())

    def test_valid_route(self):

        route_list = [self.__cells[0],self.__cells[1],self.__cells[2],self.__cells[3]]
        assert_equals(True, self.__route.add_cells(route_list))
        assert_equals(True, self.__route.valid)
        assert_equals(6, self.__route.travel_time())

    def test_single_cell_route(self):

        route_list = [self.__cells[0]]
        assert_equals(True, self.__route.add_cells(route_list))
        assert_equals(True, self.__route.valid)
        assert_equals(0, self.__route.travel_time())

    def test_misordered_route(self):

        route_list = [self.__cells[0],self.__cells[3],self.__cells[2],self.__cells[1]]
        assert_equals(True, self.__route.add_cells(route_list))
        assert_equals(True, self.__route.valid) #Every cell in list is valid, but not in order
        assert_equals(sys.maxint, self.__route.travel_time())

    @suite('disabled', reason="Basic Method Test")
    def test_route_to_string(self):
        route_list = [self.__cells[0],self.__cells[1],self.__cells[2],self.__cells[3]]
        assert_equals(True, self.__route.add_cells(route_list))

        print str(self.__route)

    @suite('disabled', reason="Basic Method Test")
    def test_cell_to_string(self):
        
        for cell in self.__cells:
            print str(cell)

    @suite('disabled', reason="Basic Method Test")
    def test_maze_to_string(self):                                     
        
        assert_equals(False, self.__maze.valid)
        self.__cells[4].add_passages({self.__cells[0]: 5})
        self.__maze.add_cells(self.__cells)
        assert_equals(True, self.__maze.valid)
        print str(self.__maze)

    def test_try_remap_cell(self):
        
        assert_equals(False, self.__cells[3].add_passages({self.__cells[0]: sys.maxint}))

    def test_try_remap_route(self):
        route_list = [self.__cells[0],self.__cells[1],self.__cells[2],self.__cells[3]]
        assert_equals(True, self.__route.add_cells(route_list))
        assert_equals(False, self.__route.add_cells(route_list))

    @suite('disabled', reason="Basic Method Test")
    def test_connected_cells(self):

        print "Testing connected_cells\n"

        for cell in self.__cells[1].connected_cells():
            print str(cell)

    def test_make_maze(self):

        assert_equals(False, self.__maze.valid)
        self.__cells[4].add_passages({self.__cells[0]: 5})
        self.__maze.add_cells(self.__cells)
        assert_equals(True, self.__maze.valid)

    def test_random_route(self):

        assert_equals(False, self.__maze.valid)
        self.__cells[4].add_passages({})
        self.__maze.add_cells(self.__cells)
        assert_equals(True, self.__maze.valid)

        #makes one of 2 possible routes
        self.__maze.__route = self.__maze.generate_route(self.__cells[1], self.__maze.choose_random)

        for cell in self.__maze.__route.get_cells():
            assert_equals(True, cell.valid)

    def test_first_vs_random_same(self):

        #makes a single possible route from cell 4
        assert_equals(False, self.__maze.valid)
        self.__cells.append(Mazes.MazeCell())
        self.__cells[4].add_passages({self.__cells[5]: 3})
        self.__cells.append(Mazes.MazeCell())
        self.__cells[5].add_passages({self.__cells[6]: 3})
        self.__cells[6].add_passages({})
        self.__maze.add_cells(self.__cells)
        assert_equals(True, self.__maze.valid)

        #makes the same route from 2 different route methods
        self.__maze.__route_random = self.__maze.generate_route(self.__cells[4], self.__maze.choose_random)
        self.__maze.__route_first = self.__maze.generate_route(self.__cells[4], self.__maze.choose_arbitrary)
        assert_equals(self.__maze.__route_random, self.__maze.__route_first)

    def ein_rand(self, min, max):
        return 1

    def test_first_vs_random_different(self):
        assert_equals(False, self.__maze.valid)
        self.__cells[4].add_passages({})
        self.__maze.add_cells(self.__cells)
        assert_equals(True, self.__maze.valid)

        #patch to make randint return 1
        with mock.patch.object(random, "randint", self.ein_rand):
            #makes the same route from 2 different route methods
            self.__maze.__route_random = self.__maze.generate_route(self.__cells[3], self.__maze.choose_random)
            self.__maze.__route_first = self.__maze.generate_route(self.__cells[3], self.__maze.choose_arbitrary)
            assert_equals(False, self.__maze.__route_random == self.__maze.__route_first)

    def test_invalid_time(self):
        assert_equals(False, self.__maze.valid)
        assert_equals(False, self.__cells[4].add_passages({self.__cells[0]: -1}))
        assert_equals(self.__cells[4].status.INVALID_TIME, self.__cells[4].status.code)

        #try to add real passages after trying to add negative ones
        assert_equals(True, self.__cells[4].add_passages({self.__cells[0]: 1}))
        self.__maze.add_cells(self.__cells)
        assert_equals(True, self.__maze.valid)
        assert_equals(self.__cells[4].status.OK, self.__cells[4].status.code)

    def test_random_times(self):
        route_list = [self.__cells[0],self.__cells[1],self.__cells[2],self.__cells[3]]
        assert_equals(True, self.__route.add_cells(route_list))
        assert_equals(True, self.__route.valid)
        assert_between(len(route_list)-1, self.__route.travel_time_random(), self.__route.travel_time())

    def test_cell_not_in_maze(self):
        #makes a single possible route from cell 4
        assert_equals(False, self.__maze.valid)
        self.__cells.append(Mazes.MazeCell())
        self.__cells[4].add_passages({self.__cells[5]: 3})
        self.__cells.append(Mazes.MazeCell())
        self.__cells[5].add_passages({self.__cells[6]: 3})
        self.__cells[6].add_passages({})
        self.__maze.add_cells(self.__cells[:-1])
        assert_equals(True, self.__maze.valid)

        #make sure route_first and route_random return an empty list if a cell is not in maze
        self.__maze.__route_random = self.__maze.generate_route(self.__cells[4], self.__maze.choose_random)
        self.__maze.__route_first = self.__maze.generate_route(self.__cells[4], self.__maze.choose_arbitrary)
            
        assert_equals(self.__empty_route, self.__maze.generate_route(self.__cells[4], self.__maze.choose_arbitrary))
        assert_equals(self.__empty_route, self.__maze.generate_route(self.__cells[4], self.__maze.choose_random))

    def test_generate_routes(self):
        assert_equals(False, self.__maze.valid)
        self.__cells[4].add_passages({})
        self.__maze.add_cells(self.__cells)
        assert_equals(True, self.__maze.valid)

        #tests new generate_route method for random
        self.__maze.__route = self.__maze.generate_route(self.__cells[1], self.__maze.choose_random)

        for cell in self.__maze.__route.get_cells():
            assert_equals(True, cell.valid)

        #tests new generate_route method for arbitrary
        self.__maze.__route = self.__maze.generate_route(self.__cells[1], self.__maze.choose_arbitrary)

        for cell in self.__maze.__route.get_cells():
            assert_equals(True, cell.valid)

        #tests new generate_route method for greedy
        self.__maze.__route = self.__maze.generate_route(self.__cells[1], self.__maze.choose_greedy)

        for cell in self.__maze.__route.get_cells():
            assert_equals(True, cell.valid)

    def nein_rand(self, min, max):
        return 0

    def test_average_escape_time(self):
        assert_equals(False, self.__maze.valid)
        self.__cells[4].add_passages({ self.__cells[1]: 1})
        self.__maze.add_cells(self.__cells)
        assert_equals(True, self.__maze.valid)

        #patch to make randint return 0
        with mock.patch.object(random, "randint", self.nein_rand):
            assert_equals(sys.maxint, self.__maze.average_exit_time(self.__cells[4] ,self.__maze.choose_random))
        assert_equals(7, self.__maze.average_exit_time(self.__cells[0] ,self.__maze.choose_arbitrary))
        assert_equals(6, self.__maze.average_exit_time(self.__cells[4] ,self.__maze.choose_greedy))

    def test_average_impossible_route(self):
        assert_equals(False, self.__maze.valid)
        self.__cells[4].add_passages({})
        self.__maze.add_cells(self.__cells)
        assert_equals(True, self.__maze.valid)

        assert_equals(sys.maxint, self.__maze.average_exit_time(self.__cells[0] ,self.__maze.choose_arbitrary))      
        assert_equals(sys.maxint, self.__maze.average_exit_time(self.__cells[0] ,self.__maze.choose_random))      
        assert_equals(sys.maxint, self.__maze.average_exit_time(self.__cells[0] ,self.__maze.choose_greedy))      

    def tearDown(self):
        del self.__cells[:]
        del self.__route


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    run()