from django.shortcuts import render
import pandas as pd
import os
from django.conf import settings
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from google import google

# Reading the data file
df = pd.read_csv(os.path.join(settings.BASE_DIR, 'zendesk_challenge.tsv'), sep='\t', encoding='cp1252')
num_page = 1
sw = set(stopwords.words('english'))


def calculate_cosine_distance(result, answer):

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

    with open(os.path.join(settings.BASE_DIR, 'results.csv'), mode='w', newline='') as results_file:
        results_writer = csv.writer(results_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)

        header = ['QuestionID', 'Question', 'DocumentID', 'DocumentTitle',
                  'SentenceID', 'Sentence', 'Label', 'Cosine Similarity']

        results_writer.writerow(header)

        for i, row in df.iterrows():
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

    similarity_df = pd.read_csv(os.path.join(settings.BASE_DIR, 'results.csv'), sep=',', encoding='cp1252')

    similarity_range_data = {
        "0-10": 0,
        "10-20": 0,
        "20-30": 0,
        "30-40": 0,
        "40-50": 0,
        "50-60": 0,
        "60-70": 0,
        "70-80": 0,
        "80-90": 0,
        "90-100": 0
    }

    for i, row in similarity_df.iterrows():
        if 0 <= row['Cosine Similarity'] < 0.1:
            similarity_range_data["0-10"] += 1
        elif 0.1 <= row['Cosine Similarity'] < 0.2:
            similarity_range_data["10-20"] += 1
        elif 0.2 <= row['Cosine Similarity'] < 0.3:
            similarity_range_data["20-30"] += 1
        elif 0.3 <= row['Cosine Similarity'] < 0.4:
            similarity_range_data["30-40"] += 1
        elif 0.4 <= row['Cosine Similarity'] < 0.5:
            similarity_range_data["40-50"] += 1
        elif 0.5 <= row['Cosine Similarity'] < 0.6:
            similarity_range_data["50-60"] += 1
        elif 0.6 <= row['Cosine Similarity'] < 0.7:
            similarity_range_data["60-70"] += 1
        elif 0.7 <= row['Cosine Similarity'] < 0.8:
            similarity_range_data["70-80"] += 1
        elif 0.8 <= row['Cosine Similarity'] < 0.9:
            similarity_range_data["80-90"] += 1
        elif 0.9 <= row['Cosine Similarity'] <= 1:
            similarity_range_data["90-100"] += 1

    context = {
        "similarity_data": similarity_range_data
    }

    return render(request, 'zendesk_challenge/index.html', context)
