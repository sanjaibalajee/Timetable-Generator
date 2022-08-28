import os
from flask import Flask, render_template, request, redirect, send_file, send_from_directory
from itertools import permutations
import csv
import random
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import dataframe_image as dfi
import six
from fpdf import FPDF

app = Flask(__name__)

class TimeTable(dict):
    def __init__(self,name,slot_filled=False):
        self.name = name
        self.filled = {}
        self.slot_filled = slot_filled
        self.days = ['monday', 'tuesday', 'wednesday', 'thursday',  'friday']
        self.create_tt()

    def create_tt(self):
        for i in self.days:
            self[i] = {1: '', 2: '', 3: '', 4: '', 5: 'LUNCH', 6: '', 7: '', 8: ''}
            self.filled[i] = {1: self.slot_filled, 2: self.slot_filled, 3: self.slot_filled, 4: self.slot_filled, 5: True, 6: self.slot_filled, 7: self.slot_filled, 8: self.slot_filled}

def digit(l):
    for i in range(len(l)):
        if l[i].isdigit():
            l[i]=int(l[i])
    return l

all_classrooms = {}
all_faculty = {}
data=[]
temp=[]
teachers = []
class_timetables = {'3a':'','3b':'','5a':'','5b':'','7a':'','7b':''}

with open("new.csv",'r') as csvfile:
    reader=csv.reader(csvfile)
    next(reader)
    for lines in reader:
        digit(lines)
        data.append(tuple(lines))
        teachers.append(lines[3]) if lines[3] not in teachers else None
        all_faculty[lines[3]] = TimeTable(lines[3])
    for i in range(len(data)): #3A
        if (data[i][1])=='3a':
            temp.append(data[i])
        all_classrooms['3a']=tuple(temp)
    temp=[]
    for i in range(len(data)): #3B
        if data[i][1]=='3b':
            temp.append(data[i])
        all_classrooms['3b']=tuple(temp)
    temp=[]
    for i in range(len(data)): #5A
        if data[i][1]=='5a':
            temp.append(data[i])
        all_classrooms['5a']=tuple(temp)
    temp=[]
    for i in range(len(data)): #5B
        if data[i][1]=='5b':
            temp.append(data[i])
        all_classrooms['5b']=tuple(temp)
    temp=[]
    for i in range(len(data)): #7A
        if data[i][1]=='7a':
            temp.append(data[i])
        all_classrooms['7a']=tuple(temp)
    temp=[]
    for i in range(len(data)): #7B
        if data[i][1]=='7b':
            temp.append(data[i])
        all_classrooms['7b']=tuple(temp)

