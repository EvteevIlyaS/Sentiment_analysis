import pymorphy2
import matplotlib.pyplot as plt
from matplotlib import dates
import numpy as np
import re
import datetime as dt
from datetime import time

morph = pymorphy2.MorphAnalyzer()


def read_data():  # считывание и распределение данных по спискам
    with open('data.txt', 'r', encoding='utf-8') as data:
        arr = data.read().splitlines()[::2]
        arr = [el.split()[2:] for el in arr if len(el.split()[2:]) != 0]
        arr = np.array(arr)
        return arr


def data_processing(data):  # подготовка и обработка данных
    new_list = list()

    for i in range(len(data)):
        new_sublist = list()
        for word in range(len(data[i])):
            p = morph.parse(data[i][word])[0]
            if p.tag.POS == 'PRCL' or p.tag.POS == 'PREP' or p.tag.POS == 'NPRO' or p.tag.POS == 'CONJ' \
                    or data[i][word] == 'нагунт' or not re.match(r'^[а-яА-Я]*$', data[i][word]):
                pass
            else:
                new_sublist.append(p.normal_form)

        new_list.append(new_sublist)

    return np.array(new_list)


def frequency(data):  # частота встречания слов
    words = set()

    for i in range(len(data)):
        for j in data[i]:
            words.add(j)

    words = list(words)
    new_arr = list()
    numb_twits = len(data)

    with open('frequency.txt', 'w', encoding='utf-8') as file:
        for wrd in range(len(words)):
            wrd_count = 0
            for twit in range(len(data)):
                if words[wrd] in data[twit]:
                    wrd_count += 1

            new_arr.append((words[wrd], wrd_count))

        new_arr.sort(key=lambda a: a[1], reverse=True)
        for el in new_arr:
            file.write('{}-{}-{}%\n'.format(el[0], el[1], round(el[1] / numb_twits * 100, 3)))


def twits_length(data):  # количества слов в твитах
    lens_file = list()
    lens = set()
    numb_twits = len(data)

    for twit in data:
        ln = len(twit)

        if ln in lens:
            continue
        else:
            lens.add(ln)
            numb_twits_with = 0
            for tw in data:
                if len(tw) == ln:
                    numb_twits_with += 1
            lens_file.append((ln, numb_twits_with, round(numb_twits_with / numb_twits * 100, 3)))
    lens_file.sort(key=lambda a: a[1], reverse=True)

    with open('twits_length.txt', 'w', encoding='utf-8') as file:
        for ln in lens_file:
            file.write('{}-{}-{}%\n'.format(ln[0], ln[1], ln[2]))


# def carryover():  # перенос данных в estimations.txt
#     wrd = open("frequency.txt", 'r', encoding="utf8")
#     est = open("estimations.txt", 'w', encoding="utf8")
#     for el in wrd.readlines():
#         line = el.split("-")
#         if int(line[1]) > 2:
#             est.write(line[0] + "\n")
#         else:
#             est.write(line[0] + " 0\n")
#     wrd.close()
#     est.close()


def first_rule(data):  # первое правило классификации твитов (сумма оценок)
    good = 0
    bad = 0
    neutral = 0
    num_twits = len(data)

    with open('estimations.txt', 'r', encoding='utf-8-sig') as file:
        arr = list()
        for line in file.readlines():
            arr.append(tuple(line[:len(line) - 1].rstrip().split(' ')))

        dc = dict(arr)

    for i in range(len(data)):
        sm = 0
        for j in data[i]:
            sm += int(dc.get(j))

        if -1 <= sm <= 1:
            neutral += 1
        elif sm < -1:
            bad += 1
        else:
            good += 1

    _chart_for_rule([good / num_twits * 100, bad / num_twits * 100, neutral / num_twits * 100],
                    'Sum of rating (1st rule)')

    with open('classifications.txt', 'a', encoding='utf-8') as file:
        file.write('Sum of rating\n')
        file.write('Good-{}-{}%\n'.format(good, round(good / num_twits * 100, 3)))
        file.write('Bad-{}-{}%\n'.format(bad, round(bad / num_twits * 100, 3)))
        file.write('Neutral-{}-{}%\n\n'.format(neutral, round(neutral / num_twits * 100, 3)))


