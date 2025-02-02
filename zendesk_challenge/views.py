from django.shortcuts import render
import pandas as pd
import os
import string
from django.conf import settings
from nltk.corpus import stopwords
from nltk.stem.wordnet import WordNetLemmatizer
from nltk.tokenize import word_tokenize
from google import google
import gensim
from gensim import corpora


def clean(doc):
    sw = set(stopwords.words('english'))
    exclude = set(string.punctuation)
    lemma = WordNetLemmatizer()
    stop_free = " ".join([i for i in doc.lower().split() if i not in sw])
    punc_free = ''.join(ch for ch in stop_free if ch not in exclude)
    normalized = " ".join(lemma.lemmatize(word) for word in punc_free.split())
    return normalized


def calculate_cosine_distance(result, answer):

    sw = set(stopwords.words('english'))

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

    df = pd.read_csv(os.path.join(settings.BASE_DIR, 'zendesk_challenge.tsv'), sep='\t', encoding='cp1252')
    num_page = 1
    sw = set(stopwords.words('english'))

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


def topical_analysis():
    from nltk.corpus import stopwords

    sw = set(stopwords.words('english'))
    df = pd.read_csv(os.path.join(settings.BASE_DIR, 'zendesk_challenge.tsv'), sep='\t', encoding='cp1252')
    from matplotlib import pyplot as plt
    from wordcloud import WordCloud
    import matplotlib.colors as mcolors


    stopwords = list(sw)
    stopwords.extend(
        ['from', 'subject', 're', 'edu', 'use', 'not', 'would', 'say', 'could', '_', 'be', 'know', 'good', 'go', 'get',
         'do', 'done', 'try', 'many', 'some', 'nice', 'thank', 'think', 'see', 'rather', 'easy', 'easily', 'lot',
         'lack', 'make', 'want', 'seem', 'run', 'need', 'even', 'right', 'line', 'even', 'also', 'may', 'take', 'come'])

    cols = [color for name, color in mcolors.TABLEAU_COLORS.items()]  # more colors: 'mcolors.XKCD_COLORS'

    cloud = WordCloud(stopwords=stopwords,
                      background_color='white',
                      width=2500,
                      height=1800,
                      max_words=10,
                      colormap='tab10',
                      color_func=lambda *args, **kwargs: cols[i],
                      prefer_horizontal=1.0)

    Lda = gensim.models.ldamodel.LdaModel

    doc_clean = []

    for i, row in df.iterrows():
        if row['Label'] == 1:
            doc_clean.append(clean(row['Question']).split())

    dictionary = corpora.Dictionary(doc_clean)
    doc_term_matrix = [dictionary.doc2bow(doc) for doc in doc_clean]
    ldamodel = Lda(doc_term_matrix, num_topics=20, id2word=dictionary, passes=20)
    # print(ldamodel.print_topics(num_topics=20, num_words=3))
    topics = ldamodel.show_topics(formatted=False)

    fig, axes = plt.subplots(2, 2, figsize=(10, 10), sharex=True, sharey=True)

    for i, ax in enumerate(axes.flatten()):
        fig.add_subplot(ax)
        topic_words = dict(topics[i][1])
        cloud.generate_from_frequencies(topic_words, max_font_size=300)
        plt.gca().imshow(cloud)
        plt.gca().set_title('Topic ' + str(i), fontdict=dict(size=16))
        plt.gca().axis('off')

    plt.subplots_adjust(wspace=0, hspace=0)
    plt.axis('off')
    plt.margins(x=0, y=0)
    plt.tight_layout()
    plt.show()


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
