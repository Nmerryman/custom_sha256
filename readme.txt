I Wanted to impliment the SHA256 hash on my own to better understand how it works.
I followed https://www.youtube.com/watch?v=f9EbD6iY9zI as I wrote this.

Each file had their own use:
implementation.py - 	First version of the hash, followed from the youtube video
my_bits.py - 		My custom bit and bitarray implementation to allow me to inject my custom hooks to record the history of use
New_implimentation.py - A remake of the first implementation, but with my custom bit classes [MAIN PROGRAM TO RUN]
comparison.py - 	verify my implimentation with my custom types
History_parser.py - 	parse the unrolled data and and use it to rebuild the hash from its primitives


The intent of this exercise was to understand how the SHA256 algorithm works and then try my hand at unrolling the algorithm.


Please let me know about any bugs found.