def second_rule(data):  # второе правило классификации твитов (наибольшая доля)
    good = 0
    bad = 0
    neutral = 0
    num_twits = len(data)

    with open('estimations.txt', 'r', encoding='utf-8-sig') as file:
        arr = list()
        for line in file.readlines():
            arr.append(tuple(line[:len(line) - 1].rstrip().split(' ')))
        dc = dict(arr)

    for i in range(len(data)):
        g = 0
        b = 0
        n = 0
        for j in data[i]:
            if int(dc.get(j)) == 0:
                n += 1
            elif int(dc.get(j)) == 1:
                g += 1
            else:
                b += 1
        if n >= b and n >= g:
            neutral += 1
        elif g >= b and g >= n:
            good += 1
        else:
            bad += 1

    _chart_for_rule([good / num_twits * 100, bad / num_twits * 100, neutral / num_twits * 100], 'Largest share '
                                                                                                '(2nd rule)')

    with open('classifications.txt', 'a', encoding='utf-8') as file:
        file.write('Largest share\n')
        file.write('Good-{}-{}%\n'.format(good, round(good / num_twits * 100, 3)))
        file.write('Bad-{}-{}%\n'.format(bad, round(bad / num_twits * 100, 3)))
        file.write('Neutral-{}-{}%\n\n'.format(neutral, round(neutral / num_twits * 100, 3)))


def third_rule(data):  # третье правило классификации твитов (смешанные или одного типа)
    good = 0
    bad = 0
    neutral = 0
    num_twits = len(data)

    with open('estimations.txt', 'r', encoding='utf-8-sig') as file:
        arr = list()
        for line in file.readlines():
            arr.append(tuple(line[:len(line) - 1].rstrip().split(' ')))
        dc = dict(arr)

    for i in range(len(data)):
        g = 0
        b = 0
        n = 0
        for j in data[i]:
            if int(dc.get(j)) == 0:
                n += 1
            elif int(dc.get(j)) == 1:
                g += 1
            else:
                b += 1
        if (g > 0 and b > 0) or (g == 0 and b == 0):
            neutral += 1
        elif b == 0 and g > 0:
            good += 1
        elif g == 0 and b > 0:
            bad += 1

    _chart_for_rule([good / num_twits * 100, bad / num_twits * 100, neutral / num_twits * 100], 'Mixed grades '
                                                                                                '(3rd rule)')

    with open('classifications.txt', 'a', encoding='utf-8') as file:
        file.write('Mixed grades\n')
        file.write('Good-{}-{}%\n'.format(good, round(good / num_twits * 100, 3)))
        file.write('Bad-{}-{}%\n'.format(bad, round(bad / num_twits * 100, 3)))
        file.write('Neutral-{}-{}%\n\n'.format(neutral, round(neutral / num_twits * 100, 3)))


def fourth_rule(data):  # четвертое правило классификации твитов (по наиболее часто встречаемым)
    good = 0
    bad = 0
    neutral = 0
    num_twits = len(data)

    with open('estimations.txt', 'r', encoding='utf-8') as file:
        arr = list()
        for line in file.readlines():
            arr.append(line[:len(line) - 1].rstrip().split(' '))

    for i in range(len(data)):
        g = 0
        b = 0
        n = 1
        for j in data[i]:
            if j == 'хороший' or j == 'гордиться' or j == 'спасибо':
                g += 1
            elif j == 'проиграть' or j == 'блять' or j == 'плакать':
                b += 1

        if n > b and n > g:
            neutral += 1
        elif g >= b and g >= n:
            good += 1
        else:
            bad += 1

    _chart_for_rule([good / num_twits * 100, bad / num_twits * 100, neutral / num_twits * 100], 'Classification'
                                                                                                ' by most common words'
                                                                                                ' (4th rule)')

    with open('classifications.txt', 'a', encoding='utf-8') as file:
        file.write('Classification by most common words\n')
        file.write('Good-{}-{}%\n'.format(good, round(good / num_twits * 100, 3)))
        file.write('Bad-{}-{}%\n'.format(bad, round(bad / num_twits * 100, 3)))
        file.write('Neutral-{}-{}%\n\n'.format(neutral, round(neutral / num_twits * 100, 3)))


def _chart_for_rule(revenues, title):  # чарты для правил
    categories = ['Good', 'Bad', 'Neutral']
    ypos = np.arange(len(categories))

    plt.xticks(ypos, categories)
    plt.bar(ypos, revenues)
    plt.ylabel('% of all twits')
    plt.title(title)

    plt.show()


