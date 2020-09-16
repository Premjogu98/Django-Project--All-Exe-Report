from django.shortcuts import render
from django.http import HttpResponse
# Create your views here.
from django.db import connection
import pymysql.cursors
import sys, os
import time
import json
from django.http import JsonResponse
from datetime import datetime,timedelta 
import time
from datetime import datetime as datetime_obj
import re
import csv
from django.core.mail import send_mail
from django.conf import settings
# send email with html tags using this import
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags


while True:
    try:
        mycursor = connection.cursor()
        mycursor.execute("SELECT * FROM dms_country_tbl")
        Country_ISO_data = mycursor.fetchall()#  Inside Country_ISO_data variable --> [{'Code': 'AD', 'Country': 'ANDORRA '}, {'Code': 'AE', 'Country': 'UNITED ARAB EMIRATES '}]
        Country_ISO_data = list(Country_ISO_data)  # inside list multiple tuples like this [(1, 2), (3, 4), (5, 6)] 
        Country_ISO_data = [list(tup) for tup in Country_ISO_data]
        break
    except Exception as e:
        time.sleep(2)
        print(e)

while True:
    try:
        exe_DB_cursor = connection.cursor()
        exe_DB_cursor.execute("SELECT * FROM exe_developer_tbl")
        exe_developer_data = exe_DB_cursor.fetchall() # data is tuple next step tuple convert to list
        exe_developer_data = list(exe_developer_data)  # inside list multiple tuples like this [(1, 2), (3, 4), (5, 6)] 
        exe_developer_data = [list(tup) for tup in exe_developer_data] # using list comprehension  || convert list of tuples to list of list 
        break
    except Exception as e:
        time.sleep(2)
        print(e)

while True:
    try:
        exe_DB_cursor.execute("SELECT * FROM exe_runby_tbl")
        exe_runby_data = exe_DB_cursor.fetchall()
        exe_runby_data = list(exe_runby_data)
        exe_runby_data = [list(tup) for tup in exe_runby_data]
        break
    except Exception as e:
        time.sleep(2)
        print(e)

email_user_dic = {}
def query_fun(obj):
    exe_DB_cursor.execute(str(obj))
    data = exe_DB_cursor.fetchall()
    return data

def index(request):
    try:
        user_id  = request.COOKIES['EXEuserid']
        EXEusername  = request.COOKIES['EXEusername']
    except:
        return HttpResponse('<div style="background-color: #00e7ff; height: 10%; font-size: 20px;">&#128545<strong>Error!</strong> <label style="font-size: 25px;">Something Went Wrong Please LogIn Again <a href="Login-page">Click Here</a></label></div>')
    query = ''
    sourcename_list = []
    avg_count = 0
    if EXEusername == 'Admin':
        query = "SELECT * FROM `source_master_tbl`"
    else:
        query = f"SELECT * FROM `source_master_tbl` WHERE exe_run_by = '{str(user_id)}'"
    source_details = query_fun(query)
    for i in source_details:
        avg_count += int(i[4])
        sourcename_list.append(str(i[2]))
    sourcenames = str(sourcename_list).replace('[','').replace(']','')
    
    if EXEusername == 'Admin':
        query = "SELECT COUNT(*) FROM `l2l_tenders_entry_tbl` WHERE compulsary_qc = '1' AND DATE(added_on) = CURDATE() UNION ALL SELECT COUNT(*) FROM `l2l_tenders_entry_tbl` where DATE(added_on) = CURDATE()"
    else:
        query = f"""SELECT COUNT(*) FROM `l2l_tenders_entry_tbl` WHERE source IN({str(sourcenames)}) AND compulsary_qc = '1' AND DATE(added_on) = CURDATE() 
                UNION ALL
                SELECT COUNT(*) FROM `l2l_tenders_entry_tbl` WHERE source IN({str(sourcenames)}) AND DATE(added_on) = CURDATE()"""
    QC_and_total_tender_details = query_fun(query)

    if EXEusername == 'Admin':
        query = f"SELECT source FROM `l2l_tenders_entry_tbl` WHERE DATE(added_on) = CURDATE()"
    else:
        query = f"SELECT source FROM `l2l_tenders_entry_tbl` WHERE source IN({str(sourcenames)}) AND DATE(added_on) = CURDATE()"
    Zero_tender_details = query_fun(query)
    zero_tender_source_list = []
    for a in Zero_tender_details:
        if not a[0] in zero_tender_source_list:
            zero_tender_source_list.append(str(a[0]))
    count = int(len(sourcename_list)) - int(len(zero_tender_source_list))

    list_of_days_str = ''
    Graph_tender_count_str = ''
    Graph_qc_count_str = ''
    list_of_days = []
    i = 1
    while True:
        date = datetime.today() - timedelta(days=i)
        day = date.strftime('%d-%b')
        qday = date.strftime('%Y-%m-%d')
        week = date.strftime('%a')
        main = f'{str(day)} {week}'
        list_of_days.append(main)
        i +=1
        if not 'Sun' in main:
            list_of_days_str += f'{main},'
            if EXEusername == 'Admin':
                query = f"""SELECT count(*) FROM `l2l_tenders_entry_tbl` WHERE DATE(added_on) = '{str(qday)}'
                        UNION ALL
                        SELECT COUNT(*) FROM `l2l_tenders_entry_tbl` WHERE compulsary_qc = '1' AND DATE(added_on) = '{str(qday)}'"""
            else:
                query = f"""SELECT count(*) FROM `l2l_tenders_entry_tbl` WHERE source IN({str(sourcenames)}) AND DATE(added_on) = '{str(qday)}'
                        UNION ALL
                        SELECT COUNT(*) FROM `l2l_tenders_entry_tbl` WHERE source IN({str(sourcenames)}) AND compulsary_qc = '1' AND DATE(added_on) = '{str(qday)}'"""
            Graph_tender_count = query_fun(query)
            Graph_tender_count_str += f'{Graph_tender_count[0][0]},'
            Graph_qc_count_str += f'{Graph_tender_count[1][0]},'
        if i>7:
            break
    list_of_days_str = list_of_days_str.rstrip(',')
    Graph_tender_count_str = Graph_tender_count_str.rstrip(',')
    Graph_qc_count_str = Graph_qc_count_str.rstrip(',')
    # print(Graph_tender_count)
    print(Graph_tender_count_str)
    print(Graph_qc_count_str)
    detail_dic = {'total_source': len(source_details), 'qc_count':QC_and_total_tender_details[0][0],'total_tender_count' : QC_and_total_tender_details[1][0],'avg_count' : avg_count,'zero_tender_count' : count ,'list_of_days':list_of_days_str,'Graph_tender_count_str':Graph_tender_count_str,'Graph_qc_count_str': Graph_qc_count_str}
    return render(request, 'home.html',detail_dic)
    # return render(request, 'home.html')

