#!/usr/bin/env python
import Tkinter as tk
import ttk
#from tkinter import ttk
import time
from time import sleep
from curses import ascii
from PIL import Image
from PIL import ImageTk
import serial
import os
# import tkMessageBox
import threading
import requests, sys
import json
import myDb


from io import BytesIO
import string


appPath = "D:\loyixa\RFID_turniket\\fitness\\test\\"
dataPath = "D:\loyixa\RFID_turniket\\fitness\\"

comPorts = []
actions=[]

isMainPageOpen=1

def errorLog(error, show=1):
    global errorLogPath
   # f = open(errorLogPath, "a")
   # f.write(time.strftime("\n%H:%M:%S#") + error)
   # f.close()
    print (error)
def on_focus_in(event):
    global isMainPageOpen
    if event.widget == win:
        isMainPageOpen=1
        print ("focus in")
        updateRegisterWindow()
def on_focus_out(event):
    global isMainPageOpen
    if event.widget == win:
        isMainPageOpen=0
        print ("focus out")
def init():
    global errorLogPath,comPorts,comError,timers,dataPath,appPath,photoImg,blankImg,unknownImg,waitImg,attendanceBack,in_img,out_img,cornerLD,countedStudents, allStudents,imgHeight, imgWidth, win,SCHOOL_ID
    global stdPhotos,stdNames,combostyle
    global windowElements,readRFID
    readRFID=0
    windowElements = []
    if not os.path.exists(dataPath + 'logs'):
        os.makedirs(dataPath + 'logs')
    errorLogPath = dataPath + "logs/error_" + time.strftime("%d-%m-%y.txt")

    serialPorts = ['COM25','/dev/ttyACM0','/dev/ttyACM1','/dev/ttyACM2','/dev/ttyACM3','/dev/ttyUSB0','/dev/ttyUSB1','/dev/ttyUSB2','/dev/ttyUSB3']
    for port in serialPorts:
        try:
            arduino_port = serial.Serial(port, baudrate=9600,
                                      parity=serial.PARITY_NONE,
                                      stopbits=serial.STOPBITS_ONE,
                                      bytesize=serial.EIGHTBITS,
                                      timeout=0.04)
            comPorts.append(arduino_port)
        except Exception as ex:
            errorLog(str(ex))
    try:
        comError = range(len(comPorts))
       # timers = [maxtime, maxtime, maxtime, maxtime, maxtime, maxtime, maxtime, maxtime, maxtime, maxtime]


        win = tk.Tk()
        win.title("main window")
       # win.attributes("-fullscreen", True)
        win.configure(background='black')
        win.bind("<FocusIn>", on_focus_in)
        win.bind("<FocusOut>", on_focus_out)
        wWidth = win.winfo_screenwidth()
        wHeight = win.winfo_screenheight()

        left_frame = tk.Frame(win)
        left_frame.pack(side=tk.LEFT)
        right_frame = tk.Frame(win,width=40, height=17)
        right_frame.pack(side=tk.RIGHT)
        scrollbar = tk.Scrollbar(left_frame, orient="vertical")
        register_list_box = tk.Listbox(left_frame, width=40, height=17, yscrollcommand=scrollbar.set, font=("Arial", 30))
        
       # register_list_box.bind('<<ListboxSelect>>', open_user_list_selected)
        register_list_box.pack( side = tk.RIGHT, fill = tk.BOTH)
        scrollbar.config( command = register_list_box.yview )
        scrollbar.pack( side = tk.LEFT, fill = tk.Y )

        payment_frame=tk.Frame(right_frame)
        payment_frame.grid(row=0, column=0)
        makeLabel(payment_frame,"PAYMENT").grid(row=0, column=0)
        makeBtn(payment_frame, "REGISTER", open_payment).grid(row=1, column=0)

        settings_frame=tk.Frame(right_frame)
        settings_frame.grid(row=1, column=0)
        makeLabel(settings_frame, "SETTINGS").grid(row=0, column=0)
        makeBtn(settings_frame, "SCHEDULE", open_schedule).grid(row=1, column=0)
        makeBtn(settings_frame,"USERS",open_users).grid(row=2,column=0)
        makeBtn(settings_frame, "COACHES", open_coaches).grid(row=3, column=0)

        stat_frame = tk.Frame(right_frame)
        stat_frame.grid(row=2, column=0)
        makeLabel(stat_frame, "STATISTICS").grid(row=0, column=0)
        makeBtn(stat_frame, "USER", open_users_stat).grid(row=1, column=0)
        makeBtn(stat_frame, "PAYMENT", open_payment_stat).grid(row=2, column=0)


        imgHeight = int(wHeight / 2 - 90)
        imgWidth = int(imgHeight * 3 / 4)
        cornerImgHeigth=int(imgHeight)
        wMargin=(wWidth-imgWidth*5)/4

        photoImg = readPhotoImg(appPath + "images/unknown.jpg", imgWidth, imgHeight)
        blankImg = readPhotoImg(appPath + "images/blank.png", imgWidth, 70)
        unknownImg = readPhotoImg(appPath + "images/unknown.jpg", imgWidth, cornerImgHeigth)
        waitImg = readPhotoImg(appPath + "images/blank.jpg", imgWidth, imgHeight)
        attendanceBack = readPhotoImg(appPath + "images/blank.png", imgWidth, imgHeight)
        in_img = readPhotoImg(appPath + "images/in1.png", imgWidth, imgHeight)
        out_img = readPhotoImg(appPath + "images/out1.png", imgWidth, imgHeight)

      
        #setAttendace()
        combostyle = ttk.Style()
        combostyle.theme_create('combostyle', parent='alt',
                         settings = {'TCombobox':
                                     {'configure':
                                      {'selectbackground': 'orange',
                                       'fieldbackground': 'orange',
                                       'background': 'black'
                                       }}}
                         )
        combostyle.theme_use('combostyle') 

        windowElements=[register_list_box]
    except Exception as ex:
        errorLog(str(ex))