def generate_tt(class_name,tt,subjects):
    not_generate = False
    global all_faculty
    global combs
    subjects = list(subjects)
    remaining_subjects = []
    filled_labs = ['monday','tuesday','thursday']
    lab_times = [1, 2, 6]
    
    #generating labs
    for i in subjects:
        hours_left = i[4]
        flag = False
        temp = [i[1],i[0],i[2],i[3],"Lab"] if i[-1] == 1 else [i[1],i[0],i[2],i[3],"Theory"]
        if i[-1] == 1:
            course_table.append(temp) if temp not in course_table else None
            while hours_left > 0:
                lab_choice = random.choice(combs)
                time = lab_choice[0]
                time_next = lab_choice[0]+1
                time_next_double = lab_choice[0]+2
                day = lab_choice[1]
                if (not all_faculty[i[3]].filled[day][time]) and ((lab_choice[0] in lab_times) and (lab_choice[1] in filled_labs)):
                    if not ((time_next,day) in combs and (time_next_double,day) in combs):
                        continue
                    for j in range(time,time+3):
                        tt[day][j] = (i[0],i[3])
                        tt.filled[day][j] = True
                        all_faculty[i[3]][day][j] = (i[1][0]+str(i[1][1]).upper(),i[2])
                        all_faculty[i[3]].filled[day][j] = True
                        combs.remove((j,day))
                        flag = True
                    if flag:
                        hours_left-=3
                        filled_labs.remove(day)
        else:
            course_table.append(temp) if temp not in course_table else None
            remaining_subjects.append(i)
    
    #generating first hour classes
    for i in remaining_subjects:
        if i[-3] == 1:
            hours_left = 1
            flag = False
            tries = 0
            times = [1]
            failure = 0
            while hours_left > 0:
                failure+=1
                day = random.choice(['monday', 'tuesday', 'wednesday', 'thursday', 'friday'])
                time = random.choice(times)
                bwoah = random.choice(combs)
                tries += 1
                if not all_faculty[i[3]].filled[bwoah[1]][bwoah[0]] and bwoah[0] in times:
                    tt[bwoah[1]][bwoah[0]] = (i[0],i[3])
                    tt.filled[bwoah[1]][bwoah[0]] = True
                    all_faculty[i[3]][bwoah[1]][bwoah[0]] = all_faculty[i[3]][bwoah[1]][bwoah[0]] = (i[1][0]+str(i[1][1]).upper(),i[2])
                    all_faculty[i[3]].filled[bwoah[1]][bwoah[0]] = True
                    flag = True
                    if flag == True:
                        hours_left -= 1
                        combs.remove(bwoah)
                        temp = list(remaining_subjects[remaining_subjects.index(i)])
                        temp[4] -= 1
                        remaining_subjects[remaining_subjects.index(i)] = tuple(temp)
                if tries > 20:
                    times = [1,2]
                if failure > 2000:
                    not_generate = True
                    break
    
    #generating all classes
    for i in remaining_subjects:
        hours_left = i[4]
        not_possible = []
        failure = 0
        while hours_left > 0:
            failure += 1
            hours_today = 0
            slot_choice = random.choice(combs)
            time = slot_choice[0]
            day = slot_choice[1]
            if failure > 2000:
                not_generate = True
                break
            if (i[0],i[3]) in list(tt[day].values()):
                hours_today = list(tt[day].values()).count((i[0],i[3]))
            if hours_today < 2:
                if (time,day) in not_possible:
                    continue
                else:
                    if (not all_faculty[i[3]].filled[day][time]):
                        #Checking for three or more consecutive classes for faculty
                        if time == 1:
                            if (all_faculty[i[3]].filled[day][time+1] and all_faculty[i[3]].filled[day][time+2]):
                                not_possible.append((time,day))
                                continue
                        elif time == 2:
                            if (all_faculty[i[3]].filled[day][time-1] and all_faculty[i[3]].filled[day][time+1]) or (all_faculty[i[3]].filled[day][time+1] and all_faculty[i[3]].filled[day][time+2]):
                                not_possible.append((time,day))
                                continue
                        elif time == 3:
                            if (all_faculty[i[3]].filled[day][time-1] and all_faculty[i[3]].filled[day][time+1]) or (all_faculty[i[3]].filled[day][time-1] and all_faculty[i[3]].filled[day][time-2]):
                                not_possible.append((time,day))
                                continue
                        elif time == 4:
                            if (all_faculty[i[3]].filled[day][time-1] and all_faculty[i[3]].filled[day][time-2]):
                                not_possible.append((time,day))
                                continue
                        elif time == 6:
                            if (all_faculty[i[3]].filled[day][time+1] and all_faculty[i[3]].filled[day][time+2]):
                                not_possible.append((time,day))
                                continue
                        elif time == 7:
                            if (all_faculty[i[3]].filled[day][time-1] and all_faculty[i[3]].filled[day][time+1]):
                                not_possible.append((time,day))
                                continue
                        elif time == 8:
                            if all_faculty[i[3]].filled[day][time-1] and all_faculty[i[3]].filled[day][time-2]:
                                not_possible.append((time,day))
                                continue
                        #Checking for consecutive classes of same subject for each class
                        if time<8 and time > 1:
                            if tt[day][time+1] == (i[0],i[3]):
                                continue
                            elif tt[day][time-1] == (i[0],i[3]):
                                continue
                        if time == 8:
                            if tt[day][time-1] == (i[0],i[3]):
                                continue

                        tt[day][time] = (i[0],i[3])
                        tt.filled[day][time] = True
                        all_faculty[i[3]][day][time] = (i[1][0]+str(i[1][1]).upper(),i[2])
                        all_faculty[i[3]].filled[day][time] = True
                        hours_left -= 1
                        combs.remove(slot_choice)

    # #generating extra curricular hours
    extra_curricular = ['Mentor','Library','Sports']
    
    if len(combs) >= 3:
        iterations = 3
    elif len(combs) == 2:
        iterations = 2
    else:
        iterations = 1

    while iterations > 0: 
        temp = random.choice(combs)
        class_choice = random.choice(extra_curricular)
        tt[temp[1]][temp[0]] = ('',class_choice)
        tt.filled[temp[1]][temp[0]] = True
        combs.remove(temp)
        iterations -= 1
    
    while any(combs):
        temp = random.choice(combs)
        tt[temp[1]][temp[0]] = ('','Tutorial')
        tt.filled[temp[1]][temp[0]] = True
        combs.remove(temp)

    if not_generate is False:
        return tt
    else:
        return "failed"

