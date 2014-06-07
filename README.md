google-news
===========

**Repository of scripts that scrape news headlines from Google News, prepare them for readability analysis, and visualize the results aggregated by news outlet.**

**google_news.py** scrapes news headlines and the name of their outlets from the Google News homepage on a set schedule. Sample data are found in *google_news.csv*. After all the scheduled jobs are run, the data are cleaned: badly-formed text, non-sensical results, and duplicate records are reformatted or removed. The [readability](http://en.wikipedia.org/wiki/Readability) of the headlines is assessed with the [Flesch-Kincaid Grade Level](http://en.wikipedia.org/wiki/Flesch%E2%80%93Kincaid_readability_tests#Flesch.E2.80.93Kincaid_Grade_Level) test, which requires the readability functions found [here](https://github.com/mmautner/readability). Finally, the cleaned data are aggregated at the level of news outlets.

**google_news.R** is called to create a visualization of the results using the [plotly R API](https://plot.ly/r/).

The scripts and their output are described in [this blog post]().
