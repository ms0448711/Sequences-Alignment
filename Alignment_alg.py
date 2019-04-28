import numpy as np
import os
import csv
import re
import time
import sys
import pandas as pd


if __name__ == '__main__':

    class Segment:
        def __init__(self):
            self.wdict=dict()
            self.score=0
            self.max_len=0
            self.mvp=list()  #moveable_page
            self.mvp_non_num=dict()
            self.temp_page=list()
            self.temp_key=None
            self.longest_page=None
            self.temp_dict=None
            
        def scoring(self,change=-1):
            p=self.wdict
            key=list(p.keys())
            self.score=0
            if change==-1:
                for k1 in range(len(key)-1):
                    for k2 in range(k1+1,len(key)):
                        tmp_score=0
                        x=p[key[k1]]
                        y=p[key[k2]]
                        for i in range(self.max_len):
                            if x[i]==None and y[i]==None:
                                tmp_score-=0.2
                                continue
                            elif x[i]==None or y[i]==None:
                                tmp_score-=0.1
                                continue
                            if x[i].ContentId==y[i].ContentId:
                                tmp_score+=2
                            if x[i].TypeSetId==y[i].TypeSetId:
                                tmp_score+=1
                            if x[i].PTypeSetId==y[i].PTypeSetId:
                                tmp_score+=0.5
                            if x[i].PathId==y[i].PathId:
                                tmp_score+=2
                            if x[i].SimTECId==y[i].SimTECId:
                                tmp_score+=1
                        self.score+=tmp_score
        
        def neighbor(self):
            self.temp_dict=dict( self.wdict )
            tmp=list()
            energy_list=list()
            page_list=list()
            key_list=list()
            #for k in self.mvp:
            k= self.mvp[ int(np.random.random()*100)%len(self.mvp) ]
            self.temp_key=k
            self.temp_page=list(self.wdict[k])
            for rl in range(-4,5):
                tmp=[index for index in range(self.max_len) if index+rl>=0 and index+rl<self.max_len and self.wdict[k][(index+rl)]==None and self.wdict[k][index]!=None]
                if len(tmp)==0:
                    continue
                for i in tmp:
                    d_temp=self.wdict[k][i]
                    self.wdict[k][i]=None
                    self.wdict[k][(i+rl)]=d_temp
                    tmp_e=self.energy(self.wdict[k])
                    energy_list.append(tmp_e)
                    page_list.append(self.wdict)
                    key_list.append(k)
                    self.wdict=self.temp_dict
            best_index=energy_list.index(max(energy_list))
            self.wdict=page_list[best_index]
                
                
        def probability(self,os,ns,temp):
            if os<ns:
                return 1.0
            else:
                return np.exp( (ns-os)/temp )
                
        def energy(self,page):
            lp=self.longest_page
            tmp_score=0
            x=page
            y=self.wdict[lp]
            if x==y:
                print("ERROR")
            for i in range(self.max_len):
                if x[i]==None and y[i]==None:
                    tmp_score-=0.2
                    continue
                elif x[i]==None or y[i]==None:
                    tmp_score-=0.1
                    continue
                if x[i].ContentId==y[i].ContentId:
                    tmp_score+=2
                if x[i].TypeSetId==y[i].TypeSetId:
                    tmp_score+=1
                if x[i].PTypeSetId==y[i].PTypeSetId:
                    tmp_score+=0.5
                if x[i].PathId==y[i].PathId:
                    tmp_score+=2
                if x[i].SimTECId==y[i].SimTECId:
                    tmp_score+=1
            return tmp_score
            
        def dp2score(self,d1,d2):
            tmp_score=0
            if d1==None and d2==None:
                return -0.2
            elif d1==None or d2==None:
                return -0.1
            if d1.ContentId==d2.ContentId:
                tmp_score+=2
            if d1.TypeSetId==d2.TypeSetId:
                tmp_score+=1
            if d1.PTypeSetId==d2.PTypeSetId:
                tmp_score+=0.5
            if d1.PathId==d2.PathId:
                tmp_score+=2
            if d1.SimTECId==d2.SimTECId:
                tmp_score+=1

            return tmp_score
                        
        def arrange(self):
            p=self.wdict
            for k in p:
                if not all(p[k]):
                    self.mvp.append(k)
                    self.mvp_non_num[k]=p[k].count(None)
            cooling_rate=0.003
            temper=1000
            self.scoring()
            print("Original Score: ",self.score)
            if len(self.mvp)!=0:
                while temper>1:
                    self.neighbor()
                    old_e=self.energy(self.temp_page)
                    new_e=self.energy(self.wdict[self.temp_key])
                    aceept_p=np.random.random()
                    if self.probability(old_e,new_e,temper)>=aceept_p:
                        pass
                    else:
                        #self.wdict[self.temp_key]=self.temp_page
                        self.wdict=self.temp_dict
                        self.temp_key=None
                        self.temp_page=None
                    temper*=1-cooling_rate
            self.scoring()  

        def sort(self):
            p=self.wdict
            for k in p:
                if not all(p[k]):
                    self.mvp.append(k)
                    self.mvp_non_num[k]=p[k].count(None)
            self.scoring()
            #print("Original Score: ",self.score)
            lp=self.longest_page    #longest page
            lp=self.wdict[lp]    #longest page
            gap_penalty=-1
            for k in self.mvp:
                #initialize
                ss=list()
                cp=[x for x in self.wdict[k] if x!=None ]   #current page
                for i in range(self.max_len+1):
                    if i==0:
                        ss.append(list(range(0,(-(len(cp)+1))*100,-100)))
                    else:
                        ss.append([-i]+[0]*(len(cp)))
                
                for i in range(1,self.max_len+1):
                    for j in range(1, len(cp)+1):
                        match=ss[i-1][j-1]+self.dp2score(lp[i-1],cp[j-1])
                        deletion=ss[i-1][j]+gap_penalty #up
                        insertion=ss[i][j-1]+gap_penalty #left
                        ss[i][j]=max(match,deletion,insertion)
                #print(ss)       
                if True:
                    i=self.max_len
                    j=len(cp)
                    tmp=list()
                    while i!=0 or j!=0:
                        if j==i:
                            tmp.append(cp[j-1])
                            i-=1
                            j-=1
                        elif i==0:
                            print("ERROR1") #Turn left
                            j-=1
                        elif j==0:
                            tmp.append(None) #Turn up
                            i-=1
                        else:
                            s1=ss[i-1][j-1]
                            s2=ss[i-1][j]
                            s3=ss[i][j-1]
                            if s1>s2:
                                tmp.append(cp[j-1]) #Turn left up
                                i-=1
                                j-=1
                            elif True:
                                tmp.append(None) #Turn up
                                i-=1
                            else:
                                print("ERROR2") #Turn left
                                j-=1
                tmp.reverse()
                self.wdict[k]=tmp
                self.scoring()
            

    class DataPoint:
        def __init__(self,ser):
            self.Webpage=ser[0]
            self.LeafIndex=ser[1]
            self.ContentId=ser[2]
            self.TypeSetId=ser[3]
            self.PTypeSetId=ser[4]
            self.PathId=ser[5]
            self.SimTECId=ser[6]
            self.Content=ser[7]

    class WebData:
        def __init__(self, p_num=5):
            self.p_num=p_num
            self.df_list=list()
            self.seg_num=0
            self.seg_list=list()
            
        def load_data(self,file_name):
            df=pd.read_csv("SegData"+str(self.p_num)+"/"+file_name,sep='\t',skip_blank_lines=False)
            df_all = np.split(df, df[df.isnull().all(1)].index)
            for df in df_all:
                self.df_list.append(df.drop(df[df.isnull().all(1)].index))
            for df in self.df_list:
                self.seg_num+=1
                self.seg_list.append(Segment())
                wd=self.seg_list[-1].wdict
                for i in df.index:
                    wpage=df.loc[i,df.keys()[0]]
                    if wpage not in wd:
                        wd[wpage]=list()
                    wd[wpage].append(DataPoint(df.loc[i]))
            for y in range(len(self.seg_list)):
                ml=max([ len(x) for x in self.seg_list[y].wdict.values() ])
                for k in self.seg_list[y].wdict:
                    if len(self.seg_list[y].wdict[k])==ml:
                        self.seg_list[y].longest_page=k
                        break
                self.seg_list[y].max_len=ml
                for wp in self.seg_list[y].wdict:
                    self.seg_list[y].wdict[wp].extend( [None]*( ml-len( self.seg_list[y].wdict[wp] ) ) )
                #print([ len(x) for x in self.seg_list[y].wdict.values() ])
                
        def output(self,file_name):
            with open("resSegData"+str(data.p_num)+"/"+re.sub(r".txt","",file_name)+".csv",'w') as res:
                for seg in self.seg_list:
                    for k in seg.wdict:
                        tmp=list()
                        for x in seg.wdict[k]:
                            if x!=None:
                                tmp.append(str(x.LeafIndex))
                            else:
                                tmp.append(" ")
                        
                        res.write(str(k)+","+",".join(tmp))
                        res.write("\n")
                    res.write(" ,Score: "+str(seg.score)+"\n\n")
    
    SEG_NUM=30
    info=open("resSegData"+str(SEG_NUM)+"/__INFO.csv",'w')
    for file_name in os.listdir("SegData"+str(SEG_NUM)+"/"):
        print(file_name,":")
        start_time=time.time()
        data=WebData(SEG_NUM)
        data.load_data(file_name)
        average_score=0
        total_time=0
        for d in data.seg_list:
            d.sort()
            average_score+=d.score
        average_score/=len(data.seg_list)
        total_time=(time.time()-start_time)
        print("Average Score: ",average_score)
        print("Total Time: ",total_time)
        info.write(file_name+","+str(average_score)+","+str(total_time)+"\n")
        data.output(file_name)
    
    