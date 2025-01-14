# -*- coding: utf-8 -*-
"""
Created on Sun Apr 17 12:40:26 2022

@author: buxared

Banana Manga Reader, also referred to as BMR, is an application designed 
to read manga on Kobo eReaders.

Copyright (C) 2022  buxared

This file is a part of Banana Manga Reader.

Banana Manga Reader is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Banana Manga Reader is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>

"""
import flask
import requests
from PIL import Image
import io
import os
import csv
import shutil
import time

app=flask.Flask(__name__)

search_results={}
manga_data={}
user_selections={'manga':1000000, 'chapter':1000000} #Global choice tracker
pg_links={}
reader_src={}
lib_selection={}

@app.route("/")
def home():
    return flask.render_template('home.html')

@app.route("/search", methods=["POST","GET"])
def GetRes():
    search_results.clear()
    return flask.render_template('searchpage.html')

@app.route("/results/<srch>", methods=["POST","GET"])
def ShowRes(srch):
    user_selections['manga']=1000000 #reset global tracking
    search_string=flask.request.form["srchstr"]
    a=search_string.replace("'","")
    a=a.split(' ')
    usable_search_string=''
    for i in range(len(a)):
        if i==0:
            usable_search_string=usable_search_string+a[i]
        else:
            usable_search_string=usable_search_string+'-'+a[i]
    
    #title search:
    data1=requests.get('https://mangakakalot.com/search/story/'+usable_search_string, headers={'User-agent': 'Mozilla/5.0'}).text
    
    # #find actual titles from data (with author last chapter and update date and link)
    
    #look for"<div class="story_item">"
    r1=data1.split('<div class="story_item">')
    n_manga=len(r1)-1
    for i in range(n_manga):
        #for every item in r1 except html headers do the following: split with "\n"    
        split_string=r1[i+1].split('\n')
        manga_url=split_string[1].split('"')[3]
        manga_title=split_string[2].split('"')[3]
        if "mangakakalot.com" in manga_url:
            manga_last_ch=split_string[11].split('"')[1].split('_')[-1]
        elif "readmanganato.com" in manga_url:
            manga_last_ch=split_string[11].split('"')[3].split('-')[-1]
        elif "chapmanganato.to" in manga_url:
            manga_last_ch=split_string[11].split('"')[3].split('-')[-1]
        else:
            manga_last_ch='not found'

        manga_author=r1[i+1].split('<span>Author(s)')[1].split(':')[1].split('<')[0].strip()
        manga_update=r1[i+1].split('<span>Updated')[1].split(':')[1].split(' ')[1]
        search_results[str(i+1)]={'url': manga_url,
                               'title': manga_title,
                               'last_ch': manga_last_ch,
                               'update': manga_update,
                               'author': manga_author}
    
    return flask.render_template('searchres.html', n_manga=n_manga, res=search_results)   

