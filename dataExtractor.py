import sys
import mysql.connector

TITLE_BASICS = "title.basics.tsv"
TITLE_RATINGS = "title.ratings.tsv"
TITLE_CREW = "title.crew.tsv"
TITLE_PRINCIPALS = "title.principals.tsv"
TITLE_AKAS = "title.akas.tsv"

NAME_BASICS = "name.basics.tsv"

DATA_RECENCY = 6

def extractAndLoad():
    cnx = mysql.connector.connect(user='root', host='127.0.0.1',database='movies')
    cursor = cnx.cursor()
    t_const_list = {}
    with open(TITLE_BASICS) as tb: #, open(TITLE_AKAS) as ta, open(TITLE_RATINGS) as tr, open(TITLE_CREW) as tc, open(TITLE_PRINCIPALS) as tp:
        line = tb.readline()
        count = 0
        old_count = 0
        insert_movie_stmt = ("INSERT INTO movie_info(tconst,primary_title,year,genres) VALUES(%s,%s,%s,%s) ON DUPLICATE KEY UPDATE genres=%s")
        while line != "":
            # print "bbb"
            line = tb.readline()
            if(line == ""):
                continue
            if line[-1] == '\n':
                line = line[:-1]
            features = line.split("\t")
            # print features
            tconst = features[0]
            title = features[3]
            startYear = features[5]
            genres = features[8]
            # print "Title : {}, Start Year: {}, Genres: {}".format(title,startYear,genres)
            movie_stmt = (tconst,title,startYear,genres,genres)
            if(startYear != "\\N" and int(startYear) > 2004):
                try:
                    # if count > 3027200:
                    cursor.execute(insert_movie_stmt, movie_stmt)
                    t_const_list[tconst] = 1
                    count += 1
                except Exception as e:
                    count -= 1
                    print e
            if(count % 1000 == 0 and old_count != count):
                if count > 3027200:
                    cnx.commit()
                    old_count = count
            if(count % 100 == 0 and old_count != count):
                print "Inserted {} tb elements".format(count)

    select_all_stmt = "SELECT tconst from movie_info WHERE year = '2017'"
    cursor.execute(select_all_stmt)

    for tconst in cursor:
        t_const_list[tconst[0]] = 1

    print "DONEEE"
    with open(TITLE_AKAS) as tb: 
        line = tb.readline()
        count = 0
        old_count = 0
        insert_movie_stmt = ("UPDATE movie_info SET region=%s, language=%s WHERE tconst=%s")
        # print t_const_list
        while line != "":
            line = tb.readline()
            if(line == ""):
                continue
            if line[-1] == '\n':
                line = line[:-1]
            features = line.split("\t")
            try:
                tconst = features[0]
                region = features[3]
                language = features[4]
                movie_stmt = (region,language,tconst)
                if tconst in t_const_list and region == "US":
                    try:
                        cursor.execute(insert_movie_stmt, movie_stmt)
                        cnx.commit()
                        count += 1
                    except Exception as e:
                        count -= 1
                        print e
                if(count % 10 == 0 and count > 0):
                    print "Inserted {} ta elements".format(count)
            except:
                print "error"
    
    print "DONEEE"
    
    with open(TITLE_CREW) as tb: 
        line = tb.readline()
        count = 0
        old_count = 0
        insert_movie_stmt = ("UPDATE movie_info SET directors=%s WHERE tconst=%s")
        while line != "":
            line = tb.readline()
            if(line == ""):
                continue
            if line[-1] == '\n':
                line = line[:-1]
            features = line.split("\t")
            try:
                tconst = features[0]
                directors = features[1]
                movie_stmt = (directors,tconst)
                if tconst in t_const_list:
                    try:
                        cursor.execute(insert_movie_stmt, movie_stmt)
                        count += 1
                    except Exception as e:
                        count -= 1
                        print e
                    if(count % 100 == 0 and count > 0):
                        cnx.commit()
                        print "Inserted {} tc elements".format(count)
            except:
                print "Error here"
                
        
    with open(TITLE_RATINGS) as tb: 
        line = tb.readline()
        count = 0
        old_count = 0
        insert_movie_stmt = ("UPDATE movie_info SET rating=%s, num_votes=%s WHERE tconst=%s")
        while line != "":
            line = tb.readline()
            if(line == ""):
                continue
            if line[-1] == '\n':
                line = line[:-1]
            features = line.split("\t")
            tconst = features[0]
            ratings = float(features[1])
            num_votes = int(features[2])
            movie_stmt = (ratings,num_votes,tconst)
            if tconst in t_const_list:
                try:
                    if count > 38700:
                        cursor.execute(insert_movie_stmt, movie_stmt)
                    count += 1
                except Exception as e:
                    count -= 1
                    print e
                if(count % 100 == 0 and count > 0):
                    if count > 38700:
                        cnx.commit()
                    print "Inserted {} tr elements".format(count)
    
    print "Done with tr "

    tconst_nconst_map = {}
    with open(TITLE_PRINCIPALS) as tb: 
        line = tb.readline()
        count = 0
        old_count = 0
        while line != "":
            line = tb.readline()
            if(line == ""):
                continue
            if line[-1] == '\n':
                line = line[:-1]
            features = line.split("\t")
            tconst = features[0]
            actor = features[2]
            if tconst not in t_const_list:
                continue
            if tconst in tconst_nconst_map:
                actor_list = tconst_nconst_map[tconst]
            else:
                actor_list = []
            actor_list.append(actor)
            tconst_nconst_map[tconst] = actor_list
            count += 1
            if count % 100000 == 0:
                print count
        print "done with getting actors"
        count = 0
        insert_movie_stmt = ("UPDATE movie_info SET actors=%s WHERE tconst=%s")
        for tconst in tconst_nconst_map:
            actor_list = tconst_nconst_map[tconst]
            movie_stmt = (",".join(actor_list),tconst)
            try:
                cursor.execute(insert_movie_stmt, movie_stmt)
                count += 1
                if count % 1000 == 0 and count > 0:
                    cnx.commit()
                    print "Inserted {} tp elements".format(count)
            except Exception as e:
                count -= 1
                print e 
    
    with open(NAME_BASICS) as tb:
        line = tb.readline()
        count = 0
        while line != "":
            line = tb.readline()
            if(line == ""):
                continue
            if line[-1] == '\n':
                line = line[:-1]
            features = line.split("\t")
            nconst = features[0]
            name = features[1]
            birth = features[2]
            death = features[3]
            titles = features[5]
            insert_movie_stmt = ("INSERT INTO name_info(nconst,name,titles,birth,death) VALUES(%s,%s,%s,%s,%s)")
            movie_stmt = (nconst,name,titles,birth,death)
            try:
                cursor.execute(insert_movie_stmt, movie_stmt)
                count += 1
                if count % 1000 == 0 and count > 0:
                    cnx.commit()
                    print "Inserted {} tp elements".format(count)
            except Exception as e:
                count -= 1
                print e 

    cnx.commit()
    cursor.close()
    cnx.close()

extractAndLoad()

