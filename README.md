# MALHelper
Welcome! MALHelper is a CLI for MyAnimeList written in Python.

## Introduction
At the moment, this CLI interface allows you to do the following:
1. Display a list of top 50 currently airing anime from MyAnimeList.
2. Display a list of top 50 trending anime from MyAnimeList.
3. Display a list of top 50 upcoming anime from MyAnimeList.
4. Search MyAnimeList for the provided query and display a list of top 50 search results.
5. Select an anime from the above-mentioned lists and view info about it.
6. Display a list of user recommendations based on a selected anime.

## Flags and options
`-h`, `--help`: Prints this help message and quits<br />
`--help-all`: Prints help messages of all sub-commands and quits<br />
`-v`, `--version`: Prints the program's version and quits<br />
`-a`, `--airing`: Displays a list of top 50 currently airing anime from MyAnimeList<br />
`-s='QUERY'`, `--search='QUERY'`: Searches MyAnimeList for the provided query and displays a list of top 50 search results<br />
`-t`, `--trending`: Displays a list of top 50 trending anime from MyAnimeList<br />
`-u`, `--upcoming`: Displays a list of top 50 upcoming anime from MyAnimeList

## Installation 
Make sure you have Python 3.10 or above installed. Next, clone the repository and `cd` into the local repository. Install the dependencies:<br />
`pip3 install -r requirements.txt`<br />
Finally, run the script:<p>
For Unix: `python3 main.py <flags/options>`<p>
For Windows: `python main.py <flags/options>`

## Demonstration
Check out the GIF below to see how the CLI works.
![](https://github.com/DSS3113/MALHelper/blob/main/demo/demo.gif)