def most_common_adj():  # 3 наиболее встречаемых положительных и 3 наиболее встречаемых отрицательных прилагательных
    est = open('estimations.txt', 'r', encoding='utf-8-sig')
    arr_est = list()

    for line in est.readlines():
        arr_est.append(tuple(line[:len(line) - 1].rstrip().split(' ')))
    dc = dict(arr_est)

    frq = open('frequency.txt', 'r', encoding='utf-8-sig')
    arr_pos, arr_neg = list(), list()

    for line in frq.readlines():

        p = morph.parse(line.split('-')[0])[0]
        pos_line = p.tag.POS

        if int(dc.get(line.split('-')[0])) == 0:
            continue

        if int(dc.get(line.split('-')[0])) == 1 and len(arr_pos) < 5 and pos_line == 'ADJF':
            arr_pos.append(line[:len(line) - 1])
            continue

        if int(dc.get(line.split('-')[0])) == -1 and len(arr_neg) < 5 and pos_line == 'ADJF':
            arr_neg.append(line[:len(line) - 1])
            continue
        if len(arr_pos) == 5 and len(arr_neg) == 5:
            break

    arr_pos.sort(key=lambda a: int(a.split('-')[1]), reverse=True)
    arr_neg.sort(key=lambda a: int(a.split('-')[1]), reverse=True)

    with open('adjectives.txt', 'w', encoding='utf-8') as file:
        file.write('Top-5 Positive:\n')
        for ln in arr_pos:
            file.write(ln + '\n')

        file.write('\nTop-5 Negative:\n')
        for ln in arr_neg:
            file.write(ln + '\n')

    # chart
    fig = plt.figure()
    ax1 = fig.add_axes([0.575, 0.125, 0.365, 0.352273])
    ax1.set_title('Positive in %')
    ax2 = fig.add_axes([0.125, 0.125, 0.365, 0.352273])
    ax2.set_title('Negative in %')
    labels1 = [el.split('-')[0] for el in arr_pos]
    labels2 = [el.split('-')[0] for el in arr_neg]
    width = 0.35
    pos = [float(el.split('-')[2][:-1]) for el in arr_pos]
    neg = [float(el.split('-')[2][:-1]) for el in arr_neg]
    ax1.bar(labels1, pos, width, label='Positive')
    ax2.bar(labels2, neg, width, label='Negative')
    ax1.set_xticklabels(labels1, fontsize=6)
    ax2.set_xticklabels(labels2, fontsize=6)
    plt.show()


def _time_prep_data(data):  # подготовка данных со временем [дата, время, оценка твита]
    data = data[:]
    with open('data.txt', 'r', encoding='utf-8') as file:
        arr = file.read().splitlines()[::2]
        arr = [el.split(' ')[1] for el in arr if len(el.split()[2:]) != 0]

    for i in range(len(arr)):
        el = arr[i].split(':')
        arr[i] = time(int(el[0]), int(el[1]))

    with open('estimations.txt', 'r', encoding='utf-8-sig') as file:
        arr_mark = list()
        for line in file.readlines():
            arr_mark.append(tuple(line[:len(line) - 1].rstrip().split(' ')))
        dc = dict(arr_mark)

    for i in range(len(data)):
        sm = 0
        for j in data[i]:
            sm += int(dc.get(j))

        if -1 <= sm <= 1:
            data[i] = ['0']
        elif sm < -1:
            data[i] = ['-1']
        else:
            data[i] = ['1']

        data[i].insert(0, arr[i])

    return data


def time_mark(data):  # оценка по времени, временные рамки - с 12:00 до 20:00
    data = data.copy()
    data = _time_prep_data(data)[::-1]
    t1 = time(12)
    t2 = time(20, 10)
    wnd = 30
    hour = 12
    numb_twit = 0
    good = 0
    bad = 0
    neutral = 0
    arr_chart = list()
    # chart
    x, yg, yb, yn, y = list(), list(), list(), list(), list()

    with open('hours.txt', 'w', encoding='utf-8') as file:
        for i in range(len(data)):
            if t1 <= data[i][0] <= t2:
                tm = time(hour, wnd)
                if data[i][0] <= tm:
                    if data[i][1] == '0':
                        neutral += 1
                    elif data[i][1] == '1':
                        good += 1
                    else:
                        bad += 1

                    numb_twit += 1

                    continue

                if wnd == 50:
                    hour += 1
                    wnd = 0
                else:
                    wnd += 10

                try:
                    arr_chart.append((tm, numb_twit, round(good / numb_twit, 3),
                                      round(neutral / numb_twit, 3), round(bad / numb_twit, 3)))
                except ZeroDivisionError:
                    arr_chart.append((tm, 0, 0,
                                      0, 0))

        for el in arr_chart:
            file.write('12:00-{} : {} {}/{}/{}\n'.format(el[0], el[1], el[2], el[3], el[4]))
            # chart
            x.append(dt.datetime.strptime(str(el[0]), "%H:%M:%S"))
            y.append(el[1])
            yg.append(el[2])
            yn.append(el[3])
            yb.append(el[4])

    # chart
    x = np.array(x)
    y = np.array(y)
    yg = np.array(yg)
    yn = np.array(yn)
    yb = np.array(yb)

    fmt = dates.DateFormatter('%H:%M:%S')

    fig, (ax1, ax2) = plt.subplots(nrows=2, ncols=1)

    ax1.set_title('Distribution of tweets classes in time')
    ax1.plot(x, yg, "ro-", label='N_pos')
    ax1.plot(x, yn, "go:", label='N_0')
    ax1.plot(x, yb, "bo--", label='N_neg')
    ax1.grid()
    ax1.legend()
    ax1.set_ylabel('Fraction')

    ax2.bar(x, y, width=0.003, color='pink')
    ax2.grid()
    ax2.set_ylabel('Number of tweets')
    ax2.set_xlabel('Time window')

    ax1.xaxis.set_major_formatter(fmt)
    ax2.xaxis.set_major_formatter(fmt)
    fig.autofmt_xdate()

    plt.show()


