##Summer/Fall 2022
 * treecat | treeviz | dot.
 * output graph
   * one circle per cc of grid at depth N
   * circles r=n^{1/6}
   * edges connect layers
   * may need to have min_cc_size
   * label with {X region name if contained}
 * method
   * online.
   * [DONE] accumulate grid as bitmap until memory trouble looms
   * [DONE] loop: * [skimage.flood]
   * [DONE] boundary connections between adjacent grids
 * rescue treecat from momsearch git history.
   * adapt to old tree format
---
 * how to connect parents of clusters
   * reasoning:
     * grids have no clusters or parents
       * therefore, shallowest clustered bb have clusters with no parents
     * `grid_to_clusters` needs to set parents of `depth+1` clusters.
       * use cluster.example.
       * straightforward if `depth+1` clusters already glued and available.
       * headache otherwise.
     * `glue_clustered` needs to reindex parents of depth+1` clusters.
       * straightforward if `depth+1` clusters already glued and available.
       * headache otherwise.
   * therefore:
     * `for i in range(...) glue loop
##Spring/Summer 2023
 * I haven't finished coding `grep -n label ./`.
 * No current plans for changes.