def makeLabel(frame,lb_text,lbl_width=20,font_size=25):
   return tk.Label(frame,bg="black", fg="orange",text=lb_text,font=("Arial", font_size),anchor="e",width =lbl_width)
def makeBtn(frame,lb_text,command_func,lbl_width=20):
    return tk.Button(frame,text=lb_text,command =command_func,bg="orange",width =lbl_width,anchor="w",font=("Arial", 20))
def makeEntry(frame,row,col,text='',font_size=25,width=15):
    e=tk.Entry(frame,font=("Arial", font_size),width =width)
    e.delete(0,tk.END)
    e.insert(0,text)
    e.grid(row=row, column=col,padx=5, pady=1)
    return e
def open_types():
    print "open types"
def open_schedule():
    global open_schedule_elements,open_schedule_win,open_schedule_vars
    font_size=25
    try:
        open_schedule_elements=[]
        open_schedule_vars=[0]
        open_schedule_win.destroy()
    except Exception as ex:
        print(ex)
    
     
    open_schedule_win = tk.Toplevel()
    open_schedule_win.title("register window")
    open_schedule_win.configure(background='black')

    left_frame = tk.Frame(open_schedule_win)
    left_frame.configure(background='black')
    left_frame.pack(side=tk.LEFT)
    right_frame = tk.Frame(open_schedule_win)
    right_frame.configure(background='black')
    right_frame.pack(side=tk.RIGHT)

    scrollbar = tk.Scrollbar(right_frame, orient="vertical")
    

    schedule_frame= tk.Frame(left_frame)
    schedule_frame.grid(row=0, column=0)
    schedule_frame.configure(background='black')

    makeLabel(schedule_frame,"ID").grid(row=0, column=0)
    makeLabel(schedule_frame,"NAME").grid(row=1, column=0)
    makeLabel(schedule_frame,"START_TIME").grid(row=2, column=0)
    makeLabel(schedule_frame,"END_TIME").grid(row=3, column=0)
    makeLabel(schedule_frame,"TRAIN_AMOUNT").grid(row=4, column=0)


    open_schedule_elements.append(makeEntry(schedule_frame,row=0,col=1,text='-1'))
    #open_schedule_elements[0].configure(state='readonly')
    open_schedule_elements.append(makeEntry(schedule_frame,row=1,col=1,text="new schedule"))
    open_schedule_elements.append(makeEntry(schedule_frame,row=2,col=1,text="08:30:00"))
    open_schedule_elements.append(makeEntry(schedule_frame,row=3,col=1,text="11:35:00"))
    open_schedule_elements.append(makeEntry(schedule_frame,row=4,col=1,text="12"))
    
    makeBtn(schedule_frame, "SAVE", save_schedule,lbl_width=10).grid(row=10, column=0,pady=5)
    makeBtn(schedule_frame, "DELETE", open_schedule_delete_schedule,lbl_width=10).grid(row=10, column=1)
    n = tk.StringVar() 
   
    schedule_list_box = tk.Listbox(right_frame, width=20, height=17, yscrollcommand=scrollbar.set, font=("Arial", font_size))
    schedule_list_box.grid(row=1, column=0)
    schedule_list_box.bind('<<ListboxSelect>>', open_schedule_list_selected)

    open_schedule_elements.append(schedule_list_box)
    open_schedule_update_schedule()
    print "open_schedule"
