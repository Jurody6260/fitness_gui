import tkinter as tk

from tkinter import ttk, messagebox
from models import *
import calendar
import functools
fp = functools.partial
lbl_width = 15
lbl_font = 20


def drop_create_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


def set_train_amount(event):
    ef_user_ta.delete(0, tk.END)
    ef_user_ta.insert(0, session.query(Schedule).filter_by(
        name=opt_user_sch.get()).first().train_amount)


def show_cl_sch():
    global opt_user_sch
    try:
        opt_user_sch = ttk.Combobox(frame_users, state="readonly", value=[str(
            _.name) for _ in session.query(Schedule.name)], width=lbl_width+12)
        opt_user_sch.current(0)
        opt_user_sch.grid(column=1, row=4)
        opt_user_sch.bind("<<ComboboxSelected>>", set_train_amount)
    except:
        opt_user_sch = ttk.Combobox(
            frame_users, value=["please add schedule"], width=lbl_width+12)
        opt_user_sch.current(0)
        opt_user_sch.grid(column=1, row=4)


def export_to_excelv2(fname, year, month):
    if fname != '':
        try:
            mon, year = int(month), int(year)
            writer = pd.ExcelWriter(fname + '.xlsx')
            session.query(Action).filter(Action.action_time)
            num_days = calendar.monthrange(year, mon)[1]
            # start_date = date(year, mon, 1)
            # end_date = date(year, mon, num_days)
            # users = session.query(User)
            # action_table = pd.read_sql_table('action', engine, columns=[
            #                                  "action_time", "is_entry", "allowed", "user_id"])
            uuids = []
            for id in session.query(Action.user_id).all():
                if id.user_id not in uuids:
                    uuids.append(id.user_id)
            dfs = []
            uuids.sort()
            for id in uuids:
                df = pd.DataFrame({'User ID': [id]})
                df["name"] = str(session.query(
                    User).filter_by(id=id).first().name)
                for day in range(1, num_days + 1):
                    def in_out_timing():
                        filtertimsesT = session.query(Action).filter(and_(Action.user_id == id, func.DATE(
                            Action.action_time) == f"{year}-{month}-{day if len(str(day)) > 1 else '0' + str(day)}", Action.is_entry == True))
                        filtertimsesF = session.query(Action).filter(and_(Action.user_id == id, func.DATE(
                            Action.action_time) == f"{year}-{month}-{day if len(str(day)) > 1 else '0' + str(day)}", Action.is_entry == False))
                        if len(filtertimsesT.all()) >= 1:
                            intim = filtertimsesT.order_by(
                                Action.id).first().action_time.strftime("%H:%M:%S")
                            if len(filtertimsesF.all()) >= 1:
                                outtim = filtertimsesF.order_by(
                                    Action.id.desc()).first().action_time.strftime("%H:%M:%S")
                                return intim + ' / ' + outtim
                            elif len(filtertimsesF.all()) == 0:
                                return intim + ' / ' + "-"
                        elif len(filtertimsesT.all()) == 0 and len(filtertimsesF.all()) >= 1:
                            outtim = filtertimsesF.order_by(
                                Action.id.desc()).first().action_time.strftime("%H:%M:%S")
                            return "-" + ' / ' + outtim
                        else:
                            return "- / -"
                    try:
                        if not session.query(Action).filter(and_(Action.user_id == id, func.DATE(Action.action_time) == f"{year}-{month}-{day if len(str(day)) > 1 else '0' + str(day)}")).order_by(Action.action_time).first():
                            df[str(day) + ' ' +
                               calendar.month_name[mon]] = "- / -"
                        else:
                            df[str(day) + ' ' + calendar.month_name[mon]
                               ] = in_out_timing()

                    except Exception as e:
                        print("EX: " + str(e))
                dfs.append(df)
                del df
                with pd.ExcelWriter(fname + '.xlsx') as writer:
                    sr = 1
                    dfs[0].to_excel(writer, sheet_name="Actions", index=False)
                    for a in range(len(dfs)):
                        dfs[a].to_excel(
                            writer, startrow=sr, sheet_name="Actions", index=False, header=False)
                        sr += 1
        except Exception as e:
            print(str(e))


def export_to_excel_pay(fname, year, month, day):
    if fname != '':
        try:
            da = f"{year}-{month}-{day}"
            year, month, day = int(year), int(month), int(day)
            payment_results = session.query(Payment).filter(
                func.DATE(Payment.action_time) == da)
            writer = pd.ExcelWriter(fname + '.xlsx')
            df = pd.DataFrame()
            # action_table = pd.read_sql_table('action', engine, columns=["action_time", "is_entry", "allowed", "user_id"])
            # payment_table = pd.read_sql_table('payment', engine, columns=["money","action_time", "coach_id", "user_id"])
            # user_table = pd.read_sql_table('user', engine, columns=["id", "name"])
            # df = pd.merge(user_table, action_table, left_on="id", right_on="user_id", how="right")
            # df1 = pd.merge(user_table, payment_table, left_on="id", right_on="user_id", how="right")
            # df2 = pd.read_sql(str(action_results), engine, params=[start_date, end_date], columns=["action_time", "is_entry", "allowed", "user_id"])
            # for i, row in df2.iterrows():
            #     df2['action_is_entry'] = df2['action_is_entry'].apply(str)
            #     df2['action_is_entry'] = df2['action_is_entry'].astype(str)
            #     df2 = df2.applymap(str)
            #     enter = "Enter"
            #     allow = "Allowed"
            #     print(i)
            #     print(row)
            #     if row["action_is_entry"] == 0:
            #         enter = "Left"
            #     if row["action_allowed"] == 0:
            #         allow = "Deny"
            #     df2.at[i,"action_user_id"] = session.query(User).filter_by(id=row["action_user_id"]).first().name
            #     df2.at[i,'action_is_entry'] = enter
            #     df2.at[i,'action_allowed'] = allow
            d = f"{year}, {month}, {day}"
            df3 = pd.read_sql_query(str(payment_results), engine, params=[da])
            for i, row in df3.iterrows():
                df3['payment_user_id'] = df3['payment_user_id'].apply(str)
                df3['payment_user_id'] = df3['payment_user_id'].astype(str)
                df3 = df3.applymap(str)
                df3.at[i, "payment_coach_id"] = session.query(
                    Coach).filter_by(id=row["payment_coach_id"]).first().name
                df3.at[i, "payment_user_id"] = session.query(
                    User).filter_by(id=row["payment_user_id"]).first().name
                df3.at[i, "payment_action_time"] = df3.at[i, "payment_action_time"].split()[
                    1].split(".")[0]
                # df3["payment_user_id"] = df3["User's Name"]
                # df3["payment_coach_id"] = df3["Coach's Name"]
            df = df3.rename(columns={'payment_user_id': "User's Name",
                            "payment_action_time": 'Action Time', "payment_coach_id": "Coach's Name"}, inplace=False)
            with writer:
                df.to_excel(writer, sheet_name="Payments", index=False)
        except Exception as e:
            print("excel export err:" + str(e))