@app.route("/manga_result/choice/<usr_choice>")
def GetMangaData(usr_choice):

    manga_selected=usr_choice
    user_selections['manga']=usr_choice #global tracking
    user_selections['chapter']=1000000 # to ensure that when a new manga is selected, but same chapter is selected, GetChap gets us the right info
    
    manga_data['url']=search_results[str(manga_selected)]['url']
    manga_data['title']=search_results[str(manga_selected)]['title']

    # open manga page, get chapter list: links and numbers
    data2=requests.get(search_results[str(manga_selected)]['url'], headers={'User-agent': 'Mozilla/5.0'}).text
    
    #Get author name:
    manga_data['author']=data2.split('/author/')[1].split('>')[1].split('<')[0]
    
    #add description
    manga_data['description']=data2.split('"description"')[1].split('"')[1].replace('&quot;','"').replace("&#39;","'")
    
    #get manga cover image
    #    first clear old image file
    try:
        os.remove('static/manga_cover/manga_cover.jpg')
    except:
        pass
    manga_cover_link=data2.split('"og:image" content')[1].split('"')[1]
    manga_cover_response=requests.get(manga_cover_link, verify=True)
    manga_cover=Image.open(io.BytesIO(manga_cover_response.content)).convert('RGB')
    manga_cover.save('static/manga_cover/manga_cover.jpg')
    
    #get genres:
    manga_data['genres']=[]
    g_data=data2.split('Genres')[1].split('</li>')[0]
    g_data=g_data.split('</a>')
    n_genres=len(g_data)-1
    for i in range(n_genres):
        if 'mangakakalot.com' in manga_data['url']:
            g_n=g_data[i].split('>')[1]
            manga_data['genres'].append(g_n)
        elif 'readmanganato.com' in manga_data['url']:
            if i not in [0,n_genres-1]:
                g_n=g_data[i].split('>')[1]
                manga_data['genres'].append(g_n)
    
    #Get chapter data
    manga_data['ch_list']={}
    #add chapters: process different for each website:
    if 'mangakakalot.com' in manga_data['url']:
        ch_data=data2.split('<div class="row">')
        n_ch=len(ch_data)-1
        for i in range(n_ch):
            each_ch_string=ch_data[i+1].split('\n')
            ch_link=each_ch_string[1].split('"')[1]
            ch_num=ch_link.split('_')[-1]
            ch_title=each_ch_string[1].split('"')[3]
            ch_update=each_ch_string[3].split('"')[1].split(' ')[0]
            manga_data['ch_list'][str(ch_num)]={'ch_link': ch_link,
                                                'ch_title': ch_title,
                                                'ch_update': ch_update}
            
    elif 'readmanganato.com' in manga_data['url']:
        ch_data=data2.split('<li class="a-h">')
        n_ch=len(ch_data)-1
        for i in range(n_ch):
            each_ch_string=ch_data[i+1].split('\n')
            ch_link=each_ch_string[1].split('"')[5]
            ch_num=ch_link.split('-')[-1]
            ch_title=each_ch_string[1].split('"')[7]
            ch_update=each_ch_string[3].split('"')[3].split(' ')[0]+each_ch_string[3].split('"')[3].split(' ')[1]
            manga_data['ch_list'][str(ch_num)]={'ch_link': ch_link,
                                                'ch_title': ch_title,
                                                'ch_update': ch_update}
            
    elif 'chapmanganato.to' in manga_data['url']:
        ch_data=data2.split('<li class="a-h">')
        n_ch=len(ch_data)-1
        for i in range(n_ch):
            each_ch_string=ch_data[i+1].split('\n')
            ch_link=each_ch_string[1].split('"')[5]
            ch_num=ch_link.split('-')[-1]
            ch_title=each_ch_string[1].split('"')[7]
            try:
                ch_update=each_ch_string[3].split('"')[5].split(' ')[0]+each_ch_string[3].split('"')[5].split(' ')[1]
            except:
                ch_update="0000"
            manga_data['ch_list'][str(ch_num)]={'ch_link': ch_link,
                                                'ch_title': ch_title,
                                                'ch_update': ch_update}
    
    manga_data['last_ch']=list(manga_data['ch_list'].keys())[0]
    manga_data['update']=manga_data['ch_list'][manga_data['last_ch']]['ch_update']
    
    return flask.render_template('mangapage.html', n_ch=n_ch, manga_data=manga_data)

