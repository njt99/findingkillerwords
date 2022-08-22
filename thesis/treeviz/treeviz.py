from dataclasses import dataclass
import copy
import gzip
import itertools

import numpy as np
import skimage
import scipy.sparse

import pdb


@dataclass
class Cluster:
    size: int
    labels: set
    example: str
    parent: int = None


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
        for i in reversed(range(len(bbs))):
            if bbs[i].clusters is None:
                bbs[i] = self._cluster_gridded(bbs[i],
                        bbs[i+1] if i + 1 < len(bbs) else None)
        self._render(bbs)

    def _walk(self, trace, location):
        bbs = [self._single_box(location)]
        key = next(trace)
        if key == self.split_key:
            bbs0 = self._walk(trace, location + "0")
            bbs1 = self._walk(trace, location + "1")
            bbs.extend(self._glue_all(bbs0, bbs1))
        return bbs


    def _single_box(self, location):
        g = np.ones(shape=[1] * 6, dtype=np.int8)
        return BoundedBoxes(location, grid=g)
    
    def _glue_all(self, bbs0, bbs1):
        n = len(bbs0) - len(bbs1);
        if n < 0:
            bbs0.extend([None] * (-n))
        elif n > 0:
            bbs1.extend([None] * n)

        n = len(bbs1)
        glued = [None] * (n + 1)
        for i in reversed(range(n)):
            glued[i] = self._glue(bbs0[i], bbs1[i], glued[i + 1])
        return glued[:-1]

    def _glue(self, bb0, bb1, bb_deeper):
        if bb0 is not None:
            depth = 1 + bb0.depth
        else:
            depth = 1 + bb1.depth

        if depth > self.max_grid_depth:
            return self._glue_clustered(bb0, bb1, bb_deeper)
        else:
            bb = self._glue_gridded(bb0, bb1)
            if depth == self.max_grid_depth:
                return self._cluster_gridded(bb, bb_deeper)
            else:
                return bb

    def _glue_gridded(self, bb0, bb1):
        if bb0 is None:
            location = bb1.location[:-1]
            axis = len(bb1.location[:-1]) % 6
            g = np.concatenate(
                    [np.zeros(bb1.grid.shape, dtype=np.int8), bb1.grid], axis)
            depth = bb1.depth + 1
        elif bb1 is None:
            location = bb0.location[:-1]
            axis = len(bb0.location[:-1]) % 6
            g = np.concatenate(
                    [bb0.grid, np.zeros(bb0.grid.shape, dtype=np.int8)], axis)
            depth = bb0.depth + 1
        else:
            location = bb0.location[:-1]
            axis = len(bb0.location[:-1]) % 6
            if bb0.grid.shape != bb1.grid.shape:
                pdb.set_trace()
            g = np.concatenate([bb0.grid, bb1.grid], axis)
            depth = bb0.depth + 1
        return BoundedBoxes(location, depth=depth, grid=g)

    def _cluster_gridded(self, bb, bb_deeper):
        clusters = []
        boundary = []
        remaining = bb.grid.copy()
        cluster_grid = np.full(remaining.shape, fill_value=-1, dtype=np.int32)

        while remaining.sum() > 0:
            coords = _guess_large_cluster(remaining)
            mask = skimage.segmentation.flood(remaining, coords)
            cluster = self._make_cluster(bb, mask, coords)
            remaining -= mask
            cluster_grid[mask] = len(clusters)
            mask[1:-1,1:-1,1:-1,1:-1,1:-1,1:-1] = 0
            boundary_coords = np.nonzero(mask)
            boundary_ids = np.full(shape=len(boundary_coords[0]),
                    fill_value=len(clusters))
            clusters.append(cluster)
            boundary.append(np.array(
                list(boundary_coords) + [boundary_ids],
                dtype=np.int32))

        if bb_deeper is not None:
            for cluster in bb_deeper.clusters:
                coords = self._boxcode_to_subcoords(bb, cluster.example)
                cluster.parent = cluster_grid[coords]
                if type(cluster.parent) != int and cluster.parent.shape != ():
                    pdb.set_trace()
                if cluster.size > 2 * clusters[cluster.parent].size:
                    pdb.set_trace()
                assert cluster.parent != -1
        bb.clusters = clusters
        bb.boundary = np.concatenate(boundary, axis=1)
        bb.grid = None
        return bb

    def _make_cluster(self, bb, mask, example_coords):
        labels = set()  # TODO
        example = self._subcoords_to_boxcode(bb, example_coords)
        return Cluster(mask.sum(), labels, example)

    def _glue_clustered(self, bb0, bb1, bb_deeper):
        axis, shape = self._get_merge_axis_and_shape(bb0 or bb1)
        depth = None
        clusters = []
        boundary = []
        adjacent = [None, None]
        if bb0 is not None:
            location = bb0.location[:-1]
            depth = 1 + bb0.depth
            face, exterior = self._select_merge_face_boundary(bb0)
            boundary.append(exterior)
            adjacent[0] = face
            clusters.extend(bb0.clusters)
        if bb1 is not None:
            location = bb1.location[:-1]
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
        self._combine_connected_clusters(bb, bb_deeper, adj_coo)
        return bb
    
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
    
    def _combine_connected_clusters(self, bb, bb_deeper, adj_mat):
        if adj_mat is None:
            return
        n, labels = scipy.sparse.csgraph.connected_components(adj_mat)
        bb.boundary[-1] = labels[bb.boundary[-1]]
        new_clusters = []
        for i in range(n):
            idxs, = np.nonzero(labels == i)
            clusters = [bb.clusters[i] for i in idxs]
            sizes = np.array([c.size for c in clusters])
            if len(sizes) == 0:
                pdb.set_trace()
            largest = clusters[np.argmax(sizes)]
            new_clusters.append(Cluster(size=sizes.sum(),
                labels=set.union(*[c.labels for c in clusters]),
                example=largest.example,
                parent=largest.parent))

        if bb_deeper:
            for c in bb_deeper.clusters:
                if c.parent is None:
                    pdb.set_trace()
                if type(c.parent) != int and c.parent.shape != ():
                    pdb.set_trace()
                if bb.clusters[c.parent].size > new_clusters[labels[c.parent]].size:
                    pdb.set_trace()
                if c.size > 2 * bb.clusters[c.parent].size:
                    pdb.set_trace()
                c.parent = labels[c.parent]
                if type(c.parent) != int and c.parent.shape != ():
                    pdb.set_trace()
        bb.clusters = new_clusters

    def _boxcode_to_subcoords(self, bb, boxcode):
        if not boxcode.startswith(bb.location):
            return None
        subcode = boxcode[len(bb.location):]
        if len(subcode) < bb.depth:
            return None
        axis = len(bb.location) % 6
        c = [0] * 6
        for i in range(bb.depth):
            ax = (axis + i) % 6
            c[ax] = 2 * c[ax] + (subcode[i] == "1")
        return tuple(c)

    def _subcoords_to_boxcode(self, bb, coords):
        subcode = ""
        coords = [c for c in coords]
        axis = len(bb.location) % 6
        for i in reversed(range(bb.depth)):
            ax = (axis + i) % 6
            if coords[ax] & 1 == 1:
                subcode = "1" + subcode
            else:
                subcode = "0" + subcode
            coords[ax] >>= 1
        assert tuple(coords) == (0, 0, 0, 0, 0, 0)
        return bb.location + subcode

    def _get_merge_axis_and_shape(self, bb):
        axis = len(bb.location) % 6
        merge_axis, shape = (axis + 5) % 6, [1] * 6
        for i in range(bb.depth):
            shape[(axis + i) % 6] *= 2
        return merge_axis, shape

    def _render(self, layers):
        print(f"digraph tree_{self.root_boxcode} {{")
        for bb in layers:
            for i, c in enumerate(bb.clusters):
                r = 0.2 * (c.size ** (1/6))
                print(f'  c{bb.depth}_{i}  [shape=circle, width={r}, fixedsize=true label="{bb.depth}|{i}"]')
                if c.parent is not None:
                    print(f"  c{bb.depth - 1}_{c.parent} -> c{bb.depth}_{i}")
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