def open_schedule_list_selected(evt):
    global open_schedule_elements,open_schedule_vars
    try:
        w = evt.widget
        index = int(w.curselection()[0])
        value = w.get(index)
       # print ('You selected item %d: "%s"' % (index, value))
        open_schedule_select_schedule(open_schedule_vars[0][index])
      #  print(windowElements[0]) 
    except Exception as ex:
        print(ex)  
def open_schedule_select_schedule(schedule_id):
    ID, NAME,START_TIME,END_TIME,TRAIN_AMOUNT=myDb.getScheduleByID(schedule_id)    
    entry_set_text(open_schedule_elements[0],ID,e_state="disabled")
    entry_set_text(open_schedule_elements[1],NAME)
    entry_set_text(open_schedule_elements[2],START_TIME)
    entry_set_text(open_schedule_elements[3],END_TIME)
    entry_set_text(open_schedule_elements[4],TRAIN_AMOUNT)
def entry_set_text(e,text,e_state='normal'):
    e.configure(state="normal")
    e.delete(0,tk.END)
    e.insert(0,text)
    e.configure(state=e_state)
def open_schedule_delete_schedule():
    global open_schedule_elements
    try:
        myDb.do_query("DELETE FROM SCHEDULE WHERE ID="+str(open_schedule_elements[0].get()))
        open_schedule_update_schedule()
        open_schedule_select_schedule(open_schedule_vars[0][0])
    except Exception as ex:
        print(ex)  
def open_schedule_update_schedule():
    global open_schedule_elements,open_schedule_vars
    try:
        open_schedule_elements[5].delete(0,tk.END)
        schedule_ids, schedule_names =myDb.getSchedule()
        open_schedule_vars[0]=schedule_ids
        schedule_count=len(schedule_names)
        for i in range(0,schedule_count):
            open_schedule_elements[5].insert(0,schedule_names[schedule_count-i-1])
    except Exception as ex:
        print(ex)     
def save_schedule():
    global open_schedule_elements
    id=open_schedule_elements[0].get()
    name=open_schedule_elements[1].get()
    start_time=open_schedule_elements[2].get()
    end_time=open_schedule_elements[3].get()
    train_amount=open_schedule_elements[4].get()

    myDb.saveSchedule(id,name,start_time,end_time,train_amount)
    open_schedule_update_schedule()