def _on_mouse_wheel(canv, event):
    canv.yview_scroll(-1 * int((event.delta / 60)), "units")


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
    ef_user_sd.delete(0, tk.END)
    ef_user_sd.insert(0, text)
    ef_user_ed.delete(0, tk.END)
    ef_user_ed.insert(0, text)
    return


def set_time(text):
    ef_sch_st.delete(0, tk.END)
    ef_sch_st.insert(0, text)
    ef_sch_et.delete(0, tk.END)
    ef_sch_et.insert(0, text)


def create_user(name, RFID, tel, schedule_id, start_d, end_d, train_amount, lvl, session):
    if name != '' and len(start_d.split('-')) == 3 and len(end_d.split('-')) == 3 and schedule_id != '' and len(session.query(User).filter_by(RFID=RFID).all()) == 0:
        usr = User(
            name=name,
            RFID=RFID,
            tel=tel,
            schedule_id=session.query(Schedule).filter_by(
                name=schedule_id).first().id,
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
        entry_field_users.delete(0, tk.END)
        ef_user_rfid.delete(0, tk.END)
        ef_user_tel.delete(0, tk.END)


def ed_user_db(name, RFID, tel, schedule_id, start_d, end_d, train_amount, lvl, id, session):
    if name != '' and tel != '' and schedule_id != '':
        usr = session.query(User).filter_by(id=id).first()
        usr.name = name
        usr.RFID = RFID
        usr.tel = tel
        usr.schedule_id = session.query(
            Schedule).filter_by(name=schedule_id).first().id
        usr.start_date = start_d
        usr.end_date = end_d
        usr.train_amount = train_amount
        usr.user_level = lvl
        session.add(usr)
        session.commit()
        print(session.query(User).filter_by(id=id).first().RFID)
        if len(session.query(User).all()) > 0:
            show_users()


def create_action(user_id, isentr, session):
    try:
        if user_id != '' and isentr != '':
            if session.query(User).filter_by(id=user_id).first().user_level == '':
                session.query(User).filter_by(
                    id=user_id).first().user_level = 0
            if (int(session.query(User).filter_by(id=user_id).first().user_level) > 0) or (isentr == False):
                allowed = True
                act = Action(user_id=user_id, is_entry=isentr,
                             allowed=allowed, action_time=datetime.now())
                session.add(act)
                session.commit()
                return True
            usr_date_come = session.query(User).filter_by(
                id=user_id).first().end_date.split("-")
            usr_ed = usr_date_come[0] + usr_date_come[1] + usr_date_come[2]
            if int(session.query(Schedule).filter_by(id=(session.query(User).filter_by(id=user_id).first().schedule_id)).first().start_time.split(":")[0]) \
                    - int(datetime.now().strftime("%H")) <= 0 and \
                    int(session.query(Schedule).filter_by(id=(session.query(User).filter_by(id=user_id).first().schedule_id)).first().end_time.split(":")[0]) - 1 \
                    - int(datetime.now().strftime("%H")) >= 0 and \
                    int(usr_ed) - int(datetime.now().strftime("%Y%m%d")) >= 0:
                if session.query(Action).filter_by(user_id=user_id).first():
                    if session.query(Action).filter_by(user_id=user_id).order_by(Action.id.desc()).first().action_time.day != date.today().day and session.query(Action).filter_by(user_id=user_id).order_by(Action.id.desc()).first().allowed == True:
                        if session.query(User).filter_by(id=user_id).first().train_amount > 0:
                            amount = session.query(User).filter_by(
                                id=user_id).first().train_amount
                            amount -= 1
                            session.query(User).filter_by(
                                id=user_id).first().train_amount = amount
                            allowed = True
                            act = Action(user_id=user_id, is_entry=isentr,
                                         allowed=allowed, action_time=datetime.now())
                            session.add(act)
                            session.commit()
                            return True
                        else:
                            print('?????????????????????? ??????????????????')
                            allowed = False
                            act = Action(user_id=user_id, is_entry=isentr,
                                         allowed=allowed, action_time=datetime.now())
                            session.add(act)
                            session.commit()
                            return False
                    else:
                        allowed = False
                        act = Action(user_id=user_id, is_entry=isentr,
                                     allowed=allowed, action_time=datetime.now())
                        session.add(act)
                        session.commit()
                        print("?????????????? ?????????? ???????????? ?????? ???? ????????. ????????????????.")
                        return False
                else:
                    amount = session.query(User).filter_by(
                        id=user_id).first().train_amount
                    amount -= 1
                    session.query(User).filter_by(
                        id=user_id).first().train_amount = amount
                    allowed = True
                    act = Action(user_id=user_id, is_entry=isentr,
                                 allowed=allowed, action_time=datetime.now())
                    session.add(act)
                    session.commit()
                    return True
            else:
                print("???? ???????????? ???? ???? ???????????? ????????????????????. ????????????????????:" + session.query(Schedule).filter_by(id=(session.query(
                    User).filter_by(id=user_id).first().schedule_id)).first().name + ". ?????? ???????????????????? ???????? ???????????????? ????????????????????")
                allowed = False
                act = Action(user_id=user_id, is_entry=isentr,
                             allowed=allowed, action_time=datetime.now())
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
    lbl = tk.Label(frame_act, text="ACTIONS", font=(
        "Arial"), borderwidth=0, bg='orange')
    lbl.grid(column=0, row=0)
    col = 0
    row = 1
    try:
        for i in search_actions(session):
            e = tk.Label(frame_act, text=f"{session.query(User).filter_by(id=i.user_id).first().name} \
at {i.action_time.strftime('%Y-%m-%d %H:%M:%S')} \
{inout(i.is_entry)} \
left: {session.query(User).filter_by(id=i.user_id).first().train_amount} \
{isallowed(i.allowed)}", width=lbl_width*4, font=(lbl_font), borderwidth=0)
            e.grid(row=row, column=col, padx=5, pady=5, sticky=tk.NSEW)
            col += 1
            if col % 1 == 0:
                row += 1
                col = 0
    except Exception as E:
        er = tk.Label(frame_act, width=lbl_width,
                      text="Nothing", borderwidth=0)
        er.grid(row=5, column=0, padx=5, pady=5)
        print("exc is " + str(E))


def show_payments():
    col = 0
    row = 1
    for i in search_payments():
        try:
            e = tk.Label(frame_pay_all, width=lbl_width*4,
                         text=f"{session.query(User).filter_by(id=i.user_id).first().name} $: {i.money} at {i.action_time.strftime('%Y-%m-%d %H:%M:%S')} coach: {session.query(Coach).filter_by(id=i.coach_id).first().name}", font=(lbl_font), borderwidth=0)
            e.grid(row=row, column=col, padx=5, pady=5, sticky=tk.NSEW)
            col += 1
            if col % 1 == 0:
                row += 1
                col = 0
        except:
            er = tk.Label(frame_pay_all, width=lbl_width,
                          text="Nothing", borderwidth=0)
            er.grid(row=row, column=col, padx=5, pady=5, sticky=tk.NSEW)
            col += 1
            if col % 1 == 0:
                row += 1
                col = 0


def show_schedules():
    show_cl_sch()
    col = 0
    row = 1
    for i in search_schedule():
        try:
            e = tk.Label(frame_sched_all, text=f"{i.name} start: {i.start_time} end: {i.end_time} Amount: {i.train_amount} id: {i.id}",
                         width=lbl_width*4, font=(lbl_font), borderwidth=0)
            e.grid(row=row, column=col, padx=5, pady=5, sticky=tk.NSEW)
            col += 1
            if col % 1 == 0:
                row += 1
                col = 0
        except:
            er = tk.Label(frame_sched_all, width=lbl_width,
                          text="Nothing", borderwidth=0)
            er.grid(row=row, column=col, padx=5, pady=5, sticky=tk.NSEW)
            col += 1
            if col % 1 == 0:
                row += 1
                col = 0
    lbl_del_c = tk.Label(frame_sched_all, width=lbl_width,
                         text="Input id to delete", borderwidth=0)
    lbl_del_c.grid(row=997, column=0, padx=5, pady=5)
    del_entry = tk.Entry(frame_sched_all, bg="white")
    del_entry.grid(row=998, column=0, padx=5, pady=5)
    del_coach = tk.Button(frame_sched_all, text="Delete", bg="#000000", fg="#FFFFFF", command=lambda: [
                          delete_sch(del_entry.get()), clear_frame_sch(), show_schedules(), show_users()], width=10)
    del_coach.grid(row=999, column=0, padx=5, pady=5)


def show_coaches():  # ???????????????? ????????????????
    col = 0
    row = 1
    for i in search_coach():
        try:
            e = tk.Label(frame_bottom, width=lbl_width+15,
                         text=f"{i.name} id: {i.id}", font=(lbl_font), borderwidth=0)
            e.grid(row=row, column=col, padx=5, pady=5, sticky=tk.NSEW)
            col += 1
            if col % 2 == 0:
                row += 1
                col = 0
        except:
            er = tk.Label(frame_bottom, text="Nothing", borderwidth=0)
            er.grid(row=row, column=col, padx=5, pady=5, sticky=tk.NSEW)
            col += 1
            if col % 3 == 0:
                row += 1
                col = 0
    lbl_del_c = tk.Label(frame_bottom, width=lbl_width,
                         text="Input id to delete", borderwidth=0)
    lbl_del_c.grid(row=997, column=0, padx=5, pady=5)
    del_entry = tk.Entry(frame_bottom, width=lbl_width, bg="white")
    del_entry.grid(row=998, column=0, padx=5, pady=5)
    del_coach = tk.Button(frame_bottom, text="Delete", bg="#000000", fg="#FFFFFF", command=lambda: [
                          delete_coach(del_entry.get()), clear_frame_coaches(), show_coaches()], width=10)
    del_coach.grid(row=999, column=0, padx=5, pady=5)


def message_box():
    messagebox.showinfo("Info", '????????????????')


def edit_user():
    def search_and_input(id):
        name_user = tk.Label(editwin, text="Name",
                             width=lbl_width, borderwidth=0)
        name_user.grid(column=0, row=1)

        entry_field_users = tk.Entry(editwin, bg='white', font=(lbl_font))
        entry_field_users.grid(column=1, row=1)
        entry_field_users.insert(0, session.query(
            User).filter_by(id=id).first().name)
        rfid_user = tk.Label(editwin, text="RFID",
                             width=lbl_width, borderwidth=0)
        rfid_user.grid(column=0, row=2)
        ef_user_rfid = tk.Entry(editwin, bg='white', font=(lbl_font))
        ef_user_rfid.grid(column=1, row=2)
        ef_user_rfid.insert(0, session.query(
            User).filter_by(id=id).first().RFID)
        tel_user = tk.Label(editwin, text="Phone Number",
                            width=lbl_width, borderwidth=0)
        tel_user.grid(column=0, row=3)
        ef_user_tel = tk.Entry(editwin, bg='white', font=(lbl_font))
        ef_user_tel.grid(column=1, row=3)
        ef_user_tel.insert(0, session.query(User).filter_by(id=id).first().tel)
        sch_user = tk.Label(editwin, text="Schedule ID",
                            width=lbl_width, borderwidth=0)
        sch_user.grid(column=0, row=4)
        opt_user_sch = ttk.Combobox(editwin, state="readonly", value=[str(
            _.name) for _ in session.query(Schedule.name)], width=lbl_width+12)
        len(session.query(Schedule).all())

        opt_user_sch.current(0)
        for i in range(len(session.query(Schedule).all())):
            opt_user_sch.current(i)
            if opt_user_sch.get() == session.query(Schedule).filter_by(id=session.query(User).filter_by(id=id).first().schedule_id).first().name:
                break
        opt_user_sch.grid(column=1, row=4)
        sd_user = tk.Label(editwin, text="Start Date",
                           width=lbl_width, borderwidth=0)
        sd_user.grid(column=0, row=5)
        ef_user_sd = tk.Entry(editwin, bg='white', font=(lbl_font))
        ef_user_sd.grid(column=1, row=5)
        ef_user_sd.insert(0, session.query(
            User).filter_by(id=id).first().start_date)
        ed_user = tk.Label(editwin, text="End Date",
                           width=lbl_width, borderwidth=0)
        ed_user.grid(column=0, row=6)
        ef_user_ed = tk.Entry(editwin, bg='white', font=(lbl_font))
        ef_user_ed.grid(column=1, row=6)
        ef_user_ed.insert(0, session.query(
            User).filter_by(id=id).first().end_date)
        ta_user = tk.Label(editwin, text="Train Amount",
                           width=lbl_width, borderwidth=0)
        ta_user.grid(column=0, row=7)
        ef_user_ta = tk.Entry(editwin, bg='white', font=(lbl_font))
        ef_user_ta.grid(column=1, row=7)
        ef_user_ta.insert(0, session.query(
            User).filter_by(id=id).first().train_amount)
        lvl_user = tk.Label(editwin, text="Level (def=0)",
                            width=lbl_width, borderwidth=0)
        lvl_user.grid(column=0, row=8)
        ef_user_lvl = tk.Entry(editwin, bg='white', font=(lbl_font))
        ef_user_lvl.grid(column=1, row=8)
        ef_user_lvl.insert(0, session.query(
            User).filter_by(id=id).first().user_level)
        Button = tk.Button(editwin, text="submit edit",
                           command=lambda: [ed_user_db(entry_field_users.get(),
                                                       ef_user_rfid.get(),
                                                       ef_user_tel.get(),
                                                       opt_user_sch.get(),
                                                       ef_user_sd.get(),
                                                       ef_user_ed.get(),
                                                       ef_user_ta.get(),
                                                       ef_user_lvl.get(),
                                                       id, session),
                                            clear_frame_users(),
                                            show_users(),
                                            message_box()
                                            ])
        Button.grid(column=1, row=10)
        Button.config(width=10, bg="#000000", fg="#FFFFFF",
                      borderwidth=2, relief=tk.RAISED)
        Button.configure(highlightbackground='#009688')
    editwin = tk.Tk()
    editwin.geometry('450x450+550+350')
    editwin.title("Edit User window")
    editwin.configure(background="orange")
    ed_ef = tk.Entry(editwin, bg='white', font=30)
    ed_ef.insert(0, 'enter id')
    ed_ef.bind("<FocusIn>", lambda args: ed_ef.delete('0', 'end'))
    ed_ef.grid(column=0, row=0)
    ed_btn = tk.Button(editwin, text="edit", command=lambda: [
                       search_and_input(ed_ef.get())])
    ed_btn.grid(column=1, row=0)
    ed_btn.config(width=10, bg="#000000", fg="#FFFFFF",
                  borderwidth=2, relief=tk.RAISED)
    ed_btn.configure(highlightbackground='#009688')


def show_users():  # ???????????????? ??????????????????????????
    lbl = tk.Label(frame_users_all, bg="orange", text="USERS",
                   font=("Arial"), borderwidth=0)
    lbl.grid(column=0, row=0)
    btn = tk.Button(frame_users_all, text="Edit", command=edit_user)
    btn.grid(row=0, column=1, padx=5, pady=5)
    btn.config(width=10, bg="#000000", fg="#FFFFFF",
               borderwidth=2, relief=tk.RAISED)
    search_btn = tk.Button(frame_users_all, text="search", command=search_show)
    search_btn.grid(column=2, row=0, padx=5, pady=5)
    search_btn.config(width=10, bg="#000000", fg="#FFFFFF",
                      borderwidth=2, relief=tk.RAISED)
    col = 0
    row = 1
    for i in session.query(User).order_by(User.id.desc()).all():
        try:
            e = tk.Label(frame_users_all, text=f"""{i.name}
    id: {i.id}\n RFID: {i.RFID}\n phone: {i.tel}
    schedule: {session.query(Schedule).filter_by(id=i.schedule_id).first().name}
    start: {i.start_date}\n end: {i.end_date} 
    train amount: {i.train_amount} 
    register {i.registered_on}""", borderwidth=0, font=(lbl_font))
            e.grid(row=row, column=col, padx=5, pady=5, sticky=tk.NSEW)
            col += 1
            if col % 3 == 0:
                row += 2
                col = 0
        except Exception as E:
            er = tk.Label(frame_users_all, text="Nothing", borderwidth=0)
            er.grid(row=row, column=col, padx=5, pady=5, sticky=tk.NSEW)
            col += 1
            if col % 3 == 0:
                row += 1
                col = 0
            print("show_users ex "+str(E))
        lbl_del = tk.Label(frame_users_all, width=lbl_width,
                           text="Input id to delete", borderwidth=0)
        lbl_del.grid(row=999, column=0)
        del_entry = tk.Entry(frame_users_all, bg="white")
        del_entry.grid(row=999, column=1, padx=5, pady=5)
        del_usr = tk.Button(frame_users_all, bg="#000000", fg="#FFFFFF", text="Delete", command=lambda: [
                            delete_user(del_entry.get()), clear_frame_users(), show_users()], width=10)
        del_usr.grid(row=999, column=2, padx=5, pady=5)


def search_show():
    def clear_frame_searc_user():
        for widgets in searchwin.winfo_children():
            widgets.destroy()

    def searching():
        cb_search(susers_cb.get(), ef_search.get())

    def cb_search(searchby, val):
        clear_frame_searc_user()
        col = 0
        row = 1
        if searchby == "by name":
            for i in session.query(User).all():
                if val.lower() in i.name.lower():
                    e = tk.Label(searchwin, text=f"""{i.name}
id: {i.id}\n RFID: {i.RFID}\n phone: {i.tel}
schedule: {session.query(Schedule).filter_by(id=i.schedule_id).first().name}
start: {i.start_date}\n end: {i.end_date} 
train amount: {i.train_amount} 
register {i.registered_on}""", font=(lbl_font), borderwidth=0)
                    e.grid(row=row, column=col, padx=5, pady=5, sticky=tk.NSEW)
                    col += 1
                    if col % 3 == 0:
                        row += 1
                        col = 0
                lbl_del = tk.Label(searchwin, width=lbl_width,
                                   text="Input id to delete", borderwidth=0)
                lbl_del.grid(row=997, column=0)
                del_entry = tk.Entry(searchwin, bg="white")
                del_entry.grid(row=998, column=0, padx=5, pady=5)
                del_usr = tk.Button(searchwin, bg="#000000", fg="#FFFFFF", text="Delete", command=lambda: [
                                    delete_user(del_entry.get()), clear_frame_users(), show_users()], width=10)
                del_usr.grid(row=999, column=0, padx=5, pady=5)
        if searchby == "by phone":
            for i in session.query(User).all():
                if val in i.tel:
                    e = tk.Label(searchwin, text=f"""{i.name}
id: {i.id}\n RFID: {i.RFID}\n phone: {i.tel}
schedule: {session.query(Schedule).filter_by(id=i.schedule_id).first().name}
start: {i.start_date}\n end: {i.end_date} 
train amount: {i.train_amount} 
register {i.registered_on}""", font=(lbl_font), borderwidth=0)
                    e.grid(row=row, column=col, padx=5, pady=5, sticky=tk.NSEW)
                    col += 1
                    if col % 3 == 0:
                        row += 1
                        col = 0
                lbl_del = tk.Label(searchwin, width=lbl_width,
                                   text="Input id to delete", borderwidth=0)
                lbl_del.grid(row=997, column=0)
                del_entry = tk.Entry(searchwin, bg="white")
                del_entry.grid(row=998, column=0, padx=5, pady=5)
                del_usr = tk.Button(searchwin, text="Delete", bg="#000000", fg="#FFFFFF", command=lambda: [
                                    delete_user(del_entry.get()), clear_frame_users(), show_users()], width=10)
                del_usr.grid(row=999, column=0, padx=5, pady=5)
        if searchby == "Search by...":
            dang = tk.Label(
                searchwin, text="Please choose filter", borderwidth=0)
            dang.grid(row=row, column=col, padx=5, pady=5, sticky=tk.NSEW)
    root = tk.Tk()
    root.geometry('650x450+450+350')
    root.title("Search window")
    root.configure(background="orange")
    searchwin = tk.Frame(root)
    searchwin.pack(fill="both", expand=True)
    ef_search = tk.Entry(searchwin, font=("Arial"))
    ef_search.insert(0, 'search')
    ef_search.bind("<FocusIn>", lambda args: ef_search.delete('0', 'end'))
    ef_search.grid(column=0, row=0)
    susers_cb = ttk.Combobox(searchwin, state="readonly", value=[
                             "by name", "by phone"])
    susers_cb.set("Search by...")
    susers_cb.grid(column=1, row=0)
    susers_btn = tk.Button(searchwin, text="search",
                           bg="#000000", fg="#FFFFFF", command=searching)
    susers_btn.grid(column=2, row=0)
    susers_btn.config(width=10, fg='#009688', borderwidth=2, relief=tk.RAISED)

    canv_fr_search_users = tk.Frame(searchwin)
    canv_fr_search_users.place(relx=0, rely=0.10, relwidth=0.9, relheight=0.85)
    #canv_fr_pay.pack(fill=tk.BOTH, expand=1)
    # create a canvas
    canv_search_users = tk.Canvas(canv_fr_search_users, bg='orange')
    canv_search_users.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)
    # add a scrollbar to canvas
    scroll_coach = ttk.Scrollbar(
        canv_fr_search_users, orient=tk.VERTICAL, command=canv_search_users.yview)
    scroll_coach.pack(side=tk.RIGHT, fill=tk.Y)
    # config the canvas
    canv_search_users.configure(yscrollcommand=scroll_coach.set)
    canv_search_users.bind_all("<MouseWheel>", fp(
        _on_mouse_wheel, canv_search_users))
    canv_search_users.bind('<Configure>', lambda e: canv_search_users.configure(
        scrollregion=canv_search_users.bbox("all")))
    # create another frame inside the canvas
    searchwin = tk.Frame(canv_search_users, bg='orange')
    # add that new frame to a window in the canvas
    canv_search_users.create_window((0, 0), window=searchwin, anchor="nw")

    searchwin.mainloop()


