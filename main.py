from flet import *
import sqlite3
import os

# تهيئة قاعدة البيانات
def init_db():
    conn = sqlite3.connect('alson.db')
    c = conn.cursor()
    
    # جدول الطلاب
    c.execute('''CREATE TABLE IF NOT EXISTS students 
                (id INTEGER PRIMARY KEY,
                 name TEXT NOT NULL,
                 code TEXT NOT NULL UNIQUE,
                 seat_number TEXT)''')
    
    # جدول النتائج
    c.execute('''CREATE TABLE IF NOT EXISTS results 
                (id INTEGER PRIMARY KEY,
                 student_id INTEGER,
                 subject TEXT,
                 grade TEXT,
                 FOREIGN KEY(student_id) REFERENCES students(id))''')
    
    # إضافة بيانات تجريبية
    if not c.execute("SELECT * FROM students").fetchall():
        c.executemany('INSERT INTO students (name, code, seat_number) VALUES (?,?,?)',
                    [('محمد علي', 'STD001', 'A123'), ('فاطمة حسن', 'STD002', 'B456')])
        c.executemany('INSERT INTO results (student_id, subject, grade) VALUES (?,?,?)',
                    [(1, 'الرياضيات', '95'), (1, 'الفيزياء', '88'), (2, 'الكيمياء', '92')])
    
    conn.commit()
    conn.close()

init_db()

def main(page: Page):
    page.title = 'الأسن للعلوم الحديثة'
    page.window_height = 740
    page.window_width = 390
    page.theme_mode = ThemeMode.LIGHT
    page.scroll = True

    # عناصر واجهة المستخدم
    name_field = TextField(label='اسم الطالب', icon=icons.PERSON)
    code_field = TextField(label='كود الطلاب', icon=icons.LOCK, password=True, can_reveal_password=True)
    seat_field = TextField(label='رقم الجلوس', icon=icons.CONFIRMATION_NUMBER)
    result_display = Column()

    def show_snackbar(message, color=colors.RED):
        page.snack_bar = SnackBar(Text(message, color=color))
        page.snack_bar.open = True
        page.update()

    def login_click(e):
        if not name_field.value or not code_field.value:
            show_snackbar("الرجاء ملء جميع الحقول")
            return
        
        conn = sqlite3.connect('alson.db')
        c = conn.cursor()
        c.execute("SELECT * FROM students WHERE name=? AND code=?", 
                 (name_field.value, code_field.value))
        user = c.fetchone()
        conn.close()
        
        if user:
            page.go("/الصفحه_الراسية")
        else:
            show_snackbar("بيانات الدخول غير صحيحة")

    def show_result_click(e):
        if not seat_field.value:
            show_snackbar("الرجاء إدخال رقم الجلوس")
            return
        
        conn = sqlite3.connect('alson.db')
        c = conn.cursor()
        c.execute('''SELECT subject, grade FROM results 
                  JOIN students ON students.id = results.student_id 
                  WHERE students.seat_number = ?''', (seat_field.value,))
        results = c.fetchall()
        conn.close()
        
        if results:
            result_display.controls.clear()
            for subject, grade in results:
                result_display.controls.append(
                    ListTile(
                        title=Text(subject),
                        subtitle=Text(f"الدرجة: {grade}"),
                    )
                )
            page.go("/عرض_النتيجة")
        else:
            show_snackbar("لا توجد نتائج")

    # تعريف الصفحات
    def route_change(e):
        page.views.clear()
        
        # صفحة تسجيل الدخول
        if page.route == "/":
            page.views.append(
                View(
                    "/",
                    [
                        AppBar(title=Text('تسجيل الدخول', color='white')),
                        name_field,
                        code_field,
                        ElevatedButton("دخول", on_click=login_click)
                    ],
                    bgcolor=colors.WHITE
                )
            )
        
        # الصفحة الرئيسية
        elif page.route == "/الصفحه_الراسية":
            page.views.append(
                View(
                    "/الصفحه_الراسية",
                    [
                        AppBar(title=Text('الرئيسية', color='white')),
                        seat_field,
                        ElevatedButton("عرض النتائج", on_click=show_result_click)
                    ],
                    bgcolor=colors.WHITE
                )
            )
        
        # صفحة النتائج
        elif page.route == "/عرض_النتيجة":
            page.views.append(
                View(
                    "/عرض_النتيجة",
                    [
                        AppBar(title=Text('النتائج', color='white')),
                        result_display,
                        ElevatedButton("رجوع", on_click=lambda _: page.go("/"))
                    ],
                    bgcolor=colors.WHITE
                )
            )

        page.update()

    page.on_route_change = route_change
    page.go(page.route)

app(target=main)