def open_payment():
    global open_payment_elements,open_payment_win,open_payment_vars
    font_size=25
    try:
        open_payment_elements=[]
        open_payment_vars=[0,0,0,0,0]
        readRFID=0
        open_payment_win.destroy()
    except Exception as ex:
        print(ex)
    
    schedule_ids, schedule_names=myDb.getSchedule(0)
    coach_ids, coach_names=myDb.getCoaches()

    open_payment_win = tk.Toplevel()
    open_payment_win.title("register window")
    open_payment_win.configure(background='black')

    top_frame = tk.Frame(open_payment_win)
    top_frame.configure(background='black')
    top_frame.pack(side=tk.TOP)
    bottom_frame = tk.Frame(open_payment_win)
    bottom_frame.configure(background='black')
    bottom_frame.pack(side=tk.BOTTOM)

    makeLabel(top_frame,"NAME").grid(row=0, column=0)
    makeLabel(top_frame,"SCHEDULE").grid(row=1, column=0)
    makeLabel(top_frame,"COACH").grid(row=2, column=0)
    makeLabel(top_frame,"TRAIN AMOUNT").grid(row=3, column=0)
    makeLabel(top_frame,"END TIME").grid(row=4, column=0)
    makeLabel(top_frame,"MONEY").grid(row=5, column=0)

    open_payment_elements.append(makeEntry(top_frame,row=0,col=1,text="-"))
   

    schedules_combo=ttk.Combobox(top_frame, font=("Arial", font_size),width = 14,state="readonly")
    schedules_combo['values']=schedule_names
    schedules_combo.grid(row=1, column=1)
    
    coaches_combo=ttk.Combobox(top_frame, font=("Arial", font_size),width = 14,state="readonly")
    coaches_combo['values']=coach_names
    coaches_combo.grid(row=2, column=1)
    open_payment_elements.append(schedules_combo)
    open_payment_elements.append(coaches_combo)

    open_payment_elements.append(makeEntry(top_frame,row=3,col=1,text=""))
    open_payment_elements.append(makeEntry(top_frame,row=4,col=1,text="2021-01-01"))
    open_payment_elements.append(makeEntry(top_frame,row=5,col=1,text=""))

    makeBtn(top_frame, "SAVE", save_user,lbl_width=10).grid(row=6, column=1,pady=5)

    

def open_users():
    global open_users_elements,open_users_win,open_users_vars,readRFID
    font_size=25
    try:
        open_users_elements=[]
        open_users_vars=[0,0,0,0,0]
        readRFID=0
        open_users_win.destroy()
    except Exception as ex:
        print(ex)
    
    open_users_win = tk.Toplevel()
    open_users_win.title("register window")
    open_users_win.configure(background='black')

    left_frame = tk.Frame(open_users_win)
    left_frame.configure(background='black')
    left_frame.pack(side=tk.LEFT)
    right_frame = tk.Frame(open_users_win)
    right_frame.configure(background='black')
    right_frame.pack(side=tk.RIGHT)

    scrollbar = tk.Scrollbar(right_frame, orient="vertical")
    

    user_frame= tk.Frame(left_frame)
    user_frame.grid(row=0, column=0)
    user_frame.configure(background='black')

    makeLabel(user_frame,"ID").grid(row=0, column=0)
    makeLabel(user_frame,"RFID").grid(row=1, column=0)
    makeLabel(user_frame,"NAME").grid(row=2, column=0)
    makeLabel(user_frame,"TEL NUMBER").grid(row=3, column=0)
    makeLabel(user_frame,"SCHEDULE").grid(row=4, column=0)
    makeLabel(user_frame,"START DATE").grid(row=5, column=0)
    makeLabel(user_frame,"END DATE").grid(row=6, column=0)
    makeLabel(user_frame,"TRAIN AMOUNT").grid(row=7, column=0)
    makeLabel(user_frame,"REGISTERED DATE").grid(row=8, column=0)
    makeLabel(user_frame,"USER LEVEL").grid(row=9, column=0)

    open_users_elements.append(makeEntry(user_frame,row=0,col=1,text='-1'))
    open_users_elements[0].configure(state='disabled')

    rfid_frame=tk.Frame(user_frame)
    rfid_frame.grid(row=1, column=1)
    makeBtn(rfid_frame, "#", readRfid_FUNC,lbl_width=1).grid(row=0, column=1)

    open_users_elements.append(makeEntry(rfid_frame,row=0,col=0,width=13))
    open_users_elements.append(makeEntry(user_frame,row=2,col=1,text="new user"))
    open_users_elements.append(makeEntry(user_frame,row=3,col=1))
    #makeEntry(user_frame,row=4,col=1)
    user_schedule=ttk.Combobox(user_frame,font=("Arial", font_size),width = 14,state="readonly")
    user_schedule.grid(row=4, column=1)
    open_users_elements.append(user_schedule)
    open_users_elements.append(makeEntry(user_frame,row=5,col=1,text="2021-01-01"))
    open_users_elements.append(makeEntry(user_frame,row=6,col=1,text="2021-02-01"))
    open_users_elements.append(makeEntry(user_frame,row=7,col=1,text="0"))
    open_users_elements.append(makeEntry(user_frame,row=8,col=1))
    open_users_elements[8].configure(state='disabled')
    open_users_elements.append(makeEntry(user_frame,row=9,col=1,text='1'))

    makeBtn(user_frame, "SAVE", save_user,lbl_width=10).grid(row=10, column=0,pady=5)
    makeBtn(user_frame, "DELETE", delete_user,lbl_width=10).grid(row=10, column=1)
    
    n = tk.StringVar() 
    schedules=ttk.Combobox(right_frame, textvariable = n,font=("Arial", font_size),width = 19,state="readonly")
    schedules.bind("<<ComboboxSelected>>", open_users_schedule_changed)
    
    schedule_ids, schedule_names=myDb.getSchedule(0)
    schedules['values']=schedule_names
    schedules.current(0)
    user_schedule['values']=schedule_names#[0,1,1]
    open_users_vars[0]=schedule_ids
    open_users_vars[3]=schedule_names

    schedules.grid(row=0, column=0)

    users_list_box = tk.Listbox(right_frame, width=20, height=17, yscrollcommand=scrollbar.set, font=("Arial", font_size))
    open_users_elements.append(users_list_box)
    users_list_box.grid(row=1, column=0)
    users_list_box.bind('<<ListboxSelect>>', open_user_list_selected)

   
    print "open_users"