win = tk.Tk()
win.geometry('650x800+150+0')
win.title("Main Window")
win.configure(background='white')
running = True

tab_parent = ttk.Notebook(win)

tab1 = ttk.Frame(tab_parent)
tab_parent.add(tab1, text="add Coach")

frame_top = tk.Frame(tab1, bg='orange', bd=5)
frame_top.place(relx=0.25, rely=0.015, relwidth=0.5, relheight=0.15)

lbl = tk.Label(frame_top, text="ADD COACH", font=(
    "Arial"), borderwidth=0, bg="orange")
lbl.grid(column=1, row=0)

Button = tk.Button(frame_top, text="add", command=lambda: [
                   create_coach(entry_field.get()), show_coaches()])
Button.grid(column=2, row=1)
Button.config(width=10, bg="#000000", fg="#FFFFFF",
              borderwidth=2, relief=tk.RAISED)
Button.configure(highlightbackground='#009688')
entry_field = tk.Entry(frame_top, bg='white', font=30)
entry_field.grid(column=1, row=1)


tab2 = ttk.Frame(tab_parent)
tab_parent.add(tab2, text="add User")

frame_users = tk.Frame(tab2, bg='orange', bd=5)
frame_users.place(relx=0.25, rely=0.015, relwidth=0.6, relheight=0.35)