def source_list(request):
    try:
        user_id  = request.COOKIES['EXEuserid']
        EXEusername  = request.COOKIES['EXEusername']
    except:
        return HttpResponse('<div style="background-color: #00e7ff; height: 10%; font-size: 20px;">&#128545<strong>Error!</strong> <label style="font-size: 25px;">Something Went Wrong Please LogIn Again <a href="Login-page">Click Here</a></label></div>')

    if EXEusername == 'Admin':
        exe_DB_cursor.execute("""SELECT sm.id,sm.source_no,sm.source_name,sm.tender_url,er.user_name AS EXE_RunBy,ed.developer_name AS Developer FROM `source_master_tbl` sm
                            INNER JOIN `exe_developer_tbl` ed ON sm.exe_developer = ed.developer_id
                            INNER JOIN `exe_runby_tbl` er ON sm.exe_run_by = er.user_id order by sm.id ASC""")
    else:
        exe_DB_cursor.execute(f"""SELECT sm.id,sm.source_no,sm.source_name,sm.tender_url,er.user_name AS EXE_RunBy,ed.developer_name AS Developer FROM `source_master_tbl` sm
                            INNER JOIN `exe_developer_tbl` ed ON sm.exe_developer = ed.developer_id
                            INNER JOIN `exe_runby_tbl` er ON sm.exe_run_by = er.user_id WHERE er.user_id = '{str(user_id)}' order by sm.id ASC""")

    source_data_list = exe_DB_cursor.fetchall()
    source_data_list = list(source_data_list)
    source_data_list = [list(tup) for tup in source_data_list]
    # print(exe_runby_data)
    source_details = {'source_data_list': source_data_list,'exe_runby_list':exe_runby_data,'Country_ISO_list':Country_ISO_data,'exe_developer_list': exe_developer_data,}
    return render(request, 'source_list.html',source_details)
    
