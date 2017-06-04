# importing the data
import os
import pandas as pd
import numpy as np
import zipfile
from config import basedir

# creating a generator to loop through zip file and read in data files one state at a time
def doc_iter(zip_name):
    for f in filter(lambda x: x.endswith('TXT'), zip_name.namelist()):
        yield pd.read_csv(zip_name.open(f), names = ['state','sex','year','name','count'])

# creating an empty dataframe to store each unique name/sex/year combo
names_all = pd.DataFrame(columns = ['sex','year','name','count'])

# iterate through each state in the zip file and sum count for each name/sex/year combo
with zipfile.ZipFile(os.path.join(basedir, 'namesbystate.zip'), 'r') as myzip:
    for df in doc_iter(myzip):
        names_all = pd.concat([names_all, df.drop('state', axis = 1)])
        names_all = names_all.groupby(['name','sex','year'], as_index = False)['count'].sum()

def prefix_search(query):
    s = names_all.groupby(['name'])['count'].sum().sort_values(ascending=False)
    q = s[s.index.str.startswith(query)]
    return pd.DataFrame(q).reset_index().to_dict('records')