def estimation_check(data):  # определение точности эмпирической оценки твитов
    arr_result = list()
    count_twits = 0

    with open('estimations.txt', 'r', encoding='utf-8-sig') as file:
        arr_mark = list()
        for line in file.readlines():
            arr_mark.append(tuple(line[:len(line) - 1].rstrip().split(' ')))
        dc = dict(arr_mark)

    for key in dc:
        sm = 0

        for i in range(len(data)):
            if key in data[i]:
                count_twits += 1
                for j in data[i]:
                    sm += int(dc.get(j))

        try:
            exp_value = round(sm / count_twits, 3)
        except ZeroDivisionError:
            continue

        diff = abs(int(dc[key]) - exp_value)

        arr_result.append((key, dc[key], exp_value, round(diff, 3)))

    arr_result.sort(key=lambda a: a[3])

    # точность общей оценик:
    # пусть, если разница меньше или равна 0.5, то считаем, что оценки совпали
    count_coincided = 0
    for el in arr_result:
        if el[3] <= 0.5:
            count_coincided += 1
        else:
            break

    try:
        estimation_accuracy = round(count_coincided / len(arr_result) * 100, 3)
    except ZeroDivisionError:
        estimation_accuracy = 0.0

    with open('estimation_check.txt', 'w', encoding='utf-8-sig') as file:
        file.write('Top-5 Closest:\n')
        for el in arr_result[:5]:
            file.write('{} {} {}\n'.format(el[0], el[1], el[2]))

        file.write('\nTop-5 Furthest:\n')
        for el in arr_result[-1:-6:-1]:
            file.write('{} {} {}\n'.format(el[0], el[1], el[2]))

        file.write('\nEstimation accuracy: {}%\n'.format(estimation_accuracy))

    return arr_result  # для определения слов с самой положительной и саиой отрицтельной окраской


def best_worst(twt_asm):  # найдём слова с самой положит. и самой отрицат. окраской (по оценкам твитов с этими словами)
    twt_asm.sort(key=lambda a: a[2], reverse=True)

    with open('best_worst.txt', 'w', encoding='utf-8-sig') as file:
        file.write('Top-5 Most Positive:\n')
        for el in twt_asm[:5]:
            file.write('{} {}\n'.format(el[0], el[2]))

        file.write('\nTop-5 Most Negative:\n')
        for el in twt_asm[-1:-6:-1]:
            file.write('{} {}\n'.format(el[0], el[2]))

        # chart
        fig = plt.figure()
        ax1 = fig.add_axes([0.575, 0.125, 0.365, 0.352273])
        ax1.set_title('Most Positive marks')
        ax2 = fig.add_axes([0.125, 0.125, 0.365, 0.352273])
        ax2.set_title('Most Negative marks')
        labels1 = [el[0] for el in twt_asm[:5]]
        labels2 = [el[0] for el in twt_asm[-1:-6:-1]]
        width = 0.35
        pos = [float(el[2]) for el in twt_asm[:5]]
        neg = [float(el[2]) for el in twt_asm[-1:-6:-1]]
        ax1.bar(labels1, pos, width, label='Positive')
        ax2.bar(labels2, neg, width, label='Negative')
        ax1.set_xticklabels(labels1, fontsize=6)
        ax2.set_xticklabels(labels2, fontsize=6)
        plt.show()


def main():  # исполнение программы
    arr = read_data()
    arr = data_processing(arr)
    frequency(arr)
    twits_length(arr)
    first_rule(arr)
    second_rule(arr)
    third_rule(arr)
    fourth_rule(arr)
    most_common_adj()
    time_mark(arr)
    twit_assessment = estimation_check(arr)
    best_worst(twit_assessment)


main()
