import matplotlib.pyplot as plt
import matplotlib as mpl
import pandas as pd
import numpy as np
import seaborn as sns
import datetime
from collections import defaultdict
import sys

def fips_to_name(FIPS):
    map = defaultdict(lambda: FIPS)
    map.update({
        '44003': 'Kent County, RI',
        '01125': 'Tuscaloosa County, AL',
        '23005': 'Cumberland County, ME'
    })
    return map[FIPS]

def comparison(FIPS_1='44003', FIPS_2='01125'):
    df_m = pd.read_csv("months.csv")
    df_m['date2']=df_m['date'].apply(lambda x: datetime.datetime.strptime(x, "%m-%d-%Y"))
    df_m = df_m.iloc[1:]
    df_m["month"]=df_m["date2"].apply(lambda x: x.strftime('%m'))
    df_m.set_index('date', inplace = True)
    df_m.drop(columns=['date2'], inplace = True)

    file_list = []
    for csv_date, month in df_m.iterrows():
        df = pd.read_csv('data/Merge/vaccinations-and-deaths-' + csv_date +'.csv', converters={'FIPS' : str})
        df['Deaths_Per_1e5'] = df['Deaths'] / df['Census2019_18PlusPop'] * 1e5
        df['Month'] = csv_date
        file_list.append(df)    

    merged_df = pd.concat(file_list)
    print(merged_df.head())
    cleaned_df = merged_df[merged_df['FIPS'].str.contains(FIPS_1+"|"+FIPS_2)]
    print(cleaned_df.head())

    ax1 = sns.barplot(data=cleaned_df, x="Month", y="Series_Complete_18PlusPop_Pct", hue="Recip_County")
    ax2 = sns.lineplot(data=cleaned_df, axes=ax1.twinx(), x="Month", y="Deaths_Per_1e5", hue="Recip_County")

    handles1, labels1 = ax1.get_legend_handles_labels()
    handles2, labels2 = ax2.get_legend_handles_labels()
    labels = [('% vaccinated -- ' if i <2 else 'deaths/100k -- ') + fips_to_name(label) for i, label in enumerate(labels1 + labels2)]
    ax1.legend(handles1 + handles2, labels)
    ax2.get_legend().remove()

    blank = mpl.text.Text(0, 0, '')
    xticklabels = [label if (i % 5) == 0 else blank for i, label in enumerate(ax1.get_xticklabels())]
    ax1.set_xticklabels(xticklabels)

    plt.savefig("img/comparison.png")

    

def main(argv):
    comparison(argv[0], argv[1])

if __name__ == "__main__":
    argv = sys.argv[1:]
    if not (len(argv) == 2 or len(argv) == 0):
        print("Invalid number of arguments.")
    main(argv)
