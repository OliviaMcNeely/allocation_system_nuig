from sklearn.metrics import accuracy_score
from sklearn.metrics import f1_score

recommendations={21,32,29,58,39}
manual={29,32,21,2,56}

interestion = recommendations.intersection(manual)
print(interestion)

intersect_num = len(interestion)
print(intersect_num)

precision = intersect_num/len(recommendations)
print(precision)

recall = intersect_num/len(manual)
print(recall)

fmeasure = 2 * (precision * recall)/(precision + recall)
print(fmeasure)

#score = accuracy_score(manual,recommendations)
#print(score)