def loadmodel_data(request):
    if request.method == 'POST':
        id = request.POST['id']
        # print(id)
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
        
        
        
        now = datetime_obj.now()
        # time = now.strftime("%H:%M:%S")
        # main_update_date = update_date + " " + time
        update_date_timestamp = now.strftime('%Y-%m-%d %H:%M:%S')
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
    try:
        user_id  = request.COOKIES['EXEuserid']
        EXEusername  = request.COOKIES['EXEusername']
    except:
        return HttpResponse('<div style="background-color: #00e7ff; height: 10%; font-size: 20px;">&#128545<strong>Error!</strong> <label style="font-size: 25px;">Something Went Wrong Please LogIn Again <a href="Login-page">Click Here</a></label></div>')

    exe_DB_cursor = connection.cursor()
    if EXEusername != 'Admin':
        exe_DB_cursor.execute(f'SELECT source_name FROM exes_manage_db.source_master_tbl WHERE exe_run_by="{str(user_id)}"')
    else:
        exe_DB_cursor.execute(f'SELECT source_name FROM exes_manage_db.source_master_tbl')
    data = exe_DB_cursor.fetchall()
    source_list = [list(tup) for tup in data]
    # print(source_list)
    data = {'source_list':source_list}
    
    if request.method == 'POST':
        source_list_text = request.POST['source_list_text']
        drop_from_date = request.POST['drop_from_date']
        drop_to_date = request.POST['drop_to_date']
        top_from_date = request.POST['top_from_date']
        top_to_date = request.POST['top_to_date']
        from_date = ''
        to_date = ''
        if drop_from_date == '' and drop_to_date == '':
            from_date = top_from_date
            to_date = top_to_date
        elif top_from_date == '' and top_to_date == '':
            from_date = drop_from_date
            to_date = drop_to_date
        print(source_list_text)
        print(from_date)
        print(to_date)
        where_condition = ""
        if source_list_text != '':
            source_list_text = source_list_text.replace(',',',,')
            selected_source_list = source_list_text.split(',,')
            source_list = str(selected_source_list).replace('[','').replace(']','')
            where_condition = f"WHERE sm.source_name IN({source_list}) ORDER BY sm.id ASC"
        else:
            if EXEusername != 'Admin':
                where_condition = f"WHERE er.user_id = '{str(user_id)}' order BY sm.id ASC"
            else:
                where_condition = "order BY sm.id ASC"
        query = f"""SELECT sm.source_name,er.user_name AS EXE_RunBy,ed.developer_name AS Developer FROM `source_master_tbl` sm
                                    INNER JOIN `exe_developer_tbl` ed ON sm.exe_developer = ed.developer_id
                                    INNER JOIN `exe_runby_tbl` er ON sm.exe_run_by = er.user_id {where_condition}"""
        data = query_fun(query)
        source_data_list = list(data)
        source_data_list = [list(tup) for tup in source_data_list]

        if from_date != "" and to_date != "":
            table_html = ''
            table_th = ""
            source_name_with_count = ''
            main_total_count_list = []
            all_total_tr = ''
            all_total_count = 0
            from_date_obj = datetime_obj.strptime(str(from_date), '%Y-%m-%d')
            to_date_datetime_obj = datetime_obj.strptime(str(to_date), '%Y-%m-%d')
            diff_date = to_date_datetime_obj - from_date_obj
            diff_date = diff_date.days

            for date in range(int(diff_date)+1):
                date_month = from_date_obj.strftime("%d-%b")
                table_th += f"<th>{str(date_month)}</th>"
                from_date_obj = from_date_obj + timedelta(days=1)
            
            for source_name in source_data_list:
                m_count_td  = ''
                m_source_count = 0
                from_date_obj = datetime_obj.strptime(str(from_date), '%Y-%m-%d') 
                total_count_list = []
                for date in range(int(diff_date)+1):
                    main_date = from_date_obj.strftime("%Y-%m-%d")
                    a = 0 
                    while a == 0 :
                        try:
                            exe_DB_cursor = connection.cursor()
                            exe_DB_cursor.execute(f"SELECT COUNT(*) AS source_count FROM `l2l_tenders_entry_tbl` WHERE source = '{str(source_name[0]).strip()}' AND DATE(added_on) = '{str(main_date).strip()}'")
                            data = exe_DB_cursor.fetchone()
                            data_list = list(data)
                            total_count_list.append(f'{data_list[0]}')
                            m_count_td += f'<td>{data_list[0]}</td>'
                            m_source_count += int(data_list[0])
                            a = 1
                        except Exception as e:
                            print(e)
                            connection.close()
                            time.sleep(2)
                            a = 0 
                    print(f'Done: {source_name}')
                    from_date_obj = from_date_obj + timedelta(days=1)
                main_total_count_list.append(total_count_list)
                all_total_count += m_source_count
                if m_source_count != 0:
                    source_name_with_count += f'<tr><td>{str(source_name[0])}</td><td>{str(source_name[1])}</td><td>{str(source_name[2])}</td>{m_count_td}<td>{m_source_count}</td></tr>'
                else:
                    source_name_with_count += f'<tr style="color: white;background: #ff2f2f;"><td>{str(source_name[0])}</td><td>{str(source_name[1])}</td><td>{str(source_name[2])}</td>{m_count_td}<td>{m_source_count}</td></tr>'
                    
            # print(main_total_count_list)
            index_no = 0
            for date in range(int(diff_date)+1):
                total_count = 0
                for count_list in main_total_count_list:
                    total_count += int(count_list[index_no])
                all_total_tr += f'<td>{str(total_count)}</td>'
                index_no +=1

            # MOST IMP NOTE When You change your html table tag then you need also do some changes on  funtion(Export_csv)
            
            table_html =  f"""<div class="d-flex justify-content-start"><h4 class="source-list-h">Source Details From: {from_date} To: {to_date}</h4></div><table id="main_table" class="table table-hover" style="text-align: left; margin-top: 25px;>
                        <thead>
                            <tr style="background: #00e7ff;">
                                <th>Source Name</th>
                                <th>EXE Run By</th>
                                <th>EXE Developer</th>
                                {str(table_th)}
                                <th>Total</th> 
                            </tr>
                        </thead>
                        <tbody>
                            {str(source_name_with_count)}
                            <tr class="Total"><td>Total</td><td></td><td></td>{str(all_total_tr)}<td>{str(all_total_count)}</td></tr>
                        </tbody>
                    </table>"""
            return JsonResponse(str(table_html), safe=False)
        
        else :
            source_name_with_count = ""
            main_source_total = 0
            main_total = 0
            now = datetime_obj.now()
            main_date = now.strftime("%d-%B-%Y")
            for source_name in source_data_list:
                m_count_td  = ''
                m_source_count = 0
                a = 0 
                while a == 0 :
                    try:
                        exe_DB_cursor = connection.cursor()
                        exe_DB_cursor.execute(f"SELECT COUNT(*) AS source_count FROM `l2l_tenders_entry_tbl` WHERE source = '{str(source_name[0]).strip()}' AND DATE(added_on) = CURDATE()")
                        data = exe_DB_cursor.fetchone()
                        data_list = list(data)
                        m_count_td += f'<td>{data_list[0]}</td>'
                        m_source_count += int(data_list[0])
                        main_source_total += m_source_count
                        main_total += m_source_count
                        a = 1
                    except Exception as e:
                        print(e)
                        connection.close()
                        time.sleep(2)
                        a = 0 
                print(f'Done: {source_name}')
                if m_source_count != 0:
                    source_name_with_count += f'<tr><td>{str(source_name[0])}</td><td>{str(source_name[1])}</td><td>{str(source_name[2])}</td>{m_count_td}<td>{m_source_count}</td></tr>'
                else:
                    source_name_with_count += f'<tr style="color: white;background: #ff2f2f;"><td>{str(source_name[0])}</td><td>{str(source_name[1])}</td><td>{str(source_name[2])}</td>{m_count_td}<td>{m_source_count}</td></tr>'
                    
            
            # MOST IMP NOTE When You change your html table tag then you need also do some changes on  funtion(Export_csv)

            table_html =  f"""<div class="d-flex justify-content-start"><h4 class="source-list-h"> Source Details Of Current Date: {main_date}</h4></div><table id="main_table" class="table table-hover" style="text-align: left; margin-top: 25px;">
                        <thead>
                            <tr>
                                <th>Source Name</th>
                                <th>EXE Run By</th>
                                <th>EXE Developer</th>
                                <th>{str(main_date)}</th> 
                                <th>Total</th>
                            </tr>
                        </thead>
                        <tbody>
                            {str(source_name_with_count)}
                            <tr class="Total"><td>Total</td><td></td><td></td><td>{str(main_source_total)}</td><td>{str(main_total)}</td></tr>
                        </tbody>
                    </table>"""
            
            return JsonResponse(str(table_html), safe=False)
    
        
    return render(request, 'source_details.html',data)

