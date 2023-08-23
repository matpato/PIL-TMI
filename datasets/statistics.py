import numpy as np # linear algebra
from numpy import count_nonzero, ndarray
import os
import pandas as pd # data processing, CSV file I/O (e.g. pd.read_csv)
import matplotlib.pyplot as plt
from wordcloud import WordCloud, STOPWORDS, ImageColorGenerator
import warnings
warnings.filterwarnings("ignore")



def statistics(df):
    print(f'Dataset has {len(df.user.unique())} unique users')
    print('__'*20)
    print(f'And the top 5 counts are :')
    print(df.user.value_counts().head(5))
    print('*'*20)
    print(f'Dataset has {len(df.item.unique())} unique items')
    print('_'*20)
    print(f'Dataset has {len(df.rating)} ratings')
    print('_'*20)
    print(f'And the top 5 counts are :')
    print(df.item.value_counts().head(5))
    print(f'And the top 5 counts are :')
    print(df.item_name.value_counts().head(5))
    print('_'*20)

# ------------------------------------------------------------------------- #
def cold_start(df):
    print(f'And the only one item rated (cold start problem):')

    count_df = df.user.value_counts()  # Replace 'column_name' with your column name
    count_df = count_df.reset_index()
    count_df.columns=['DO','count']
    return len(count_df[count_df['count'] == 1])
    
# ------------------------------------------------------------------------- #
def sparsity(df):
    user_unique: ndarray = df['user'].unique()
    len_user = user_unique.size

    item_unique: ndarray = df['item'].unique()
    len_item = item_unique.size

    # create dense matrix
    # A = np.zeros((len_user, len_item))
    A = np.zeros((len_item, len_user))

    for _, row in df.iterrows():
        #print(row)
        if row.rating == 1 :
            ru = row['user']
            ri = row['item']
            idr = np.where(user_unique == ru)[0][0]
            idc = np.where(item_unique == ri)[0][0]
            A[idc][idr] += 1
            # A[idr][idc] += 1

    # calculate sparsity
    sparsity = 1.0 - (count_nonzero(A) / float(A.size))
    return sparsity

# ------------------------------------------------------------------------- #
def plot_fig(df,path,file):

    data = pd.DataFrame(df.item.value_counts().head(10)).reset_index().to_numpy()
    #print(data)
    vals_films = [x[1] for x in data]
    legends_films = [x[0] for x in data]
    fig, ax = plt.subplots()

    index = np.arange(len(data))
    bar_width = 0.25
    opacity = 0.4
    rects1 = plt.bar(index, vals_films, bar_width,
                    alpha=opacity,
                    color='b',
                    label='Ocurrences')

    plt.xlabel('Occurrences')
    plt.ylabel('Words')
    plt.title('Occurrences by word')
    plt.xticks(rotation=45)
    plt.xticks(index, legends_films)
    plt.legend()
    plt.tight_layout()
    plt.savefig(path+file)
    plt.close(fig)    # close the figure window

# ------------------------------------------------------------------------- #

def wordcloud(df,path,file):
    #unique_items = df['item'].unique()
    new_data = []
    for row in df.item_name:
        if ' ' in row:
            row = '_'.join(row.split(' '))
        new_data.append(''.join(row.split(' ')))
    new_data = pd.DataFrame(new_data)
    # https://www.datacamp.com/tutorial/wordcloud-python
    text = new_data.to_string(index=False)

    wordcloud = WordCloud(width=1600, height=800, max_words=len(df.item.unique()), colormap='Reds', background_color="black").generate(text)
    plt.figure(figsize=(15,10))
    # # Display the generated image:
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis("off")
    #plt.figure(1,figsize=(12, 12))
    wordcloud.to_file(path+file)

# ------------------------------------------------------------------------- #

# Input data files are available in the read-only "../input/" directory
# For example, running this (by clicking run or pressing Shift+Enter) will list all files under the input directory

path = '/Users/matildepato/Downloads/Med2Care-main/datasets/csv/'

emc_original = pd.read_csv(path+'emc/original/emc_medicine_dataset.csv', low_memory = False)

db_original = pd.read_csv(path+'drugbank/original/drugbank_medicine_dataset.csv', low_memory = False)

print(emc_original.head(5))
print('-'*20)
print(db_original.head(5))

print('ds shape:\n')
print(emc_original.shape)
print('-'*20)
print(db_original.shape)

print('-'*20, ' EMC ', '-'*20)
statistics(emc_original)
print(sparsity(emc_original))
print(cold_start(emc_original) )
print('__'*20) 

print('-'*20, ' DB ', '-'*20)
statistics(db_original)
print(sparsity(db_original))
print('DB: ', cold_start(db_original) )
print('__'*20) 

#plot_fig(emc_original,path,filename)

## plots
# wordcloud(emc_original,path,file='emc_original.pdf')
# wordcloud(db_original,path,file='db_original.pdf')

# db = ['emc','drugbank']

# for d in db:
#     for root,dirs,files in os.walk(path+d+'/kb'):
#          for file in files:
#             print(file)
#             if file.endswith(".csv"):
#                 df =  pd.read_csv(os.path.join(root,file), low_memory = False)
#                 if file.startswith('emc'):
#                     print('-'*20, ' EMC ', '-'*20)
#                     statistics(df)
#                     print(sparsity(df))
#                     print(cold_start(df) )
#                     print('__'*20) 
#                 else:     
#                     print('-'*20, ' DB ', '-'*20)
#                     statistics(df)
#                     print(sparsity(df))
#                     print(cold_start(df) )
#                     print('__'*20) 
         
       

# #word cloud
# text = " ".join(str(each) for each in emc_original.item_name)
# # Create and generate a word cloud image:
# wordcloud = WordCloud(max_words=200,colormap='Reds', background_color="black").generate(text)
# plt.figure(figsize=(10,6))
# plt.figure(figsize=(15,10))
# # Display the generated image:
# plt.imshow(wordcloud, interpolation='Bilinear')
# plt.axis("off")
# plt.figure(1,figsize=(12, 12))
# plt.savefig('data.pdf')