from django.shortcuts import render
from django.http import HttpResponse,HttpResponseRedirect
# Create your views here.
from django.db import connection
import pymysql.cursors
import sys, os
import time
import json
from django.http import JsonResponse
import datetime
import time


from django.urls import reverse

from datetime import datetime as datetime_now
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
    exe_DB_cursor.execute("""SELECT sm.id,sm.source_no,sm.source_name,sm.tender_url,er.user_name AS EXE_RunBy,ed.developer_name AS Developer FROM `source_master_tbl` sm
                            INNER JOIN `exe_developer_tbl` ed ON sm.exe_developer = ed.developer_id
                            INNER JOIN `exe_runby_tbl` er ON sm.exe_run_by = er.user_id order by sm.id ASC""")
    source_data_list = exe_DB_cursor.fetchall()
    source_data_list = list(source_data_list)
    source_data_list = [list(tup) for tup in source_data_list]
    print(exe_runby_data)
    source_details = {'source_data_list': source_data_list,'exe_runby_list':exe_runby_data,'Country_ISO_list':Country_ISO_data,'exe_developer_list': exe_developer_data,}

    return render(request, 'source_list.html',source_details)

def loadmodel_data(request):
    if request.method == 'POST':
        id = request.POST['id']
        exe_DB_cursor.execute(f"SELECT * FROM source_master_tbl WHERE id = '{str(id).strip()}'")
        data = exe_DB_cursor.fetchall()
        # data = list(data)
        list_data = [list(tup) for tup in data]
        # print(list_data)
        return JsonResponse(list_data, safe=False)

def update_model(request):
    if request.method == 'POST':
        rowid = request.POST['rowid']
        # print(rowid)
        source_no = request.POST['source_no']
        # print(source_no)
        source_name = request.POST['source_name']
        # print(source_name)
        contry_iso = request.POST['contry_iso']
        # print(contry_iso)
        avg_tender = request.POST['avg_tender']
        # print(avg_tender)
        exe_run_by = request.POST['exe_run_by']
        # print(exe_run_by)
        exe_developer = request.POST['exe_developer']
        # print(exe_developer)
        Devloped_language = request.POST['Devloped_language']
        # print(Devloped_language)
        is_english = request.POST['is_english']
        # print(is_english)
        status = request.POST['status']
        # print(status)
        tender_url = request.POST['tender_url']
        # print(tender_url)
        remark = request.POST['remark']
        # print(remark)
        update_date = request.POST['update_date']
        
        if update_date != '':
            now = datetime_now.now()
            time = now.strftime("%H:%M:%S")
            main_update_date = update_date + " " + time
            update_date_timestamp = datetime.datetime.strptime(main_update_date, '%Y-%m-%d %H:%M:%S')
            print(type(update_date_timestamp))
            if source_no == '' or source_name == '' or remark == '' or tender_url == '' or contry_iso == '' or avg_tender == '' or exe_run_by == '' or exe_developer == '' or is_english == '' or status == '' or Devloped_language == '':
                return HttpResponse('All Fields Are Required !!!')

            elif not source_no.isdigit():
                return HttpResponse('Source number allow only Digit !!!')

            elif not avg_tender.isdigit():
                return HttpResponse('AVG Tender allow only Digit !!!')
            else:
                update_query = f"UPDATE exes_manage_db.source_master_tbl SET source_no = '{str(source_no).strip()}', source_name = '{str(source_name).strip()}', country_iso = '{str(contry_iso).strip()}', avg_tender = '{str(avg_tender).strip()}', exe_run_by = '{str(exe_run_by).strip()}', exe_developer = '{str(exe_developer).strip()}', develop_language = '{str(Devloped_language).strip()}', is_english = '{str(is_english).strip()}', status = '{str(status).strip()}', updated_on = '{update_date_timestamp}', tender_url = '{str(tender_url).strip()}', remark = '{str(remark).strip()}' WHERE id = {str(rowid).strip()}"
                exe_DB_cursor.execute(update_query)
                connection.commit()
                return HttpResponse('Update Data')
        else:
            return HttpResponse('Please Select When You Update Data !!!')