def Export_csv(request):
    if request.method == 'POST':
        now = datetime_obj.now()
        main_date = now.strftime("%d%m%Y%H%M")
        response = HttpResponse(content_type='text/csv')
        main_table = request.POST['html_table_input']
        main_table = main_table.replace('\n',' ')
        main_table = re.sub("\s+" , " ", main_table)
        Th_list = re.findall(r"(?<=<th>).*?(?=</th>)", main_table)
        tbody_text = main_table.partition("<tbody>")[2].partition('<tr class="Total">')[0].replace('style="color: white;background: #ff2f2f;"','').replace('<tr >','<tr>')
        total_text = main_table.partition('<tr class="Total">')[2].partition('</tr>')[0].strip()
        tbody_text = tbody_text.replace('<td></td>','') 
        td_list = tbody_text.split('<tr>')
        writer = csv.writer(response)
        writer.writerow(Th_list)
        for td in td_list:
            td = td.replace('<td>','').replace("<a href='","").replace("' target='_blank'>Click Here</a>",'')
            td = td.split('</td>')
            del td[-1]
            print(td)
            writer.writerow(td)
        total_text =  total_text.replace('<td>','')
        total_list = total_text.split('</td>')
        del total_list[-1]
        print(total_list)
        writer.writerow(total_list)
        response['Content-Disposition'] = f'attachment; filename="sourceDetails{main_date}.csv"'
        return response