def readRfid_FUNC():
    global readRFID
    readRFID=1
    print ("readRFid")
def open_user_list_selected(evt):
    global open_user_elements,open_users_vars
    try:
        w = evt.widget
        index = int(w.curselection()[0])
        value = w.get(index)
       # print ('You selected item %d: "%s"' % (index, value))
        open_user_select_user(open_users_vars[2][index])
      #  print(windowElements[0]) 
    except Exception as ex:
        print("open_user_list_selected:",ex)  
def open_user_select_user(user_id):
    global open_users_elements
    ID, RFID,NAME,TEL_NUMBER,SCHEDULE_ID,START_DATE,END_DATE,TRAIN_AMOUNT,REGISTERED_DATE,USER_LEVEL=myDb.getUserByID(user_id)    
    entry_set_text(open_users_elements[0],ID,e_state="disabled")
    entry_set_text(open_users_elements[1],RFID)
    entry_set_text(open_users_elements[2],NAME)
    entry_set_text(open_users_elements[3],TEL_NUMBER)
    entry_set_text(open_users_elements[4],SCHEDULE_ID)
    entry_set_text(open_users_elements[5],START_DATE)
    entry_set_text(open_users_elements[6],END_DATE)
    entry_set_text(open_users_elements[7],TRAIN_AMOUNT)
    entry_set_text(open_users_elements[8],REGISTERED_DATE)
    entry_set_text(open_users_elements[9],USER_LEVEL)
def save_user():
    global open_users_elements,open_users_vars
    id=open_users_elements[0].get()
    rfid=open_users_elements[1].get()
    name=open_users_elements[2].get()
    tel_numb=open_users_elements[3].get()
    schedule=open_users_vars[0][open_users_vars[3].index(open_users_elements[4].get())]
    start_date=open_users_elements[5].get()
    end_date=open_users_elements[6].get()
    train_amount=open_users_elements[7].get()
    reg_date=open_users_elements[8].get()
    user_level=open_users_elements[9].get()
    myDb.saveUser(id,rfid,name,tel_numb,schedule,start_date,end_date,train_amount,user_level)
    updateUsers(schedule)
