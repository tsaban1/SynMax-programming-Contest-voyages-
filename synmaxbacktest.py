import pandas as pd
from datetime import datetime
from math import sqrt, e, radians, cos, sin, asin
from collections import Counter

dfports=pd.read_csv("ports.csv", delimiter=";")

df_list_ports=dfports.values.tolist()
    
dftracking=pd.read_csv("tracking.csv", delimiter=";")

df_list_tracking=dftracking.values.tolist()

L_vessels=dftracking["vessel"].unique()

epic_vyg=[]
epic_vyg_predict=[]

voyage_tabel=pd.read_csv("voyages.csv", delimiter=";")
df_voyages=voyage_tabel.values.tolist()

def haversine(lon1, lat1, lon2, lat2):
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    dlon = lon2 - lon1 
    dlat = lat2 - lat1 
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a)) 
    km = 6371* c
    return km

for vessel in L_vessels:
    L=[]
    for i in df_list_tracking:
        if i[0]==vessel:
            L.append(i)
        else:
            pass
    L.sort(key=lambda x: datetime.strptime(x[1], "%d.%m.%Y %H:%M"))
    stp=[]
    strt=[]
    for i in df_list_ports:
        if i[0] ==142:
            i[1]=30.962778
            i[2]=121.934167
            new_min=10*e
        elif i[0]==76 or i[0]==98:
            new_min=7*e
        elif i[0]==13:
            new_min=2*e
        elif i[0]==102 or i[0]==102 or i[0]==136 or i[0]==153 or i[0]==99 or i[0]==70 or i[0]==100 or i[0]==72 or i[0]==32:
            new_min=5*e
        elif i[0]==115 or i[0]==154:
            new_min=4*e
        elif i[0]==54:
            new_min=2*e
        elif i[0]==34:
            new_min=11*e
        else:
            new_min=10*e
        euc=[]
        for j in L:
            hav=haversine(i[2],i[1],j[3],j[2])
            if hav <= new_min and j[5]<1:
                euc.append(j)
            else:
                pass
        for j in euc:
            for k in range(1,len(L)):
                if L[k]==j:
                    if L[k][5]<1 and L[k-1][5]!=0:
                        stp.append(L[k])
                    else:
                        pass
                elif L[k-1]==j:
                    if L[k][5]!=0 and L[k-1][5]<1:
                        strt.append(L[k-1])
                    else:
                        pass
                else:
                    pass
        if not euc:
            euc=[]
            for j in L:
                hav=haversine(i[2],i[1],j[3],j[2])
                if hav <= 1.9*new_min and j[5]<1:
                    euc.append(j)
                else:
                    pass
            for j in euc:
                for k in range(1,len(L)):
                    if L[k]==j:
                        if L[k][5]<1 and L[k-1][5]!=0:
                            stp.append(L[k])
                        else:
                            pass
                    elif L[k-1]==j:
                        if L[k][5]!=0 and L[k-1][5]<1:
                            strt.append(L[k-1])
                        else:
                            pass
                    else:
                        pass
            if not euc:
                for j in range(1,len(L)):
                    hav=haversine(i[2],i[1],L[j-1][3],L[j-1][2])
                    if hav <= 2.8*new_min and 160<abs(L[j][4]-L[j-1][4])<200 and (L[j][5] or L[j-1][5])>1:
                        stp.append(L[j-1])
                        strt.append(L[j])
                    else:
                        pass
    newstrt=[]
    newstp=[]
    for i in strt:
        if i not in newstrt:
            newstrt.append(i)

    for i in stp:
        if i not in newstp:
            newstp.append(i)
    voyage=newstrt+newstp
    voyage.sort(key=lambda x: datetime.strptime(x[1], "%d.%m.%Y %H:%M"))
    new_voyage=[]
    for i in voyage:
        if i not in new_voyage:
            new_voyage.append(i)
    for i in new_voyage:
        minimum=75
        info=[0]*3
        for j in df_list_ports:
            radius=haversine(i[3],i[2],j[2],j[1])
            if radius<=minimum:
                minimum=radius
                info=j
            else:
                pass
        i.append(info[0])
    new_voyage=[x for x in new_voyage if x[7]!=0]
    voyage_eliminate=[]
    voyage_add=[]
    for i in range(2,len(new_voyage)):
        if new_voyage[i-1][7] == new_voyage[i-2][7] and new_voyage[i-1][7] == new_voyage[i][7] and new_voyage[i][7] == new_voyage[i-2][7] and (datetime.strptime(new_voyage[i-1][1], "%d.%m.%Y %H:%M") - datetime.strptime(new_voyage[i-2][1], "%d.%m.%Y %H:%M")).total_seconds()<432000 and (datetime.strptime(new_voyage[i][1], "%d.%m.%Y %H:%M") - datetime.strptime(new_voyage[i-1][1], "%d.%m.%Y %H:%M")).total_seconds()<432000:
            voyage_eliminate.append(new_voyage[i-1])
        elif new_voyage[i-1][7] != new_voyage[i-2][7] and new_voyage[i-1][7] != new_voyage[i][7]:
            voyage_add.append(new_voyage[i-1])
        elif i==len(new_voyage)-1 and new_voyage[i-1][7] != new_voyage[i][7]:
            voyage_add.append(new_voyage[i])
        elif i==2 and new_voyage[i-2][7] != new_voyage[i-1][7]:
            voyage_add.append(new_voyage[i-2])
        else:
            pass
    voyage_final=[item for item in new_voyage if item not in voyage_eliminate]        
    voyage_ultimate=voyage_final + voyage_add
    voyage_ultimate.sort(key=lambda x: datetime.strptime(x[1], "%d.%m.%Y %H:%M"))
    vyg=voyage_ultimate[1:-1]
    for i in range(1,len(vyg)):
        if i%2!=0:
            prt_vyg=[vyg[i][0], vyg[i-1][1], vyg[i][1], vyg[i-1][7], vyg[i][7]]
            epic_vyg.append(prt_vyg)


    begin=L.index(voyage_ultimate[-1])
    other_vssl=[]
    for i in df_list_ports:
        if i[0]==voyage_ultimate[-1][7]:
            starting_port=i

    possibilities=[]
    probabilities=[]
    self_possibilities=[]
    self_probabilities=[]
    possibilities_combined=[]
    maybe_this=[]
    if haversine(starting_port[2],starting_port[1],L[-1][3],L[-1][2])>147*e:
        for i in df_voyages:
            if i[3]==voyage_ultimate[-1][7] and i[4]!=voyage_ultimate[-1][7]:
                all_points=[]
                for j in df_list_tracking:
                    if j[0]==i[0]:
                        all_points.append(j)
                all_points.sort(key=lambda x: datetime.strptime(x[1], "%d.%m.%Y %H:%M"))
                for j in range(len(all_points)-1):
                    if all_points[j][1]==i[1]:
                        others_begin=j
                    elif all_points[j][1]==i[2]:
                        others_end=j
                vssl=all_points[others_begin:others_end+1]
                for j in L[begin:]:
                    route_nearby=0
                    cnt=1
                    for k in vssl:
                        hvrsn=haversine(j[3],j[2],k[3],k[2])
                        if hvrsn<=37*e and j[0]!=k[0]:
                            route_nearby+=cnt
                        cnt+=1
                other_vssl.append([i[0],route_nearby, i[4]])
                
        other_vssl.sort(key=lambda x: x[1])
        epic_vyg_predict.append([vessel, starting_port[0], other_vssl[-1][2], 1])  
    else:
        for i in df_voyages:
            if i[3]==starting_port[0] and i[4]!=starting_port[0]:
                possibilities.append(i)
        for i in possibilities:
            probabilities.append(i[4])
        counting=Counter(probabilities)
        how_many=counting.most_common(1)
        check= [k for k,v in counting.items() if v == how_many[0][1]]
        if len (check) >=2:
            for i in possibilities:
                if i[0]==vessel:
                    self_possibilities.append(i)
            for i in self_possibilities:
                self_probabilities.append(i[4])

            for i in check:
                for j in self_probabilities:
                    if j==i:
                        possibilities_combined.append(j)
            if len(possibilities_combined)>=2:
                counting_self=Counter(self_probabilities)
                how_many_self=counting_self.most_common(1)
                check_self=[k for k,v in counting_self.items() if v == how_many_self[0][1]]
                epic_vyg_predict.append([vessel, starting_port[0], how_many_self[0][0], 1])
            elif not possibilities_combined and len(self_probabilities)>=1:
                epic_vyg_predict.append([vessel, starting_port[0], self_probabilities[0], 1])                              
            elif 2>len(possibilities_combined)>=1:
                epic_vyg_predict.append([vessel, starting_port[0], possibilities_combined[0], 1])
            else:
                epic_vyg_predict.append([vessel, starting_port[0], check[0], 1]) 
        else:
            epic_vyg_predict.append([vessel, starting_port[0], how_many[0][0], 1]) 
    

    if not other_vssl:
        if len(check)>=2:
            if len(possibilities_combined)>=2:
                starting_port_num=how_many_self[0][0]
            elif not possibilities_combined and len(self_probabilities)>=1:
                starting_port_num=self_probabilities[0]
            elif 2>len(possibilities_combined)>=1:
                starting_port_num=possibilities_combined[0]
            else:
                starting_port_num=check[0]
        else:
            starting_port_num=how_many[0][0]
    else:
        starting_port_num=other_vssl[-1][2]

    possibilities=[]
    probabilities=[]
    self_possibilities=[]
    self_probabilities=[]
    possibilities_combined=[]
    maybe_this=[]

    for i in df_voyages:
        if i[3]==starting_port_num and i[4]!=starting_port_num:
            possibilities.append(i)
    for i in possibilities:
        probabilities.append(i[4])
    counting=Counter(probabilities)
    how_many=counting.most_common(1)
    check= [k for k,v in counting.items() if v == how_many[0][1]]
    if len (check) >=2:
        for i in possibilities:
            if i[0]==vessel:
                self_possibilities.append(i)
        for i in self_possibilities:
            self_probabilities.append(i[4])
        for i in check:
            for j in self_probabilities:
                if j==i:
                    possibilities_combined.append(j)
        if len(possibilities_combined)>=2:
            counting_self=Counter(self_probabilities)
            how_many_self=counting_self.most_common(1)
            check_self=[k for k,v in counting_self.items() if v == how_many_self[0][1]]
            epic_vyg_predict.append([vessel, starting_port_num, how_many_self[0][0], 2])
        elif not possibilities_combined and len(self_probabilities)>=1:
            epic_vyg_predict.append([vessel, starting_port_num, self_probabilities[0], 2])                              
        elif 2>len(possibilities_combined)>=1:
            epic_vyg_predict.append([vessel, starting_port_num, possibilities_combined[0], 2])
        else:
            epic_vyg_predict.append([vessel, starting_port_num, check[0], 2]) 
    else:
        epic_vyg_predict.append([vessel, starting_port_num, how_many[0][0], 2]) 

    
    if len(check)>=2:
        if len(possibilities_combined)>=2:
            starting_port_num3=how_many_self[0][0]
        elif not possibilities_combined and len(self_probabilities)>=1:
            starting_port_num3=self_probabilities[0]
        elif 2>len(possibilities_combined)>=1:
            starting_port_num3=possibilities_combined[0]
        else:
            starting_port_num3=check[0]
    else:
        starting_port_num3=how_many[0][0]
    
    possibilities=[]
    probabilities=[]
    self_possibilities=[]
    self_probabilities=[]
    possibilities_combined=[]
    maybe_this=[]

    for i in df_voyages:
        if i[3]==starting_port_num3 and i[4]!=starting_port_num3:
            possibilities.append(i)
    for i in possibilities:
        probabilities.append(i[4])
    counting=Counter(probabilities)
    how_many=counting.most_common(1)
    check= [k for k,v in counting.items() if v == how_many[0][1]]
    if len (check) >=2:
        for i in possibilities:
            if i[0]==vessel:
                self_possibilities.append(i)
        for i in self_possibilities:
            self_probabilities.append(i[4])
        for i in check:
            for j in self_probabilities:
                if j==i:
                    possibilities_combined.append(j)
        if len(possibilities_combined)>=2:
            counting_self=Counter(self_probabilities)
            how_many_self=counting_self.most_common(1)
            check_self=[k for k,v in counting_self.items() if v == how_many_self[0][1]]
            epic_vyg_predict.append([vessel, starting_port_num3, how_many_self[0][0], 3])
        elif not possibilities_combined and len(self_probabilities)>=1:
            epic_vyg_predict.append([vessel, starting_port_num3, self_probabilities[0], 3])                              
        elif 2>len(possibilities_combined)>=1:
            epic_vyg_predict.append([vessel, starting_port_num3, possibilities_combined[0], 3])
        else:
            epic_vyg_predict.append([vessel, starting_port_num3, check[0], 3]) 
    else:
        epic_vyg_predict.append([vessel, starting_port_num3, how_many[0][0], 3])                        
                       

voyage_tabel_predict=pd.DataFrame(epic_vyg_predict, columns=['vessel', 'begin_port_id', 'end_port_id', 'voyage'])
voyage_tabel_predict.to_csv("predict.csv", index=False)


