from django.shortcuts import render
import pandas as pd
import os
from django.conf import settings
from bs4 import BeautifulSoup
import requests
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from google import google

# Reading the data file
df = pd.read_csv(os.path.join(settings.BASE_DIR, 'zendesk_challenge.tsv'), sep='\t', encoding='cp1252')
num_page = 1
sw = set(stopwords.words('english'))


def calculate_cosine_distance(result, answer):
    # page = requests.get("https://www.google.com/search?q={}".format("how much is 1 tablespoon of water"))
    # soup = BeautifulSoup(page.content, "html5lib")

    # print(soup)
    # subdf = df.head(10)
    # print(len(list(set(df['Question']))))
    #
    # search_results = google.search("how are glacier caves formed?", num_page)
    #
    # result = search_results[0].description
    # result = result.split('.')[0].lower()
    # answer = "The ice facade is approximately 60 m high".lower()

    result_list = word_tokenize(result)
    answer_list = word_tokenize(answer)

    l1 = []
    l2 = []

    X_set = {w for w in result_list if not w in sw}
    Y_set = {w for w in answer_list if not w in sw}

    rvector = X_set.union(Y_set)
    for w in rvector:
        if w in X_set:
            l1.append(1)  # create a vector
        else:
            l1.append(0)
        if w in Y_set:
            l2.append(1)
        else:
            l2.append(0)
    c = 0

    for i in range(len(rvector)):
        c += l1[i] * l2[i]

    try:
        cosine = c / float((sum(l1) * sum(l2)) ** 0.5)
    except ZeroDivisionError:
        cosine = 0

    return cosine


def write_results():
    import csv

    with open(os.path.join(settings.BASE_DIR, 'results.csv'), mode='a', newline='') as results_file:
        results_writer = csv.writer(results_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)

        header = ['QuestionID', 'Question', 'DocumentID', 'DocumentTitle',
                  'SentenceID', 'Sentence', 'Label', 'Cosine Similarity']

        # results_writer.writerow(header)

        for i, row in df.iterrows():
            if i < 18946:
                continue
            if row['Label'] == 1:
                try:
                    search_results = google.search(row['Question'], num_page)

                    result = search_results[0].description.lower()
                    answer = row['Sentence'].lower()
                    temp_array = [row['QuestionID'], row['Question'], row['DocumentID'], row['DocumentTitle'],
                                             row['SentenceID'], row['Sentence'], row['Label'], calculate_cosine_distance(result, answer)]

                    results_writer.writerow(temp_array)

                    print(result, calculate_cosine_distance(result, answer))
                except IndexError:
                    continue

        results_file.close()


def index(request):

    context = {
        'title': 'Latest Posts'
    }

    with open(os.path.join(settings.BASE_DIR, 'results.txt'), 'w') as resultsPipe:
        for index, row in df.iterrows():
            if row['Label'] == 1:
                try:
                    search_results = google.search(row['Question'], num_page)

                    result = search_results[0].description.lower()
                    answer = row['Sentence'].lower()
                    temp_array = [row['QuestionID'], row['Question'], row['DocumentID'], row['DocumentTitle'],
                                             row['SentenceID'], row['Sentence'], row['Label'], playground(result, answer)]

                    line = '\t'.join(str(v) for v in temp_array)
                    resultsPipe.write(line + '\n')

                    print(result)
                except IndexError:
                    continue
        # #
        # new_df.to_csv(os.path.join(settings.BASE_DIR, 'results.tsv'), sep='\t')

    return render(request, 'zendesk_challenge/index.html', context)
