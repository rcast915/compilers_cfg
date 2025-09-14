# compilers_cfg
This repo contains a cfg implementation by Adrian Sampson with extended functinality.

I tested the functinality of the functions with three test.
- jmp.bril
- gcd.bril
- irreducible.bril (Note this code cannot be run as we will get an infinite loop this is just used to test the functionality of the irreducuble function)

# Usage

The base command to run is (Execute this command from test file):

bril2json < [file].bril | python3 ../cfg.py


This always prints the CFG in DOT format. You can add optional flags to show extra analysis:

--paths → shortest path lengths from the entry block.

--rpo → reverse postorder traversal of the CFG.

--backs → back edges (used to detect loops).

--reducible → check if the CFG is reducible.

--all → run all of the above in addition to printing the CFG.

# Example:

bril2json < gcd.bril | python3 ../cfg.py --all

# Each of the files also has a corresponding turnt file to test agaisnt expected output