def delete_user():
    global open_users_elements,open_users_vars
    try:
        myDb.do_query("DELETE FROM ACTIONS WHERE USER_ID="+str(open_users_elements[0].get()))
        myDb.do_query("DELETE FROM USERS WHERE ID="+str(open_users_elements[0].get()))
        updateUsers(open_users_vars[0][open_users_vars[3].index(open_users_elements[4].get())])
        open_user_select_user(open_users_vars[0][0])
    except Exception as ex:
        print(ex)  
def open_users_schedule_changed(event):
    global open_users_elements,open_users_vars
    try:
        w = event.widget
        print (w.get())
        choosenGroupID=open_users_vars[0][w.current()]
        open_users_vars[1]=choosenGroupID
        updateUsers(choosenGroupID)
    except Exception as ex:
        print(ex)  
#def open_users_updateGroups():
def updateUsers(SCHEDULE_ID):
    global open_users_elements,open_users_vars
    try:
        user_ids, user_names =myDb.getUsersByScheduleID(SCHEDULE_ID)
        open_users_vars[2]=user_ids
        USER_COUNT=len(user_names)
        open_users_vars[1]=SCHEDULE_ID
        open_users_elements[10].delete(0,tk.END)
        for i in range(0,USER_COUNT):
            open_users_elements[10].insert(0,user_names[USER_COUNT-i-1])
    except Exception as ex:
        print(ex)

def open_coaches():
    global open_coaches_elements,open_coaches_win,open_coaches_vars
    font_size=25
    try:
        open_coaches_elements=[]
        open_coaches_vars=[0,0,0,0,0]
        open_coaches_win.destroy()
    except Exception as ex:
        print(ex)
    
    open_coaches_win = tk.Toplevel()
    open_coaches_win.title("register window")
    open_coaches_win.configure(background='black')

    left_frame = tk.Frame(open_coaches_win)
    left_frame.configure(background='black')
    left_frame.pack(side=tk.LEFT)
    right_frame = tk.Frame(open_coaches_win)
    right_frame.configure(background='black')
    right_frame.pack(side=tk.RIGHT)

    scrollbar = tk.Scrollbar(right_frame, orient="vertical")
    

    coach_frame= tk.Frame(left_frame)
    coach_frame.grid(row=0, column=0)
    coach_frame.configure(background='black')

    makeLabel(coach_frame,"ID").grid(row=0, column=0)
    makeLabel(coach_frame,"NAME").grid(row=1, column=0)
    
    open_coaches_elements.append(makeEntry(coach_frame,row=0,col=1,text='-1'))
    open_coaches_elements[0].configure(state='disabled')
    open_coaches_elements.append(makeEntry(coach_frame,row=1,col=1,text="new user"))
   
    makeBtn(coach_frame, "SAVE", save_couch,lbl_width=10).grid(row=10, column=0,pady=5)
    makeBtn(coach_frame, "DELETE", delete_couch,lbl_width=10).grid(row=10, column=1)
 
 
 
    users_list_box = tk.Listbox(right_frame, width=20, height=17, yscrollcommand=scrollbar.set, font=("Arial", font_size))
    open_coaches_elements.append(users_list_box)
    users_list_box.grid(row=1, column=0)
    users_list_box.bind('<<ListboxSelect>>', open_coach_list_selected)
    updateCoaches()
    print "open_coaches"
def updateCoaches():
    global open_coaches_elements,open_coaches_vars
    try:
        coach_ids, coach_names =myDb.getCoaches()
        open_coaches_vars[0]=coach_ids
        USER_COUNT=len(coach_names)
        open_coaches_elements[2].delete(0,tk.END)
        for i in range(0,USER_COUNT):
            open_coaches_elements[2].insert(0,coach_names[USER_COUNT-i-1])
    except Exception as ex:
        print(ex)
def open_coach_list_selected(evt):
    global open_coaches_elements,open_coaches_vars
    try:
        w = evt.widget
        index = int(w.curselection()[0])
        value = w.get(index)
       # print ('You selected item %d: "%s"' % (index, value))
       # open_user_select_user(open_users_vars[2][index])
       # print(open_coaches_vars[0][index])
        ID, NAME=myDb.getCouchByID(open_coaches_vars[0][index])    
        entry_set_text(open_coaches_elements[0],ID,e_state="disabled")
        entry_set_text(open_coaches_elements[1],NAME)
      #  print(windowElements[0]) 
    except Exception as ex:
        print("open_coach_list_selected:",ex)  
   