lbl = tk.Label(frame_users, bg='orange', text="ADD USER",
               font=("Arial"), borderwidth=0)
lbl.grid(column=1, row=0)


name_user = tk.Label(frame_users, text="Name", width=lbl_width, borderwidth=0)
name_user.grid(column=0, row=1)
entry_field_users = tk.Entry(frame_users, bg='white', font=30)
entry_field_users.grid(column=1, row=1)

rfid_user = tk.Label(frame_users, text="RFID", width=lbl_width, borderwidth=0)
rfid_user.grid(column=0, row=2)
ef_user_rfid = tk.Entry(frame_users, bg='white', font=30)
ef_user_rfid.grid(column=1, row=2)

tel_user = tk.Label(frame_users, text="Phone Number",
                    width=lbl_width, borderwidth=0)
tel_user.grid(column=0, row=3)
ef_user_tel = tk.Entry(frame_users, bg='white', font=30)
ef_user_tel.grid(column=1, row=3)

sch_user = tk.Label(frame_users, text="Schedule",
                    width=lbl_width, borderwidth=0)
sch_user.grid(column=0, row=4)


sd_user = tk.Label(frame_users, text="Start Date",
                   width=lbl_width, borderwidth=0)
sd_user.grid(column=0, row=5)
ef_user_sd = tk.Entry(frame_users, bg='white', font=30)
ef_user_sd.grid(column=1, row=5)

