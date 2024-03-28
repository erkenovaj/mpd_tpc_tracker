# NICA Experiment

This repository belongs to the MPD project and contains software developed during the research
to clean up data obtained after running the ACTS tool.

Repository organization:
1) The file usage_example.py contains an example of processing data from one event using all the algorithms we have developed
2) analyze folder - contains software for analyzing the operation of algorithms (including visualization)
3) data folder - contains examples of test data
4) data_processing folder - contains software for loading data or type casting
5) post_processing folder - Contains the post-processing methods we developed

# OS and Python:
_All tests were performed in Python-3.10 on Linux-22.04, Windows 10/11_

# Installation:
```shell
pip install pandas pyopengl PyQt6 pyqtgraph scipy

# to load large files
git-lfs pull
```

Also you have to install tensorflow in your venv if you want to test post-processing based on Neural Net

# Visualization:
Navigation:
1) Mouse wheel - Zoom
2) LMB - Rotate the object
3) CTRL + LMB - Move an object

Hotkeys:
1) Press 'i' - Enable/Disable display of track indexes
2) Press 's' - Enable/Disable display of data from simulation
3) Press 't' - Enable/Disable display of track arcs
4) When you enable multiple post-processing methods at the same time, you can use the number keys (1, 2, etc.) to switch visualization between them

