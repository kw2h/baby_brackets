# importing the data
import os
import pandas as pd
import numpy as np
import zipfile
from config import basedir


def doc_iter(zip_name):
    ''' Creating a generator to loop through zip file and
        read in data files one state at a time
    '''
    for f in filter(lambda x: x.endswith('TXT'), zip_name.namelist()):
        yield pd.read_csv(zip_name.open(f), names = ['state','sex','year','name','count'])

# creating an empty dataframe to store each unique name/sex/year combo
names_all = pd.DataFrame(columns = ['sex','year','name','count'])

# iterate through each state in the zip file and sum count for each name/sex/year combo
with zipfile.ZipFile(os.path.join(basedir, 'namesbystate.zip'), 'r') as myzip:
    for df in doc_iter(myzip):
        names_all = pd.concat([names_all, df.drop('state', axis = 1)])
        cols = ['name','sex','year']
        names_all = names_all.groupby(cols, as_index=False)['count'].sum()

def prefix_search(query, sex):
    ''' Prefix search based on query + sex and return
        top 10 sorted by descending frequency
    '''
    df = (names_all.groupby(['name','sex'])['count']
                   .sum()
                   .reset_index()
                   .sort_values('count', ascending=False))
    df = df[df.sex == sex] if sex else df
    q = df[df.name.str.startswith(query)]
    return q[:10].to_dict('records')

def random_name(n, sex):
    df = names_all.groupby(['name','sex'])['count'].sum().reset_index()
    q = df[df.sex == sex] if sex else df
    return q.sample(n).to_dict('records')
