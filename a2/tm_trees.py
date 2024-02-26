"""
Assignment 2: Trees for Treemap

=== CSC148 Summer 2023 ===
This code is provided solely for the personal and private use of
students taking the CSC148 course at the University of Toronto.
Copying for purposes other than this use is expressly prohibited.
All forms of distribution of this code, whether as given or with
any changes, are expressly prohibited.

All of the files in this directory and all subdirectories are:
Copyright (c) 2023 Bogdan Simion, David Liu, Diane Horton,
                   Haocheng Hu, Jacqueline Smith, Andrea Mitchell,
                   Bahar Aameri

=== Module Description ===
This module contains the basic tree interface required by the treemap
visualiser. You will both add to the abstract class, and complete a
concrete implementation of a subclass to represent files and folders on your
computer's file system.
"""
from __future__ import annotations

import math
import os
from random import randint
from typing import List, Tuple, Optional


def get_colour() -> Tuple[int, int, int]:
    """This function picks a random colour selectively such that it is not on
    the grey scale. The colour is close to the grey scale if the r g b values
    have a small variance. This function checks if all the numbers are close
    to the mean, if so, it shifts the last digit by 150.

    This way you can't confuse the leaf rectangles with folder rectangles,
    because the leaves will always be a colour, never close to black / white.
    """
    rgb = [randint(0, 255), randint(0, 255), randint(0, 255)]
    avg = sum(rgb) // 3
    count = 0
    for item in rgb:
        if abs(item - avg) < 20:
            count += 1
    if count == 3:
        rgb[2] = (rgb[2] + 150) % 255
    return tuple(rgb)


