import csv
import random

tab1 = list()
tab2 = list()
tab3 = list()
tab4 = list()
tab5 = list()
tab6 = list()
tab7 = list()
tab8 = list()
tab9 = list()

skupi = list()

with open('podpira.csv', 'r', encoding='utf-8') as file:
    reader = csv.reader(file)
    for row in reader:
        tab1.append(row[0])
        tab2.append(row[1])
        tab3.append(row[2])



for i in range(0, 26684):
    skupi.append([i, random.randint(0,11)])

print(len(skupi))

with open('podpira2.csv', 'w', newline='',encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerow(["id,ime_igre,datum_izdaje,cena,vsebuje,razvija,povprecno_igranje,mediana,ocena"])
    for i in range(0, 26684):
        writer.writerow(skupi[i])
