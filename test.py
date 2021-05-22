import tkinter as tk
from tkinter import ttk
from models import *
import calendar
import functools
fp=functools.partial
lbl_width = 15
def drop_create_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    
def show_cl_sch():
    global opt_user_sch
    try:
        opt_user_sch = ttk.Combobox(frame_users, value=[str(_.name) for _ in session.query(Schedule.name)], width=lbl_width+12)
        opt_user_sch.current(0)
        opt_user_sch.grid(column=1, row=4)
    except:
        opt_user_sch = ttk.Combobox(frame_users, value=["please add schedule"], width=lbl_width+12)
        opt_user_sch.current(0)
        opt_user_sch.grid(column=1, row=4)
def export_to_excel(fname, year, month):
    if fname != '':
        year, month = int(year), int(month)   
        try:
            num_days = calendar.monthrange(year, month)[1]
            start_date = date(year, month, 1)
            end_date = date(year, month, num_days)
            action_results = session.query(Action).filter(
and_(Action.action_time >= start_date, Action.action_time <= end_date))
            payment_results = session.query(Payment).filter(
and_(Payment.action_time >= start_date, Payment.action_time <= end_date))
            writer = pd.ExcelWriter(fname + '.xlsx')
            action_table = pd.read_sql_table('action', engine, columns=["action_time", "is_entry", "allowed", "user_id"])
            payment_table = pd.read_sql_table('payment', engine, columns=["money","action_time", "coach_id", "user_id"])
            user_table = pd.read_sql_table('user', engine, columns=["id", "name"])
            df = pd.merge(user_table, action_table, left_on="id", right_on="user_id", how="right")
            df1 = pd.merge(user_table, payment_table, left_on="id", right_on="user_id", how="right")
            df2 = pd.read_sql(str(action_results), engine, params=[start_date, end_date], columns=["action_time", "is_entry", "allowed", "user_id"])
            for i, row in df2.iterrows():
                df2['action_is_entry'] = df2['action_is_entry'].apply(str)
                df2['action_is_entry'] = df2['action_is_entry'].astype(str)
                df2 = df2.applymap(str)
                enter = "Enter"
                allow = "Allowed"
                print(i)
                print(row)
                if row["action_is_entry"] == 0:
                    enter = "Left"
                if row["action_allowed"] == 0:
                    allow = "Deny"
                df2.at[i,"action_user_id"] = session.query(User).filter_by(id=row["action_user_id"]).first().name
                df2.at[i,'action_is_entry'] = enter
                df2.at[i,'action_allowed'] = allow
            df3 = pd.read_sql(str(payment_results), engine,params=[start_date, end_date], columns=["money","action_time", "coach_id", "user_id"])
            for i, row in df3.iterrows():
                df3['payment_user_id'] = df3['payment_user_id'].apply(str)
                df3['payment_user_id'] = df3['payment_user_id'].astype(str)
                df3 = df3.applymap(str)
                df3.at[i,"payment_coach_id"] = session.query(Coach).filter_by(id=row["payment_coach_id"]).first().name
                df3.at[i,"payment_user_id"] = session.query(User).filter_by(id=row["payment_user_id"]).first().name
            with writer:
                df2.to_excel(writer, sheet_name="Actions", index=False)
                df3.to_excel(writer, sheet_name="Payments", index=False)
        except Exception as e:
            print("excel export err:" + str(e))
def _on_mouse_wheel(canv, event):
    canv.yview_scroll(-1 * int((event.delta / 120)), "units")
def clear_frame_coaches():
   for widgets in frame_bottom.winfo_children():
      widgets.destroy()
def clear_frame_actions():
   for widgets in frame_act.winfo_children():
      widgets.destroy()
def clear_frame_users():
   for widgets in frame_users_all.winfo_children():
      widgets.destroy()
def clear_frame_sch():
   for widgets in frame_sched_all.winfo_children():
      widgets.destroy()   

def set_date(text):
    ef_user_sd.delete(0,tk.END)
    ef_user_sd.insert(0,text)
    ef_user_ed.delete(0,tk.END)
    ef_user_ed.insert(0,text)
    return
def set_time(text):
    ef_sch_st.delete(0,tk.END)
    ef_sch_st.insert(0,text)
    ef_sch_et.delete(0,tk.END)
    ef_sch_et.insert(0,text)
def create_user(name, RFID, tel, schedule_id, start_d, end_d, train_amount, lvl):
    if name !='' and tel != '' and schedule_id != '' and len(session.query(User).filter_by(RFID=RFID).all()) == 0:
        usr = User(
            name=name, 
            RFID=RFID, 
            tel=tel, 
            schedule_id=session.query(Schedule).filter_by(name=schedule_id).first().id, 
            start_date=start_d, 
            end_date=end_d, 
            train_amount=train_amount, 
            user_level=lvl,
            registered_on=date.today()
            )
        session.add(usr)
        session.commit()
        if len(session.query(User).all()) > 0:
            show_users()
def ed_user_db(name, RFID, tel, schedule_id, start_d, end_d, train_amount, lvl, id):
    if name !='' and tel != '' and schedule_id != '':
        usr=session.query(User).filter_by(id=id).first()
        usr.name = name
        usr.RFID = RFID
        usr.tel = tel
        usr.schedule_id = session.query(Schedule).filter_by(name=schedule_id).first().id
        usr.start_date = start_d
        usr.end_date = end_d
        usr.train_amount = train_amount
        usr.user_level = lvl
        session.add(usr)
        session.commit()
        if len(session.query(User).all()) > 0:
            show_users()
