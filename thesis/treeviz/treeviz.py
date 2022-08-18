import gzip
import itertools

import numpy as np
import skimage
#import scikit.sparse

import pdb

class GraphBuilder:
    def __init__(self, root_boxcode, label_boxcodes, split_key="0"):
        self.root_boxcode = root_boxcode
        self.label_boxcodes = label_boxcodes
        self.split_key = split_key

        self.max_grid_size = 2 ** 24

    def make_graph(self, trace):
        grids = self._walk(iter(trace), self.root_boxcode)
        for g in reversed(grids):
            self._cluster_grid(self.root_boxcode, g)
        self._render()

    def _walk(self, trace, location):
        grids = [np.array([[[[[[1]]]]]], dtype=np.int8)]
        key = next(trace)
        if key == self.split_key:
            grids0 = self._walk(trace, location + "0")
            grids1 = self._walk(trace, location + "1")
            grids.extend(self._merge(location, grids0, grids1))
        return grids

    def _merge(self, location, grids1, grids2):
        for g1, g2 in itertools.zip_longest(grids1, grids2):
            if g1 is None:
                g1 = np.zeros(g2.shape, dtype=np.int8)
            if g2 is None:
                g2 = np.zeros(g1.shape, dtype=np.int8)
            axis = len(location) % 6
            g = np.concatenate([g1, g2], axis)
            if g.size < self.max_grid_size:
                yield g
            else:
                self._cluster_grid(location, g)

    def _cluster_grid(self, location, grid):
        print(location, grid.shape, grid.sum())
        while grid.sum() > 0:
            coords = _guess_large_cluster(grid)
            mask = skimage.segmentation.flood(grid, coords)
            print(coords, mask.sum())
            grid -= mask

    def _render(self):
        pass

def _guess_large_cluster(grid):
    c = []
    while len(grid.shape) > 0:
        m = np.argmax(grid.sum(axis=tuple(range(1,len(grid.shape)))))
        c.append(m)
        grid = grid[m]
    return tuple(c)


b = GraphBuilder("011001100110100110011110", [])
with gzip.open("../x/verify/data/011001.d/100110.d/100110.d/011110.gz") as f:
    b.make_graph(l.strip().decode("utf8") for l in f)
