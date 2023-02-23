import os
import pickle
import random

from subprocess import Popen


path = '/media/gog/external1/legislation'
start_year = 2000
num_years = 21

d = {
     'primary legislation': ['ukpga', 'ukla'],
     'statutory instruments': ['uksi']
    }

####

with open('d.pickle', 'wb') as f:
    pickle.dump(d, f)

genres = []
for key in d:
    genres += d[key]

print('\n')
print(genres)
print('\n')

for genre in genres:

    processes = [Popen(['scrapy', 'crawl', 'legspider',
                        '-a', 'path={}'.format(path),
                        '-a', 'year={}'.format(start_year + i),
                        '-a', 'genre={}'.format(genre)]) \
                        for i in range(num_years)]

while processes:

    for p in processes[:]:
        if p.poll() is not None:
            processes.remove(p)


