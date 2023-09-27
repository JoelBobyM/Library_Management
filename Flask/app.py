from flask import Flask, render_template, request, jsonify, make_response, g
import pymssql
import datetime

server = 'localhost'
database = 'JOELBOBYM'
username = 'SA'
password = 'Jbm@21102001'

app = Flask(__name__)

def get_db():
    if 'db' not in g:
        g.db = pymssql.connect(server, username, password, database)
    return g.db.cursor()

def date_to_string(date_obj):
    if date_obj is None:
        return "N/A"  
    else:
        return date_obj.strftime("%d-%m-%Y") 
    
@app.teardown_appcontext
def close_db(error):
    db = g.pop('db', None)
    if db is not None:
        db.close()

@app.route("/")
def index():
    return render_template('index.html')

@app.route('/sign-in', methods=["GET", "POST"])
def signin():
    message = ''
    if request.method == "POST":
        try:

            fullname = request.form.get("fullname")
            admn_no = request.form.get("id")
            password = request.form.get("password")
            
            cursor = get_db()
            cursor.execute("SELECT Password FROM STUDENTS WHERE ADMISSION_NUMBER = %s", (admn_no,))
            row = cursor.fetchone()
            
            if row:
                # If a row is found, the admission number exists
                existing_password = row[0]
                if existing_password == 'NULL':
                    # If the password is 'NULL', update it
                    cursor.execute("UPDATE STUDENTS SET PASSWORD = %s WHERE ADMISSION_NUMBER = %s", (password, admn_no))
                    g.db.commit()
                    message = "Account Successfully Created"
                else:
                    message = "Account Already Exists"
            else:
                message = "Admission No. Not Found"

        except Exception as e:
            g.db.rollback()
            print("Error:", str(e))

        finally:
            cursor.close()

    return render_template('signin.html', msg_sup=message)



@app.route('/stud', methods=["GET", "POST"])
def client():
    message = ''
    render = 'signin.html'
    my_admn = " "

    if request.method == "POST":
        try:
            cursor = get_db()
            admn_no = request.form.get("id")
            password = request.form.get("password")

            if admn_no == "admin" and password == "admin":
                render = 'admin.html'
            else:
                cursor.execute("SELECT Password FROM STUDENTS WHERE ADMISSION_NUMBER = %s", (admn_no,))
                row = cursor.fetchone()

                if row and row[0] == password:
                    render = 'stud.html'
                    my_admn = admn_no
                else:
                    message = 'Incorrect Admission Number or Password'

        except Exception as e:
            g.db.rollback()
            print("Error:", str(e))

        finally:
            cursor.close()

    return render_template(render, admn_no=my_admn, msg_lin=message)


@app.route('/search-book', methods=['POST'])
def search_books():
    search_query = '%' + request.json.get('search_query') + '%'

    try:
        cursor = get_db()
        query = "SELECT Title, Available, ImageURL FROM Books WHERE Title LIKE %s"
        cursor.execute(query, search_query)
        rows = cursor.fetchall()

        books = []
        for row in rows:
            status = "Available" if row[1] == 1 else "Not Available"
            book = {"title": row[0], "status": status, "image_url": row[2]}
            books.append(book)

        if not books:
            return make_response('No Result Found', 200)

        return make_response(jsonify(books), 200)

    except Exception as e:
        g.db.rollback()
        print("Error:", str(e))
        return make_response('', 500)

    finally:
        cursor.close()


