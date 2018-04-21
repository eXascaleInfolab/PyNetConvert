# PyNetConvert - Network (Graph, Dataset) Converter
Network (graph, dataset) converter from Pajek, Metis and .nsl formats (including *.ncol*, Stanford SNAP and Edge/Arcs Graph) to *.nsl* (*.nse/a* that are more common than *.snap* and *.ncol*) and *.rcg* (Readable Compact Graph, former *.hig*; used by DAOC / HiReCS libs) formats.

\author: Artem Lutov <artem@exascale.info>  
(c) RCG (Readable Compact Graph)

## Content
- [Input Formats](#input-formats)
- [Output Formats](#output-formats)
- [Requirements](#requirements)
- [Usage](#usage)
	- [Example](#example)
	- [Options](#options)
- [Datasets](#datasets)
- [Format Specification](#format-specification)
	- [RCG](#rcg)
	- [MTS](#mts)
	- [PJK](#pjk)
	- [NSL](#nsl)
		- [NSE](#nse)
		- [NSA](#nsa)
- [Related Projects](#related-projects)

## Input formats
- [*pajek* network](http://gephi.github.io/users/supported-graph-formats/pajek-net-format/)
- [*metis* graph (network)](http://glaros.dtc.umn.edu/gkhome/fetch/sw/metis/manual.pdf)
- *nse*  - nodes are specified in lines consisting of the single Space/tab separated, possibly weighted Edge (undirected link, i.e. either AB or BA is specified):  `<src_id> <dst_id> [<weight>]`  
		with `#` comments and selflinks, without backward direction specification.  
		The same as [Stanford SNAP network format](https://snap.stanford.edu/data/index.html#communities)  
		Also known as [[Weighted] Edge Graph](https://www.cs.cmu.edu/~pbbs/benchmarks/graphIO.html)  
		Optionally reduced to the [ncol format](http://lgl.sourceforge.net/#FileFormat)
- *nsa*  - nodes are specified in lines consisting of the single Space/tab separated, possibly weighted Arc (directed link): `<src_id> <dst_id> <weight>`  
		with `#` comments, selflinks and backward direction specification that is a [Weighted] Arcs Graph, a generalization of the [LFR Benchmark generated networks](https://sites.google.com/site/santofortunato/inthepress2)

## Output formats:
- *rcg* format (former [*hig*](http://www.lumais.com/docs/hig_format.hig))
- *nsl* (stands for *nse/nsa* and includes SNAP, ncol and Edge/Arcs Graph)
  - *snap* format is *nse* with removed weights (use `--unweight -o nse` options)
  - *ncol* format is *snap* without the comments (use `--unweight --nocoms -o nse` options)

## Requirements

The converter is written for the Python3 considering backward compatibility with Pyhon2 and PyPy. It is tested on Python3, but should also run on Python2 and PyPy.  
There no any external dependencies.  

The converter is implemented as a serial parser, i.e. it can process files of any size having very small memory footprint (until the `--remdup` option is specified to remove the duplicated links).

## Usage

Just run the converter with specified input and output formats. Some formats are automatically recognized by the file extension.

### Example
```
$ ./convert.py tmp/karate.graph -i mts
File "tmp/karate.graph" is opened, converting...
	unweight: False
	remdub: False
	frcedg: False
	inpfmt: mts
	resolve: o
	outfmt: rcg
	commented: True
File tmp/karate.rcg is created, filling...
Metis format  weighted: False, selfweights: 0
Parsed weighted: False, newsection: True
tmp/karate.graph -> tmp/karate.rcg conversion is completed
```
### Options
```
$ ./convert.py -h
usage: convert.py [-h] [-f] [-i {pjk,nsa,nse,mts}] [-d] [-e] [-u] [-c]
                  [-o {nsa,nse,rcg}] [-r {o,r,s}]
                  [network]

Convert format of the specified network (graph).

positional arguments:
  network               the network (graph) to be converted

optional arguments:
  -h, --help            show this help message and exit
  -f, --showfmt         show supporting I/O formats description and exit

Input Format:
  -i {pjk,nsa,nse,mts}, --inpfmt {pjk,nsa,nse,mts}
                        input network (graph) format

Additional Modifiers:
  -d, --remdup          remove duplicated links to have unique ones
  -e, --frcedg          force edges output even in case of ars input: the
                        output edge is created by the first occurrence of the
                        input link (edge/arc) and has weight of this link
                        omitting the subsequent back link (if exists)
  -u, --unweight        force links to be unweighted instead of having the
                        input weights
  -c, --nocoms          clear (avoid) comments in the output file (conversion
                        provenance is not added, headers for .nsX are omitted,
                        etc.). Can be useful when .ncol file should be
                        produces instead of the Stanford SNAP-like format

Output Format:
  -o {nsa,nse,rcg}, --outfmt {nsa,nse,rcg}
                        output format for the network (graph)
  -r {o,r,s}, --resolve {o,r,s}
                        resolution strategy in case the output file is already
                        exists: o - overwrite the output file, r - rename the
                        existing output file and create the new one, s - skip
                        processing if such output file already exists
```

## Datasets
* Networks form the [10th DIMACS'13 competition in Metis format](http://www.cc.gatech.edu/dimacs10/archive/clustering.shtml) with ground-truth modularity
* Networks from [Standford SNAP](https://snap.stanford.edu/data/index.html#communities) (unweinghted *nse* format) with ground-truth clusters
* [LFR Benchmark to produce synthetic networks](https://github.com/eXascaleInfolab/LFR-Benchmark_UndirWeightOvp) in *nsa* format with ground-truth clusters

## Format Specification

### RCG
Rcg (OUTP)  - Readable Compact Graph format (former hig), native input format of DAOC. This format is similar to Pajek, but ids can start from any non-negative number and might not form a solid range. RCG is a readable and compact network format suitable for the evolving networks.. File extensions: rcg, hig

### MTS
Mts (INP)  - [Metis Graph (Network) format](http://glaros.dtc.umn.edu/gkhome/fetch/sw/metis/manual.pdf). File extensions: graph, mtg, met. Specification:
```
  % Comments start with '%' symbol
  % Header:
  <vertices_num> <endges_num> [<format_bin> [vwnum]]
  % Body, vertices_num lines without the comments:
  [vsize] [vweight_1 .. vweight_vwnum] vid1 [eweight1]  vid2 [eweight2] ...
  ...
```
**Notations:**  
*Header:*  
- `ertices_num`  - the number of vertices in the network (graph)
- `endges_num`  - the number of edges (not directed, A-B and B-A counted
      as a single edge)
  > ATTENTION: The edges are conunted only once, but specified in each
          direction. The arcs must exist in both directions and their weights
          are symmetric, i.e. edges.  

- `format_bin` - up to `3` digits `{0, 1}`: `<vsized><vweighted><eweighted>`
  - `vsized`  - whether the size of each vertex is specified (vsize)  
  - `vweighted`  - whether the vertex weights are specified (`vweight_1 .. vweight_vmnum`)
  - `eweighted`  - whether edges weights are specified `eweight<i>`

  > ATTENTION: When the fmt parameter is not provided, it is assumed that the vertex sizes, vertex WEIGHTS, and edge weights are all equal to 1 and NOT present in the file.

- `vm_num`  - the number of weights in each vertex (not the number of edges)

*Body:*  
- `vsize`  - size of the vertex, integer >= 0. NOTE: do not used normally
- `vweight`  - weight the vertex, integer >= 0
- `vid`  - vertex id, integer >= 1. ATTENTION: can't be equal to 0
- `eweight`  - edge weight, integer >= 1

### PJK
Pjk (INP)  - [Pajek Network format](https://gephi.org/users/supported-graph-formats/pajek-net-format/).  Node ids started with 1, both [weighted] arcs and edges might be present.. File extensions: pjk, pajek, net, pjn

### NSL
Nsl  - [nodes graph specified by the newline separated links](https://github.com/eXascaleInfolab/PyCABeM/blob/master/formats/format.nsl) (edges/arcs), which are optionally weighted.

#### NSE
Nse (INP, OUTP)  - nodes are specified in lines consisting of the single Space/tab separated, possibly weighted Edge (undirected link). It is similar to the [ncol format](http://lgl.sourceforge.net/#FileFormat) and [[Weighted] Edge Graph](https://www.cs.cmu.edu/~pbbs/benchmarks/graphIO.html), but self-edges are allowed to represent node weights and the line comment is allowed using `#` symbol.. File extensions: nse, snap, ncol. Specification:
```
  # Comments start with '#', the header is optional:
  # Nodes: <nodes_num>	Edges: <edges_num>
  <from_id> <to_id> [<weight>]
  ...
```
  **Notations:**  
  The header is optional. The edges (undirected links) are unique, i.e. either AB or BA is specified.  
  Id is a positive integer number (>= 1), id range is solid.  
  Weight is a non-negative floating point number.

#### NSA
Nsa (INP, OUTP)  - nodes are specified in lines consisting of the single Space/tab separated, possibly weighted Arc (directed link), a self-arc can be used to represent the node weight and the line comment is allowed using `#` symbol.. File extensions: nsa. Specification:
```
  # Comments start with '#', the header is optional:
  # Nodes: <nodes_num>	Arcs: <arcs_num>
  <from_id> <to_id> [<weight>]
  ...
```
  **Notations:**  
  The header is optional. The arcs (directed links) are unique and always in pairs, i.e. BA should be specified until it's weight is zero if AB is specified.  
  Id is a positive integer number (>= 1), id range is solid.  
  Weight is a non-negative floating point number.  

## Related Projects
- [PyCABeM](https://github.com/eXascaleInfolab/PyCABeM) - Python Benchmarking Framework for the Clustering Algorithms Evaluation. Uses extrinsic (NMIs) and intrinsic (Q) measures for the clusters quality evaluation considering overlaps (nodes membership by multiple clusters).
- [LFR Benchmark](https://github.com/eXascaleInfolab/LFR-Benchmark_UndirWeightOvp) for Undirected Weighted Overlapping networks - generates synthetic networks in *nsa* format with ground-truth clustering to evaluate clustering algorithms.

**Note:** Please, [star this project](https://github.com/eXascaleInfolab/PyNetConvert) if you use it.
