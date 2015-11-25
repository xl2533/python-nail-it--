# -*- coding: utf-8 -*-
"""
Created on Mon Nov 23 12:04:02 2015

@author: lingxilove
"""
import numpy as np
import pandas as pd
import urllib.request as ul
from bs4 import BeautifulSoup

########## RUN THIS at Last##############
##Run
All_year = main(main_page,year);

############Initial parameter ###########
Init_url='http://www.presidency.ucsb.edu/showelection.php?year=2012'
Init_url_request = ul.urlopen(Init_url)
main_page = BeautifulSoup(Init_url_request);

year = np.arange(1856,2016,4) 
All_year = {};
########## define function #############
def main(main_page,year):
    for i in range(26,len(year)):
        single_year = year[i];
        url = Init_url.replace("2012",str(single_year))
        url_request = ul.urlopen(url)
        web_page = BeautifulSoup(url_request);
        All_year[single_year] = web_scrawl(web_page,single_year);
        print ("\n **** Finish scrawling year %d ****\n " % single_year);
    return All_year;
     
def find_position(line,position):
    for i in range(0,len(line)):
        temp = str(line[i]);
        if('STATE' in temp):
            position['party'] = i;
            position['start'] = i+3;
        elif('Totals' in temp or 'Total' in temp):
            position['end'] = i-1;
    return position;

def web_scrawl(web_page,single_year):
    content =  web_page.find('center').find_all(class_='elections_states')
    if (len(content)==1):  
        table = content[0];     
    else:
        table = content[1];    
    line = table.find_all('tr');  
    
    ##identify the start point and end point
    position_temp = {};
    position = find_position(line,position_temp);
    
    #dealling with abnormal web page
    if(len(position)==0):
        try:
            table = content[1]; 
            line = table.find_all('tr');   
            position = find_position(line,position_temp);
        except:
            print('\n !!!abnormal web page\n ');
    if(len(position)==0):
        try:
            table = content[0]; 
            line = table.find_all('tr');   
            position = find_position(line,position_temp);
        except:
            print('\n !!!abnormal web page\n ');   
    if(len(position)==0):
        content = web_page.find('center').table
        line = content.find_all('tr');   
        position = find_position(line,position_temp);
        
    ##identify how many parties run the election
    party_raw = line[position['party']];       
    All_party= ['Republican','Democrat','Green','Reform','Independent'
    ,"States' Rights",'Progressive','Socialist','Populist','Southern Democratic',
    'Constitutional Union','Whig-American'];
    party = list();
    for temp in All_party:
        if temp in str(party_raw):
            party.append(temp);
    if(len(party)==0):
        position['party'] = position['party']-1;
        party_raw = line[position['party']];
        for temp in All_party:
            if temp in str(party_raw):
                party.append(temp);

    party = np.array(party);
    ncol = 1+len(party)*3;
    
    ##create header for final DataFramce
    header =[ np.append( np.array(['total']) , np.repeat(party,3) ) 
    , np.append( np.array(['total']) , np.array(['num','per','ev']*len(party)) )];  
     
    ##fetch all the states
    state = list();
    for i in range(position['start'],position['end']) :
        temp = line[i].td;
        state.append(temp.string);
    nrow= len(state);   
    
    ##scrawling web
    Result = np.zeros((nrow,ncol) );         
    delimiter='' 
    for i in range(position['start'],position['end']) :
        temp = line[i];
        temp = temp.find_all('td');
        for h in range(1,len(temp)):    
            data= temp[h].string;
            if(data==None):
                try :
                    data=float(temp[h].p.string);
                except:
                    data=0; ##<p> sub_paragraph can not be extracted by string 
            elif (',' in data) :
                data = delimiter.join(data.split(',')); #votes
                data = float(data);
            elif('%' in data):
                data = float(data.split("%")[0]); #percentage
            elif('\xa0' in data or '*' in data):
                data = 0; # different representation of zero
            else:
                try:
                    data= float(data); #normail number
                except:
                    data=0; # deal with abnormal but unidentified situation
            Result[i-position['start'],h-1] = data;  
            
    ##create dataframe for indexing     
    D_Result = pd.DataFrame(Result,index=state,columns=header);
    return D_Result;
    


        
                