def zero_count(request):
    try:
        user_id  = request.COOKIES['EXEuserid']
        EXEusername  = request.COOKIES['EXEusername']
    except:
        return HttpResponse('<div style="background-color: #00e7ff; height: 10%; font-size: 20px;">&#128545<strong>Error!</strong> <label style="font-size: 25px;">Something Went Wrong Please LogIn Again <a href="Login-page">HomePage</a></label></div>')

    if request.method == 'POST':
        Category = request.POST['Category']
        from_date = request.POST['from_date']
        to_date = request.POST['to_date']
        where_query = ''
        if EXEusername != "Admin":
            if Category == 'IN':
                where_query = f"WHERE sm.country_iso = 'IN' AND er.user_id = '{str(user_id)}'"
            elif Category == 'none-in':
                where_query = f"WHERE sm.country_iso <> 'IN' AND er.user_id = '{str(user_id)}'"
            elif Category == 'all':
                where_query = f"WHERE er.user_id = '{str(user_id)}'"
        else:
            if Category == 'IN':
                where_query = f"WHERE sm.country_iso = 'IN'"
            elif Category == 'none-in':
                where_query = f"WHERE sm.country_iso <> 'IN'"
            elif Category == 'all':
                where_query = ""
        
        a = 0 
        while a == 0:
            try:
                exe_DB_cursor = connection.cursor()
                exe_DB_cursor.execute(f"""SELECT sm.source_name,sm.country_iso,sm.avg_tender,CASE sm.status WHEN '1' THEN 'Working' WHEN '2' THEN 'GTS Maintenance' WHEN '3' THEN 'Website Issue' WHEN '4' THEN 'GTS Stopped' ELSE '-' END AS `status`,
                                        sm.tender_url,er.user_name AS EXE_RunBy,ed.developer_name AS Developer FROM `source_master_tbl` sm
                                        INNER JOIN `exe_developer_tbl` ed ON sm.exe_developer = ed.developer_id
                                        INNER JOIN `exe_runby_tbl` er ON sm.exe_run_by = er.user_id
                                        {str(where_query)}
                                        ORDER BY avg_tender DESC""")
                a = 1
            except Exception as e:
                print(e)
                connection.close()
                time.sleep(2)
                a = 0

        data = exe_DB_cursor.fetchall()
        
        source_list = [list(tup) for tup in data]
        now = datetime_obj.now()
        main_date = now.strftime("%Y-%m-%d")
        print(f'Category : {Category}')
        print(f'from_date : {from_date}')
        print(f'from_date : {to_date}')

        main_Category = ''
        if Category == 'all':
            main_Category = 'All'
        elif Category == 'in':
            main_Category = 'India'
        elif Category == 'none-in':
            main_Category = 'Other Than India'


        if from_date != "" and to_date != "":
            email_user_dic["date"] = f'<h3 style="color:red">{main_Category} Zero Tender Report From: <b>{from_date}</b> To: <b>{to_date}</b></h3>'
        elif from_date != "" and to_date == "":
            email_user_dic["date"] = f'<h3 style="color:red">{main_Category} Zero Tender Report From: <b>{from_date}</b> To: <b>{main_date}</b></h3>'
        else:
            email_user_dic["date"] = f'<h3 style="color:red">{main_Category} Zero Tender Report Date: <b>{main_date}</b></h3>'
        for user in exe_runby_data:
            email_user_dic[f"{user[1]}"] = [f"{str(user[2])}"]
        source_detail_tr = ""
        for source in source_list:
            if from_date != "" and to_date != "":
                exe_DB_cursor.execute(f"SELECT COUNT(*) AS source_count FROM `l2l_tenders_entry_tbl` WHERE source = '{str(source[0])}' AND (DATE(added_on) BETWEEN '{str(from_date)}' AND '{str(to_date)}')")
                data = exe_DB_cursor.fetchone()
                data_list = list(data)
                if data_list[0] == 0:
                    tr = f"<tr><td>{str(source[0])}</td><td>{str(source[5])}</td><td>{str(source[6])}</td><td>{str(source[2])}</td><td>{str(source[3])}</td><td><a href='{str(source[4])}' target='_blank'>Click Here</a></td></tr>"
                    source_detail_tr += tr
                    email_user_dic[f'{str(source[5])}'].append(str(tr))
            elif from_date != "" and to_date == "":
                exe_DB_cursor.execute(f"SELECT COUNT(*) AS source_count FROM `l2l_tenders_entry_tbl` WHERE source = '{str(source[0])}' AND DATE(added_on) >= '{str(from_date)}'")
                data = exe_DB_cursor.fetchone()
                data_list = list(data)
                if data_list[0] == 0:
                    tr = f"<tr><td>{str(source[0])}</td><td>{str(source[5])}</td><td>{str(source[6])}</td><td>{str(source[2])}</td><td>{str(source[3])}</td><td><a href='{str(source[4])}' target='_blank'>Click Here</a></td></tr>"
                    source_detail_tr += tr
                    email_user_dic[f'{str(source[5])}'].append(str(tr))
            elif from_date == "" and to_date == "":
                exe_DB_cursor.execute(f"SELECT COUNT(*) AS source_count FROM `l2l_tenders_entry_tbl` WHERE source = '{str(source[0])}' AND DATE(added_on) = CURDATE()")
                data = exe_DB_cursor.fetchone()
                data_list = list(data)
                if data_list[0] == 0:
                    tr = f"<tr><td>{str(source[0])}</td><td>{str(source[5])}</td><td>{str(source[6])}</td><td>{str(source[2])}</td><td>{str(source[3])}</td><td><a href='{str(source[4])}' target='_blank'>Click Here</a></td></tr>"
                    source_detail_tr += tr
                    email_user_dic[f'{str(source[5])}'].append(str(tr))
            #=============================================================================================================================
            
            print(f'Done: {source[0]}')
        # print(email_user_dic)
        table_html =  f""" <table id="main_table" class="table table-hover" style="text-align: left; margin-top: 25px;">
                            <thead>
                                <tr>
                                    <th>Source Name</th>
                                    <th>EXE Run By</th>
                                    <th>EXE Developer</th>
                                    <th>Tender AVG</th>
                                    <th>Status</th>
                                    <th>Tender Link</th>
                                </tr>
                            </thead>
                            <tbody>
                                {str(source_detail_tr)}
                            </tbody>
                        </table>"""
        return JsonResponse(table_html, safe=False)

    return render(request, 'Zero_count_page.html')

