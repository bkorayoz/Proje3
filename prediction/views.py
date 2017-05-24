from django.shortcuts import render
from datetime import date, timedelta
import datetime
import csv
from django.http import HttpResponse
from prediction.models import Data, Date_Group
from pprint import pprint
import xlsxwriter

def readData(request):
    if Data.objects.all().count() > 20:
         arrange()
         return HttpResponse("Calisiyo hocam devam et")
    else:
         Data.objects.all().delete()
         #pprint('readDataya girdik')
         with open("example.csv", newline = '') as f:
             reader = csv.reader(f)
             next(reader)
             
             for row in reader:
                temptime = datetime.datetime.strptime(row[0],'%d-%m-%Y').strftime('%Y-%m-%d')
                #pprint(str(temptime))
                newrow = Data(tarih = temptime, magaza = row[1], lokasyon = row[2], kod = row[3], urunAdi = row[4], anaGrup = row[5], altGrup = row[6], urunCesidi = row[7], miktar = row[8])
                newrow.save()
                
         arrange()
         #excelwrite()
    
         return HttpResponse("Calisiyo hocam devam et")
 
 
def arrange():
    Date_Group.objects.all().delete()
    book = xlsxwriter.Workbook('output.xlsx')
    hformat = book.add_format()
    hformat.set_align('center')
    hformat.set_align('vcenter')
    hformat.set_bold()

    format = book.add_format()
    format.set_align('center')
    format.set_align('vcenter')

    sheet1 = book.add_worksheet('Alinan Veriler')
    sheet2 = book.add_worksheet('Haftalik')
    sheet3 = book.add_worksheet('Aylik')
    
    sheet1.write(0,0,'DATE',hformat)
    sheet1.write(0,1,'35000212',hformat)
    sheet1.write(0,2,'31001045',hformat)
    sheet1.write(0,3,'35000313',hformat)
    sheet1.write(0,4,'31000368',hformat)
     
    urun = [35000212, 31001045, 35000313, 31000368]
    counter = 0
    haftac = 0;
    haftaici = [0] * 200
    haftasonu = [0] * 200
    for i in range(0, 4):
        if i==1:
            haftac = counter
        date = datetime.date(2016,5,2)
        j = 1
        dcount = 0
        while date < datetime.date(2017, 4, 17):
            dcount = dcount + 1
            #pprint("TARIH = " + str(date) + "  i = " + str(i))
            data = Data.objects.filter(tarih = date, kod = urun[i])
            
            if data.count() > 0:
                sum = 0
                for foo in data:
                    sum += foo.miktar
                    
                if i == 0:
                    sheet1.write(j,0,str(date),format)
                    
                sheet1.write(j,i+1,sum,format)
                j = j + 1
                newval = Date_Group(tarih = date, kod = urun[i], miktar = sum)
                newval.save()
                
            else:
                if i == 0:
                    sheet1.write(j,0,str(date),format)
                    
                sheet1.write(j,i+1,0,format)
                j += 1
            
            if i==0 or i==1:
                if (dcount % 7) == 0:
                    haftasonu[counter] = haftasonu[counter] + sum
                    haftasonu[counter] = haftasonu[counter] / 2
                    haftaici[counter] = haftaici[counter] / 5
                    sheet2.write(counter,0,counter+1,format)
                    sheet2.write(counter,1,haftaici[counter],format)
                    sheet2.write(counter,2,haftasonu[counter],format)
                    counter+=1
                elif dcount % 7 < 6:
                    haftaici[counter] = haftaici[counter] + sum
                else:
                    haftasonu[counter] = haftasonu[counter] + sum 
                
            date = date + timedelta(days = 1)
            