def create_action(user_id, isentr, session):
    try:
        if user_id != '' and isentr != '':
            if session.query(User).filter_by(id=user_id).first().user_level == '':
                session.query(User).filter_by(id=user_id).first().user_level = 0
            if (int(session.query(User).filter_by(id=user_id).first().user_level) > 0) or (isentr==False):
                allowed=True
                act = Action(user_id=user_id, is_entry=isentr, allowed=allowed, action_time=datetime.now())
                session.add(act)
                session.commit()
                return True
            usr_ed = session.query(User).filter_by(id=user_id).first().end_date.split("-")[0]\
                + session.query(User).filter_by(id=user_id).first().end_date.split("-")[1]\
                    + session.query(User).filter_by(id=user_id).first().end_date.split("-")[2]
            if int(session.query(Schedule).filter_by(id=(session.query(User).filter_by(id=user_id).first().schedule_id)).first().start_time.split(":")[0]) \
            - int(datetime.now().strftime("%H")) <= 0 and \
            int(session.query(Schedule).filter_by(id=(session.query(User).filter_by(id=user_id).first().schedule_id)).first().end_time.split(":")[0]) - 1 \
            - int(datetime.now().strftime("%H")) >= 0 and \
                int(usr_ed) - int(datetime.now().strftime("%Y%m%d")) >= 0:
                if len(session.query(Action).filter_by(user_id=user_id).all()) > 0:
                    if session.query(Action).filter_by(user_id=user_id).order_by(Action.id.desc()).first().action_time.day != date.today().day and session.query(Action).filter_by(user_id=user_id).order_by(Action.id.desc()).first().allowed == True:
                        if session.query(User).filter_by(id=user_id).first().train_amount > 0:
                            amount = session.query(User).filter_by(id=user_id).first().train_amount
                            amount -= 1
                            session.query(User).filter_by(id=user_id).first().train_amount = amount
                            allowed=True
                            act = Action(user_id=user_id, is_entry=isentr, allowed=allowed, action_time=datetime.now())
                            session.add(act)
                            session.commit()
                            return True
                        else:
                            print('You should pay for enter')
                            allowed=False
                            act = Action(user_id=user_id, is_entry=isentr, allowed=allowed, action_time=datetime.now())
                            session.add(act)
                            session.commit()
                            return False
                    else:
                        allowed=True
                        act = Action(user_id=user_id, is_entry=isentr, allowed=allowed, action_time=datetime.now())
                        session.add(act)
                        session.commit()
                        return True
                else:
                    amount = session.query(User).filter_by(id=user_id).first().train_amount
                    amount -= 1
                    session.query(User).filter_by(id=user_id).first().train_amount = amount
                    allowed=True
                    act = Action(user_id=user_id, is_entry=isentr, allowed=allowed, action_time=datetime.now())
                    session.add(act)
                    session.commit()
                    return True
            else:
                print("You come not in correct time! Or ended date your allowing")
                allowed=False
                act = Action(user_id=user_id, is_entry=isentr, allowed=allowed, action_time=datetime.now())
                session.add(act)
                session.commit()
                return False
    except Exception as E:
        print("create_action exc " + str(E))

def show_actions(session):
    def inout(inna):
        if inna == False:
            return "Exit"
        else:
            return "Enter"
    def isallowed(all):
        if all:
            return "Allowed"
        else:
            return "Deny"
    clear_frame_actions()
    lbl = tk.Label(frame_act, text="ACTIONS", font=("Arial"), borderwidth=0, bg='orange')
    lbl.grid(column=0, row=0)
    col=0
    row=1
    try:
        for i in search_actions(session):
            e = tk.Label(frame_act, text=f"{session.query(User).filter_by(id=i.user_id).first().name} \
at {i.action_time.strftime('%Y-%m-%d %H:%M:%S')} \
{inout(i.is_entry)} \
left: {session.query(User).filter_by(id=i.user_id).first().train_amount} \
{isallowed(i.allowed)}", width=lbl_width*3+4, borderwidth=0)
            e.grid(row=row, column=col,padx=5, pady=5, sticky=tk.NSEW)
            col += 1
            if col % 1 == 0:
                row+=1
                col=0
    except Exception as E:
        er = tk.Label(frame_act, width=lbl_width, text="Nothing", borderwidth=0)
        er.grid(row=5, column=0, padx=5, pady=5)
        print("exc is " + str(E))
def show_payments():
    col=0
    row=1
    for i in search_payments():
        try:
            e = tk.Label(frame_pay_all, width=lbl_width*4-5, text=f"{session.query(User).filter_by(id=i.user_id).first().name} $: {i.money} at {i.action_time.strftime('%Y-%m-%d %H:%M:%S')} coach: {session.query(Coach).filter_by(id=i.coach_id).first().name}", borderwidth=0)
            e.grid(row=row, column=col,padx=5, pady=5, sticky=tk.NSEW)
            col += 1
            if col % 1 == 0:
                row+=1
                col=0
        except:
            er = tk.Label(frame_pay_all, width=lbl_width, text="Nothing", borderwidth=0)
            er.grid(row=row, column=col,padx=5, pady=5, sticky=tk.NSEW)
            col += 1
            if col % 1 == 0:
                row+=1
                col=0
