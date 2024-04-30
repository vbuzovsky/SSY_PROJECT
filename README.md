# WSN Demo | Python implementation

Very basic WSN topology visualizer.

![Demo Image](./misc/demo.PNG)

## Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) (for example) to install packages.

```bash
pip install -r requirement.txt
```

## Usage

```bash
python main.py
```

##

## TODO, Bugs, etc.
Note: All sorts of testing is completely missing, the following bugs and errors are result of that (+ bad program design choices, + limited time):
1. **CRITICAL**: Whole program (looks like parser stops working) starts to get very slow all of a sudden. No futher changes in topology can be made and program needs to be restared.
2. **MINOR**: Topology re-draw itself each 10s even there are no changes.
3. **MODERATE**: Stop button doesnt really work (QRunnable cannot be stopped, which was discovered after implementing the whole threading "thing"). This needs complete rework into QThread.
4. **MINOR**: The nodes doesnt have custom images (for Coordinator, Router, End device,..). Fixing this will involve removing MplCanvas and Interactive graph for matplotlib.pyplot and reworking the onclick listener.
5. **MINOR**: The NetworkGraph class is redundant -> implement graph straight in nx.Graph()
6. **MINOR**: The configs for the message struct are not yet suppored, only default can be used.
7. **MODERATE**: UART parser is missing additional data parsing for:
   - Packet Number
   - Time stamp
   - Active period
8. **MINOR**: After initial start of the program, the canvas has 1 node (graph needs to have atleast one node since its creation). This can be fixed by printing white canvas on the start, after start button is clicked, the graph can be shown.
9. **MINOR**: The displayed info is missing some nice conversion of values (board type sensors, etc..)
10. **MINOR**: The whole program is very shallow, there should be some additional tabs with config, logs, etc..
11. **??**: when removing the print statements in the parser, the whole thing just crumbles like a house of cards (honesly, the whole program just needs to be reworked from the ground up, and write tests for each component in the process)