combs = []
course_table = []
all_classes = list(class_timetables.keys())
counter = 0

while counter < len(all_classes): 
    i = all_classes[counter]
    days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday']
    times = [1, 2, 3, 4, 6, 7, 8]
    permut = permutations(times, len(days))
    combs = []
    for comb in permut:
        zipped = zip(comb, days)
        combs.extend(list(zipped))
    combs = list(set(combs))
    temp = generate_tt(i,TimeTable(i),all_classrooms[i])
    if temp != 'failed':
        class_timetables[i] = temp
        counter += 1

days = ["Day","8:00-8:50","8:50-9:40","9:40-10:30","10:30-11:20","11:20-12:10","12:10-1:00","1:00-1:50","1:50-2:40"]
sems = ['3rd Sem','5th Sem','7th Sem']
sections = ['A','B']


def render_mpl_table(data, class_name, class1, col_width=3.0, row_height=0.8, font_size=14,header_color='#40466e', row_colors=['#f1f1f2', 'w'], edge_color='w',bbox=[0, 0, 1, 1], header_columns=0,ax=None, **kwargs):
    if ax is None:
        size = (np.array(data.shape[::-1]) + np.array([0, 1])) * np.array([col_width, row_height])
        fig, ax = plt.subplots(figsize=size)
        ax.axis('off')
        ax.axis('tight')

    mpl_table = ax.table(cellText=data.values, bbox=bbox, colLabels=data.columns, **kwargs)

    mpl_table.auto_set_font_size(False)
    mpl_table.set_fontsize(font_size)
    mpl_table.auto_set_column_width(col=len(data.columns))
    for k, cell in six.iteritems(mpl_table._cells):
        cell.set_edgecolor(edge_color)
        if k[0] == 0 or k[1] < header_columns:
            cell.set_text_props(weight='bold', color='w', ha='center')
            cell.set_facecolor(header_color)
        else:
            cell.set_facecolor(row_colors[k[0]%len(row_colors)])
            cell.set_text_props(ha='center')
    fig1 = ax.get_figure()
    if class1 == True:
        fig1.savefig(f'{class_name}/{class_name}.png', bbox_inches='tight')
    else:
        fig1.savefig(f'{class_name}/{class_name}course.png', bbox_inches='tight')
        
#######################FLASK###################################

@app.route('/faculty', methods = ['GET',"POST"])
def faculty():

    def calculation():
        s = []
        bleh = []
        working_days = all_faculty[request.form.get('comp_selected')]
        for timetable in working_days:
            temp = [timetable.capitalize()]
            temp1 = [timetable.capitalize()]
            for j in working_days[timetable]:
                if type(working_days[timetable][j]) == str:
                    temp.append(working_days[timetable][j])
                    temp1.append(working_days[timetable][j])
                else:
                    temp.append(working_days[timetable][j])
                    temp1.append(working_days[timetable][j][0]+'\n'+working_days[timetable][j][1])
            s.append(temp)
            bleh.append(temp1)
        return [s,bleh]

    if request.form.get('submit_button') == 'show_tt':
        return render_template("ftt.html", teachers = teachers, days = days, working_days = calculation()[0], isSelected = True, select = request.form.get('comp_selected'))

    elif request.form.get('submit_button') == 'print_pdf':
        if not os.path.exists(request.form.get('comp_selected')):
            os.mkdir(request.form.get('comp_selected'))
        table = pd.DataFrame(calculation()[1],columns=days)
        render_mpl_table(table, class1 = True, class_name=request.form.get('comp_selected'), header_columns=0, col_width=3.0)
        pdf = FPDF(orientation='L') 
        pdf.add_page()
        pdf.set_font('Arial', 'B', 24)
        pdf.cell(40,20, f"{request.form.get('comp_selected')}'s Timetable")
        pdf.image(f"{request.form.get('comp_selected')}/{request.form.get('comp_selected')}.png",x=15,y=30, w=270)
        pdf.output(f"{request.form.get('comp_selected')}/{request.form.get('comp_selected')}.pdf")
        return send_file(f"{request.form.get('comp_selected')}/{request.form.get('comp_selected')}.pdf",as_attachment=True)

    return render_template("ftt.html", teachers = teachers, isSelected = False, select = '')

