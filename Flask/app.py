from flask import Flask, render_template, request, jsonify, make_response
import pymssql
import datetime

driver = 'SQL Server'
server = 'localhost'
database = 'JOELBOBYM'
username = 'SA'
password = 'Jbm@21102001'

app = Flask(__name__)

def date_to_string(date_obj):
    if date_obj is None:
        return "N/A"  
    else:
        return date_obj.strftime("%d-%m-%Y") 

@app.route("/")
def index():
    return render_template('index.html')

@app.route('/sign-in', methods=["GET", "POST"])
def signin():
    message = ''
    if request.method == "POST":
        try:
            connection = pymssql.connect(server,username,password,database)
            cursor = connection.cursor()
            signup_det = {}
            signup_det["fullname"] = request.form.get("fullname")
            signup_det["admn_no"] = request.form.get("id")
            signup_det["password"] = request.form.get("password")
            query = "SELECT * FROM STUDENTS WHERE ADMISSION_NUMBER = %s"
            cursor.execute(query,signup_det["admn_no"])
            row = cursor.fetchall()
            print(len(row))
            if len(row) == 1:
                if row[0][3] == 'NULL': 
                    query = "UPDATE STUDENTS SET PASSWORD = %s WHERE ADMISSION_NUMBER = %s"
                    cursor.execute(query,(signup_det["password"], signup_det["admn_no"]))
                    connection.commit()
                    message = "Account Successfully Created"
                else:
                    message = "Account Already Exist"
            else:
                message = "Admission No. Not Found"

        except Exception as e:
            print("Error:", str(e))

        finally:
            cursor.close()
            connection.close()

    return render_template('signin.html', msg_sup=message)


@app.route('/stud', methods=["GET", "POST"])
def client():
    message = ''
    render = 'signin.html'
    my_admn = " "
    if request.method == "POST":
        try:
            connection = pymssql.connect(server,username,password,database)
            cursor = connection.cursor()
            signin_det = {}
            signin_det["admn_no"] = request.form.get("id")
            signin_det["password"] = request.form.get("password")
            if signin_det["admn_no"] == "admin":
                if signin_det["password"] == "admin":
                    render = 'admin.html'
                else:
                    message = 'Incorrect Password'
            else:
                query = "SELECT * FROM STUDENTS WHERE ADMISSION_NUMBER = %s"
                cursor.execute(query,signin_det["admn_no"])
                row = cursor.fetchall()
                print(len(row))
                if len(row) == 1:
                    if row[0][3] == signin_det["password"]: 
                        render = 'stud.html'
                        my_admn = signin_det["admn_no"]
                    else:
                        message = 'Incorrect Password'
                else:
                    message = "Admission No. Not Found"

        except Exception as e:
            print("Error:", str(e))

        finally:
            cursor.close()
            connection.close()
    return render_template(render, admn_no=my_admn, msg_lin = message)

@app.route('/search-book', methods=['POST'])
def search_books():
    search_query = '%'+request.json.get('search_query')+'%'
    print(search_query)

    connection = pymssql.connect(server,username,password,database)
    cursor = connection.cursor()
    query = "SELECT * FROM Books WHERE Title LIKE %s"
    cursor.execute(query,search_query)
    rows = cursor.fetchall()
    print(rows)
    
    if len(rows) == 0:
        response = make_response('', 400)
    else:
        books = []
        for row in rows:
            book = {"title": row[1], "status": "Available" if row[-1] == 1 else "Not Available", "image_url": row[3]}
            books.append(book)
        response = make_response(jsonify(books), 200)

    return response