def Send_email(request):
    if request.method == 'POST':
        html_table_input = request.POST['html_table_input']
        # send_Email_dic = send_Email_dic.replace("'",'"').replace('href=""',"href=''").replace('target="_blank"',"target='_blank'").replace('style="color:red"',"style='color:red'")
        # print(email_user_dic)
        # Email_dic = json.loads(f'{send_Email_dic}')
        if html_table_input == '':
            return HttpResponse('No Data Found')
        try:
            H3_date = email_user_dic.get('date')
        except:
            return HttpResponse('Something Wentwrong on Send_email function (email_user_dic)')
        del email_user_dic['date']
        is_there_any_email = 0
        for user_tr_list in email_user_dic.values():
            total_tr = ''
            user_email_id = user_tr_list[0]
            # print(user_email_id)
            del user_tr_list[0]
            for tr in user_tr_list:
                total_tr += str(tr)
                # print(tr)
            if total_tr != '':
                total_tr = total_tr.replace("'",'"').replace('<td>','<td style="border: 1px solid black; border-collapse: collapse;">').replace(' style="color: white;background: #ff2f2f;"','')
                # 'r' or 'R'. Python raw string treats backslash (\) as a literal character.
                table = f"""{str(H3_date)}<table style="width:100%; border: 1px solid black; border-collapse: collapse;">
                                <thead style="text-align: left;">
                                    <tr>
                                        <th style="border: 1px solid black; border-collapse: collapse;">Source Name</th>
                                        <th style="border: 1px solid black; border-collapse: collapse;">EXE Run By</th>
                                        <th style="border: 1px solid black; border-collapse: collapse;">EXE Developer</th>
                                        <th style="border: 1px solid black; border-collapse: collapse;">Tender AVG</th>
                                        <th style="border: 1px solid black; border-collapse: collapse;">Status</th>
                                        <th style="border: 1px solid black; border-collapse: collapse;">Tender Link</th>
                                    </tr>
                                </thead>
                                <tbody style="text-align: left;">{total_tr}
                                </tbody>
                                </table>"""
                # print(table)
                # html_content = render_to_string('email_template.html',{'title':'Test Email','content': str(total_tr)})
                # text_content = strip_tags(html_content)
                try:
                    email = EmailMultiAlternatives(
                        'Zero Tender Report',
                        'Zero Tender Report',
                        settings.EMAIL_HOST_USER,
                        [f'{user_email_id}']
                    )
                    email.attach_alternative(table,'text/html')
                    email.send()
                except:
                    return HttpResponse('Email Failed')
                is_there_any_email +=1
            else:
                is_there_any_email +=0
        if is_there_any_email != 0:
            return HttpResponse('Email Send Successfully!!!!')
        else:
            return HttpResponse('There Is No Data Found ')
     