def show_schedules():
    show_cl_sch()
    col=0
    row=1
    for i in search_schedule():
        try:
            e = tk.Label(frame_sched_all, text=f"{i.name}, start: {i.start_time}, end: {i.end_time}, Amount: {i.train_amount}, id: {i.id}", borderwidth=0)
            e.grid(row=row, column=col,padx=5, pady=5, sticky=tk.NSEW)
            col += 1
            if col % 1 == 0:
                row+=1
                col=0
        except:
            er = tk.Label(frame_sched_all, width=lbl_width, text="Nothing", borderwidth=0)
            er.grid(row=row, column=col,padx=5, pady=5, sticky=tk.NSEW)
            col += 1
            if col % 1 == 0:
                row+=1
                col=0
    lbl_del_c = tk.Label(frame_sched_all, width=lbl_width, text="Input id to delete", borderwidth=0)
    lbl_del_c.grid(row=997, column=0, padx=5, pady=5)
    del_entry = tk.Entry(frame_sched_all, bg="white")
    del_entry.grid(row=998, column=0, padx=5, pady=5)
    del_coach = tk.Button(frame_sched_all, text="Delete", bg="#000000", fg="#FFFFFF", command=lambda: [delete_sch(del_entry.get()), clear_frame_sch(), show_schedules()], width=10)
    del_coach.grid(row=999, column=0, padx=5, pady=5)
def show_coaches(): #показать тренеров
    col=0
    row=1
    for i in search_coach():
        try:
            e = tk.Label(frame_bottom, width=lbl_width+15, text=f"{i.name} id: {i.id}", borderwidth=0)
            e.grid(row=row, column=col,padx=5, pady=5, sticky=tk.NSEW)
            col += 1
            if col % 2 == 0:
                row+=1
                col=0
        except:
            er = tk.Label(frame_bottom, text="Nothing", borderwidth=0)
            er.grid(row=row, column=col,padx=5, pady=5, sticky=tk.NSEW)
            col += 1
            if col % 3 == 0:
                row+=1
                col=0
    lbl_del_c = tk.Label(frame_bottom, width=lbl_width, text="Input id to delete", borderwidth=0)
    lbl_del_c.grid(row=997, column=0, padx=5, pady=5)
    del_entry = tk.Entry(frame_bottom, width=lbl_width, bg="white")
    del_entry.grid(row=998, column=0, padx=5, pady=5)
    del_coach = tk.Button(frame_bottom, text="Delete", bg="#000000", fg="#FFFFFF", command=lambda: [delete_coach(del_entry.get()), clear_frame_coaches(), show_coaches()], width=10)
    del_coach.grid(row=999, column=0, padx=5, pady=5)
def edit_user():
    def search_and_input(id):
        name_user = tk.Label(editwin, text="Name", width=lbl_width, borderwidth=0)
        name_user.grid(column=0,row=1)
        
        entry_field_users = tk.Entry(editwin, bg='white', font=30)
        entry_field_users.grid(column=1, row=1)
        entry_field_users.insert(0, session.query(User).filter_by(id=id).first().name)
        rfid_user = tk.Label(editwin, text="RFID", width=lbl_width, borderwidth=0)
        rfid_user.grid(column=0,row=2)
        ef_user_rfid = tk.Entry(editwin, bg='white', font=30)
        ef_user_rfid.grid(column=1, row=2)
        ef_user_rfid.insert(0, session.query(User).filter_by(id=id).first().RFID)
        tel_user = tk.Label(editwin, text="Phone Number", width=lbl_width, borderwidth=0)
        tel_user.grid(column=0,row=3)
        ef_user_tel = tk.Entry(editwin, bg='white', font=30)
        ef_user_tel.grid(column=1, row=3)
        ef_user_tel.insert(0, session.query(User).filter_by(id=id).first().tel)
        sch_user = tk.Label(editwin, text="Schedule ID", width=lbl_width, borderwidth=0)
        sch_user.grid(column=0,row=4)
        opt_user_sch = ttk.Combobox(editwin, value=[str(_.name) for _ in session.query(Schedule.name)], width=lbl_width+12)
        opt_user_sch.current(0)
        opt_user_sch.grid(column=1, row=4)
        sd_user = tk.Label(editwin, text="Start Date", width=lbl_width, borderwidth=0)
        sd_user.grid(column=0,row=5)
        ef_user_sd = tk.Entry(editwin, bg='white', font=30)
        ef_user_sd.grid(column=1, row=5)
        ef_user_sd.insert(0, session.query(User).filter_by(id=id).first().start_date)
        ed_user = tk.Label(editwin, text="End Date", width=lbl_width, borderwidth=0)
        ed_user.grid(column=0,row=6)
        ef_user_ed = tk.Entry(editwin, bg='white', font=30)
        ef_user_ed.grid(column=1, row=6)
        ef_user_ed.insert(0, session.query(User).filter_by(id=id).first().end_date)
        ta_user = tk.Label(editwin, text="Train Amount", width=lbl_width, borderwidth=0)
        ta_user.grid(column=0,row=7)
        ef_user_ta = tk.Entry(editwin, bg='white', font=30)
        ef_user_ta.grid(column=1, row=7)
        ef_user_ta.insert(0, session.query(User).filter_by(id=id).first().train_amount)
        lvl_user = tk.Label(editwin, text="Level (def=0)", width=lbl_width, borderwidth=0)
        lvl_user.grid(column=0,row=8)
        ef_user_lvl = tk.Entry(editwin, bg='white', font=30)
        ef_user_lvl.grid(column=1, row=8)
        ef_user_lvl.insert(0, session.query(User).filter_by(id=id).first().user_level)
        Button = tk.Button(editwin, text="submit edit", 
        command=lambda: [ed_user_db(entry_field_users.get(), 
                        ef_user_rfid.get(), 
                        ef_user_tel.get(), 
                        opt_user_sch.get(), 
                        ef_user_sd.get(), 
                        ef_user_ed.get(), 
                        ef_user_ta.get(), 
                        ef_user_lvl.get(),
                        id=id),
                        clear_frame_users(),
                        show_users(),
                        ])
        Button.grid(column=1, row=10)
        Button.config(width=10, bg="#000000", fg="#FFFFFF", borderwidth=2, relief=tk.RAISED)
        Button.configure(highlightbackground='#009688')
    editwin = tk.Tk()
    editwin.geometry('450x450+350+350')
    editwin.title("Edit User window")
    editwin.configure(background="orange")
    ed_ef = tk.Entry(editwin, bg='white', font=30)
    ed_ef.insert(0, 'enter id')
    ed_ef.bind("<FocusIn>", lambda args: ed_ef.delete('0', 'end'))
    ed_ef.grid(column=0, row=0)
    ed_btn = tk.Button(editwin, text="edit", command=lambda: [search_and_input(ed_ef.get())])
    ed_btn.grid(column=1, row=0)
    ed_btn.config(width=10, bg="#000000", fg="#FFFFFF", borderwidth=2, relief=tk.RAISED)
    ed_btn.configure(highlightbackground='#009688')
    
    
    