def save_couch():
    global open_coaches_elements,open_coaches_vars
    id=open_coaches_elements[0].get()
    name=open_coaches_elements[1].get()
    myDb.saveCoach(id,name)
    updateCoaches()
def delete_couch():
    global open_coaches_elements,open_users_vars
    try:
        print(str(open_coaches_elements[0].get()))
        myDb.do_query("DELETE FROM COACHES WHERE ID="+str(open_coaches_elements[0].get()))
        
        updateCoaches()
       # open_user_select_user(open_users_vars[0][0])
    except Exception as ex:
        print(ex)  

def open_users_stat():
    global users_stat_elements,users_stat_win,users_stat_vars
    font_size=25
    try:
        users_stat_elements=[]
        users_stat_vars=[0,0,0,0,0]
        users_stat_win.destroy()
    except Exception as ex:
        print(ex)

    users_stat_win = tk.Toplevel()
    users_stat_win.title("register window")
    users_stat_win.configure(background='black')
    
    left_frame = tk.Frame(users_stat_win,width=40, height=17)
    left_frame.pack(side=tk.LEFT)
    scrollbar = tk.Scrollbar(left_frame, orient="vertical")
    users_list_box = tk.Listbox(left_frame, width=40, height=17, yscrollcommand=scrollbar.set, font=("Arial", 30))
        
       # register_list_box.bind('<<ListboxSelect>>', open_user_list_selected)
    users_list_box.pack( side = tk.RIGHT, fill = tk.BOTH)
    scrollbar.config( command = users_list_box.yview )
    scrollbar.pack( side = tk.LEFT, fill = tk.Y )
    
    
    users_stat_elements.append(users_list_box)
   # users_list_box.grid(row=1, column=1)
    print ("open_users_stat")
def users_stat_date_choosen():
    global users_stat_elements,users_stat_vars
    try:
        users_list_box = users_stat_elements[0]
        users_list_box.delete(0, tk.END)
        registerCount=len(lastRegisterActions)
        for i in range(0,registerCount):
            users_list_box.insert(0,lastRegisterActions[i])
    except Exception as ex:
        print(ex) 
def open_payment_stat():
    print "open_payment_stat"
def searchConfigVal(f, key, defaultVal, strip=1):
    if strip == 1:
        string = f.readline().strip()
    else:
        string = f.readline()
    index = string.find(key)
    if index > -1:
        index = string.find('=')
        return string[index + 1:]
    return defaultVal
def readPhotoImg(src, width, height):
    img = Image.open(src)
    img = img.resize((width, height), Image.ANTIALIAS)
    return ImageTk.PhotoImage(img)
def makeStdPhoto(img):
    global imgHeight, imgWidth, win
    return tk.Label(win, image=img, height=imgHeight, width=imgWidth)

def makeStdName():
    global blankImg
    return tk.Label(win, font=("Arial", 18), image=blankImg, text="Aniqlanmagan", height=70, width=imgWidth,
                    compound=tk.CENTER)
lastRegisterActions=[]
def updateRegisterWindow():
    global windowElements,isMainPageOpen
    if isMainPageOpen==1:
        register_list_box = windowElements[0]
        register_list_box.delete(0, tk.END)
        registerCount=len(lastRegisterActions)
        for i in range(0,registerCount):
            register_list_box.insert(0,lastRegisterActions[i])

def setAttendace():

    global open_schedule_elements,open_schedule_vars
    try:
        open_schedule_elements[5].delete(0,tk.END)
        schedule_ids, schedule_names =myDb.getSchedule()
        open_schedule_vars[0]=schedule_ids
        schedule_count=len(schedule_names)
        for i in range(0,schedule_count):
            open_schedule_elements[5].insert(0,schedule_names[schedule_count-i-1])
    except Exception as ex:
        print(ex)     


    global countedStudents, allStudents, cornerLD
    try:

        countedStudents= myDb.getStatistics()
        allStudents=myDb.getAllUsersCount()
        if countedStudents == 0:
            percentage = 0
        else:
            percentage = int(countedStudents * 100 / allStudents)
        cornerLD.config(text=time.strftime("%H:%M") + "\n\nALL USERS:\n" + str(allStudents) + "\nCOUNTED:\n" + str(
            countedStudents) + "\nPERCENTAGE:\n" + str(percentage) + "%")
    except Exception as ex:
        errorLog(str(ex), 0)


