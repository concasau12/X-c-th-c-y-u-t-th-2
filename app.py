from flask import Flask, render_template, request, redirect, url_for, session, abort
import random
import time
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import mysql.connector
app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Secret key để lưu session

# Kết nối MySQL
db_config = {
    'host': 'localhost',
    'user': 'root',          # Tên người dùng MySQL
    'password': 'Dinh@150620',  # Mật khẩu MySQL
    'database': 'flask_app', # Tên cơ sở dữ liệu
}
def get_db_connection():
    return mysql.connector.connect(**db_config)
# Hàm truy vấn thông tin người dùng từ MySQL
def get_user_by_email(email):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)  # dictionary=True để kết quả là dict
    query = "SELECT * FROM user WHERE email = %s"
    cursor.execute(query, (email,))
    user = cursor.fetchone()
    cursor.close()
    conn.close()
    return user


# Hàm sinh OTP
def generate_otp():
    random_component = ''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', k=6))
    time_component = str(int(time.time()))[-6:]
    otp = (random_component + time_component).upper()[:6]
    otp = otp.replace('O', 'X').replace('I', 'X').replace('L', 'X')
    return otp


# Hàm gửi email OTP
def send_otp(email_sent, otp):
    email = "alldinhnguyen@gmail.com"
    password = "ngistiumgcohwjvw"

    subject = "Mã OTP của bạn"
    body = f"Mã OTP của bạn là: {otp}\nMã này có hiệu lực trong 5 phút."

    message = MIMEMultipart()
    message["From"] = email
    message["To"] = email_sent
    message["Subject"] = subject
    message.attach(MIMEText(body, "plain"))

    try:
        session = smtplib.SMTP("smtp.gmail.com", 587)
        session.starttls()
        session.login(email, password)
        session.send_message(message)
        session.quit()
        print("Mail sent successfully!")
    except Exception as e:
        print(f"Error: {e}")


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        email = request.form["username"]
        password = request.form["password"]

        # Truy vấn người dùng từ MySQL
        user = get_user_by_email(email)
        if user and user["password"] == password:
            session["username"] = email  # Lưu email vào session
            return redirect(url_for('otp'))
        else:
            return "Thông tin email hoặc mật khẩu không đúng. Vui lòng thử lại."
    return render_template("index.html")

@app.route("/otp", methods=["GET", "POST"])
def otp():
    if request.method == "POST":
        otp_input = request.form["otp"]
        otp_session = session.get("otp")  # Lấy mã OTP từ session

        if otp_input == otp_session:
            return redirect(url_for('main'))
        else:
            return "Mã OTP không đúng. Bạn sẽ bị thoát khỏi ứng dụng.", 401  # Thoát ứng dụng với HTTP status 401
    else:
        otp = generate_otp()
        session["otp"] = otp  # Lưu OTP vào session
        email_sent = session.get("username")  # Lấy email từ session
        send_otp(email_sent, otp)  # Gửi OTP qua email
        return render_template("login.html")


@app.route("/main")
def main():
    if "username" in session:
        return render_template("main.html")
    else:
        abort(401)  # Trả về lỗi 401 nếu không có session hợp lệ


if __name__ == "__main__":
    app.run(debug=True)