def show_users(): #показать пользователей
    lbl = tk.Label(frame_users_all, bg="orange", text="USERS", font=("Arial"), borderwidth=0)
    lbl.grid(column=0, row=0)
    btn = tk.Button(frame_users_all, text="Edit", command=edit_user)
    btn.grid(row=0, column=1, padx=5, pady=5)
    btn.config(width=10, bg="#000000", fg="#FFFFFF", borderwidth=2, relief=tk.RAISED)
    search_btn = tk.Button(frame_users_all, text="search", command=search_show)
    search_btn.grid(column=2, row=0, padx=5, pady=5)
    search_btn.config(width=10, bg="#000000", fg="#FFFFFF", borderwidth=2, relief=tk.RAISED)
    col=0
    row=1
    for i in session.query(User).all():
        try:
            e = tk.Label(frame_users_all, text=f"""{i.name}
    id: {i.id}\n RFID: {i.RFID}\n phone: {i.tel}
    schedule: {session.query(Schedule).filter_by(id=i.schedule_id).first().name}
    start: {i.start_date}\n end: {i.end_date} 
    train amount: {i.train_amount} 
    register {i.registered_on}""", borderwidth=0)
            e.grid(row=row, column=col, padx=5, pady=5, sticky=tk.NSEW)
            col += 1
            if col % 3 == 0:
                row+=2
                col=0
        except Exception as E:
            er = tk.Label(frame_users_all, text="Nothing", borderwidth=0)
            er.grid(row=row, column=col, padx=5, pady=5, sticky=tk.NSEW)
            col += 1
            if col % 3 == 0:
                row+=1
                col=0
            print("show_users ex "+str(E))
        lbl_del = tk.Label(frame_users_all, width=lbl_width, text="Input id to delete", borderwidth=0)
        lbl_del.grid(row=999, column=0)
        del_entry = tk.Entry(frame_users_all, bg="white")
        del_entry.grid(row=999, column=1, padx=5, pady=5)
        del_usr = tk.Button(frame_users_all, bg="#000000", fg="#FFFFFF", text="Delete", command=lambda: [delete_user(del_entry.get()), clear_frame_users(), show_users()], width=10)
        del_usr.grid(row=999, column=2, padx=5, pady=5)
