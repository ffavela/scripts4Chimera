# scripts4Chimera

Just a set of programs for improving the data flow speed from the
acquired data to making analysis.

The python scripts have only been tested for python 3. I'll see if I
can make it work with python 2.

The "format4SpreadSheet" program simply takes channel information from
txt files (created by taglierina for example) and also energy
information from other txt files given as input. It pastes them
together as columns and in case the number of channel files and the
number of energy files are equal then it will make a directory (
"files4Gnuplot" in case it did not previously exist) and put files
separated by telescope in order to calibrate them easely with gnuplot
via another script ("simpleGpltScript.sh").

For the script "format4SpreadSheet", assuming it has already been
installed, you can run it from any directory by simply typing it's
name:

$ format4SpreadSheet
usage: format4SpreadSheet chFiles... [options] #use -h for help

A small synopsis of the usage is printed. Using the -h option we get:

$ format4SpreadSheet -h
usage: format4SpreadSheet chFiles... [options] #use -h for help
options:
        -h | --help:     displays this menu.
        -c eFiles... :   expects a set of files chimera format, 35 lines single col.
        -C Efiles... :   expects a set of 2 col tNum (or histo) energ files.
        -s enerVa... :   expects a set of values that will be the same for all rows.
        --prefixShift:   expects a prefix and a shift rule for converting histograms to teles.
        --range min max:         expects the range for printing the rows.

We get an extended help with some options.

For using the "simpleGpltScript" (assuming that it was also installed)
simply type from any directory on the terminal:

$ simpleGpltScript

It will plot out a simple synopsis along with some options.

I'll add more descriptions later.