ed_user = tk.Label(frame_users, text="End Date",
                   width=lbl_width, borderwidth=0)
ed_user.grid(column=0, row=6)
ef_user_ed = tk.Entry(frame_users, bg='white', font=30)
ef_user_ed.grid(column=1, row=6)

ta_user = tk.Label(frame_users, text="Train Amount",
                   width=lbl_width, borderwidth=0)
ta_user.grid(column=0, row=7)
ef_user_ta = tk.Entry(frame_users, bg='white', font=30)
ef_user_ta.grid(column=1, row=7)

lvl_user = tk.Label(frame_users, text="Level (def=0)",
                    width=lbl_width, borderwidth=0)
lvl_user.grid(column=0, row=8)
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
                                                ef_user_lvl.get(), session),
                                    clear_frame_users(),
                                    show_users()
                                    ])
Button.grid(column=1, row=10)
Button.config(width=10, bg="#000000", fg="#FFFFFF",
              borderwidth=2, relief=tk.RAISED)
Button.configure(highlightbackground='#009688')
tab3 = ttk.Frame(tab_parent)
tab_parent.add(tab3, text="add Schedule")
frame_sched = tk.Frame(tab3, bg='orange', bd=5)
frame_sched.place(relx=0.15, rely=0.015, relwidth=0.7, relheight=0.25)
frame_sched_all = tk.Frame(tab3, bg='orange', bd=5)
frame_sched_all.place(relx=0.015, rely=0.28, relwidth=0.9, relheight=0.75)