def search_show():
    def clear_frame_searc_user():
        for widgets in searchwin.winfo_children():
            widgets.destroy()
    def searching():
        cb_search(susers_cb.get(), ef_search.get())
    def cb_search(searchby, val):
        clear_frame_searc_user()
        col=0
        row=1
        if searchby == "by name":
            for i in session.query(User).all():
                if val.lower() in i.name.lower():
                    e = tk.Label(searchwin, text=f"""{i.name}
id: {i.id}\n RFID: {i.RFID}\n phone: {i.tel}
schedule: {session.query(Schedule).filter_by(id=i.schedule_id).first().name}
start: {i.start_date}\n end: {i.end_date} 
train amount: {i.train_amount} 
register {i.registered_on}""", borderwidth=0)
                    e.grid(row=row, column=col, padx=5, pady=5, sticky=tk.NSEW)
                    col += 1
                    if col % 3 == 0:
                        row+=1
                        col=0
                lbl_del = tk.Label(searchwin, width=lbl_width, text="Input id to delete", borderwidth=0)
                lbl_del.grid(row=997, column=0)
                del_entry = tk.Entry(searchwin, bg="white")
                del_entry.grid(row=998, column=0, padx=5, pady=5)
                del_usr = tk.Button(searchwin, bg="#000000", fg="#FFFFFF", text="Delete", command=lambda: [delete_user(del_entry.get()), clear_frame_users(), show_users()], width=10)
                del_usr.grid(row=999, column=0, padx=5, pady=5)
        if searchby == "by phone":
            for i in session.query(User).all():
                if val in i.tel:
                    e = tk.Label(searchwin, text=f"""{i.name}
id: {i.id}\n RFID: {i.RFID}\n phone: {i.tel}
schedule: {session.query(Schedule).filter_by(id=i.schedule_id).first().name}
start: {i.start_date}\n end: {i.end_date} 
train amount: {i.train_amount} 
register {i.registered_on}""", borderwidth=0)
                    e.grid(row=row, column=col, padx=5, pady=5, sticky=tk.NSEW)
                    col += 1
                    if col % 3 == 0:
                        row+=1
                        col=0
                lbl_del = tk.Label(searchwin, width=lbl_width, text="Input id to delete", borderwidth=0)
                lbl_del.grid(row=997, column=0)
                del_entry = tk.Entry(searchwin, bg="white")
                del_entry.grid(row=998, column=0, padx=5, pady=5)
                del_usr = tk.Button(searchwin, text="Delete", bg="#000000", fg="#FFFFFF", command=lambda: [delete_user(del_entry.get()), clear_frame_users(), show_users()], width=10)
                del_usr.grid(row=999, column=0, padx=5, pady=5)
        if searchby == "Search by...":
            dang = tk.Label(searchwin, text="Please choose filter", borderwidth=0)
            dang.grid(row=row, column=col, padx=5, pady=5, sticky=tk.NSEW)
    root = tk.Tk()
    root.geometry('450x450+350+350')
    root.title("Search window")
    root.configure(background="orange")
    searchwin = tk.Frame(root)
    searchwin.pack(fill="both", expand=True)
    ef_search = tk.Entry(searchwin, font=("Arial"))
    ef_search.insert(0, 'search')
    ef_search.bind("<FocusIn>", lambda args: ef_search.delete('0', 'end'))
    ef_search.grid(column=0, row=0)
    susers_cb = ttk.Combobox(searchwin, value=["by name", "by phone"])
    susers_cb.set("Search by...")
    susers_cb.grid(column=1, row=0)
    susers_btn = tk.Button(searchwin, text="search", bg="#000000", fg="#FFFFFF", command=searching)
    susers_btn.grid(column=2, row=0)
    susers_btn.config(width=10, fg='#009688', borderwidth=2, relief=tk.RAISED)

    canv_fr_search_users = tk.Frame(searchwin)
    canv_fr_search_users.place(relx=0, rely=0.10, relwidth=0.9, relheight=0.85)
    #canv_fr_pay.pack(fill=tk.BOTH, expand=1)
    #create a canvas
    canv_search_users = tk.Canvas(canv_fr_search_users, bg='orange')
    canv_search_users.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)
    #add a scrollbar to canvas
    scroll_coach = ttk.Scrollbar(canv_fr_search_users, orient=tk.VERTICAL, command=canv_search_users.yview)
    scroll_coach.pack(side=tk.RIGHT, fill=tk.Y)
    #config the canvas
    canv_search_users.configure(yscrollcommand=scroll_coach.set)
    canv_search_users.bind_all("<MouseWheel>", fp(_on_mouse_wheel, canv_search_users))
    canv_search_users.bind('<Configure>', lambda e: canv_search_users.configure(scrollregion = canv_search_users.bbox("all")))
    #create another frame inside the canvas
    searchwin = tk.Frame(canv_search_users, bg='orange')
    #add that new frame to a window in the canvas
    canv_search_users.create_window((0,0), window=searchwin, anchor="nw")
    
    searchwin.mainloop()

win = tk.Tk()
win.geometry('600x750+150+150')
win.title("Main Window") 
win.configure(background='white')
running = True

tab_parent = ttk.Notebook(win)

tab1 = ttk.Frame(tab_parent)
tab_parent.add(tab1, text="add Coach")

frame_top = tk.Frame(tab1, bg='orange', bd=5)
frame_top.place(relx=0.15, rely=0.015, relwidth=0.8, relheight=0.2)

lbl = tk.Label(frame_top, text="ADD COACH", font=("Arial"), borderwidth=0, bg="orange")
lbl.grid(column=1, row=0)

Button = tk.Button(frame_top, text="add", command=lambda: [create_coach(entry_field.get()), show_coaches()])
Button.grid(column=2, row=1)
Button.config(width=10, bg="#000000", fg="#FFFFFF", borderwidth=2, relief=tk.RAISED)
Button.configure(highlightbackground='#009688')
entry_field = tk.Entry(frame_top, bg='white', font=30)
entry_field.grid(column=1, row=1)


tab2 = ttk.Frame(tab_parent)
tab_parent.add(tab2, text="add User")

frame_users = tk.Frame(tab2, bg='orange', bd=5)
frame_users.place(relx=0.15, rely=0.015, relwidth=0.8, relheight=0.35)

lbl = tk.Label(frame_users, bg='orange', text="ADD USER", font=("Arial"), borderwidth=0)
lbl.grid(column=1, row=0)


name_user = tk.Label(frame_users, text="Name", width=lbl_width, borderwidth=0)
name_user.grid(column=0,row=1)
entry_field_users = tk.Entry(frame_users, bg='white', font=30)
entry_field_users.grid(column=1, row=1)

rfid_user = tk.Label(frame_users, text="RFID", width=lbl_width, borderwidth=0)
rfid_user.grid(column=0,row=2)
ef_user_rfid = tk.Entry(frame_users, bg='white', font=30)
ef_user_rfid.grid(column=1, row=2)

tel_user = tk.Label(frame_users, text="Phone Number", width=lbl_width, borderwidth=0)
tel_user.grid(column=0,row=3)
ef_user_tel = tk.Entry(frame_users, bg='white', font=30)
ef_user_tel.grid(column=1, row=3)

sch_user = tk.Label(frame_users, text="Schedule ID", width=lbl_width, borderwidth=0)
sch_user.grid(column=0,row=4)


sd_user = tk.Label(frame_users, text="Start Date", width=lbl_width, borderwidth=0)
sd_user.grid(column=0,row=5)
ef_user_sd = tk.Entry(frame_users, bg='white', font=30)
ef_user_sd.grid(column=1, row=5)

ed_user = tk.Label(frame_users, text="End Date", width=lbl_width, borderwidth=0)
ed_user.grid(column=0,row=6)
ef_user_ed = tk.Entry(frame_users, bg='white', font=30)
ef_user_ed.grid(column=1, row=6)

