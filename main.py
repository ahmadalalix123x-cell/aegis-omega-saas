import sqlite3
import uuid
from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse
from datetime import datetime, timedelta

DB_NAME = "aegis_omega_core.db"
PORT = 8080

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS aegis_licenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            client_name TEXT,
            license_key TEXT,
            tier TEXT,
            features_limit TEXT,
            payment_method TEXT,
            requests_left INTEGER,
            status TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    # ترحيل آمن للجداول إن وجدت مسبقاً
    for col, col_type in [("features_limit", "TEXT"), ("payment_method", "TEXT"), ("requests_left", "INTEGER")]:
        try:
            cursor.execute(f"ALTER TABLE aegis_licenses ADD COLUMN {col} {col_type}")
        except sqlite3.OperationalError:
            pass
    conn.commit()
    conn.close()

class AegisWebHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed_path = urllib.parse.urlparse(self.path)
        path = parsed_path.path
        query_params = urllib.parse.parse_qs(parsed_path.query)

        if path == '/':
            # واجهة المتجر الرئيسية وبوابة الاشتراكات
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            
            html_content = """
            <!DOCTYPE html>
            <html lang="ar" dir="rtl">
            <head>
                <meta charset="UTF-8">
                <title>AegisCode AI v7.0 Omega - منصة السحاب السيادية</title>
                <style>
                    body { font-family: Tahoma, sans-serif; background: #0f172a; color: #f8fafc; margin: 0; padding: 20px; }
                    .container { max-width: 1100px; margin: auto; background: #1e293b; padding: 30px; border-radius: 12px; box-shadow: 0 10px 30px rgba(0,0,0,0.5); }
                    h1 { color: #38bdf8; text-align: center; }
                    .nav-bar { text-align: center; margin-bottom: 25px; }
                    .nav-bar a { color: #38bdf8; text-decoration: none; margin: 0 15px; font-weight: bold; padding: 8px 15px; background: #334155; border-radius: 6px; }
                    .pricing-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; }
                    .card { background: #334155; padding: 20px; border-radius: 8px; text-align: center; border: 1px solid #475569; }
                    .card.free { border-color: #38bdf8; }
                    .price { font-size: 24px; font-weight: bold; margin: 15px 0; color: #34d399; }
                    .card.free .price { color: #38bdf8; }
                    ul { text-align: right; padding-right: 20px; color: #cbd5e1; font-size: 13px; margin: 15px 0; }
                    ul li { margin-bottom: 6px; }
                    input, select { width: 85%; padding: 10px; margin: 8px 0; border-radius: 6px; background: #0f172a; color: #fff; border: 1px solid #64748b; font-size: 14px; }
                    label { display: block; text-align: right; width: 85%; margin: 0 auto; color: #94a3b8; font-size: 12px; }
                    button { background: #2563eb; color: white; border: none; padding: 12px 20px; border-radius: 6px; cursor: pointer; font-weight: bold; width: 90%; margin-top: 10px; }
                    button.free-btn { background: #0284c7; }
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>AegisCode AI v7.0 Omega 🛡️</h1>
                    <p style="text-align: center; color: #94a3b8;">منصة التراخيص والذكاء السيادي السحابية</p>
                    
                    <div class="nav-bar">
                        <a href="/">🏠 المتجر والباقات</a>
                        <a href="/portal">🔑 بوابة العميل (تسجيل الدخول بالمفتاح)</a>
                        <a href="/admin">👑 لوحة تحكم المطور</a>
                    </div>
                    
                    <div class="pricing-grid">
                        <!-- الخطة التجريبية -->
                        <div class="card free">
                            <h3 style="color:#38bdf8;">Free Trial (تجربة محدودة)</h3>
                            <div class="price">مجاناً $0</div>
                            <ul>
                                <li><b>المدة:</b> يوم واحد فقط</li>
                                <li><b>الذكاء الاصطناعي:</b> 10 طلبات أساسية</li>
                                <li><b>أنفاق الـ VPN:</b> سرعة محدودة</li>
                            </ul>
                            <form action="/subscribe" method="POST">
                                <input type="hidden" name="tier" value="Free Trial">
                                <input type="text" name="client_name" placeholder="اسمك الكريم" required><br>
                                <label>وسيلة التحقق والدفع الآمن:</label>
                                <select name="payment_method" required>
                                    <option value="Credit Card (Stripe)">بطاقة ائتمان (Stripe)</option>
                                    <option value="PayPal">باي بال (PayPal)</option>
                                    <option value="USDT Crypto">عملات رقمية (USDT)</option>
                                    <option value="Apple Pay">أبل باي (Apple Pay)</option>
                                </select><br>
                                <button type="submit" class="free-btn">تفعيل النسخة المحدودة</button>
                            </form>
                        </div>

                        <!-- الخطة القيادية -->
                        <div class="card">
                            <h3 style="color:#f43f5e;">Restricted Tier</h3>
                            <div class="price">$29 / شهر</div>
                            <ul>
                                <li><b>المدة:</b> شهرياً</li>
                                <li><b>الذكاء الاصطناعي:</b> طلبات غير محدودة</li>
                                <li><b>أنفاق الـ VPN:</b> وصول قياسي آمن</li>
                            </ul>
                            <form action="/subscribe" method="POST">
                                <input type="hidden" name="tier" value="Restricted">
                                <input type="text" name="client_name" placeholder="اسم العميل" required><br>
                                <label>وسيلة الدفع الآمنة:</label>
                                <select name="payment_method" required>
                                    <option value="Credit Card (Stripe)">بطاقة ائتمان (Stripe)</option>
                                    <option value="PayPal">باي بال (PayPal)</option>
                                    <option value="USDT Crypto">عملات رقمية (USDT)</option>
                                    <option value="Apple Pay">أبل باي (Apple Pay)</option>
                                </select><br>
                                <button type="submit">دفع واشتراك فوراً</button>
                            </form>
                        </div>

                        <!-- الخطة المؤسسية -->
                        <div class="card">
                            <h3 style="color:#38bdf8;">Sovereign Enterprise</h3>
                            <div class="price">$199 / شهر</div>
                            <ul>
                                <li><b>المدة:</b> مفتوح (دائم)</li>
                                <li><b>الذكاء الاصطناعي:</b> محركات Omega الكاملة</li>
                                <li><b>أنفاق الـ VPN:</b> أولوية قصوى وعقد مشفرة</li>
                            </ul>
                            <form action="/subscribe" method="POST">
                                <input type="hidden" name="tier" value="Sovereign Enterprise">
                                <input type="text" name="client_name" placeholder="اسم العميل" required><br>
                                <label>وسيلة الدفع الآمنة:</label>
                                <select name="payment_method" required>
                                    <option value="Credit Card (Stripe)">بطاقة ائتمان (Stripe)</option>
                                    <option value="PayPal">باي بال (PayPal)</option>
                                    <option value="USDT Crypto">عملات رقمية (USDT)</option>
                                    <option value="Apple Pay">أبل باي (Apple Pay)</option>
                                </select><br>
                                <button type="submit" style="background: #059669;">دفع واشتراك فوراً</button>
                            </form>
                        </div>
                    </div>
                </div>
            </body>
            </html>
            """
            self.wfile.write(html_content.encode('utf-8'))

        elif path == '/portal':
            # بوابة العميل للتحقق من المفتاح واستهلاك الطلبات
            key_query = query_params.get('key', [''])[0]
            client_info = None
            error_msg = ""

            if key_query:
                conn = sqlite3.connect(DB_NAME)
                cursor = conn.cursor()
                cursor.execute("SELECT client_name, tier, features_limit, requests_left, status, created_at FROM aegis_licenses WHERE license_key = ?", (key_query,))
                client_info = cursor.fetchone()
                conn.close()
                if not client_info:
                    error_msg = "مفتاح الترخيص غير صحيح أو غير موجود في النظام!"

            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            
            portal_html = f"""
            <!DOCTYPE html>
            <html lang="ar" dir="rtl">
            <head><meta charset="UTF-8"><title>بوابة العميل - AegisCode AI</title>
            <style>
                body {{ font-family: Tahoma, sans-serif; background: #0f172a; color: #fff; padding: 30px; }}
                .box {{ max-width: 600px; margin: auto; background: #1e293b; padding: 30px; border-radius: 12px; border: 1px solid #38bdf8; }}
                input {{ width: 80%; padding: 10px; margin: 10px 0; border-radius: 6px; background: #0f172a; color: #fff; border: 1px solid #64748b; }}
                button {{ background: #2563eb; color: white; border: none; padding: 10px 20px; border-radius: 6px; cursor: pointer; font-weight: bold; }}
            </style>
            </head>
            <body>
                <div class="box" style="text-align: center;">
                    <h1>🔑 بوابة إدارة الترخيص للعميل</h1>
                    <p style="color: #94a3b8;">أدخل مفتاح الترخيص الخاص بك لعرض حصتك واستخدام محركات الذكاء الاصطناعي والـ VPN</p>
                    <form method="GET" action="/portal">
                        <input type="text" name="key" placeholder="أدخل مفتاح الترخيص هنا..." value="{key_query}" required><br>
                        <button type="submit">تحقق من المفتاح</button>
                    </form>
                    <br><a href="/" style="color:#38bdf8; text-decoration:none;">العودة للمتجر الرئيسي</a>
            """
            if error_msg:
                portal_html += f"<p style='color: #f43f5e; margin-top:20px;'>{error_msg}</p>"
            elif client_info:
                requests_display = "غير محدود (Unlimited)" if client_info[3] > 9000 else f"{client_info[3]} طلب متبقي"
                portal_html += f"""
                    <div style="background: #334155; padding: 20px; border-radius: 8px; margin-top: 20px; text-align: right;">
                        <p><b>اسم العميل:</b> {client_info[0]}</p>
                        <p><b>مستوى الصلاحية:</b> <span style="color:#38bdf8;">{client_info[1]}</span></p>
                        <p><b>القيود والميزات:</b> {client_info[2]}</p>
                        <p><b>الرصيد المتبقي:</b> <span style="color:#34d399;">{requests_display}</span></p>
                        <p><b>حالة الترخيص:</b> <span style="color:#34d399;">{client_info[4]}</span></p>
                        <p><b>تاريخ الإصدار:</b> {client_info[5]}</p>
                    </div>
                    <form action="/use_ai" method="POST" style="margin-top: 20px;">
                        <input type="hidden" name="key" value="{key_query}">
                        <button type="submit" style="background: #059669; width: 100%;">استهلاك طلب ذكاء اصطناعي (اختبار الحصة)</button>
                    </form>
                """
            portal_html += "</div></body></html>"
            self.wfile.write(portal_html.encode('utf-8'))

        elif path == '/admin':
            # لوحة تحكم المطور السيادية
            conn = sqlite3.connect(DB_NAME)
            cursor = conn.cursor()
            cursor.execute("SELECT client_name, license_key, tier, features_limit, payment_method, requests_left, status FROM aegis_licenses")
            rows = cursor.fetchall()
            conn.close()

            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            
            admin_html = f"""
            <!DOCTYPE html>
            <html lang="ar" dir="rtl">
            <head><meta charset="UTF-8"><title>لوحة القيادة السيادية</title></head>
            <body style="background: #0f172a; color: #fff; font-family: Tahoma; padding: 20px;">
                <h1>👑 لوحة القيادة السيادية للمطور (إدارة المشتركين والمدفوعات)</h1>
                <div style="margin-bottom: 20px;"><a href="/" style="color:#38bdf8; text-decoration:none; background:#1e293b; padding:8px 15px; border-radius:6px;">العودة للمتجر</a></div>
                <table border="1" style="width:100%; border-collapse: collapse; text-align: center; background:#1e293b;">
                    <tr style="background: #334155; color: #38bdf8; height:45px;">
                        <th>اسم العميل</th><th>مفتاح الترخيص</th><th>الباقة</th><th>القيود والميزات</th><th>وسيلة الدفع</th><th>الطلبات المتبقية</th><th>الحالة</th>
                    </tr>
            """
            for row in rows:
                admin_html += f"<tr style='height:40px;'><td>{row[0]}</td><td>{row[1]}</td><td>{row[2]}</td><td>{row[3]}</td><td>{row[4]}</td><td>{row[5]}</td><td>{row[6]}</td></tr>"
            admin_html += "</table></body></html>"
            self.wfile.write(admin_html.encode('utf-8'))

    def do_POST(self):
        parsed_path = urllib.parse.urlparse(self.path)
        path = parsed_path.path
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length).decode('utf-8')
        parsed_data = urllib.parse.parse_qs(post_data)

        if path == '/subscribe':
            client_name = parsed_data.get('client_name', ['مجهول'])[0]
            tier = parsed_data.get('tier', ['Free Trial'])[0]
            payment_method = parsed_data.get('payment_method', ['Credit Card (Stripe)'])[0]
            
            if tier == "Free Trial":
                prefix = "AEGIS-TRIAL-"
                features_limit = "محدد: يوم واحد / 10 طلبات AI / VPN سرعة محدودة"
                requests_left = 10
            elif tier == "Restricted":
                prefix = "AEGIS-RESTRICTED-"
                features_limit = "قياسي: شهر / AI غير محدود / VPN قياسي"
                requests_left = 999999
            else:
                prefix = "AEGIS-ENTERPRISE-"
                features_limit = "مفتوح: صلاحيات كاملة وأولوية قصوى"
                requests_left = 999999

            license_key = prefix + str(uuid.uuid4())[:8].upper()
            status = "Active"

            conn = sqlite3.connect(DB_NAME)
            cursor = conn.cursor()
            cursor.execute("INSERT INTO aegis_licenses (client_name, license_key, tier, features_limit, payment_method, requests_left, status) VALUES (?, ?, ?, ?, ?, ?, ?)",
                           (client_name, license_key, tier, features_limit, payment_method, requests_left, status))
            conn.commit()
            conn.close()

            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            
            success_page = f"""
            <!DOCTYPE html>
            <html lang="ar" dir="rtl">
            <head><meta charset="UTF-8"><title>تفعيل الترخيص</title></head>
            <body style="background: #0f172a; color: #fff; font-family: Tahoma; text-align: center; padding: 50px;">
                <h1 style="color: #34d399;">تمت عملية التحقق والدفع بنجاح! 🎉</h1>
                <p>عزيزي <b>{client_name}</b>، تم ربط باقة (<b>{tier}</b>) بوسيلة الدفع <b>{payment_method}</b> بنجاح ومفتاحك جاهز:</p>
                <div style="background: #1e293b; padding: 20px; display: inline-block; border-radius: 8px; border: 1px solid #38bdf8; font-size: 22px; color: #38bdf8;">
                    {license_key}
                </div>
                <p style="color: #94a3b8; margin-top: 15px;">{features_limit}</p>
                <br><br><a href="/portal?key={license_key}" style="color: #38bdf8; font-weight: bold; margin-left:20px;">انتقل إلى بوابة العميل</a>
                <a href="/" style="color: #f43f5e; text-decoration: none; font-weight: bold;">العودة للمتجر الرئيسي</a>
            </body>
            </html>
            """
            self.wfile.write(success_page.encode('utf-8'))

        elif path == '/use_ai':
            key = parsed_data.get('key', [''])[0]
            conn = sqlite3.connect(DB_NAME)
            cursor = conn.cursor()
            cursor.execute("SELECT id, requests_left FROM aegis_licenses WHERE license_key = ?", (key,))
            res = cursor.fetchone()
            
            msg = ""
            if res:
                row_id, requests_left = res
                if requests_left > 9000:
                    msg = "تم تنفيذ طلب الذكاء الاصطناعي بنجاح (باقة غير محدودة)."
                elif requests_left > 0:
                    new_left = requests_left - 1
                    cursor.execute("UPDATE aegis_licenses SET requests_left = ? WHERE id = ?", (new_left, row_id))
                    conn.commit()
                    msg = f"تم استهلاك طلب AI بنجاح! المتبقي لديك: {new_left} طلبات."
                else:
                    msg = "عذراً، لقد نفدت حصتك التجريبية بالكامل (0 طلبات متبقية). يرجى الترقية لإحدى الباقات المدفوعة!"
            conn.close()

            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(f"""
            <!DOCTYPE html>
            <html lang="ar" dir="rtl"><head><meta charset="UTF-8"><title>استهلاك الطلب</title></head>
            <body style="background: #0f172a; color: #fff; text-align: center; padding: 50px; font-family: Tahoma;">
                <h2>{msg}</h2>
                <br><a href="/portal?key={key}" style="color: #38bdf8;">العودة لبوابة العميل</a>
            </body></html>
            """.encode('utf-8'))

def run():
    init_db()
    server_address = ('', PORT)
    httpd = HTTPServer(server_address, AegisWebHandler)
    print(f"🌐 [Aegis Cloud SaaS] Running securely on http://localhost:{PORT}")
    httpd.serve_forever()

if __name__ == '__main__':
    run()
          