lbl = tk.Label(frame_sched, bg='orange', text="ADD SCHEDULE",
               font=("Arial"), borderwidth=0)
lbl.grid(column=1, row=0)
lbl = tk.Label(frame_sched, bg='orange', text="*24H-FORMAT",
               font=("Arial"), borderwidth=0)
lbl.grid(column=2, row=0)
lbl = tk.Label(frame_sched_all, text="SCHEDULES",
               bg="orange", font=("Arial"), borderwidth=0)
lbl.grid(column=0, row=0)

name_sch = tk.Label(frame_sched, text="Name", width=lbl_width, borderwidth=0)
name_sch.grid(column=0, row=1)
ef_sch = tk.Entry(frame_sched, bg='white', font=30)
ef_sch.grid(column=1, row=1)

st_sch = tk.Label(frame_sched, text="Start Time",
                  width=lbl_width, borderwidth=0)
st_sch.grid(column=0, row=2)
ef_sch_st = tk.Entry(frame_sched, bg='white', font=30)
ef_sch_st.grid(column=1, row=2)

et_sch = tk.Label(frame_sched, text="End Time", width=lbl_width, borderwidth=0)
et_sch.grid(column=0, row=3)
ef_sch_et = tk.Entry(frame_sched, bg='white', font=30)
ef_sch_et.grid(column=1, row=3)

ta_sch = tk.Label(frame_sched, text="Train Amount",
                  width=lbl_width, borderwidth=0)
ta_sch.grid(column=0, row=4)
ef_sch_ta = tk.Entry(frame_sched, bg='white', font=30)
ef_sch_ta.grid(column=1, row=4)

Button = tk.Button(frame_sched, text="add", command=lambda: [create_schedule(
    ef_sch.get(), ef_sch_st.get(), ef_sch_et.get(), ef_sch_ta.get()), show_schedules()])
Button.grid(column=1, row=10)
Button.config(width=10, pady=5, padx=5, bg="#000000",
              fg="#FFFFFF", borderwidth=2, relief=tk.RAISED)
Button.configure(highlightbackground='#009688')

tab4 = ttk.Frame(tab_parent)
tab_parent.add(tab4, text="add Payment")
frame_pay = tk.Frame(tab4, bg='orange', bd=5)
frame_pay.place(relx=0.20, rely=0.015, relwidth=0.6, relheight=0.25)

lbl = tk.Label(frame_pay, bg='orange', text="ADD PAYMENT",
               font=("Arial"), borderwidth=0)
lbl.grid(column=1, row=0)


id_pay = tk.Label(frame_pay, text="User ID", width=lbl_width, borderwidth=0)
id_pay.grid(column=0, row=1)
ef_pay = tk.Entry(frame_pay, bg='white', font=30)
ef_pay.grid(column=1, row=1)

money_pay = tk.Label(frame_pay, text="Amount of Money",
                     width=lbl_width, borderwidth=0)
money_pay.grid(column=0, row=2)
ef_moneypay = tk.Entry(frame_pay, bg='white', font=30)
ef_moneypay.grid(column=1, row=2)

coach_pay = tk.Label(frame_pay, text="Coach ID",
                     width=lbl_width, borderwidth=0)
coach_pay.grid(column=0, row=3)
ef_coachpay = tk.Entry(frame_pay, bg='white', font=30)
ef_coachpay.grid(column=1, row=3)

Button = tk.Button(frame_pay, text="add", command=lambda: [create_payment(
    ef_pay.get(), ef_moneypay.get(), ef_coachpay.get()), show_payments()])
Button.grid(column=1, row=10)
Button.config(width=10, bg="#000000", fg="#FFFFFF",
              borderwidth=2, relief=tk.RAISED)
Button.configure(highlightbackground='#009688')
tab5 = ttk.Frame(tab_parent)
tab_parent.add(tab5, text="Actions")

tab6 = ttk.Frame(tab_parent)
tab_parent.add(tab6, text="Settings")
settings_fr = tk.Frame(tab6)
settings_fr.place(relx=0.015, rely=0.015, relwidth=0.9, relheight=0.6)

lbl = tk.Label(settings_fr, text="EXPORT ACTIONS DATA",
               font=("Arial"), borderwidth=0)
lbl.grid(column=1, row=0)

name_exc_file = tk.Label(settings_fr, text="FILE NAME",
                         width=lbl_width, borderwidth=0)
name_exc_file.grid(column=0, row=1)
e_f_exc_file = tk.Entry(settings_fr, bg='white', font=30)
e_f_exc_file.grid(column=1, row=1)

year_lbl = tk.Label(settings_fr, text="PLACE YEAR",
                    width=lbl_width, borderwidth=0)