ta_user = tk.Label(frame_users, text="Train Amount", width=lbl_width, borderwidth=0)
ta_user.grid(column=0,row=7)
ef_user_ta = tk.Entry(frame_users, bg='white', font=30)
ef_user_ta.grid(column=1, row=7)

lvl_user = tk.Label(frame_users, text="Level (def=0)", width=lbl_width, borderwidth=0)
lvl_user.grid(column=0,row=8)
ef_user_lvl = tk.Entry(frame_users, bg='white', font=30)
ef_user_lvl.grid(column=1, row=8)

Button = tk.Button(frame_users, text="add", 
command=lambda: [create_user(entry_field_users.get(), 
                ef_user_rfid.get(), 
                ef_user_tel.get(), 
                opt_user_sch.get(), 
                ef_user_sd.get(), 
                ef_user_ed.get(), 
                ef_user_ta.get(), 
                ef_user_lvl.get()),
                clear_frame_users(),
                show_users()
                ])
Button.grid(column=1, row=10)
Button.config(width=10, bg="#000000", fg="#FFFFFF", borderwidth=2, relief=tk.RAISED)
Button.configure(highlightbackground='#009688')
tab3 = ttk.Frame(tab_parent)
tab_parent.add(tab3, text="add Schedule")
frame_sched = tk.Frame(tab3, bg='orange', bd=5)
frame_sched.place(relx=0.15, rely=0.015, relwidth=0.7, relheight=0.2)
frame_sched_all = tk.Frame(tab3, bg='orange', bd=5)
frame_sched_all.place(relx=0.15, rely=0.24, relwidth=0.7, relheight=0.75)

lbl = tk.Label(frame_sched, bg='orange', text="ADD SCHEDULE", font=("Arial"), borderwidth=0)
lbl.grid(column=1, row=0)
lbl = tk.Label(frame_sched, bg='orange', text="*24H-FORMAT", font=("Arial"), borderwidth=0)
lbl.grid(column=2, row=0)
lbl = tk.Label(frame_sched_all, text="SCHEDULES", bg="orange", font=("Arial"), borderwidth=0)
lbl.grid(column=0, row=0)

name_sch = tk.Label(frame_sched, text="Name", width=lbl_width, borderwidth=0)
name_sch.grid(column=0,row=1)
ef_sch = tk.Entry(frame_sched, bg='white', font=30)
ef_sch.grid(column=1, row=1)

st_sch = tk.Label(frame_sched, text="Start Time", width=lbl_width, borderwidth=0)
st_sch.grid(column=0,row=2)
ef_sch_st = tk.Entry(frame_sched, bg='white', font=30)
ef_sch_st.grid(column=1, row=2)

et_sch = tk.Label(frame_sched, text="End Time", width=lbl_width, borderwidth=0)
et_sch.grid(column=0,row=3)
ef_sch_et = tk.Entry(frame_sched, bg='white', font=30)
ef_sch_et.grid(column=1, row=3)

ta_sch = tk.Label(frame_sched, text="Train Amount", width=lbl_width, borderwidth=0)
ta_sch.grid(column=0,row=4)
ef_sch_ta = tk.Entry(frame_sched, bg='white', font=30)
ef_sch_ta.grid(column=1, row=4)

Button = tk.Button(frame_sched, text="add", command=lambda: [create_schedule(ef_sch.get(), ef_sch_st.get(), ef_sch_et.get(), ef_sch_ta.get()), show_schedules()])
Button.grid(column=1, row=10)
Button.config(width=10, pady=5, padx=5, bg="#000000", fg="#FFFFFF", borderwidth=2, relief=tk.RAISED)
Button.configure(highlightbackground='#009688')

tab4 = ttk.Frame(tab_parent)
tab_parent.add(tab4, text="add Payment")
frame_pay = tk.Frame(tab4, bg='orange', bd=5)
frame_pay.place(relx=0.15, rely=0.015, relwidth=0.7, relheight=0.3)

lbl = tk.Label(frame_pay, bg='orange', text="ADD PAYMENT", font=("Arial"), borderwidth=0)
lbl.grid(column=1, row=0)


id_pay = tk.Label(frame_pay, text="User ID", width=lbl_width, borderwidth=0)
id_pay.grid(column=0,row=1)
ef_pay = tk.Entry(frame_pay, bg='white', font=30)
ef_pay.grid(column=1, row=1)

money_pay = tk.Label(frame_pay, text="Amount of Money", width=lbl_width, borderwidth=0)
money_pay.grid(column=0,row=2)
ef_moneypay = tk.Entry(frame_pay, bg='white', font=30)
ef_moneypay.grid(column=1, row=2)

coach_pay = tk.Label(frame_pay, text="Coach ID", width=lbl_width, borderwidth=0)
coach_pay.grid(column=0,row=3)
ef_coachpay = tk.Entry(frame_pay, bg='white', font=30)
ef_coachpay.grid(column=1, row=3)

Button = tk.Button(frame_pay, text="add", command=lambda: [create_payment(ef_pay.get(), ef_moneypay.get(), ef_coachpay.get()), show_payments()])
Button.grid(column=1, row=10)
Button.config(width=10, bg="#000000", fg="#FFFFFF", borderwidth=2, relief=tk.RAISED)
Button.configure(highlightbackground='#009688')
tab5 = ttk.Frame(tab_parent)
tab_parent.add(tab5, text="Actions")

tab6 = ttk.Frame(tab_parent)
tab_parent.add(tab6, text="Settings")
settings_fr = tk.Frame(tab6)
settings_fr.place(relx=0.15, rely=0.015, relwidth=0.7, relheight=0.3)