@app.route("/manga_reader/ch/<ch_no>/p<p_no>")
def GetChap(ch_no,p_no):
    if user_selections['chapter']!=ch_no: #if new chapter is selected
        
        #clear old files from cache
        dir2clear = 'static/chapter_cache'
        for f in os.listdir(dir2clear):
            os.remove(os.path.join(dir2clear, f))
            
        chapter_selected=ch_no
        user_selections['chapter']=ch_no #update for global tracking
        
        #open chapter page, get page links
        data3=requests.get(manga_data['ch_list'][str(chapter_selected)]['ch_link'], headers={'User-agent': 'Mozilla/5.0'}).text
        
        #look for <div class="container-chapter-reader">
        pg_data=data3.split('<div class="container-chapter-reader">')[1].split('\n')[1].split('<img src')
        pg_links.clear()
        
        n_pg=len(pg_data)-1
        for i in range(n_pg):
            each_pg_link=pg_data[i+1].split('"')[1]
            pg_links[str(i+1)]=each_pg_link
        
        #Now, download all chapter pages and store in app 'chapter_cache' folder
        
        host_link=pg_links['1'].split('/')[2]
        referer_link=manga_data['ch_list'][str(chapter_selected)]['ch_link']

        s = requests.Session()

        headers = {
                    "user-agent" : "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko)", 
                    "accept" : "text/html,application/xhtml+xml,application/xml;q=0.9,image/jpg,image/webp,image/apng,/;q=0.8,application/signed-exchange;v=b3;q=0.9", 
                    "accept-encoding" : "gzip, deflate, br", 
                    "accept-language" : "en-GB,en;q=0.9,en-US;q=0.8,de;q=0.7", 
                    "cache-control"   : "no-cache", 
                    "pragma" : "no-cache", 
                    "upgrade-insecure-requests" : "1" ,
                    "Host": host_link,#example: 'bu3.mkklcdnv6tempv3.com',#
                    "referer": referer_link
                    }
        s.headers = headers
        
        #here, try to get one image, if works, proceed, except (else) follow link to other server button, reconstruct session by changing host_link
        try:
            page_response=s.get(pg_links['1'], verify=True)
            img = Image.open(io.BytesIO(page_response.content))
        except:
            server_num=['','1','2','3','4','5','6','7','8','9','10','11','12','13','14','15','16','17','18','19','20','mn']
            for hostname in [host_link.split('.')[1], 'mncdnbuv1']:
                for num in server_num:
                    host_link='bu'+num+'.'+hostname+'.'+host_link.split('.')[2]
                    pg_links['1']='https://'+host_link+'/'+'/'.join(pg_links['1'].split('/')[3:])
                    headers = {
                                "user-agent" : "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko)", 
                                "accept" : "text/html,application/xhtml+xml,application/xml;q=0.9,image/jpg,image/webp,image/apng,/;q=0.8,application/signed-exchange;v=b3;q=0.9", 
                                "accept-encoding" : "gzip, deflate, br", 
                                "accept-language" : "en-GB,en;q=0.9,en-US;q=0.8,de;q=0.7", 
                                "cache-control"   : "no-cache", 
                                "pragma" : "no-cache", 
                                "upgrade-insecure-requests" : "1" ,
                                "Host": host_link,
                                "referer": referer_link
                                }
                    s.headers = headers#redefined since host_link got updated
                    
                    try:
                        page_response=s.get(pg_links['1'], verify=True)
                        img = Image.open(io.BytesIO(page_response.content))
                        break
                    except:
                        pass
                
        #fix pg_links
        for pg_no in pg_links:
            pg_links[pg_no]='https://'+host_link+'/'+'/'.join(pg_links[pg_no].split('/')[3:])
            
        reader_src.clear()
        
        for pg_no in pg_links:
            page_response=s.get(pg_links[pg_no], verify=True)
            try:
                img = Image.open(io.BytesIO(page_response.content))
            except:
                img=Image.open('static/images/pgunavail.jpg', mode='r') 
            
            if img.mode != 'RGB':
                img = img.convert('RGB')
            img.save('static/chapter_cache/'+str(chapter_selected)+'-'+"{:03d}".format(int(pg_no))+'.jpg')
            # generate link to page for reader webpage
            reader_src[pg_no]='chapter_cache/'+str(chapter_selected)+'-'+"{:03d}".format(int(pg_no))+'.jpg'

        
    #link for manga title page
    manga_home_link='/manga_result/choice/'+user_selections['manga']
    
    #we need key of next chap and previous chap
    ch_all=list(manga_data['ch_list'].keys()) #list of keys
    this_ch_index=ch_all.index(ch_no)         #index of this chapter in list
    
    #construct links for next and previous chapter
    if this_ch_index > 0: #this is not the first in the list [most recent release]
        next_ch_key=ch_all[this_ch_index-1]       #key of next chapter is this_ch_index - 1, since descending order
        next_ch_link='/manga_reader/ch/'+next_ch_key+'/p1'
    else:
        next_ch_link=manga_home_link
        
    if this_ch_index < len(ch_all)-1: #final index of the list [first or oldest chapter]
        prev_ch_key=ch_all[this_ch_index+1]       #similar for previous chapter
        prev_ch_link='/manga_reader/ch/'+prev_ch_key+'/p1'
    else:
        prev_ch_link=manga_home_link
    
    while True: #keep looping unless returning is possible
        try:
            return flask.render_template('mangareader3.html', ch_no=ch_no, p_no=int(p_no), pg_last=len(reader_src), pg_src=reader_src[str(p_no)], next_ch_link=next_ch_link, prev_ch_link=prev_ch_link, manga_home_link=manga_home_link)
        except:
            #wait if not done downloading all images
            time.sleep(3)

