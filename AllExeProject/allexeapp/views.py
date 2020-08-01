from django.shortcuts import render
from django.http import HttpResponse
# Create your views here.
from django.db import connection
import pymysql.cursors
import sys, os
import time
def country_db_connection():
    a = 0
    while a == 0:
        try:
            connection = pymysql.connect(host='185.142.34.92',
                user='ams',
                password='TgdRKAGedt%h',
                db='tenders_db',
                charset='utf8',
                cursorclass=pymysql.cursors.DictCursor)
            print('tenders_db Database Connected')
            return connection
        except Exception as e:
            exc_type , exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print("Error Details : \nFunction Name: " , sys._getframe().f_code.co_name + "\nException: " + str(e) , "\n Exception Type: " , exc_type , "\nFile Name: ", fname ,"\nError Line No: " , exc_tb.tb_lineno)
            a = 0
            time.sleep(10)


mydb = country_db_connection()
mycursor = mydb.cursor()
mycursor.execute("SELECT * FROM dms_country_tbl")
Country_ISO_data = mycursor.fetchall()#  Inside Country_ISO_data variable --> [{'Code': 'AD', 'Country': 'ANDORRA '}, {'Code': 'AE', 'Country': 'UNITED ARAB EMIRATES '}]
mycursor.close()
mydb.close()  


exe_DB_cursor = connection.cursor()
exe_DB_cursor.execute("SELECT * FROM exe_developer_tbl")
exe_developer_data = exe_DB_cursor.fetchall() # data is tuple next step tuple convert to list
exe_developer_data = list(exe_developer_data)  # inside list multiple tuples like this [(1, 2), (3, 4), (5, 6)] 
exe_developer_data = [list(tup) for tup in exe_developer_data] # using list comprehension  || convert list of tuples to list of list 

exe_DB_cursor.execute("SELECT * FROM exe_runby_tbl")
exe_runby_data = exe_DB_cursor.fetchall()
exe_runby_data = list(exe_runby_data)
exe_runby_data = [list(tup) for tup in exe_runby_data]


def index(request):

    return render(request, 'home.html')

def source_list(request):
    exe_DB_cursor.execute("""SELECT sm.source_no,sm.source_name,sm.tender_url,er.user_name AS EXE_RunBy,ed.developer_name AS Developer FROM `source_master_tbl` sm
                            INNER JOIN `exe_developer_tbl` ed ON sm.exe_developer = ed.developer_id
                            INNER JOIN `exe_runby_tbl` er ON sm.exe_run_by = er.user_id""")
    source_data_list = exe_DB_cursor.fetchall()
    source_data_list = list(source_data_list)
    source_data_list = [list(tup) for tup in source_data_list]
    source_details = {'source_data_list': source_data_list}
    return render(request, 'source_list.html',source_details)
    
def Add_source(request):
    
    test_data = {'exe_developer_list': exe_developer_data, 'exe_runby_list':exe_runby_data,'Country_ISO_list':Country_ISO_data}

    if request.method == 'POST':
        source_no = request.POST['source_no']
        # print(source_no)
        source_name = request.POST['source_name']
        # print(source_name)
        contry_iso = request.POST.get('contry_iso', '')
        # print(contry_iso)
        avg_tender = request.POST['avg_tender']
        # print(avg_tender)
        exe_run_by = request.POST.get('exe_run_by', '')
        # print(exe_run_by)
        exe_developer = request.POST.get('exe_developer', '')
        # print(exe_developer)
        Devloped_language = request.POST.get('Devloped_language', '')
        # print(Devloped_language)
        is_english = request.POST.get('is_english', '')
        # print(is_english)
        status = request.POST.get('status', '')
        # print(status)
        tender_url = request.POST['tender_url']
        # print(tender_url)
        if source_no == '' and source_name == '' and contry_iso == '' and avg_tender == '' and exe_run_by == '' and exe_developer == '' and status == '' and Devloped_language == '':
            error = {'error_alert': 'alert','exe_developer_list': exe_developer_data, 'exe_runby_list':exe_runby_data,'Country_ISO_list':Country_ISO_data}
            return render(request, 'Add_source.html',error)
        elif not source_no.isdigit():
            error = {'source_no_error': 'not Digit','exe_developer_list': exe_developer_data, 'exe_runby_list':exe_runby_data,'Country_ISO_list':Country_ISO_data}
            return render(request, 'Add_source.html',error)
        elif not avg_tender.isdigit():
            error = {'avg_tender_error': 'not Digit','exe_developer_list': exe_developer_data, 'exe_runby_list':exe_runby_data,'Country_ISO_list':Country_ISO_data}
            return render(request, 'Add_source.html',error)
        else:
            exe_DB_cursor.execute(f"SELECT * FROM `source_master_tbl` WHERE source_no='{source_no.strip()}'")
            duplicate_data = exe_DB_cursor.fetchall()
            if len(duplicate_data) > 0:
                error = {'Duplicate_source_no': 'Duplicate source no','exe_developer_list': exe_developer_data, 'exe_runby_list':exe_runby_data,'Country_ISO_list':Country_ISO_data}
                return render(request, 'Add_source.html',error)
            exe_DB_cursor.execute(f"SELECT * FROM `source_master_tbl` WHERE source_name='{source_name.strip()}'")
            duplicate_data = exe_DB_cursor.fetchall()
            if len(duplicate_data) > 0:
                error = {'Duplicate_source_name': 'Duplicate source name','exe_developer_list': exe_developer_data, 'exe_runby_list':exe_runby_data,'Country_ISO_list':Country_ISO_data}
                return render(request, 'Add_source.html',error)
            else:
                insert_query = f"INSERT INTO source_master_tbl(source_no,source_name,country_iso,avg_tender,exe_run_by,exe_developer,develop_language,is_english,status,tender_url) VALUES('{source_no.strip()}','{source_name.strip()}','{contry_iso.strip()}','{avg_tender.strip()}','{exe_run_by.strip()}','{exe_developer.strip()}','{Devloped_language.strip()}','{is_english.strip()}','{status.strip()}','{tender_url.strip()}')"
                exe_DB_cursor.execute(insert_query)
                connection.commit()
                error = {'sucess': 'inserted','exe_developer_list': exe_developer_data, 'exe_runby_list':exe_runby_data,'Country_ISO_list':Country_ISO_data}
                return render(request, 'Add_source.html',error)
    return render(request, 'Add_source.html',test_data)