lbl = tk.Label(settings_fr, text="EXPORT DATA", font=("Arial"), borderwidth=0)
lbl.grid(column=1, row=0)

name_exc_file = tk.Label(settings_fr, text="FILE NAME", width=lbl_width, borderwidth=0)
name_exc_file.grid(column=0,row=1)
e_f_exc_file = tk.Entry(settings_fr, bg='white', font=30)
e_f_exc_file.grid(column=1, row=1)

year_lbl = tk.Label(settings_fr, text="PLACE YEAR", width=lbl_width, borderwidth=0)
year_lbl.grid(column=0,row=2)
e_f_year_lbl = tk.Entry(settings_fr, bg='white', font=30)
e_f_year_lbl.grid(column=1, row=2)
e_f_year_lbl.insert(0, datetime.now().strftime("%Y"))
month_lbl = tk.Label(settings_fr, text="MONTH", width=lbl_width, borderwidth=0)
month_lbl.grid(column=0,row=3)
e_f_month = tk.Entry(settings_fr, bg='white', font=30)
e_f_month.grid(column=1, row=3)
e_f_month.insert(0, datetime.now().strftime("%m"))


imp_btn = tk.Button(settings_fr, text="Export data", command=lambda: [export_to_excel(e_f_exc_file.get(),
e_f_year_lbl.get(), e_f_month.get() )])
imp_btn.grid(column=1, row=15)
imp_btn.config(width=10, padx=5, pady=5, bg="#000000", fg="#FFFFFF", borderwidth=2, relief=tk.RAISED)
imp_btn.configure(highlightbackground='#006400')


drp_lbl = tk.Label(settings_fr, bg="#df4759", text="DROP ALL DATABASE", width=lbl_width + 5, borderwidth=0)
drp_lbl.grid(column=0,row=998, padx=5, pady=5)
reload_btn = tk.Button(settings_fr, text="clear all", command=drop_create_db)
reload_btn.grid(column=0, row=999, padx=5, pady=5)
reload_btn.config(width=10, bg="#df4759", fg="#FFFFFF", borderwidth=2, relief=tk.RAISED)
reload_btn.configure(highlightbackground='#006400')


#------------scrollbar to action---------------
#create frame
canv_fr_act = tk.Frame(tab5)
canv_fr_act.place(relx=0.15, rely=0.015, relwidth=0.6, relheight=0.9)
#create a canvas
canv_act = tk.Canvas(canv_fr_act, bg="orange")
canv_act.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)
#add a scrollbar to canvas
scroll_act = ttk.Scrollbar(canv_fr_act, orient=tk.VERTICAL, command=canv_act.yview)
scroll_act.pack(side=tk.RIGHT, fill=tk.Y)
#config the canvas
canv_act.configure(yscrollcommand=scroll_act.set)
canv_act.bind("<MouseWheel>", fp(_on_mouse_wheel, canv_act))    
canv_act.bind('<Configure>', lambda e: canv_act.configure(scrollregion = canv_act.bbox("all")))
#create another frame inside the canvas
frame_act = tk.Frame(canv_act, bg='orange')
#add that new frame to a window in the canvas
canv_act.create_window((0,0), window=frame_act, anchor="nw")


canv_fr_pay = tk.Frame(tab4)
canv_fr_pay.place(relx=0.15, rely=0.35, relwidth=0.7, relheight=0.65)
#create a canvas
canv_pay = tk.Canvas(canv_fr_pay, bg='orange')
canv_pay.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)
#add a scrollbar to canvas
scroll_pay = ttk.Scrollbar(canv_fr_pay, orient=tk.VERTICAL, command=canv_pay.yview)
scroll_pay.pack(side=tk.RIGHT, fill=tk.Y)
#config the canvas
canv_pay.configure(yscrollcommand=scroll_act.set)
canv_pay.bind("<MouseWheel>", fp(_on_mouse_wheel, canv_pay))
canv_pay.bind('<Configure>', lambda e: canv_pay.configure(scrollregion = canv_pay.bbox("all")))
#create another frame inside the canvas
frame_pay_all = tk.Frame(canv_pay, bg='orange')
#add that new frame to a window in the canvas
canv_pay.create_window((0,0), window=frame_pay_all, anchor="nw")
lbl = tk.Label(frame_pay_all, text="PAYMENTS", bg="orange", font=("Arial"), borderwidth=0)
lbl.grid(column=0, row=0)


canv_fr_user = tk.Frame(tab2)
canv_fr_user.place(relx=0.15, rely=0.40, relwidth=0.8, relheight=0.6)
#canv_fr_pay.pack(fill=tk.BOTH, expand=1)
#create a canvas
canv_user = tk.Canvas(canv_fr_user, bg='orange')
canv_user.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)
#add a scrollbar to canvas
scroll_user = ttk.Scrollbar(canv_fr_user, orient=tk.VERTICAL, command=canv_user.yview)
scroll_user.pack(side=tk.RIGHT, fill=tk.Y)
#config the canvas
canv_user.configure(yscrollcommand=scroll_user.set)
canv_user.bind("<MouseWheel>", fp(_on_mouse_wheel, canv_user))
canv_user.bind('<Configure>', lambda e: canv_user.configure(scrollregion = canv_user.bbox("all")))
#create another frame inside the canvas
frame_users_all = tk.Frame(canv_user, bg='orange')
#add that new frame to a window in the canvas
canv_user.create_window((0,0), window=frame_users_all, anchor="nw")