def QC_Detail(request):
    try:
        user_id  = request.COOKIES['EXEuserid']
        EXEusername  = request.COOKIES['EXEusername']
    except:
        return HttpResponse('<div style="background-color: #00e7ff; height: 10%; font-size: 20px;">&#128545<strong>Error!</strong> <label style="font-size: 25px;">Something Went Wrong Please LogIn Again <a href="Login-page">Click Here</a></label></div>')

    exe_DB_cursor = connection.cursor()
    if EXEusername != 'Admin':
        exe_DB_cursor.execute(f'SELECT source_name FROM exes_manage_db.source_master_tbl WHERE exe_run_by="{str(user_id)}"')
    else:
        exe_DB_cursor.execute(f'SELECT source_name FROM exes_manage_db.source_master_tbl')
    data = exe_DB_cursor.fetchall()
    source_list = [list(tup) for tup in data]
    # print(source_list)
    data = {'source_list':source_list}
    
    if request.method == 'POST':
        source_list_text = request.POST['source_list_text']
        drop_from_date = request.POST['drop_from_date']
        drop_to_date = request.POST['drop_to_date']
        top_from_date = request.POST['top_from_date']
        top_to_date = request.POST['top_to_date']
        from_date = ''
        to_date = ''
        if drop_from_date == '' and drop_to_date == '':
            from_date = top_from_date
            to_date = top_to_date
        elif top_from_date == '' and top_to_date == '':
            from_date = drop_from_date
            to_date = drop_to_date
        # print(source_list_text)
        where_condition = ''
        if source_list_text != '':
            source_list_text = source_list_text.replace(',',',,')
            selected_source_list = source_list_text.split(',,')
            source_list = str(selected_source_list).replace('[','').replace(']','')
            where_condition = f'WHERE sm.source_name IN({source_list}) ORDER BY sm.id ASC'
        else:
            if EXEusername != 'Admin':
                 where_condition = f"WHERE er.user_id = '{str(user_id)}' order BY sm.id ASC"
            else:
                where_condition = 'order BY sm.id ASC'
        query = f"""SELECT sm.source_name,er.user_name AS EXE_RunBy,ed.developer_name AS Developer FROM `source_master_tbl` sm
                                    INNER JOIN `exe_developer_tbl` ed ON sm.exe_developer = ed.developer_id
                                    INNER JOIN `exe_runby_tbl` er ON sm.exe_run_by = er.user_id {where_condition}"""
        data = query_fun(query)
        source_data_list = list(data)
        source_data_list = [list(tup) for tup in source_data_list]

        # print(source_data_list)
        now = datetime_obj.now()
        main_date = now.strftime("%Y-%m-%d")
        if from_date != "" and to_date != "":
            email_user_dic["date"] = f'<h3 style="color:red">QC Report From: <b>{from_date}</b> To: <b>{to_date}</b></h3>'
        elif from_date != "" and to_date == "":
            email_user_dic["date"] = f'<h3 style="color:red">QC Report From: <b>{from_date}</b> To: <b>{main_date}</b></h3>'
        else:
            email_user_dic["date"] = f'<h3 style="color:red">QC Report Date: <b>{main_date}</b></h3>'
        for user in exe_runby_data:
            email_user_dic[f"{user[1]}"] = [f"{str(user[2])}"]

        if from_date != "" and to_date != "":
            table_html = ''
            table_th = ""
            source_name_with_count = ''
            main_total_count_list = []
            all_total_tr = ''
            all_total_count = 0
            from_date_obj = datetime_obj.strptime(str(from_date), '%Y-%m-%d')
            to_date_datetime_obj = datetime_obj.strptime(str(to_date), '%Y-%m-%d')
            diff_date = to_date_datetime_obj - from_date_obj
            diff_date = diff_date.days

            for date in range(int(diff_date)+1):
                date_month = from_date_obj.strftime("%d-%b")
                table_th += f"<th>{str(date_month)}</th>"
                from_date_obj = from_date_obj + timedelta(days=1)
            
            for source_name in source_data_list:
                m_count_td  = ''
                m_source_count = 0
                from_date_obj = datetime_obj.strptime(str(from_date), '%Y-%m-%d') 
                total_count_list = []
                for date in range(int(diff_date)+1):
                    main_date = from_date_obj.strftime("%Y-%m-%d")
                    a = 0 
                    while a == 0 :
                        try:
                            exe_DB_cursor = connection.cursor()
                            exe_DB_cursor.execute(f"SELECT COUNT(*) AS source_count FROM `l2l_tenders_entry_tbl` WHERE source = '{str(source_name[0]).strip()}' AND compulsary_qc = '1' AND DATE(added_on) = '{str(main_date).strip()}'")
                            data = exe_DB_cursor.fetchone()
                            data_list = list(data)
                            total_count_list.append(f'{data_list[0]}')
                            m_count_td += f'<td>{data_list[0]}</td>'
                            m_source_count += int(data_list[0])
                            a = 1
                        except Exception as e:
                            print(e)
                            connection.close()
                            time.sleep(2)
                            a = 0 
                    print(f'Done: {source_name}')
                    from_date_obj = from_date_obj + timedelta(days=1)
                main_total_count_list.append(total_count_list)
                all_total_count += m_source_count
                if m_source_count != 0:
                    tr = f'<tr><td>{str(source_name[0])}</td><td>{str(source_name[1])}</td><td>{str(source_name[2])}</td>{m_count_td}<td>{m_source_count}</td></tr>'
                    email_user_dic[f'{str(source_name[1])}'].append(str(tr))
                    source_name_with_count += tr
                    
            # print(main_total_count_list)
            index_no = 0
            for date in range(int(diff_date)+1):
                total_count = 0
                for count_list in main_total_count_list:
                    total_count += int(count_list[index_no])
                all_total_tr += f'<td>{str(total_count)}</td>'
                index_no +=1

            # MOST IMP NOTE When You change your html table tag then you need also do some changes on  funtion(Export_csv)
            
            table_html =  f"""<div class="d-flex justify-content-start"><h4 class="source-list-h">QC Report From: {from_date} To: {to_date}</h4></div><table id="main_table" class="table table-hover" style="text-align: left; margin-top: 25px;>
                        <thead>
                            <tr style="background: #00e7ff;">
                                <th>Source Name</th>
                                <th>EXE Run By</th>
                                <th>EXE Developer</th>
                                {str(table_th)}
                                <th>Total</th> 
                            </tr>
                        </thead>
                        <tbody>
                            {str(source_name_with_count)}
                            <tr class="Total"><td>Total</td><td></td><td></td>{str(all_total_tr)}<td>{str(all_total_count)}</td></tr>
                        </tbody>
                    </table>"""
            return JsonResponse(str(table_html), safe=False)
        
        else :
            source_name_with_count = ""
            main_source_total = 0
            main_total = 0
            now = datetime_obj.now()
            main_date = now.strftime("%d-%B-%Y")
            for source_name in source_data_list:
                m_count_td  = ''
                m_source_count = 0
                a = 0 
                while a == 0 :
                    try:
                        exe_DB_cursor = connection.cursor()
                        exe_DB_cursor.execute(f"SELECT COUNT(*) AS source_count FROM `l2l_tenders_entry_tbl` WHERE source = '{str(source_name[0]).strip()}' AND compulsary_qc = '1' AND DATE(added_on) = CURDATE()")
                        data = exe_DB_cursor.fetchone()
                        data_list = list(data)
                        m_count_td += f'<td>{data_list[0]}</td>'
                        m_source_count += int(data_list[0])
                        main_source_total += m_source_count
                        main_total += m_source_count
                        a = 1
                    except Exception as e:
                        print(e)
                        connection.close()
                        time.sleep(2)
                        a = 0 
                print(f'Done: {source_name}')
                if m_source_count != 0:
                    tr = f'<tr><td>{str(source_name[0])}</td><td>{str(source_name[1])}</td><td>{str(source_name[2])}</td>{m_count_td}<td>{m_source_count}</td></tr>'
                    email_user_dic[f'{str(source_name[1])}'].append(str(tr))
                    source_name_with_count += tr
            
            # MOST IMP NOTE When You change your html table tag then you need also do some changes on  funtion(Export_csv)

            table_html =  f"""<div class="d-flex justify-content-start"><h4 class="source-list-h"> QC Report Of Current Date: {main_date}</h4></div><table id="main_table" class="table table-hover" style="text-align: left; margin-top: 25px;">
                        <thead>
                            <tr>
                                <th>Source Name</th>
                                <th>EXE Run By</th>
                                <th>EXE Developer</th>
                                <th>{str(main_date)}</th> 
                                <th>Total</th>
                            </tr>
                        </thead>
                        <tbody>
                            {str(source_name_with_count)}
                            <tr class="Total"><td>Total</td><td></td><td></td><td>{str(main_source_total)}</td><td>{str(main_total)}</td></tr>
                        </tbody>
                    </table>"""
            
            return JsonResponse(str(table_html), safe=False)
    return render(request, 'QC_Detail.html',data)