@app.route("/add2fav")
def FavAdd():    
    m_title=search_results[user_selections['manga']]['title']
    m_url=search_results[user_selections['manga']]['url']
    #write data required to simulate search results
    #step 1:check if entry already exists
    with open('static/mangafavs.csv', 'r', newline='') as csv_file:
        counter=0
        reader=csv.reader(csv_file)
        for line in reader:
            if m_title in line:
                counter=counter+1
    csv_file.close()
    #step 2: write entry if it doesn't exists
    with open('static/mangafavs.csv', 'a', newline='') as csv_file:
        writer = csv.writer(csv_file)  # Note: writes lists, not dicts.
        if counter==0:#write only if entry does not exist already
            writer.writerow([m_title, m_url])
    csv_file.close()
        
    manga_home_link='/manga_result/choice/'+user_selections['manga']
    
    return flask.render_template('favadded.html', favtitle=m_title, manga_home_link=manga_home_link)

@app.route("/favorites")
def FavDisp():
    #reset user_selections
    user_selections['manga']=1000000
    user_selections['chapter']=1000000
    search_results.clear()
    
    #read data from mangafavs.csv to dictionary
    with open('static/mangafavs.csv', 'r', newline='') as csv_file:
        reader=csv.reader(csv_file)
        manga_favs=dict(reader)
    csv_file.close()

    #simulate search_results
    num=0
    for manga in manga_favs:
        num=num+1
        search_results[str(num)]={'title': manga,
                                  'url': manga_favs[manga]}
    n_manga=len(search_results)
    #This page should be similar to searchres
    return flask.render_template('favoriteshome.html', n_manga=n_manga, res=search_results)

@app.route("/removeFavConfirm/<fav_num>")
def FavDel(fav_num):
    #delete entry from dictionary
    removed_title=search_results[fav_num]['title']
    
    #read data from mangafavs.csv to dictionary
    with open('static/mangafavs.csv', 'r', newline='') as csv_file:
        reader=csv.reader(csv_file)
        manga_favs=dict(reader)
    csv_file.close()
    
    del manga_favs[removed_title]
    
    #rewrite updated dictionary to mangafavs.csv
    with open('static/mangafavs.csv', 'w', newline='') as csv_file:  
        writer = csv.writer(csv_file)
        for key, value in manga_favs.items():
            writer.writerow([key, value])
    csv_file.close()
    #provide button to go back to favoriteshome page
    return flask.render_template('favremoval.html', removed_title=removed_title)

@app.route("/add2lib")
def LibUpdate():   
    #get usable manga and chapter title
    manga_title=manga_data['title'].strip()
    chapter_title=manga_data['ch_list'][user_selections['chapter']]['ch_title'].strip()
    
    bad_char=['.', ' ', '"', '?', '>', '<', '/' , '|', '\\', '*', ':', '\\0']
    for c in bad_char:
        if c in manga_title:
            manga_title=manga_title.replace(c, '_')
            
    for c in bad_char:
        if c in chapter_title:
            chapter_title=chapter_title.replace(c, '_')
            
    #Add (prefix) chapter number tag for sorting
    chapter_title='[c'+ str(float(user_selections['chapter'])).zfill(6) + ']' + chapter_title
    
    #if this manga title is not already in the library, create directory
    mangadir = 'static/library/'+manga_title
    if not os.path.exists(mangadir):
        os.makedirs(mangadir)
    
    #now that manga title is created or already exists, if this chapter title is not already under the manga title, create directory
    chapdir='static/library/'+manga_title+'/'+chapter_title

    if os.path.exists(chapdir):
        manga_home_link='/manga_result/choice/'+user_selections['manga']
        return flask.render_template('libadded.html', t=manga_data['title'], c=manga_data['ch_list'][user_selections['chapter']]['ch_title'], manga_home_link=manga_home_link)

    else: #if it does not exist, meaning that chapter is new; create dir
        os.makedirs(chapdir)
        #now that the chapter folder is created, copy chapter pages from chapter cache
        shutil.copytree('static/chapter_cache', chapdir, dirs_exist_ok=True)
        manga_home_link='/manga_result/choice/'+user_selections['manga']
        return flask.render_template('libadded.html', t=manga_data['title'], c=manga_data['ch_list'][user_selections['chapter']]['ch_title'], manga_home_link=manga_home_link)
    
    