lbl = tk.Label(frame_users_all, bg="orange", text="Users", font=("Arial"), borderwidth=0)
lbl.grid(column=0, row=0)


canv_fr_coach = tk.Frame(tab1)
canv_fr_coach.place(relx=0.15, rely=0.30, relwidth=0.8, relheight=0.7)
#canv_fr_pay.pack(fill=tk.BOTH, expand=1)
#create a canvas
canv_coach = tk.Canvas(canv_fr_coach, bg='orange')
canv_coach.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)
#add a scrollbar to canvas
scroll_coach = ttk.Scrollbar(canv_fr_coach, orient=tk.VERTICAL, command=canv_coach.yview)
scroll_coach.pack(side=tk.RIGHT, fill=tk.Y)
#config the canvas
canv_coach.configure(yscrollcommand=scroll_coach.set)
canv_coach.bind_all("<MouseWheel>", fp(_on_mouse_wheel, canv_coach))
canv_coach.bind('<Configure>', lambda e: canv_coach.configure(scrollregion = canv_coach.bbox("all")))
#create another frame inside the canvas
frame_bottom = tk.Frame(canv_coach, bg='orange')
#add that new frame to a window in the canvas
canv_coach.create_window((0,0), window=frame_bottom, anchor="nw")


lbl = tk.Label(frame_bottom, bg="orange", text="COACHES", font=("Arial"), borderwidth=0)
lbl.grid(column=0, row=0)


tab_parent.pack(expand=1, fill='both')

try:
    opt_user_sch = ttk.Combobox(frame_users, value=[str(_.id) for _ in session.query(Schedule.id)], width=lbl_width+12)
    opt_user_sch.current(0)
    opt_user_sch.grid(column=1, row=4)
except:
    opt_user_sch = ttk.Combobox(frame_users, value=["please add schedule"], width=lbl_width+12)
    opt_user_sch.current(0)
    opt_user_sch.grid(column=1, row=4)
#scrollY = tk.Scrollbar(frame_act, orient=tk.VERTICAL, command=lbl.yview)
#scrollY.grid(row=0, column=1, sticky=tk.N+tk.S)
clear_frame_sch

show_actions(session)
show_coaches()
show_users()
set_date(date.today())
set_time(time().strftime("%H:%M"))
show_schedules()
show_payments()
show_cl_sch()

comPorts = []
serialPorts = ['COM3']#, 'COM25','/dev/ttyACM0','/dev/ttyACM1','/dev/ttyACM2','/dev/ttyACM3','/dev/ttyUSB0','/dev/ttyUSB1','/dev/ttyUSB2','/dev/ttyUSB3']
for port in serialPorts:
    try:
        arduino_port = serial.Serial(port, baudrate=9600,
                                    parity=serial.PARITY_NONE,
                                    stopbits=serial.STOPBITS_ONE,
                                    bytesize=serial.EIGHTBITS,
                                    timeout=0.04)
        comPorts.append(arduino_port)
    except Exception as E:
        print(str(E))

def serialThread1():
    global running
    meta = MetaData()
    Base = declarative_base()
    engine = create_engine("sqlite:///fitness.db", echo=True)
    Session = sessionmaker(bind=engine)
    session = Session()
    while running:
        serialThread(comPorts, session)
def serialThread(comPorts, session):
    #global win, comPorts,timers,stdPhotos,actions,dataforserver,readRFID,open_users_elements
    portIndex = -1
    # comError = range(len(comPorts))
    for comPort in comPorts:
        portIndex = portIndex + 1
        try:
            rec = str(comPort.readline())
            
            if len(rec) > 4:
                rec=rec.strip()
                data= rec.strip().split('#')
                if len(data) > 3: 
                    dev_id =int(data[1])
                    index = dev_id - 1
                    RFID = data[2].strip().upper()
                    gate = int(data[3])
                    if RFID == "TEST" or RFID == "RESET":
                        date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        
                        # comError[portIndex] = 0
                    else:
                        if gate != 1:#1-come,0-leave
                            gate = False
                            index = dev_id - 1 + 4
                        else:
                            gate = True
                        #timers[index] = maxtime   
                        # comError[portIndex] = 0
                        try:
                            #session = Session()
                            usr = session.query(User).filter_by(RFID=RFID).first()
                            if usr.id==None:
                                if usr.RFID!=None:
                                    print("Net usera id")
                                else:
                                    #stdNames[index].config(text="Aniqlanmagan")
                                    comPort.write(str.encode("@"+str(dev_id)+"$ERROR&"+str(gate) + '*\n'))
                            else:
                                print(f'ID={usr.id}, gate={gate}, {session}')
                                if create_action(usr.id, gate, session):
                                    comPort.write(str.encode("@"+str(dev_id)+"$OK&"+str(gate) + '*\n'))
                                else:
                                    print("OTKAZANO")
                                show_actions(session)
                               # setAttendace()
                               # stdNames[index].config(text=name+"\n"+group_id)
                          
                        except Exception as ex:  
                            print(str(ex))
                           # stdNames[index].config(text="Aniqlanmagan")
                           # stdPhotos[index].config(image=unknownImg)
                           # stdPhotos[index].image = unknownImg   
        except Exception as ex:
            # if comError[portIndex] > 60:
            #      comError[portIndex] = 0
            #      print("abort:" + str(comPorts.pop(portIndex)))
            #      reboot()
            print("Serial thread:" + str(ex))
thread = threading.Thread(target=serialThread1)
thread.start()
def on_closing():
    session.close()
    global running
    running = False
    win.destroy()

show_users()
win.protocol("WM_DELETE_WINDOW", on_closing)
win.mainloop()
thread.join()