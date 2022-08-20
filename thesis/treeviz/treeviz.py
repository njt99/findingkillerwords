from dataclasses import dataclass
import gzip
import itertools

import numpy as np
import skimage
import scipy.sparse

import pdb


@dataclass
class Cluster:
    size: int
    labels: list


@dataclass
class BoundedBoxes:
    location: str
    depth: int = 0
    grid: np.ndarray = None
    clusters: list = None
    boundary: np.ndarray = None


class GraphBuilder:
    def __init__(self, root_boxcode, label_boxcodes, split_key="0"):
        self.root_boxcode = root_boxcode
        self.label_boxcodes = label_boxcodes
        self.split_key = split_key

        self.max_grid_depth = 24

    def make_graph(self, trace):
        bbs = self._walk(iter(trace), self.root_boxcode)
        for bb in reversed(bbs):
            if bb.grid is not None:
                self._grid_to_clusters(bb)
        self._render(bbs)

    def _walk(self, trace, location):
        bbs = [self._single_box(location)]
        key = next(trace)
        if key == self.split_key:
            bbs0 = self._walk(trace, location + "0")
            bbs1 = self._walk(trace, location + "1")
            bbs.extend(
                self._merge(bb0, bb1, location)
                for bb0, bb1 in itertools.zip_longest(bbs0, bbs1))
        return bbs


    def _single_box(self, location):
        g = np.ones(shape=[1] * 6, dtype=np.int8)
        return BoundedBoxes(location, grid=g)

    def _merge(self, bb0, bb1, location):
        if bb0 is not None:
            depth = 1 + bb0.depth
        else:
            depth = 1 + bb1.depth
        if depth > self.max_grid_depth:
            return self._merge_clusters(bb0, bb1, location)
        bb = self._merge_grid(bb0, bb1, location)
        if depth == self.max_grid_depth:
            self._grid_to_clusters(bb)
        return bb

    def _merge_grid(self, bb0, bb1, location):
        axis = len(location) % 6
        if bb0 is None:
            if bb1.grid is None:
                pdb.set_trace()
            g = np.concatenate(
                    [np.zeros(bb1.grid.shape, dtype=np.int8), bb1.grid], axis)
            depth = bb1.depth + 1
        elif bb1 is None:
            g = np.concatenate(
                    [bb0.grid, np.zeros(bb0.grid.shape, dtype=np.int8)], axis)
            depth = bb0.depth + 1
        else:
            if bb0.grid.shape != bb1.grid.shape:
                pdb.set_trace()
            g = np.concatenate([bb0.grid, bb1.grid], axis)
            depth = bb0.depth + 1
        return BoundedBoxes(location, depth=depth, grid=g)

    def _grid_to_clusters(self, bb):
        clusters = []
        boundary = []
        while bb.grid.sum() > 0:
            coords = _guess_large_cluster(bb.grid)
            mask = skimage.segmentation.flood(bb.grid, coords)
            cluster = self._make_cluster(bb, mask)
            bb.grid -= mask
            mask[1:-1,1:-1,1:-1,1:-1,1:-1,1:-1] = 0
            cluster_boundary_coords = np.nonzero(mask)
            cluster_boundary_ids = np.full(
                    shape=len(cluster_boundary_coords[0]),
                    fill_value=len(clusters))
            clusters.append(cluster)
            boundary.append(np.array(
                list(cluster_boundary_coords) + [cluster_boundary_ids],
                dtype=np.int32))
        bb.grid = None
        bb.clusters = clusters
        bb.boundary = np.concatenate(boundary, axis=1)

    def _make_cluster(self, bb, mask):
        labels = []  # TODO
        return Cluster(mask.sum(), labels)

    def _merge_clusters(self, bb0, bb1, location):
        axis, shape = self._get_merge_axis_and_shape(bb0 or bb1)
        depth = None
        clusters = []
        boundary = []
        adjacent = [None, None]
        if bb0 is not None:
            assert bb0.location == location + "0"
            depth = 1 + bb0.depth
            face, exterior = self._select_merge_face_boundary(bb0)
            boundary.append(exterior)
            adjacent[0] = face
            clusters.extend(bb0.clusters)
        if bb1 is not None:
            assert bb1.location == location + "1"
            depth = 1 + bb1.depth
            face, exterior = self._select_merge_face_boundary(bb1)
            for b in face, exterior:
                b[axis] += shape[axis]
                b[-1] += len(clusters)
            boundary.append(exterior)
            adjacent[1] = face
            clusters.extend(bb1.clusters)
        boundary = np.concatenate(boundary, axis=1)
        bb = BoundedBoxes(location, depth=depth, clusters=clusters, boundary=boundary)
        adj_coo = self._cross_connections(bb, adjacent)
        self._combine_connected_clusters(bb, adj_coo)
        return bb
    
    def _get_merge_axis_and_shape(self, bb):
        axis = len(bb.location) % 6
        merge_axis, shape = (axis + 5) % 6, [1] * 6
        for i in range(bb.depth):
            shape[(axis + i) % 6] *= 2
        return merge_axis, shape

    def _select_merge_face_boundary(self, bb):
        merge_axis, shape = self._get_merge_axis_and_shape(bb)
        if bb.location[-1] == "0":
            target = shape[merge_axis] - 1
        else:
            target = 0
        face_sel = bb.boundary[merge_axis] == target
        face = bb.boundary[:, face_sel]
        not_face = bb.boundary[:, ~face_sel]
        exterior_sels = [face[ax] == side * (shape[ax] - 1)
                for ax in range(6)
                for side in range(2)
                if ax != merge_axis]
        exterior_sel = np.any(exterior_sels, axis=0)
        face_exterior = face[:, exterior_sel]
        face_interior = face[:, ~exterior_sel]
        exterior = np.concatenate([not_face, face_exterior], axis=1)
        return face, exterior

    def _cross_connections(self, bb, facing):
        if facing[0] is None or facing[1] is None:
            return
        axis = len(bb.location) % 6
        s = np.concatenate(facing, axis=1)
        s = np.concatenate([s[:axis], s[axis + 1:]], axis=0)
        idxs = np.lexsort([x for x in s[::-1]])
        s = s[:, idxs]
        diff = s[:,1:] - s[:,:-1]
        eq = np.all(diff[:-1]==0, axis=0)
        if eq.any():
            starts = s[-1,:-1][eq]
            ends = s[-1,1:][eq]
            adj_mat = scipy.sparse.coo_array(
                    (np.ones(len(starts)), (starts, ends)),
                    shape=(len(bb.clusters), len(bb.clusters)))
            return adj_mat
        else:
            return None
    
    def _combine_connected_clusters(self, bb, adj_mat):
        if adj_mat is None:
            return
        n, labels = scipy.sparse.csgraph.connected_components(adj_mat)
        bb.boundary[-1] = labels[bb.boundary[-1]]
        new_clusters = []
        for i in range(n):
            idxs, = np.nonzero(labels == i)
            clusters = [bb.clusters[i] for i in idxs]
            size = sum(c.size for c in clusters)
            new_clusters.append(Cluster(size=size, labels=[]))
        bb.clusters = new_clusters

    def _render(self, layers):
        print(f"digraph tree-{self.root_boxcode} {{")
        for bb in layers:
            for i, c in enumerate(bb.clusters):
                r = 0.1 * (c.size ** (1/6))
                print(f"  c-{bb.depth}-{i}  [shape=circle, width={r}, fixedsize=true]")
        print(f"}}")


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