@app.route("/library")
def LibDisp():
    #find all manga titles in library
    title_list=os.listdir('static/library/')
    
    #display titles in a table in libraryhome
    n_titles=len(title_list)
    
    return flask.render_template('libraryhome.html', n_titles=n_titles, title_list=title_list)

@app.route("/library/<title>")
def LibDispL2(title):
    #This is library level 2
    #Here we want to see chapters listed under the manga title
    mangapath='static/library/'+title+'/'
    chapter_list=os.listdir(mangapath)
    
    n_ch=len(chapter_list)
    
    #create lib_selection dictionary for creating links easily
    lib_selection['title']=title
    lib_selection['ch_list']=chapter_list
    lib_selection['ch_sel']=1000000 #"chapter selcted" initialized
    lib_selection['pg_links']=[] #empty list
    
    #display chapter titles in a table    
    return flask.render_template('librarymanga.html', m_title=title, n_ch=n_ch, chapter_list=chapter_list)

@app.route("/libChapRemoval/<title>/<ch_title>")
def LibChDel(title, ch_title):
    chapterpath='static/library/' + title + '/' + ch_title
    shutil.rmtree(chapterpath)
    return flask.render_template('libchremoval.html', removed_title=title, removed_ch=ch_title)

@app.route("/libTitleRemoval/<title>")
def LibTitleDel(title):
    mangapath='static/library/' + title
    shutil.rmtree(mangapath)
    return flask.render_template('libtitleremoval.html', removed_title=title)

@app.route("/offline_reader/ch/<ch_num>/p<p_num>")
def OpenOfflineReader(ch_num, p_num):
    if lib_selection['ch_sel']!=ch_num:
        lib_selection['ch_sel']=ch_num #set new selection
        
        #get pages in chapter
        ch_path='static/library/'+lib_selection['title']+'/'+lib_selection['ch_list'][int(ch_num)-1]+'/'
        lib_selection['pg_links']=[f for f in os.listdir(ch_path) if os.path.isfile(os.path.join(ch_path, f))]
    
    #create links    
    manga_home_link='/library/'+lib_selection['title']
    
    if int(ch_num)<len(lib_selection['ch_list']):
        next_ch_link='/offline_reader/ch/'+str(int(ch_num)+1)+'/p1'
    else:
        next_ch_link=manga_home_link
        
    
    if int(ch_num)>1:
        prev_ch_link='/offline_reader/ch'+str(int(ch_num)-1)+'/p1'
    else:
        prev_ch_link=manga_home_link
    
    while True: #keep looping unless pg_src is filled
        try:
            pg_src='library/'+lib_selection['title']+'/'+lib_selection['ch_list'][int(ch_num)-1]+'/'+lib_selection['pg_links'][int(p_num)-1]
            break
        except:
            #wait if not done loading pg_src
            time.sleep(2)
    
    return flask.render_template('offlinemangareader3.html', ch_no=ch_num, p_no=int(p_num), pg_last=len(lib_selection['pg_links']), pg_src=pg_src, next_ch_link=next_ch_link, prev_ch_link=prev_ch_link, manga_home_link=manga_home_link)
        
    

@app.route("/nav")
def navigationpage():
    return flask.render_template('navigation.html')

@app.route("/about")
def aboutpage():
    return flask.render_template('about.html')
    
@app.route("/shutdown", methods=["POST","GET"])
def shutdown():
    if flask.request.method=="POST":  
        #clear old files from cache
        dir2clear = 'static/chapter_cache'
        for f in os.listdir(dir2clear):
            os.remove(os.path.join(dir2clear, f))
            
        try:
            os.remove('static/manga_cover/manga_cover.jpg')
        except:
            pass
            
        # return ip to what it was
        os.system('ip addr del 127.0.0.1/8 dev lo')
        os.system('ip addr del 127.0.0.42/32 dev lo')
        
        # shutdown_server()
        os.system('pkill -15 -f "BMR"')
        return flask.render_template('shutdown.html')
    else:
        return flask.render_template('shutdown.html')

# if __name__=="__main__":
#     app.run(host='127.0.0.42', port=1234) #Alternative code to run; Must change last line in BMRrun.sh to: "/mnt/onboard/.BMR/bmrpyenv/bin/python3 BMRmain.py
#     app.run(host='0.0.0.0', port=1234) #For desktop only, do not run on Kobo