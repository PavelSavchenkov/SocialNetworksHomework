import pandas
import editdistance


class DataHandler:
    infinity_score = 100000
    threshold_score = 10
    min_result_size = 1

    def __init__(self, data_path):
        self.data = pandas.read_csv(data_path, header=0)

    def matchScoreSurname(self, querySurname, surname):
        return editdistance.eval(querySurname, surname)

    def matchScoreName(self, queryName, name):
        if name.startswith(''.join(filter(str.isalpha, queryName))):
            return 0
        return editdistance.eval(queryName, name)

    def matchScorePatronymic(self, queryPatronymic, patronymic):
        if patronymic.startswith(''.join(filter(str.isalpha, queryPatronymic))):
            return 0
        return editdistance.eval(queryPatronymic, patronymic)

    def matchScore(self, query, row):
        tokens = query.split(' ')
        if not tokens:
            return self.infinity_score
        score = self.matchScoreSurname(tokens[0], row['Surname'])
        if len(tokens) > 1:
            score += self.matchScoreName(tokens[1], row['Name'])
        if len(tokens) > 2:
            score += self.matchScorePatronymic(tokens[2], row['Patronymic'])
        return score

    def getBestResponses(self, query):
        rows_with_scores = []
        for index, row in self.data.iterrows():
            rows_with_scores.append((self.matchScore(query, row), row))
        rows_with_scores = sorted(rows_with_scores, key=lambda row_with_score: row_with_score[0])
        result = []
        for score, row in rows_with_scores:
            if score > self.threshold_score and len(result) >= self.min_result_size:
                continue
            key = row['Surname'] + ' ' + row['Name'] + ' ' + row['Patronymic']
            # key += ' '+str(score)
            # print('key = ', key)
            result.append((key, row['Description']))
        return reversed(result)