year_lbl.grid(column=0, row=2)
e_f_year_lbl = tk.Entry(settings_fr, bg='white', font=30)
e_f_year_lbl.grid(column=1, row=2)
e_f_year_lbl.insert(0, datetime.now().strftime("%Y"))
month_lbl = tk.Label(settings_fr, text="MONTH", width=lbl_width, borderwidth=0)
month_lbl.grid(column=0, row=3)
e_f_month = tk.Entry(settings_fr, bg='white', font=30)
e_f_month.grid(column=1, row=3)
e_f_month.insert(0, datetime.now().strftime("%m"))

imp_btn = tk.Button(settings_fr, text="Export data", command=lambda: [export_to_excelv2(e_f_exc_file.get(),
                                                                                        e_f_year_lbl.get(), e_f_month.get())])
imp_btn.grid(column=1, row=4)
imp_btn.config(width=10, padx=5, pady=5, bg="#000000",
               fg="#FFFFFF", borderwidth=2, relief=tk.RAISED)
imp_btn.configure(highlightbackground='#006400')
lbl1 = tk.Label(settings_fr)
lbl1.grid(column=1, row=5)
lbl = tk.Label(settings_fr, text="EXPORT PAYMENTS DATA",
               font=("Arial"), borderwidth=0)
lbl.grid(column=1, row=6)

name_exc_file_pay = tk.Label(
    settings_fr, text="FILE NAME", width=lbl_width, borderwidth=0)
name_exc_file_pay.grid(column=0, row=7)
e_f_exc_file_pay = tk.Entry(settings_fr, bg='white', font=30)
e_f_exc_file_pay.grid(column=1, row=7)

year_lbl_pay = tk.Label(settings_fr, text="PLACE YEAR",
                        width=lbl_width, borderwidth=0)
year_lbl_pay.grid(column=0, row=8)
e_f_year_lbl_pay = tk.Entry(settings_fr, bg='white', font=30)
e_f_year_lbl_pay.grid(column=1, row=8)
e_f_year_lbl_pay.insert(0, datetime.now().strftime("%Y"))
month_lbl_pay = tk.Label(settings_fr, text="MONTH",
                         width=lbl_width, borderwidth=0)
month_lbl_pay.grid(column=0, row=9)
e_f_month_pay = tk.Entry(settings_fr, bg='white', font=30)
e_f_month_pay.grid(column=1, row=9)
e_f_month_pay.insert(0, datetime.now().strftime("%m"))
day_lbl_pay = tk.Label(settings_fr, text="DAY", width=lbl_width, borderwidth=0)
day_lbl_pay.grid(column=0, row=10)
e_f_day_pay = tk.Entry(settings_fr, bg='white', font=30)
e_f_day_pay.grid(column=1, row=10)
e_f_day_pay.insert(0, datetime.now().strftime("%d"))

imp_btn_pay = tk.Button(settings_fr, text="Export data", command=lambda: [export_to_excel_pay(e_f_exc_file_pay.get(),
                                                                                              e_f_year_lbl_pay.get(), e_f_month_pay.get(), e_f_day_pay.get())])
imp_btn_pay.grid(column=1, row=11)
imp_btn_pay.config(width=10, padx=5, pady=5, bg="#000000",
                   fg="#FFFFFF", borderwidth=2, relief=tk.RAISED)
imp_btn_pay.configure(highlightbackground='#006400')

drp_lbl_pay = tk.Label(settings_fr, bg="#df4759",
                       text="DROP ALL DATABASE", width=lbl_width + 5, borderwidth=0)
drp_lbl_pay.grid(column=0, row=998, padx=5, pady=5)
reload_btn_pay = tk.Button(
    settings_fr, text="clear all", command=drop_create_db)
reload_btn_pay.grid(column=0, row=999, padx=5, pady=5)
reload_btn_pay.config(width=10, bg="#df4759", fg="#FFFFFF",
                      borderwidth=2, relief=tk.RAISED)
reload_btn_pay.configure(highlightbackground='#006400')


# ------------scrollbar to action---------------
# create frame
canv_fr_act = tk.Frame(tab5)
canv_fr_act.place(relx=0.015, rely=0.015, relwidth=0.9, relheight=0.9)
# create a canvas
canv_act = tk.Canvas(canv_fr_act, bg="orange")
canv_act.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)
# add a scrollbar to canvas
scroll_act = ttk.Scrollbar(
    canv_fr_act, orient=tk.VERTICAL, command=canv_act.yview)
scroll_act.pack(side=tk.RIGHT, fill=tk.Y)
# config the canvas
canv_act.configure(yscrollcommand=scroll_act.set)
canv_act.bind("<MouseWheel>", fp(_on_mouse_wheel, canv_act))
canv_act.bind('<Configure>', lambda e: canv_act.configure(
    scrollregion=canv_act.bbox("all")))
# create another frame inside the canvas
frame_act = tk.Frame(canv_act, bg='orange')
# add that new frame to a window in the canvas
canv_act.create_window((0, 0), window=frame_act, anchor="nw")


canv_fr_pay = tk.Frame(tab4)
canv_fr_pay.place(relx=0.015, rely=0.32, relwidth=0.9, relheight=0.65)
# create a canvas
canv_pay = tk.Canvas(canv_fr_pay, bg='orange')
canv_pay.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)
# add a scrollbar to canvas
scroll_pay = ttk.Scrollbar(
    canv_fr_pay, orient=tk.VERTICAL, command=canv_pay.yview)
scroll_pay.pack(side=tk.RIGHT, fill=tk.Y)
# config the canvas
canv_pay.configure(yscrollcommand=scroll_act.set)
canv_pay.bind("<MouseWheel>", fp(_on_mouse_wheel, canv_pay))
canv_pay.bind('<Configure>', lambda e: canv_pay.configure(
    scrollregion=canv_pay.bbox("all")))
# create another frame inside the canvas
frame_pay_all = tk.Frame(canv_pay, bg='orange')
# add that new frame to a window in the canvas
canv_pay.create_window((0, 0), window=frame_pay_all, anchor="nw")
lbl = tk.Label(frame_pay_all, text="PAYMENTS",
               bg="orange", font=("Arial"), borderwidth=0)
lbl.grid(column=0, row=0)


canv_fr_user = tk.Frame(tab2)
canv_fr_user.place(relx=0.015, rely=0.40, relwidth=0.9, relheight=0.6)
#canv_fr_pay.pack(fill=tk.BOTH, expand=1)
# create a canvas
canv_user = tk.Canvas(canv_fr_user, scrollregion=(
    0, 0, 1000, 1000), bg='orange')
