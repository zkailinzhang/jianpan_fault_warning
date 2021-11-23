import numpy as np
import pandas as pd
from database import *


kks = ('40HFC50CT011', '40HFC50AJ001XB01',
       '40HFC50CP011', '40CXA56007CGA01R', '40HFC52CT001',
       '40HFC50CT001', '40HFC52CT011', '40HFC50CT031', '40HFC50CP001')
hbase = Hbase()
hbase.connect('localhost', 9090)
data_dict = {}
for i in kks:
    print(i)
    data_1 = hbase.get_data('mill', row_start='2021-07-02 06:24:45', row_end='2021-07-03 19:35:45', key_need=i)
    data_dict[i] = data_1

for i in range(len(kks)):
    for m in range(len(kks)):
        coef = np.corrcoef(data_dict[kks[i]], data_dict[kks[m]])[1][0]
        if coef > 0.85:
            if kks[i] == kks[m]:
                pass
            else:
                print(kks[i], ':', kks[i+1], coef)