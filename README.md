### usage

`scrape_easychair.py` will ask for your username and password, and then store
everything it finds on the bidding page. I hard coded the bidding page for my
conference.

`rank_papers.py` is meant to be run twice. 

The first time it runs, it will output a file `interests.txt` that has a list
of keywords ordered by popularity. Delete lines from that file for keywords you
are not interested in, and leave lines that you are interested in. Sorry, no "indifferent" option!

The second time `rank_papers.py` runs, it will use your interests to create a
desirability metric, with 1.00 meaning all keywords were desirable, and -1.00
meaning all keywords were undesirable. It will then print paper details to
stdout in descending desirability order. Protip: page through this with `less`
in one window and make your bids in another window.

Other generated files:

`papers.json` is the raw output from scraping easychair.
`papers.ngrams.json` normalizes keywords to lowercase, adds bigrams of all keywords 3+ words long and trigrams of all keywords 4+ words long, and includes the interest metric for the most recent run of `rank_papers.py` in case you want to use it programmatically someplace else.
