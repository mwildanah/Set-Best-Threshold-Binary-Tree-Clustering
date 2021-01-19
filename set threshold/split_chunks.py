import pandas as pd
import time

def split_chunks(data, n):
    """ 
       Splits list l into n chunks with approximately equals sum of values
       see  http://stackoverflow.com/questions/6855394/splitting-list-in-chunks-of-balanced-weight
    """
    data = data.sort_values(by = 'total_distance', ascending = False).reset_index(drop=True)
    result = [[] for i in range(n)]
    sums   = {i:0 for i in range(n)}

    lst = []
    c = 0
    for e in range(len(data)):
        for i in sums:
            if c == sums[i]:
                result[i].append(data['total_distance'][e])
                lst.append(i)
                break
        sums[i] += data['total_distance'][e]
        c = min(sums.values())
    data['fleet ke'] = lst
    return data


if __name__ == '__main__':
    
    CHUNKS = 24
    data = pd.read_csv(r'C:\Users\Anak warung\Downloads\warpin\ROUTE\kotret buat panggil panggil\olooool\result\distance cvrp.csv',sep=';')
    t = time.time()
    r = split_chunks(data, CHUNKS)
    
    print(time.time() - t)