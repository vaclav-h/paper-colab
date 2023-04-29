# Visualization of collaboration on scientific papers

Implementation of visualization of a collaboration network taken from <http://www-personal.umich.edu/~mejn/netdata>. The layout algorithm is implemented in ``fr.py``.  It is a modified version of the Fruchterman and Reingold algorithm [1]. While the visualization is only for the network in ``netscience.gml``, the layout algorithm is applicable to any graph encoded in an adjacency matrix.

The visualization can be run by ``python3 main.py``.


![preview](https://github.com/vaclav-h/paper-colab/example.gif)



## Reference 

[1] Fruchterman, T. M., & Reingold, E. M. (1991). Graph drawing by force‐directed placement. Software: Practice and experience, 21(11), 1129-1164.