def Login_page(request):
    
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        print('Username: ',username)
        print('Password: ',password)
        exe_DB_cursor.execute(f"SELECT user_id,user_name,email_id,PASSWORD FROM `exe_runby_tbl` WHERE email_id='{str(username)}' AND PASSWORD = '{str(password)}'")
        data = exe_DB_cursor.fetchall()
        source_list = [list(tup) for tup in data]
        print(source_list)
        if len(source_list) != 0:
            exeuser_id = str(source_list[0][0])
            exeuser_name = str(source_list[0][1])
            response = HttpResponse("User Login")
            response.delete_cookie('EXEusername')
            response.delete_cookie('EXEuserid')
            response.set_cookie('EXEusername', exeuser_name,max_age=1200)
            response.set_cookie('EXEuserid', exeuser_id,max_age=1200)
            return response
        else:
            return HttpResponse("Error")
    try:
        test = request.COOKIES['EXEusername']
        print(test)
        return HttpResponse('<div class="alert alert-danger alert-dismissible" style="background-color: #00e7ff; height: 10%; font-size: 20px;">&#128545<strong>Error!</strong> <label style="font-size: 25px;">You Are Already Login Please Logout First Then Log In Again <a href="homepage">HomePage</a></label></div>')
    except: 
        return render(request, 'login_page.html')

def Logout(request):
    response = HttpResponse("""<div style="background-color: #00e7ff; font-size: 21px;"><label style="color: black; font-size: 32px;">TendersOnTime </label>If You Wants To Login Again Then <a href="Login-page"> Click Here</a></div>""")
    response.delete_cookie('EXEusername')
    return response