@app.route('/ir_data', methods=['POST'])
def ir_data():
    req = request.json.get('selected_tab')
    if req == 'ir_act':
        query = """
            SELECT IR.Issue_ID, IR.Admission_Number, S.S_Name, B.Title, IR.Issue_Date, IR.Due_Date
            FROM Issue_Register AS IR
            INNER JOIN Students AS S ON IR.Admission_Number = S.Admission_Number
            INNER JOIN Books AS B ON IR.Book_ID = B.Book_ID
            WHERE IR.Return_Date IS NULL
            ORDER BY IR.Issue_ID DESC;;
        """
    elif req == 'ir_full':
        query = """
            SELECT IR.Issue_ID, IR.Admission_Number, S.S_Name, B.Title, IR.Issue_Date, IR.Due_Date, IR.Return_Date
            FROM Issue_Register AS IR
            INNER JOIN Students AS S ON IR.Admission_Number = S.Admission_Number
            INNER JOIN Books AS B ON IR.Book_ID = B.Book_ID
            ORDER BY IR.Issue_ID DESC;;
        """
    elif req == 'ir_stud_act':
        query = """
            SELECT IR.Issue_ID, B.Title , IR.Issue_Date, IR.Due_Date
            FROM Issue_Register AS IR
            INNER JOIN Books AS B ON IR.Book_ID = B.Book_ID
            WHERE
                IR.Admission_Number = %s
                AND IR.Return_Date IS NULL
            ORDER BY IR.Issue_ID DESC;
        """
    elif req == 'ir_stud_full':
        query = """
            SELECT IR.Issue_ID, B.Title AS Book_Title, IR.Issue_Date, IR.Due_Date, IR.Return_Date
            FROM Issue_Register AS IR
            INNER JOIN Books AS B ON IR.Book_ID = B.Book_ID
            WHERE IR.Admission_Number = %s
            ORDER BY IR.Issue_ID DESC;
        """
    else:
        return make_response('', 400)

    try:
        connection = pymssql.connect(server, username, password, database)
        cursor = connection.cursor()

        if (req == 'ir_stud_act') or (req == 'ir_stud_full'):
            admn_no = request.json.get('admn_no')
            cursor.execute(query,admn_no)
        elif (req == 'ir_act') or (req == 'ir_full'):
            cursor.execute(query)

        rows = cursor.fetchall()
        regs = []

        if (req == 'ir_act') or (req == 'ir_full'):
            for row in rows:
                print(row, row[5])
                reg = {
                    "Issue_ID": row[0],
                    "Admission_Number": row[1],
                    "S_Name": row[2],
                    "Title": row[3],
                    "Issue_Date": date_to_string(row[4]),
                    "Due_Date": date_to_string(row[5]),
                }
                if req == 'ir_full' :
                    reg["Return_Date"] = date_to_string(row[6])
                regs.append(reg)
            
        elif (req == 'ir_stud_act') or (req == 'ir_stud_full'):
            for row in rows:
                reg = {
                    "Issue_ID": row[0],
                    "Title": row[1],
                    "Issue_Date": date_to_string(row[2]),
                    "Due_Date" : date_to_string(row[3]),
                }
                if (req == 'ir_stud_full') :
                    reg["Return_Date"] = date_to_string(row[4])
                regs.append(reg)
        response = make_response(jsonify(regs), 200)
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        response = make_response('', 500)
    finally:
        cursor.close()
        connection.close()

    return response



@app.route('/get_stud_det', methods=['POST'])
def stud_data():
    admn_no = request.json.get('admission_number')

    connection = pymssql.connect(server,username,password,database)
    cursor = connection.cursor()
    query = "SELECT S_Name FROM Students WHERE Admission_Number = %s "
    cursor.execute(query,admn_no)
    rows = cursor.fetchall()
    print(rows)

    if len(rows) == 1:
        s_data = {"Name" : rows[0][0]}
        response = make_response(jsonify(s_data), 200)
        return response
    else:
        return render_template("signin.html")


@app.route('/iot-input', methods=['POST'])
def receive_data():
    try:
        data = request.get_json()
        print(data)
        connection = pymssql.connect(server,username,password,database)
        cursor = connection.cursor()
        query = """
                SELECT S.Admission_Number, B.Book_ID
                FROM Students AS S
                INNER JOIN Books AS B ON S.NFC_UID = %s AND B.NFC_UID = %s;"""
        cursor.execute(query,(data["s_data"],data["b_data"]))
        rows = cursor.fetchall()
        if len(rows)==1:
            admn_no = rows[0][0]
            b_id = rows[0][1]
            current_date = datetime.date.today()
            query = "SELECT TOP 1 * FROM Issue_Register WHERE Admission_Number = %s AND Book_ID = %s AND Return_Date IS NULL"
            cursor.execute(query,(admn_no,b_id))
            existing_row = cursor.fetchone()
            if existing_row:
                print(existing_row)
                query = "UPDATE Issue_Register SET Return_Date = %s WHERE Issue_ID = %s"
                cursor.execute(query, (current_date, existing_row[0]) )
                connection.commit()
                message = "Return_Date updated successfully."
                s_code = 200
            else:
                due_date = current_date + datetime.timedelta(days=30)
                query = "INSERT INTO Issue_Register (Admission_Number, Book_ID, Issue_Date, Due_Date, Return_Date) VALUES (%s, %s, %s, %s, NULL)"
                cursor.execute(query, (admn_no, b_id, current_date, due_date) )
                connection.commit()
                message = "New row inserted successfully."
                s_code = 200
        else:
            message = "No matching record found"
            s_code = 400
        print(message,s_code)
        return jsonify({"message": message}), s_code

    except Exception as e:
        # If there's an error, respond with an appropriate status code (e.g., 400 for bad request)
        return jsonify({"error": "Invalid JSON data"}), 400


if __name__=="__main__":
    app.run(debug=True)

    
