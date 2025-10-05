import smtplib
import sqlite3
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime


# تابع ارسال ایمیل به مشتری
def send_email_to_customer(sender_email, sender_password, receiver_email, subject, body):
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = subject

    msg.attach(MIMEText(body, 'html'))

    server = None  # مقداردهی اولیه به server برای جلوگیری از ارور

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, sender_password)
        text = msg.as_string()
        server.sendmail(sender_email, receiver_email, text)
        print(f"ایمیل به {receiver_email} با موفقیت ارسال شد.")
    except Exception as e:
        print(f"خطا در ارسال ایمیل به {receiver_email}: {e}")
    finally:
        if server:  # فقط اگر server مقداردهی شده باشد
            try:
                server.quit()
            except Exception as e:
                print(f"خطا در قطع اتصال: {e}")



# تابع برای خواندن داده‌ها از پایگاه داده SQLite و ارسال ایمیل
def process_db_and_send_emails(sender_email, sender_password):
    # اتصال به پایگاه داده SQLite و استفاده از Row برای دیکشنری‌گونه بودن داده‌ها
    conn = sqlite3.connect('account_data.db')
    conn.row_factory = sqlite3.Row  # اینجا Row به داده‌ها اجازه می‌دهد به صورت دیکشنری نمایش داده شوند
    c = conn.cursor()

    # تاریخ امروز
    today = datetime.today().strftime('%Y-%m-%d')

    # خواندن داده‌ها از جدول users (اطلاعات مشتریان)
    c.execute("SELECT * FROM users")
    users_data = c.fetchall()

    # برای هر مشتری در جدول users
    for user_row in users_data:
        receiver_email = user_row['email']  # ایمیل مشتری از جدول users

        # بررسی هر محصول و تاریخ
        for product in ['grammarly', 'quillbot', 'trunitin']:
            # گرفتن تاریخ انقضای محصول از ستون‌های مربوطه
            product_date = user_row[f'{product}_date']  # استفاده از نام ستون به صورت داینامیک

            # تبدیل تاریخ به فرمت استاندارد (YYYY-MM-DD)
            try:
                # تبدیل تاریخ به datetime
                if isinstance(product_date, str):
                    # شناسایی فرمت تاریخ‌ها و تبدیل آنها به فرمت YYYY-MM-DD
                    if '/' in product_date:  # تاریخ به صورت MM/DD/YY یا مشابه
                        product_date = datetime.strptime(product_date, '%m/%d/%y').strftime('%Y-%m-%d')
                    else:  # تاریخ به صورت YYYY-MM-DD
                        product_date = datetime.strptime(product_date, '%Y-%m-%d').strftime('%Y-%m-%d')
            except Exception as e:
                print(f"خطا در تبدیل تاریخ {product_date}: {e}")
                continue

            # خواندن اطلاعات اکانت از جدول accounts
            c.execute("SELECT * FROM accounts WHERE product = ?", (product,))
            account_data = c.fetchone()

            if account_data:
                # اطلاعات اکانت برای محصول مورد نظر
                product_email = account_data['email']  # ایمیل اکانت
                product_password = account_data['password']  # رمز عبور اکانت
                product_login_link = account_data['login_link']  # لینک ورود اکانت

                # اگر تاریخ محصول بزرگتر از امروز باشد، ایمیل ارسال می‌شود
                if product_date > today:
                    subject = f"اطلاعات اکانت برای خرید {product.capitalize()}"
                    body = f"""
                    <html>
                    <body dir="rtl">
                        <p>با سلام,</p>
                        <p>با تشکر از خرید شما از گروه VIP GRAMMARLY</p>
                        <p>لطفاً از اطلاعات زیر برای ورود به {product.capitalize()} استفاده کنید:</p>
                        <p><strong>ایمیل: {product_email}</strong></p>
                        <p><strong>رمز عبور: {product_password}</strong></p>
                        <br>
                        <p><strong>لینک ورود: <a href="{product_login_link}">{product_login_link}</a></strong></p>
                        <br>
                    </body>
                    </html>
                    """
                    send_email_to_customer(sender_email, sender_password, receiver_email, subject, body)

    # بستن اتصال به پایگاه داده
    conn.close()


# پارامترهای ایمیل
sender_email = "customervipgrammarly@gmail.com"  # ایمیل فرستنده
sender_password = "hync rmms phzt cbgs"  # رمز عبور اپلیکیشن

# فراخوانی تابع برای پردازش داده‌ها از پایگاه داده و ارسال ایمیل
process_db_and_send_emails(sender_email, sender_password)
