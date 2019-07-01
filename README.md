# How to run this project

To run this project, first:

1. Clone this project

2. Install and create Virtual Environment

`pip install virtualenv`

`virtualenv zendesk`

`source zendesk/bin/activate`

3. Change to the project

`cd ../zendesk-challenge`

4. Run the server

`python manage.py runserver 8000`

4.a Download all required dependencies as promped in error messages while trying to run server.

  `pip install pandas` etc.
  
5. Open the link as promped on the cmd screen. Most likely will be 127.0.0.1:8000

# About the code

All logic is in `zendesk-challenge/views.py`

The `write_results` function iterates over all the rows with label '1' in the zendesk_challenge.py file and writes the columns into a csv called `results.csv` and adds another column for its `Cosine Similarity`. This is then used in the `index` view rendered by the page.

The `topical_analysis` function generates a word cloud plot using matplotlib. I could not find the time to integrate this in Highcharts. I will work on this though.
