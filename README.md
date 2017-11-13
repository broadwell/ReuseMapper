# ReuseMapper
Generate an interactive heatmap matrix based on text reuse data

*Requirements*: Uses built-in Python 2.7 modules, with the exception of [slugify](https://github.com/un33k/python-slugify).

The [Plotly.js](https://plot.ly/javascript/) Javascript library renders the heatmaps, and is included in the repository along with its various dependencies (D3.js, jQuery, etc.).

## How to run

Running ReuseMapper.py (see below for usage) generates the requisite output files (itext_sim.txt, bin_labels.txt, and the files in the binsJSON/ folder) to populate the interactive heatmap, which can be viewed by opening itextmap.html in a web browser, provided it's in a web-accessible folder (e.g., http://localhost/~yourname/ReuseMapper/itextmap.html) or is being served via a simple server like node.js's [simple-server](https://www.npmjs.com/package/simple-server) module.

*Note*: Changing the --bins parameter can have a major effect on the resulting heatmap (see screenshots below).

ReuseMapper.py also generates a summary of "commonly used phrases" in itext_phrases.txt

```
  usage: ReuseMapper.py [-h] [--version] [--bins BINS] [--url URL] [--no_cache]
                        [--get_texts]

  optional arguments:
    -h, --help   show this help message and exit
    --version    show program's version number and exit
    --bins BINS  The number of "bins" on each dimension of the matrix. Affects
                 the resolution of the heatmap. Default=1000.
    --url URL    The URL (with port number) of the running Intertextualitet
                 service. Default=http://localhost:8080/
    --no_cache   Do not use the previous results from the API that are stored
                 locally. Will re-download all data. Default behavior is to use
                 the cache.
    --get_texts  Use to download the full text of each document. Can take a long
                 time. Default behavior is not to download the texts.
```

## MergeMatrices.py

This script can be used to merge two matrix files, for example itext_sim.txt produced by ReuseHeatmapper.py and a dist_sim.txt output file from [TextHeatmapper](https://github.com/UCLALibLab/text-heatmapper), for example, provided they have the same dimensions. It produces a merged matrix file, imerged_sim.txt that can be used with the Plotly.js viewer (see for example Screenshot 3), provided the link is changed from itext_sim.txt to imerged_sim.txt in the source code of itextmap.html.

## Screenshots

### Screenshot 1 (100 bins per axis)
![Screenshot 1](https://github.com/broadwell/ReuseMapper/blob/master/screenshots/100bins.png)

### Screenshot 2 (1,000 bins per axis, zoomed in)
![Screenshot 2](https://github.com/broadwell/ReuseMapper/blob/master/screenshots/1000bins_zoomed.png)

### Screenshot 3 (3,555 bins per axis, merged with an n-gram cosine similarity matrix)
![Screenshot 3](https://github.com/broadwell/ReuseMapper/blob/master/screenshots/3555bins_merged.png)
