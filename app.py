import streamlit as st
import sqlite3
import subprocess

# تابع برای اتصال به دیتابیس SQLite
def connect_db():
    conn = sqlite3.connect('account_data.db')
    return conn

# صفحه اصلی
def show_main_page():
    st.title("ثبت اطلاعات اکانت و کاربران جدید")

    # فرم وارد کردن اطلاعات اکانت
    with st.form(key='account_form'):
        product = st.selectbox('محصول:', ['grammarly', 'quillbot', 'trunitin'])
        email = st.text_input('ایمیل:')
        password = st.text_input('رمز عبور:')
        login_link = st.text_input('لینک ورود:')

        submit_button = st.form_submit_button(label='ثبت اکانت')

        if submit_button:
            add_or_update_account(product, email, password, login_link)

    # فرم برای ثبت یا بروزرسانی اطلاعات کاربر
    with st.form(key='user_form'):
        user_email = st.text_input('ایمیل کاربر:')
        grammarly_date = st.date_input('تاریخ انقضای Grammarly')
        quillbot_date = st.date_input('تاریخ انقضای Quillbot')
        trunitin_date = st.date_input('تاریخ انقضای Turnitin')

        submit_button = st.form_submit_button(label='ثبت یا بروزرسانی اطلاعات')

        if submit_button:
            add_or_update_user(user_email, grammarly_date, quillbot_date, trunitin_date)

    # ارسال ایمیل
    if st.button('ارسال ایمیل‌ها'):
        send_email()

# تابع برای افزودن یا بروزرسانی اکانت
def add_or_update_account(product, email, password, login_link):
    conn = connect_db()
    c = conn.cursor()

    c.execute("SELECT * FROM accounts WHERE product = ?", (product,))
    existing_account = c.fetchone()

    if existing_account:
        c.execute('''
            UPDATE accounts
            SET email = ?, password = ?, login_link = ?
            WHERE product = ?
        ''', (email, password, login_link, product))
        st.success(f"اکانت {product} بروزرسانی شد.")
    else:
        c.execute("INSERT INTO accounts (product, email, password, login_link) VALUES (?, ?, ?, ?)",
                  (product, email, password, login_link))
        st.success(f"اکانت جدید برای {product} اضافه شد.")

    conn.commit()
    conn.close()

# تابع برای افزودن یا بروزرسانی اطلاعات کاربر
def add_or_update_user(user_email, grammarly_date, quillbot_date, trunitin_date):
    conn = connect_db()
    c = conn.cursor()

    c.execute("SELECT * FROM users WHERE email = ?", (user_email,))
    existing_user = c.fetchone()

    if existing_user:
        c.execute('''
            UPDATE users
            SET grammarly_date = ?, quillbot_date = ?, trunitin_date = ?
            WHERE email = ?
        ''', (grammarly_date, quillbot_date, trunitin_date, user_email))
        st.success(f"تاریخ‌ها برای کاربر {user_email} بروزرسانی شد.")
    else:
        c.execute("INSERT INTO users (email, grammarly_date, quillbot_date, trunitin_date) VALUES (?, ?, ?, ?)",
                  (user_email, grammarly_date, quillbot_date, trunitin_date))
        st.success(f"اطلاعات جدید برای کاربر {user_email} اضافه شد.")

    conn.commit()
    conn.close()

# تابع برای ارسال ایمیل
def send_email():
    try:
        subprocess.run(['python', 'email_sender_sql.py'], check=True)
        st.success("ایمیل‌ها با موفقیت ارسال شدند.")
    except subprocess.CalledProcessError as e:
        st.error(f"خطا در ارسال ایمیل‌ها: {e}")


show_main_page()
