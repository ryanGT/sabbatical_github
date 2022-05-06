# To Do:

- fill in the empty functions for Python code generation

    - hopefully, mild changes from Arduino code gen are all that is
      needed

- I need to save the python code gen params to the `gui_params_pybd.txt`
  file

- I need to save the print blocks list and load it correctly.

- at some point, I need to auto-generate the execution order and
  possibly let the user set it

    - put certain blocks automatically at the top of the list:
	
	    - inputs and constants
		- plants that read over i2c and essentially have no BD inputs
		- have each block check that its inputs are above it in the
          execution order
		
	- I don't think I can trust students to do this correctly and the
	  implications will be very bad if they get it wrong



# Completed:

- create methods in pybd block_diagram for changing the name of a block and deleting a block
    - must search for all references to the block in the inputs of other blocks
	
	