@app.route('/classroom', methods = ["GET","POST"])
def classroom():
    def show():
        s = []
        bleh = []
        working_days = class_timetables[str(str(request.form.get("sem"))[0]+""+str(request.form.get("section"))).lower()]
        for timetable in working_days:
            temp = [timetable.capitalize()]
            temp1 = [timetable.capitalize()]
            for j in working_days[timetable]:
                if type(working_days[timetable][j]) == str:
                    temp1.append(working_days[timetable][j])
                    temp.append(working_days[timetable][j])
                else:
                    temp.append(working_days[timetable][j])
                    temp1.append(working_days[timetable][j][0]+'\n'+working_days[timetable][j][1])
            s.append(temp)
            bleh.append(temp1)
        return [s,bleh]
    
    if request.form.get('submit_button') == 'show_tt':
        return render_template("ctt.html", course_table = course_table, days = days, working_days = show()[0], isSelected = True, sems = sems, sections = sections, select_sem = str(request.form.get("sem")), select_section = str(request.form.get("section")))

    elif request.form.get('submit_button') == 'print_pdf':
        if not os.path.exists(str(str(request.form.get("sem"))[0]+""+str(request.form.get("section"))).lower()):
            os.mkdir(str(str(request.form.get("sem"))[0]+""+str(request.form.get("section"))).lower())
        table = pd.DataFrame(show()[1],columns=days)
        course = pd.DataFrame(course_table, columns = ['Class','Code','Course Name','Faculty Name','Category'])
        course = course[course['Class'] == str(str(request.form.get("sem"))[0]+""+str(request.form.get("section"))).lower()]
        course.drop('Class',axis=1, inplace=True)
        render_mpl_table(table, class1 = True, class_name=str(str(request.form.get("sem"))[0]+""+str(request.form.get("section"))).lower(), header_columns=0, col_width=3.0)
        render_mpl_table(course, class1 = False, class_name=str(str(request.form.get("sem"))[0]+""+str(request.form.get("section"))).lower(), header_columns=0, col_width=3.0)
        pdf = FPDF(orientation='L') 
        pdf.add_page()
        pdf.set_font('Arial', 'B', 24)
        pdf.cell(40, 20, f'Class {str(str(request.form.get("sem"))[0]+""+str(request.form.get("section"))).lower()} Timetable')
        pdf.image(f'{str(str(request.form.get("sem"))[0]+""+str(request.form.get("section"))).lower()}/{str(str(request.form.get("sem"))[0]+""+str(request.form.get("section"))).lower()}.png',x=15,y=30, w=270)
        pdf.add_page()
        pdf.image(f'{str(str(request.form.get("sem"))[0]+""+str(request.form.get("section"))).lower()}/{str(str(request.form.get("sem"))[0]+""+str(request.form.get("section"))).lower()}course.png',x=15,y=30, w=270)
        pdf.output(f'{str(str(request.form.get("sem"))[0]+""+str(request.form.get("section"))).lower()}/{str(str(request.form.get("sem"))[0]+""+str(request.form.get("section"))).lower()}.pdf')
        return send_file(f'{str(str(request.form.get("sem"))[0]+""+str(request.form.get("section"))).lower()}/{str(str(request.form.get("sem"))[0]+""+str(request.form.get("section"))).lower()}.pdf',as_attachment=True)

    return render_template("ctt.html", isSelected = False, sections = sections, sems = sems, select_sem = '', select_section = '')

@app.route('/', methods=['POST', 'GET'])
def main_page():
    if request.form.get('submit_button') == 'Class timetable':
        return redirect('classroom')
    elif request.form.get('submit_button') == 'Faculty timetable':
        return redirect('faculty')
    return render_template("index.html")

if __name__ == "__main__":
    app.run()