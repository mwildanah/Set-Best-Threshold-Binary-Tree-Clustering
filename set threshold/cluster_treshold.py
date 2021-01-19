from helper import *
from jalur import *

def get_cluster_treshold(data,treshold):
    data = get_cluster(data)
    data_final = pd.DataFrame()

    #Define condition
    total_cluster = data['result'].max()
    cluster_kecil = 0

    while total_cluster != cluster_kecil:
        vol = data[['vol_cbm','result']].groupby('result').sum().reset_index()

        #cluster before process
        total_cluster = len(vol)
        kecil = vol[vol['vol_cbm'] < treshold*2.8]['result'].tolist()
        data_besar = data[~data['result'].isin(kecil)].reset_index(drop=True)

        #cluster naming
        lst = []
        for i,j in enumerate(data_besar['result'].unique()):
            for k in range(len(data_besar)):
                if data_besar['result'][k] == j:
                    lst.append(i)
                else:
                    pass

        if len(data_final) > 0:
            lst = [x + 1 + max(data_final['new_result']) for x in lst]
        else:
            pass

        data_besar['new_result'] = lst
        data_final = pd.concat([data_final,data_besar])

        #re run data below treshold
        data = data[data['result'].isin(kecil)].reset_index(drop=True)
        data = data.drop(columns='result')
        data = get_cluster(data)
        
        #cluster after process
        cluster_kecil = len(data['result'].unique())
    
    #append to data_final
    data_final['result'] = data_final.new_result.astype(int)
    data_final = data_final.drop(columns='new_result')
    data_final['result'] = [x + 1 for x in data_final['result']]
    data['result'] = [x + data_final['result'].max() for x in data['result']]

    data_final = pd.concat([data_final,data]).reset_index(drop=True)
    
    return data_final