class TMTree:
    """A TreeMappableTree: a tree that is compatible with the treemap
    visualiser.

    This is an abstract class that should not be instantiated directly.

    You may NOT add any attributes, public or private, to this class.
    However, part of this assignment will involve you implementing new public
    *methods* for this interface.
    You should not add any new public methods other than those required by
    the client code.
    You can, however, freely add private methods as needed.

    === Public Attributes ===
    rect: The pygame rectangle representing this node in the visualization.
    data_size: The size of the data represented by this tree.

    === Private Attributes ===
    _colour: The RGB colour value of the root of this tree.
    _name: The root value of this tree, or None if this tree is empty.
    _subtrees: The subtrees of this tree.
    _parent_tree: The parent tree of this tree; i.e., the tree that contains
    this tree as a subtree, or None if this tree is not part of a larger tree.
    _expanded: Whether this tree is considered expanded for visualization.
    _depth: The depth of this tree node in relation to the root.

    === Representation Invariants ===
    - data_size >= 0
    - If _subtrees is not empty, then data_size is equal to the sum of the
      data_size of each subtree.
    - _colour's elements are each in the range 0-255.
    - If _name is None, then _subtrees is empty, _parent_tree is None, and
      data_size is 0.
      This setting of attributes represents an empty tree.
    - if _parent_tree is not None, then self is in _parent_tree._subtrees
    - if _expanded is True, then _parent_tree._expanded is True
    - if _expanded is False, then _expanded is False for every tree
      in _subtrees
    - if _subtrees is empty, then _expanded is False
    """

    rect: Tuple[int, int, int, int]
    data_size: int
    _colour: Tuple[int, int, int]
    _name: str
    _subtrees: List[TMTree]
    _parent_tree: Optional[TMTree]
    _expanded: bool
    _depth: int

    def __init__(self, name: str, subtrees: List[TMTree],
                 data_size: int = 0) -> None:
        """Initializes a new TMTree with a random colour, the provided name
        and sets the subtrees to the list of provided subtrees. Sets this tree
        as the parent for each of its subtrees.

        Precondition: if <name> is None, then <subtrees> is empty.
        """
        self.rect = (0, 0, 0, 0)
        self._parent_tree = None
        self._depth = 0
        self._expanded = False

        if len(subtrees) > 0:
            # self._expanded = True
            lst_of_data_sizes = [subtree.data_size for subtree in subtrees]
            self.data_size = sum(lst_of_data_sizes)
        else:
            # self._expanded = False
            self.data_size = data_size

        # 1. Initialize: - self._name
        #                - self._colour (use the get_colour() function)
        #                - self._subtrees
        #                - self.data_size
        self._name = name
        self._colour = get_colour()
        self._subtrees = subtrees

        # 2. Set this tree as the parent for each of its subtrees.
        #
        # NOTES: - self._expanded will be changed in task 5
        #        - Leaf nodes will have data_size set to the size of the file
        #        - Internal nodes will have the data_size = 0
        #           -> this needs to be updated based on the sizes of subtrees
        #
        for sub in subtrees:
            sub._parent_tree = self

        # because update_colours_and_depths needs to be called every time
        # a change is made, or instantiation is done, we must call it here
        self.update_colours_and_depths()

    def is_empty(self) -> bool:
        """Returns True iff this tree is empty.
        """
        return self._name is None

    def get_parent(self) -> Optional[TMTree]:
        """Returns the parent of this tree.
        """
        return self._parent_tree

    # **************************************************************************
    # ************* TASK 2: UPDATE AND GET RECTANGLES **************************
    # **************************************************************************

    def update_rectangles(self, rect: Tuple[int, int, int, int]) -> None:
        """Updates the rectangles in this tree and its descendants using the
        treemap algorithm to fill the area defined by the <rect> parameter.
        """
        # Read the Treemap Algorithm description in the handout thoroughly and
        # implement this algorithm to set the <rect> parameter for each
        # tree node.
        #
        # NOTES: - Empty folders should not take up any space
        #        - Both files AND folders need to be assigned a rect attribute
        #        - Don't forget that the last subtree occupies remaining space
        #        - tip: use "tuple unpacking assignment" for easy extraction:
        #           -> x, y, width, height = rect
        #
        # shortcut to get the values
        x_coord, y_coord, width, height = rect

        # to keep track of initial x and y values so that they don't get
        # lost in the iterations
        initial_x, initial_y = rect[0], rect[1]

        # the coords of the rectangle in the bottom right corner
        bottom_right_x, bottom_right_y = initial_x + width, initial_y + height

        self.rect = rect

        if self.data_size == 0 or self.is_empty():
            self.rect = (0, 0, 0, 0)
            # updates the colours and depths after every change
            self.update_colours_and_depths()

        else:
            if width > height:
                for subtree in self._subtrees:
                    # if we have reached the last subtree, we must use up the
                    # remaining space, else, the size must be proportional to
                    # the width and the subtree's data size
                    new_width = bottom_right_x - x_coord \
                        if subtree == self._subtrees[-1] \
                        else math.trunc(subtree.data_size
                                        * width / self.data_size)

                    subtree.update_rectangles((x_coord, y_coord,
                                               new_width, height))
                    # update the colours and depths after every change
                    subtree.update_colours_and_depths()

                    # this updates the x_coord (not the intial_x) for
                    # the next iteration
                    x_coord += new_width

            else:
                for subtree in self._subtrees:
                    # the comments for this are analogous to
                    # the previous one
                    new_height = bottom_right_y - y_coord \
                        if subtree == self._subtrees[-1] \
                        else math.trunc(subtree.data_size
                                        * height / self.data_size)

                    subtree.update_rectangles((x_coord, y_coord,
                                               width, new_height))
                    subtree.update_colours_and_depths()
                    y_coord += new_height

    def get_rectangles(self) -> List[Tuple[Tuple[int, int, int, int],
                                           Tuple[int, int, int]]]:
        """Returns a list with tuples for every leaf in the displayed-tree
        rooted at this tree. Each tuple consists of a tuple that defines the
        appropriate pygame rectangle to display for a leaf, and the colour
        to fill it with.
        """
        #
        # NOTES: - This method will be modified in Task 6 to return both leaf
        #          nodes and internal nodes which are not expanded
        #
        if not self._expanded:
            return [(self.rect, self._colour)]

        else:
            rectangles = []

            for subtree in self._subtrees:
                rectangles.extend(subtree.get_rectangles())

            return rectangles

    # **************************************************************************
    # **************** TASK 3: GET_TREE_AT_POSITION ****************************
    # **************************************************************************

    def get_tree_at_position(self, pos: Tuple[int, int]) -> Optional[TMTree]:
        """Returns the leaf in the displayed-tree rooted at this tree whose
        rectangle contains position <pos>, or None if <pos> is outside of this
        tree's rectangle.

        If <pos> is on the shared edge between two or more rectangles,
        always return the leftmost and topmost rectangle (wherever applicable).
        """
        #
        # NOTES: - This method will be modified in Task 6 to return either a
        #          leaf node or an internal node which is not expanded
        #
        # if out of bounds, return None
        # if we have reached a folder/file with no subtrees, return
        # the tree if the pos is within bounds
        # if we have reached a folder with subtree(s), recurse on the subtree(s)
        x, y, width, height = self.rect
        pos_x, pos_y = pos

        # only gets a position if the "click" or "hover" is within bounds
        if x <= pos_x <= width + x and y <= pos_y <= height + y:
            return self._get_tree_at_position_helper(pos)

        else:
            return None

    def _get_tree_at_position_helper(self, pos: Tuple[int, int]) \
            -> Optional[TMTree]:
        """Helper for get_tree_at_position."""
        if self._subtrees == [] or not self._expanded:
            return self

        else:
            for subtree in self._subtrees:
                check = subtree.get_tree_at_position(pos)
                if check:  # if we have reached the subtree with
                    # this position, return
                    return check
            return None

    # **************************************************************************
    # ********* TASK 4: MOVE, CHANGE SIZE, DELETE, UPDATE SIZES ****************
    # **************************************************************************

    def update_data_sizes(self) -> int:
        """Updates the data_size attribute for this tree and all its subtrees,
        based on the size of their leaves, and return the new size of the given
        tree node after updating.

        If this tree is a leaf, return its size unchanged.
        """
        #
        # NOTES: - This method is called after some change is made to the tree
        #          so that the change of is reflected in all ancestor
        #          nodes which are affected. (i.e., one leaf node size being
        #          modified results in size changes for its ancestral nodes)
        #
        if self.is_empty():
            self.data_size = 0
            # update the depths and colours of the tree
            self.update_colours_and_depths()
            return 0

        elif self._subtrees == []:
            # update the depths and colours of the tree
            self.update_colours_and_depths()
            return self.data_size

        else:
            data_size = 0
            for subtree in self._subtrees:
                data_size += subtree.update_data_sizes()
            self.data_size = data_size
            # update the depths and colours of the tree
            self.update_colours_and_depths()
            return self.data_size

    def change_size(self, factor: float) -> None:
        """Changes the value of this tree's data_size attribute by <factor>.
        Always rounds up the amount to change, so that it's an int, and
        some change is made. If the tree is not a leaf, this method does
        nothing.
        """
        #
        # NOTES: - factor is a percentage in the form of a decimal.
        #          (i.e., factor = 0.01 should increase size by 1%)
        #        - factor may be negative
        #        - the lower limit on data_size is 1 (i.e., you can't let the
        #          size decrease below 1)
        # since we are not making any changes to the "structure" of the tree
        # we don't need to call update_colours_and_depths
        if not self._subtrees:
            change = math.ceil(self.data_size * factor)

            if factor < 0:
                change = math.floor(self.data_size * factor)
                if self.data_size == 0:
                    return
                elif self.data_size + change < 1:
                    self.data_size = 1
                    return

            self.data_size += change

    def delete_self(self) -> bool:
        """Removes the current node from the visualization and
        returns whether the deletion was successful. Only do this if this node
        has a parent tree.

        Do not set self._parent_tree to None, because it might be used
        by the visualizer to go back to the parent folder.
        """
        #
        # NOTES: - if this tree node is an "only child", you need to
        #          recursively keep deleting the empty folder above
        #        - the root node should not be deleted, and the size won't be
        #          updated if the root node is attempted to be deleted
        #
        if self._parent_tree is None:
            self.update_colours_and_depths()
            return False

        if len(self._parent_tree._subtrees) > 1:
            self._parent_tree._subtrees.remove(self)
            self._parent_tree.data_size -= self.data_size
            self.update_colours_and_depths()
            return True
        else:
            self._parent_tree._subtrees.remove(self)
            self._parent_tree.data_size -= self.data_size
            self.update_colours_and_depths()
            return self._parent_tree.delete_self()

    # **************************************************************************
    # ************* TASK 5: UPDATE_COLOURS_AND_DEPTHS **************************
    # **************************************************************************

    def _update_depths_helper(self, d: int) -> None:
        """Helper for update_depths."""
        if self.is_empty():
            self._depth = 0
        else:
            depth = 1 + d
            for subtree in self._subtrees:
                subtree._depth = depth
                subtree._update_depths_helper(depth)

    def update_depths(self) -> None:
        """Updates the depths of the nodes, starting with a depth of 0 at this
        tree node.
        """
        self._update_depths_helper(0)

    def max_depth(self) -> int:
        """Returns the maximum depth of the tree, which is the maximum length
        between a leaf node and the root node.
        """
        if self.is_empty():
            return 0
        else:
            max_depth = 0
            for subtree in self._subtrees:
                depth_temp = subtree.max_depth() + 1
                if depth_temp > max_depth:
                    max_depth = depth_temp
            return max_depth

    def update_colours(self, step_size: int) -> None:
        """Updates the colours so that the internal tree nodes are
        shades of grey depending on their depth. The root node will be black
        (0, 0, 0) and all internal nodes will be shades of grey depending on
        their depth, where the step size determines the shade of grey.
        Leaf nodes should not be updated.
        """
        if self._parent_tree is None and self._subtrees:
            self._colour = (0, 0, 0)

        elif self.data_size == 0:
            self._colour = get_colour()

        for subtree in self._subtrees:
            if subtree._subtrees == []:
                pass
            else:
                subtree._colour = (step_size, step_size, step_size)
                subtree.update_colours(step_size + step_size)

    def update_colours_and_depths(self) -> None:
        """This method is called any time the tree is manipulated or right after
        instantiation. Updates the _depth and _colour attributes throughout
        the tree.
        """
        # 1. Call the update depths method you wrote.
        # 2. Find the maximum depth of the tree.
        # 3. Use the maximum depth to determine the step_size.
        # 4. Call the update_colours method and use step_size as the parameter.
        self.update_depths()
        max_depth = self.max_depth()
        if max_depth == 1:
            step_size = 200
        elif max_depth > 1:
            step_size = 200 // (max_depth - 1)
        else:
            return
        self.update_colours(step_size)

    # **************************************************************************
    # ********* TASK 6: EXPAND, COLLAPSE, EXPAND ALL, COLLAPSE ALL *************
    # **************************************************************************

    def expand(self) -> None:
        """Sets this tree to be expanded. But not if it is a leaf.
        """
        if self._subtrees:
            self._expanded = True

    def expand_all(self) -> None:
        """Sets this tree and all its descendants to be expanded, apart from the
        leaf nodes.
        """
        if not self._subtrees:
            pass
        else:
            self._expanded = True
            for subtree in self._subtrees:
                subtree.expand_all()

    def collapse(self) -> None:
        """Collapses the parent tree of the given tree node and also collapse
        all of its descendants.
        """
        #
        # NOTES: - This method could be called with any node on the tree.
        #        - After this method is called, the parent of the given node
        #          should not be expanded, and any node underneath this tree
        #          should not be expanded.
        #
        if not self.is_empty():
            self._expanded = False

        if self._parent_tree:
            self._parent_tree._expanded = False
            for subtree in self._parent_tree._subtrees:
                subtree._expanded = False
                # since we are supposed to collapse the subtrees
                # of the subtree as well (and this cannot bee done
                # through recursion as in the main loop, we are
                # searching through the parent's subtrees -> will
                # get stuck in a maximum recursion depth, we
                # must make a new loop within this one for each
                # subtree of the parent's subtrees.
                for sub in subtree._subtrees:
                    sub.collapse()

    def collapse_all(self) -> None:
        """ Collapses ALL nodes in the tree.
        """
        #
        # NOTES - This should work if it is called on any node in the tree.
        #       - After this method is called, _expanded should be set to false
        #         for all nodes in the tree.
        self.collapse()
        # collapse this tree first and then collapse its ancestor(s), if any
        if self._parent_tree:
            self._parent_tree.collapse_all()
    # **************************************************************************
    # ************* TASK 7 : DUPLICATE MOVE COPY_PASTE *************************
    # **************************************************************************

    def move(self, destination: TMTree) -> None:
        """If this tree is a leaf, and <destination> is not a leaf, moves this
        tree to be the last subtree of <destination>. Otherwise, does nothing.
        """
        if (not self._subtrees) and destination._subtrees:
            # remove all traces of subtree from its current parent tree
            if self._parent_tree:
                self._parent_tree._subtrees.remove(self)
                self._parent_tree.data_size -= self.data_size
            # transfer the tree to the destination
            self._parent_tree = destination
            destination._subtrees.append(self)

    def duplicate(self) -> Optional[TMTree]:
        """Duplicates the given tree, if it is a leaf node. It stores
        the new tree with the same parent as the given leaf. Returns the
        new node. If the given tree is not a leaf, does nothing.
        """
        #
        # NOTES: - make good use of the FileSystemTree constructor to
        #          instantiate a new node.
        if not self._subtrees:
            duplicate = FileSystemTree(self.get_full_path())
            duplicate._parent_tree = self._parent_tree
            duplicate._depth = self._depth
            if self._parent_tree:
                self._parent_tree._subtrees.append(duplicate)
            return duplicate
        else:
            return None

    def copy_paste(self, destination: TMTree) -> None:
        """If this tree is a leaf, and <destination> is not a leaf, this method
        copies the given, and moves the copy to the last subtree of
        <destination>. Otherwise, does nothing.
        """
        if (not self._subtrees) and destination._subtrees:
            copy = self.duplicate()
            copy._parent_tree._subtrees.remove(copy)
            copy._parent_tree = destination
            copy._depth = destination._depth + 1
            destination._subtrees.append(copy)

    # **************************************************************************
    # ************* HELPER FUNCTION FOR TESTING PURPOSES  **********************
    # **************************************************************************
    def tree_traversal(self) -> List[Tuple[str, int, Tuple[int, int, int]]]:
        """For testing purposes to see the depth and colour attributes for each
        internal node in the tree. Used for passing test case 5.
        """
        if len(self._subtrees) > 0:
            output_list = [(self._name, self._depth, self._colour)]
            for tree in self._subtrees:
                output_list += tree.tree_traversal()
            return output_list
        else:
            return []

    # **************************************************************************
    # *********** METHODS DEFINED FOR STRING REPRESENTATION  *******************
    # **************************************************************************
    def get_path_string(self) -> str:
        """Return a string representing the path containing this tree
        and its ancestors, using the separator for this OS between each
        tree's name.
        """
        if self._parent_tree is None:
            return self._name
        else:
            return self._parent_tree.get_path_string() + \
                self.get_separator() + self._name

    def get_separator(self) -> str:
        """Returns the string used to separate names in the string
        representation of a path from the tree root to this tree.
        """
        raise NotImplementedError

    def get_suffix(self) -> str:
        """Returns the string used at the end of the string representation of
        a path from the tree root to this tree.
        """
        raise NotImplementedError

    # **************************************************************************
    # **************** HELPER FUNCTION FOR TASK 7  *****************************
    # **************************************************************************
    def get_full_path(self) -> str:
        """Returns the path attribute for this tree.
        """
        raise NotImplementedError