# haftalik
    # urun 1
    charthafta1 = book.add_chart({'type' : 'column'})
    charthafta1.add_series({
         'values': ['Haftalik', 0, 1, haftac-1, 1],
         'categories' : ['Haftalik', 0, 0, haftac-1, 0],
         'column' : {'color': 'blue'},
         'name' : 'hafta ici',
            })
    charthafta1.add_series({
         'values': ['Haftalik', 0, 2, haftac-1, 2],
         'column' : {'color': 'red'},
         'name' : 'hafta sonu',
            })
    charthafta1.set_x_axis({
    'name': 'Hafta',
    'num_font':  {'italic': True },
})
    charthafta1.set_title({
    'name': '1. Urun',
})
    charthafta1.set_size({'x_scale' : 3})
    sheet2.insert_chart('E1', charthafta1)
    
    # urun 2
    charthafta2 = book.add_chart({'type' : 'column'})
    charthafta2.add_series({
         'values': ['Haftalik', haftac, 1, counter-1, 1],
         'categories' : ['Haftalik', 0, 0, haftac-1, 0],
         'column' : {'color': 'blue'},
         'name' : 'hafta ici',
            })
    charthafta2.add_series({
         'values': ['Haftalik', haftac, 2, counter-1, 2],
         'column' : {'color': 'red'},
         'name' : 'hafta sonu',
            })
    charthafta2.set_title({
    'name': '2. Urun',
})
    charthafta2.set_x_axis({
    'name': 'Hafta',
    'num_font':  {'italic': True },
})
    charthafta2.set_size({'x_scale' : 3})
    sheet2.insert_chart('E19', charthafta2)
# haftalik

# aylik
    aygunsayar = 12 *[0]
    a1 = 12 *[0]
    a2 = 12 *[0]
    aylar = ["May", "Haz", "Tem", "Agu", "Eyl", "Eki" , "Kas", "Ara", "Oca", "Sub", "Mar", "Nis"]
    aycounter = 0
    tempcount = 0
    data = Date_Group.objects.values()
    for d in data:
        ay = d['tarih'].month
        if ay < 5:
            ay = ay + 7
        else:
            ay = ay - 5
            
        aygunsayar[ay] += 1
        
        if d['kod'] == 35000212:
            a1[ay] += d['miktar']
        elif d['kod'] == 31001045:
            a2[ay] += d['miktar']

    for i in range(0,12):
        a1[i] = a1[i] / aygunsayar[i]
        a2[i] = a2[i] / aygunsayar[i]
        
    sheet3.write_column('A1', aylar)
    sheet3.write_column('B1', a1)
    sheet3.write_column('C1', a2)
    
    chartay = book.add_chart({'type': 'column'})
    chartay.add_series({
        'values': ['Aylik', 0, 1, 11, 1],
         'categories' : ['Aylik', 0, 0, 11, 0],
         'column' : {'color': 'blue'},
         'name' : 'Urun 1',
        })
    
    chartay.add_series({
        'values': ['Aylik', 0, 2, 11, 2],
         'column' : {'color': 'red'},
         'name' : 'Urun 2',
        })
    chartay.set_size({'x_scale' : 2, 'y_scale' : 1.5})
    chartay.set_title({
    'name': '1 Gundeki Ortalama Satis Miktari',
})
    sheet3.insert_chart('D1', chartay)
# aylik
         
    chart = book.add_chart({'type': 'line'})
    chart.add_series({
         'values': ['Alinan Veriler', 1, 1, dcount-1, 1],
         'categories' : ['Alinan Veriler', 1, 0, dcount-1, 0],
         'line' : {'color': 'blue'},
         'name' : '1',
            })
    chart.add_series({
         'values': ['Alinan Veriler', 1, 2, dcount-1, 2],
         'line' : {'color': 'red'},
         'name' : '2',
            })
    chart.add_series({
         'values': ['Alinan Veriler', 1, 3, dcount-1, 3],
         'line' : {'color': 'yellow'},
         'name' : '3',
            })
    chart.add_series({
         'values': ['Alinan Veriler', 1, 4, dcount-1, 4],
         'line' : {'color': 'green'},
         'name' : '4',
            })
    
    chart.set_title({
    'name': 'Tum Veriler',
})
    chart.set_size({'x_scale' : 4, 'y_scale' : 2})
    sheet1.set_column(0, 0, 15)
    sheet1.insert_chart('F1', chart)
    
    book.close()

             