canv_user.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)
# add a scrollbar to canvas
scroll_user = ttk.Scrollbar(
    canv_fr_user, orient=tk.VERTICAL, command=canv_user.yview)
scroll_user.pack(side=tk.RIGHT, fill=tk.Y)
# config the canvas
canv_user.configure(yscrollcommand=scroll_user.set)
canv_user.bind("<MouseWheel>", fp(_on_mouse_wheel, canv_user))
canv_user.bind('<Configure>', lambda e: canv_user.configure(
    scrollregion=canv_user.bbox("all")))
# create another frame inside the canvas
frame_users_all = tk.Frame(canv_user, bg='orange')
# add that new frame to a window in the canvas
canv_user.create_window((0, 0), window=frame_users_all, anchor="nw")

lbl = tk.Label(frame_users_all, bg="orange", text="Users",
               font=("Arial"), borderwidth=0)
lbl.grid(column=0, row=0)


canv_fr_coach = tk.Frame(tab1)
canv_fr_coach.place(relx=0.030, rely=0.20, relwidth=0.9, relheight=0.7)
#canv_fr_pay.pack(fill=tk.BOTH, expand=1)
# create a canvas
canv_coach = tk.Canvas(canv_fr_coach, bg='orange')
canv_coach.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)
# add a scrollbar to canvas
scroll_coach = ttk.Scrollbar(
    canv_fr_coach, orient=tk.VERTICAL, command=canv_coach.yview)
scroll_coach.pack(side=tk.RIGHT, fill=tk.Y)
# config the canvas
canv_coach.configure(yscrollcommand=scroll_coach.set)
canv_coach.bind_all("<MouseWheel>", fp(_on_mouse_wheel, canv_coach))
canv_coach.bind('<Configure>', lambda e: canv_coach.configure(
    scrollregion=canv_coach.bbox("all")))
# create another frame inside the canvas
frame_bottom = tk.Frame(canv_coach, bg='orange')
# add that new frame to a window in the canvas
canv_coach.create_window((0, 0), window=frame_bottom, anchor="nw")


lbl = tk.Label(frame_bottom, bg="orange", text="COACHES",
               font=("Arial"), borderwidth=0)
lbl.grid(column=0, row=0)


tab_parent.pack(expand=1, fill='both')

try:
    opt_user_sch = ttk.Combobox(frame_users, state="readonly", value=[str(
        _.id) for _ in session.query(Schedule.id)], width=lbl_width+12)
    opt_user_sch.current(0)
    opt_user_sch.grid(column=1, row=4)
except:
    opt_user_sch = ttk.Combobox(
        frame_users, value=["please add schedule"], width=lbl_width+12)
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
serialPorts = []
try:
    with open('ports.json') as json_file:
        data = load(json_file)
        serialPorts = data
except Exception:
    a = ['COM1', 'COM2', 'COM3', 'COM4', 'COM5', 'COM25', '/dev/ttyACM0', '/dev/ttyACM1', '/dev/ttyACM2',
         '/dev/ttyACM3', '/dev/ttyUSB0', '/dev/ttyUSB1', '/dev/ttyUSB2', '/dev/ttyUSB3']
    with open('ports.json', 'w') as outfile:
        dump(a, outfile)
finally:
    with open('ports.json') as json_file:
        data = load(json_file)
        serialPorts = data
# ]
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
array1 = [-1, -1, -1, -1]


def serialThread1():
    global running, comPorts
    meta = MetaData()
    Base = declarative_base()
    engine = create_engine("sqlite:///fitness.db")
    Session = sessionmaker(bind=engine)
    session = Session()
    while running:
        sleep(0.1)
        serialThread(comPorts, session)


def serialThread(comPorts, session):
    #global win, comPorts,timers,stdPhotos,actions,dataforserver,readRFID,open_users_elements
    portIndex = -1
    # comError = range(len(comPorts))
    for comPort in comPorts:
        portIndex = portIndex + 1
        try:
            rec = str(comPort.readline())
            global array1
            for i in range(4):
                if array1[i] >= 0:
                    array1[i] = array1[i] + 1
                    if array1[i] > 10:  # ??????????????
                        array1[i] = -1
                        if i == 0:
                            dev_id = "!"
                        elif i == 1:
                            dev_id = "@"
                        elif i == 2:
                            dev_id = "#"
                        else:
                            dev_id = "$"
                        comPort.write(str.encode(str(dev_id) + '*\n'))

            if len(rec) > 4:
                rec = rec.strip()
                data = rec.strip().split('#')
                if len(data) >= 2:  # was 3 and w/o =
                    # was without [2::] and -1
                    dev_id = int(str(data[1-1])[2::])
                    if dev_id in [1, 3]:
                        gate = 1
                    else:
                        gate = 0
                    RFID = data[2-1].strip().upper()[:8]  # was without -1
                    # gate = int(data[3]) #wasn't comment
                    if session.query(User).filter_by(RFID=RFID).first() is None:
                        ef_user_rfid.delete(0, tk.END)
                        ef_user_rfid.insert(0, RFID)
                    if RFID == "TEST" or RFID == "RESET":
                        date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        # comError[portIndex] = 0
                    else:  # wasnt comment
                        if gate == 0:  # 1-come,0-leave
                            gate = False
                        else:
                            gate = True

                        try:
                            #session = Session()
                            usr = session.query(User).filter_by(
                                RFID=RFID).first()
                            if usr.id is None:
                                if usr.RFID is not None:
                                    print("Net usera id")
                                else:
                                    # stdNames[index].config(text="Aniqlanmagan")
                                    print("Aniqlanmagan")
                                    comPort.write(str.encode(
                                        "@"+str(dev_id)+"$ERROR&"+str(gate) + '*\n'))
                            else:

                                if create_action(usr.id, gate, session):
                                    #comPort.write(str.encode("1"+str(dev_id)+"$OK&"+str(gate) + '*\n'))

                                    array1[dev_id-1] = 0

                                    comPort.write(str.encode(
                                        str(dev_id) + '*\n'))
                                else:
                                    print("OTKAZANO")
                                    array1[dev_id-1] = 0
                                show_actions(session)
                               # setAttendace()
                               # stdNames[index].config(text=name+"\n"+group_id)

                        except Exception as ex:
                            print(str(ex))
                            print("???????????????????????? ???? ????????????!")
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
# pyinstaller --onefile --icon fitnesslogog.ico test.py -n fitness-GUI