def serialThread1():
    while True:
        serialThread()
def serialThread():
    global win, comPorts,timers,stdPhotos,actions,dataforserver,readRFID,open_users_elements
    portIndex = -1
    for comPort in comPorts:
        portIndex = portIndex + 1
        try:
            rec = str(comPort.readline())
            if len(rec) > 4:
                rec=rec.strip()
                data= rec.strip().split('#')
                if len(data) > 3: 
                    print (data)
                    dev_id =int(data[1])
                    index = dev_id - 1
                    RFID = data[2].strip().upper()
                    gate = int(data[3])

                    if RFID == "TEST" or RFID == "RESET":
                        date = time.strftime("%Y-%m-%d %H:%M:%S")
                        
                        comError[portIndex] = 0
                    else:
                        if not gate == 1:#1-come,2-leave
                            gate = 2
                            index = dev_id - 1 + 4
                        #timers[index] = maxtime   
                        comError[portIndex] = 0
                        try:
                            id, name,USER_LEVEL,SCHEDULE_NAME,TRAIN_AMOUNT,permission=myDb.findUser(RFID,gate-1)
                            if id==None:
                                if readRFID==1:
                                    readRFID=0
                                    entry_set_text(open_users_elements[1],RFID)
                                else:
                                   
                                    #stdNames[index].config(text="Aniqlanmagan")
                                    comPort.write("@"+str(dev_id)+"$ERROR&"+str(gate) + '*\n')
                            else:
                                if permission==1:
                                    comPort.write("@"+str(dev_id)+"$OK&"+str(gate) + '*\n')
                                    print("open")
                                lastRegisterActions.append("S("+SCHEDULE_NAME+") T("+str(TRAIN_AMOUNT)+"): "+name)
                                if len(lastRegisterActions)>20:
                                    lastRegisterActions.pop(0)                                    
                                updateRegisterWindow()
                               # setAttendace()
                               # stdNames[index].config(text=name+"\n"+group_id)
                          
                        except Exception as ex:  
                            print (ex)
                           # stdNames[index].config(text="Aniqlanmagan")
                           # stdPhotos[index].config(image=unknownImg)
                           # stdPhotos[index].image = unknownImg   
        except Exception as ex:
            comError[portIndex] = int(comError[portIndex]) + 1
            if comError[portIndex] > 60:
                 comError[portIndex] = 0
                 print ("abort:" + str(comPorts.pop(portIndex)))
                 reboot()
            errorLog("Serial thread:" + str(ex))
    # try:
    #     for i in range(0, 8):

    #         if timers[i] < 4:
    #             if timers[i] > 0:
    #                 timers[i] = timers[i] - 1
    #                # stdPhotos[i].config(image=waitImg)
    #                # stdPhotos[i].image = waitImg
    #                # stdNames[i].config(text="\n \n")
    #         else:
    #             # print timers[i]
    #             timers[i] = timers[i] - 1
    # except Exception as ex:
    #     errorLog(str(ex), 0)
   # minut = int(time.strftime("%M"))
  #  hour = int(time.strftime("%H"))
  #  second = int(time.strftime("%S"))
  #  if hour == REBOOT_TIME1[0] and minut == REBOOT_TIME1[1] and second > 45 or hour == REBOOT_TIME2[0] and minut == REBOOT_TIME2[1] and second > 45:
      #  reboot()
   # win.after(1, serialThread)

def reboot():
    os.system("sudo reboot")



try:
    
    init()
    
    thread = threading.Thread(target=serialThread1)
    thread.start()


except Exception as ex:
    errorLog(str(ex))
    sys.exit()
    win.quit()
tk.mainloop()