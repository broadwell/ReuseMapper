# ReuseMapper
Generate an interactive heatmap matrix based on text reuse data

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