def Add_source(request):
    
    test_data = {'exe_developer_list': exe_developer_data, 'exe_runby_list':exe_runby_data,'Country_ISO_list':Country_ISO_data}

    if request.method == 'POST':
        source_no = request.POST['source_no']
        # print(source_no)
        source_name = request.POST['source_name']
        # print(source_name)
        contry_iso = request.POST['contry_iso']
        # print(contry_iso)
        avg_tender = request.POST['avg_tender']
        # print(avg_tender)
        exe_run_by = request.POST['exe_run_by']
        # print(exe_run_by)
        exe_developer = request.POST['exe_developer']
        # print(exe_developer)
        Devloped_language = request.POST['Devloped_language']
        # print(Devloped_language)
        is_english = request.POST['is_english']
        # print(is_english)
        status = request.POST['status']
        # print(status)
        tender_url = request.POST['tender_url']
        # print(tender_url)
        remark = request.POST['remark']
        # print(remark)
        if source_no == '' or source_name == '' or contry_iso == '' or avg_tender == '' or exe_run_by == '' or exe_developer == '' or is_english == '' or status == '' or Devloped_language == '' or tender_url == '' or remark == '':
            return HttpResponse('All Fields Are Required !!!')

        elif not source_no.isdigit():
            return HttpResponse('Source number allow only Digit !!!')

        elif not avg_tender.isdigit():
            return HttpResponse('AVG Tender allow only Digit !!!')

        else:
            exe_DB_cursor.execute(f"SELECT * FROM `source_master_tbl` WHERE source_no='{source_no.strip()}'")
            duplicate_data = exe_DB_cursor.fetchall()

            if len(duplicate_data) > 0:
                return HttpResponse('This Source Number Is Duplicate Please Insert New One !!!')

            exe_DB_cursor.execute(f"SELECT * FROM `source_master_tbl` WHERE source_name='{source_name.strip()}'")
            duplicate_data = exe_DB_cursor.fetchall()

            if len(duplicate_data) > 0:
                return HttpResponse('This Source Name Is Duplicate Please Insert New One !!!')
            else:
                insert_query = f"INSERT INTO source_master_tbl(source_no,source_name,country_iso,avg_tender,exe_run_by,exe_developer,develop_language,is_english,status,tender_url) VALUES('{source_no.strip()}','{source_name.strip()}','{contry_iso.strip()}','{avg_tender.strip()}','{exe_run_by.strip()}','{exe_developer.strip()}','{Devloped_language.strip()}','{is_english.strip()}','{status.strip()}','{tender_url.strip()}')"
                exe_DB_cursor.execute(insert_query)
                connection.commit()
                return HttpResponse('Data Added')
    return render(request, 'Add_source.html',test_data)


def source_details(request):
    exe_DB_cursor = connection.cursor()
    exe_DB_cursor.execute('SELECT source_name FROM exes_manage_db.source_master_tbl')
    data = exe_DB_cursor.fetchall()
    source_list = [list(tup) for tup in data]
    # print(source_list)
    data = {'source_list':source_list[0:100]}
    if request.method == 'POST':
        source_list_text = request.POST['source_list_text']
        source_list_text = source_list_text.replace(',',',,')
        selected_source_list = source_list_text.split(',,')
        # print(selected_source_list)
        source_list_count = []
        i = 0
        for source_name in selected_source_list:
            a = 0 
            while a == 0 :
                try:
                    exe_DB_cursor = connection.cursor()
                    exe_DB_cursor.execute(f"SELECT COUNT(*) AS source_count FROM `l2l_tenders_entry_tbl` WHERE source = '{str(source_name)}' AND DATE(added_on) = CURDATE()")
                    data = exe_DB_cursor.fetchone()
                    data_list = list(data)
                    print(f'{i}:{source_name}, {data_list[0]}')
                    test_list = [str(source_name),str(data_list[0])] # Multidimenstion Array
                    source_list_count.append(test_list)
                    i += 1
                    a = 1
                except Exception as e:
                    print(e)
                    connection.close()
                    time.sleep(2)
                    a = 0 
        return JsonResponse(source_list_count, safe=False)
    
        
    return render(request, 'source_details.html',data)