class FileSystemTree(TMTree):
    """A tree representation of files and folders in a file system.

    The internal nodes represent folders, and the leaves represent regular
    files (e.g., PDF documents, movie files, Python source code files, etc.).

    The _name attribute stores the *name* of the folder or file, not its full
    path. E.g., store 'assignments', not '/Users/Diane/csc148/assignments'

    The data_size attribute for regular files is simply the size of the file,
    as reported by os.path.getsize.

    === Private Attributes ===
    _path: the path that was used to instantiate this tree.
    """
    _path: str

    def __init__(self, my_path: str) -> None:
        """Stores the directory given by <my_path> into a tree data structure
        using the TMTree class.

        Precondition: <my_path> is a valid path for this computer.
        """
        # 1. Initialize the single attribute: self._path
        # 2. Implement the algorithm described in the handout.
        #
        data_size = 0
        subtrees = []
        if not os.path.isdir(my_path):
            data_size = os.path.getsize(my_path)
        else:
            list_of_files = os.listdir(my_path)
            for file in list_of_files:
                # recursively add each subtree to the subtrees list
                subtrees.append(FileSystemTree(os.path.join(my_path, file)))

        TMTree.__init__(self, os.path.basename(my_path), subtrees, data_size)

        self._path = my_path
        # NOTES: - Review OS module documentation summary provided!
        #        - Remember to make good use of the superclass constructor!
        #        - Notice that the size of folders is calculated in the TMTree
        #          initializer. Thus, set data_size = 0 for the folders
        #

    def get_full_path(self) -> str:
        """Returns the file path for the tree object.
        """
        return self._path

    def get_separator(self) -> str:
        """Returns the file separator for this OS.
        """
        return os.sep

    def get_suffix(self) -> str:
        """Returns the final descriptor of this tree.
        """

        def convert_size(data_size: float, suffix: str = 'B') -> str:
            suffixes = {'B': 'kB', 'kB': 'MB', 'MB': 'GB', 'GB': 'TB'}
            if data_size < 1024 or suffix == 'TB':
                return f'{data_size:.2f}{suffix}'
            return convert_size(data_size / 1024, suffixes[suffix])

        components = []
        if len(self._subtrees) == 0:
            components.append('file')
        else:
            components.append('folder')
            components.append(f'{len(self._subtrees)} items')
        components.append(convert_size(self.data_size))
        return f' ({", ".join(components)})'


if __name__ == '__main__':
    import python_ta

    python_ta.check_all(config={
        'allowed-import-modules': [
            'python_ta', 'typing', 'math', 'random', 'os', '__future__'
        ]
    })