@app.route('/ir_data', methods=['POST'])
def ir_data():
    req = request.json.get('selected_tab')
    
    queries = {
        'ir_act': """
            SELECT IR.Issue_ID, B.Title, IR.Issue_Date, IR.Due_Date,  IR.Admission_Number, S.S_Name
            FROM Issue_Register AS IR
            INNER JOIN Students AS S ON IR.Admission_Number = S.Admission_Number
            INNER JOIN Books AS B ON IR.Book_ID = B.Book_ID
            WHERE IR.Return_Date IS NULL
            ORDER BY IR.Issue_ID DESC;
        """,
        'ir_full': """
            SELECT IR.Issue_ID, B.Title, IR.Issue_Date, IR.Due_Date, IR.Return_Date, IR.Admission_Number, S.S_Name
            FROM Issue_Register AS IR
            INNER JOIN Students AS S ON IR.Admission_Number = S.Admission_Number
            INNER JOIN Books AS B ON IR.Book_ID = B.Book_ID
            ORDER BY IR.Issue_ID DESC;
        """,
        'ir_stud_act': """
            SELECT IR.Issue_ID, B.Title, IR.Issue_Date, IR.Due_Date
            FROM Issue_Register AS IR
            INNER JOIN Books AS B ON IR.Book_ID = B.Book_ID
            WHERE IR.Admission_Number = %s AND IR.Return_Date IS NULL
            ORDER BY IR.Issue_ID DESC;
        """,
        'ir_stud_full': """
            SELECT IR.Issue_ID, B.Title, IR.Issue_Date, IR.Due_Date, IR.Return_Date
            FROM Issue_Register AS IR
            INNER JOIN Books AS B ON IR.Book_ID = B.Book_ID
            WHERE IR.Admission_Number = %s
            ORDER BY IR.Issue_ID DESC;
        """
    }

    if req not in queries:
        return make_response('', 400)

    try:
        cursor = get_db()
        if req in ('ir_stud_act', 'ir_stud_full'):
            admn_no = request.json.get('admn_no')
            cursor.execute(queries[req], (admn_no,))
        else:
            cursor.execute(queries[req])

        rows = cursor.fetchall()
        regs = []

        for row in rows:
            reg = {
                "Issue_ID": row[0],
                "Title": row[1],
                "Issue_Date": date_to_string(row[2]),
                "Due_Date": date_to_string(row[3]),
            }
            i=4
            if req in ('ir_stud_full', 'ir_full'):
                reg["Return_Date"] = date_to_string(row[i])
                i+=1
            if req in ('ir_full', 'ir_act'):
                reg["Admission_Number"] = row[i]
                i+=1
                reg["S_Name"] = row[i]
                i+=1

            regs.append(reg)

        response = make_response(jsonify(regs), 200)

    except Exception as e:
        g.db.rollback()
        print(f"An error occurred: {str(e)}")
        response = make_response('', 500)

    finally:
        cursor.close()

    return response


@app.route('/get_stud_det', methods=['POST'])
def stud_data():
    admn_no = request.json.get('admission_number')

    try:
        cursor = get_db()
        query = "SELECT S_Name FROM Students WHERE Admission_Number = %s"
        cursor.execute(query, (admn_no,))
        row = cursor.fetchone()

        if row:
            s_data = {"Name": row[0]}
            return jsonify(s_data), 200
        else:
            return render_template("signin.html")

    except Exception as e:
        g.db.rollback()
        print(f"An error occurred: {str(e)}")
        return make_response('', 500)

    finally:
        cursor.close()


@app.route('/iot-input', methods=['POST'])
def receive_data():
    try:
        data = request.get_json()

        if "s_data" not in data or "b_data" not in data:
            return jsonify({"error": "Invalid JSON data"}), 400

        cursor = get_db()

        query = """
            SELECT S.Admission_Number, B.Book_ID
            FROM Students AS S
            INNER JOIN Books AS B ON S.NFC_UID = %s AND B.NFC_UID = %s;
        """
        cursor.execute(query, (data["s_data"], data["b_data"]))
        rows = cursor.fetchall()

        if len(rows) == 1:
            admn_no, b_id = rows[0]
            current_date = datetime.date.today()

            query = """
                SELECT TOP 1 * FROM Issue_Register
                WHERE Admission_Number = %s AND Book_ID = %s AND Return_Date IS NULL;
            """
            cursor.execute(query, (admn_no, b_id))
            existing_row = cursor.fetchone()

            if existing_row:
                query = "UPDATE Issue_Register SET Return_Date = %s WHERE Issue_ID = %s"
                cursor.execute(query, (current_date, existing_row[0]))
                message = "Return_Date updated successfully."
            else:
                due_date = current_date + datetime.timedelta(days=30)
                query = """
                    INSERT INTO Issue_Register (Admission_Number, Book_ID, Issue_Date, Due_Date, Return_Date)
                    VALUES (%s, %s, %s, %s, NULL);
                """
                cursor.execute(query, (admn_no, b_id, current_date, due_date))
                message = "New row inserted successfully."
            g.db.commit()
            s_code = 200
        else:
            message = "No matching record found"
            s_code = 400

        return jsonify({"message": message}), s_code

    except Exception as e:
        g.db.rollback()
        return jsonify({"error": "Invalid JSON data"}), 400
    finally:
        cursor.close()

if __name__=="__main__":
    app.run(debug=True)

    
