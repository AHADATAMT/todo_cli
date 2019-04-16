import fire
import os
import sqlite3
import re
DEFAULT_PATH = os.path.join(os.path.dirname(__file__), 'database.sqlite3')


def db_connect(db_path=DEFAULT_PATH):
    con = sqlite3.connect(db_path)
    return con


def todo_table():
    con = db_connect()
    cur = con.cursor()
    todo_sql = """
        CREATE TABLE IF NOT EXISTS todo (
            id INTEGER PRIMARY KEY,
            task TEXT NOT NULL,
            due_date DATETIME,
            is_done INTEGER DEFAULT 0,
            project_id INTEGER)
        """
    cur.execute(todo_sql)


def project_table():
    con = db_connect()
    cur = con.cursor()
    todo_sql = """
        CREATE TABLE IF NOT EXISTS project (
            id INTEGER PRIMARY KEY,
            title TEXT NOT NULL)
        """
    cur.execute(todo_sql)


def user_table():
    con = db_connect()
    cur = con.cursor()
    todo_sql = """
        CREATE TABLE IF NOT EXISTS user (
            id INTEGER PRIMARY KEY,
            fullname TEXT NOT NULL,
            email TEXT)
        """
    cur.execute(todo_sql)


def initTable():
    todo_table()
    project_table()
    user_table()


initTable()


def insertcolumn():
    con = db_connect()
    cur = con.cursor()
    todo_sql = """ALTER TABLE todo ADD user_id INTEGER;"""
    cur.execute(todo_sql)


def add_task_sql(task):
    try:
        text = task["text"]
        due_date = task["due_date"]
        project_id = int(task["project_id"])
        con = db_connect()
        cur = con.cursor()
        sql = """ INSERT INTO todo (task, due_date, project_id, user_id )
                    VALUES ('{text}','{due_date}',{project_id})"""
        cur.execute(sql)
        con.commit()
        print(cur.rowcount, "Record inserted successfully into todo table")
    except sqlite3.Error as error:
        print("Failed inserting record into python_users table {}".format(error))


def show_tasks_sql(cmd_obj):
    cmd = ""
    if cmd_obj['select']:
        ids_str = f"""{cmd_obj['select']['ids']}"""
        if cmd_obj['select']['status'] == "-1":
            status = f"""is_done IN (0,1)"""
        else:
            status = f"""is_done = {cmd_obj['select']['status']}"""
        if cmd_obj['select']['ids'] == "-1":
            ids_str = ""
        elif "," in ids_str:
            ids_str = f"""AND id IN ({ids_str})"""
        else:
            ids_str = f"""AND id = {ids_str}"""

        cmd += f"" if ids_str and status else f"""WHERE {status} {ids_str}"""

    if cmd_obj['sort']:
        column = cmd_obj['sort']['column']
        is_asc = "ASC" if cmd_obj['sort']['is_asc'].lower(
        ) == 'true' or 'yes' else "DESC"

        cmd += f""" ORDER BY {column} {is_asc}"""
    try:
        con = db_connect()
        cur = con.cursor()
        sql = f"SELECT * FROM `todo` {cmd}"
        cur.execute(sql)
        records = cur.fetchall()
        cur.close()
        return records
    except sqlite3.Error as error:
        print(format(error))


def mark_complete_sql(id):
    try:
        con = db_connect()
        cur = con.cursor()
        sql = f"""UPDATE todo SET is_done = 1 WHERE id = {id}"""
        cur.execute(sql)
        con.commit()
        print(cur.rowcount, "Update successfully")
        return True
    except sqlite3.Error as error:
        print("Failed Update {}".format(error))


def show_task_by_project_sql(id):
    try:
        con = db_connect()
        cur = con.cursor()
        sql = f"""SELECT * FROM todo WHERE project_id = {id}"""
        cur.execute(sql)
        records = cur.fetchall()
        con.commit()
        cur.close()
        return records
    except sqlite3.Error as error:
        print("Failed {}".format(error))


def show_projects_sql():
    try:
        con = db_connect()
        cur = con.cursor()
        sql = f"""SELECT * FROM project"""
        cur.execute(sql)
        records = cur.fetchall()
        con.commit()
        cur.close()
        return records
    except sqlite3.Error as error:
        print("Failed {}".format(error))


def add_projects_sql(title_project):
    try:
        con = db_connect()
        cur = con.cursor()
        sql = f""" INSERT INTO project (title)
                    VALUES ('{title_project}')"""
        cur.execute(sql)
        con.commit()
        print(cur.rowcount, "Record inserted successfully into Project table")
    except sqlite3.Error as error:
        print("Failed inserting record into Project table {}".format(error))


def print_users_sql():
    try:
        con = db_connect()
        cur = con.cursor()
        sql = f"""SELECT * FROM user"""
        cur.execute(sql)
        records = cur.fetchall()
        con.commit()
        cur.close()
        return records
    except sqlite3.Error as error:
        print("Failed {}".format(error))


def add_user_sql(user):
    try:
        con = db_connect()
        cur = con.cursor()
        sql = f""" INSERT INTO user (fullname,email)
                    VALUES ('{user["fullname"]}','{user["email"]}')"""
        cur.execute(sql)
        con.commit()
        print(cur.rowcount, "Record inserted successfully into Project table")
    except sqlite3.Error as error:
        print("Failed inserting record into Project table {}".format(error))


def update_task_sql(column_name, value, taskid):
    try:
        con = db_connect()
        cur = con.cursor()
        sql = f"""UPDATE todo SET {column_name} = {value} WHERE id = {taskid}"""
        cur.execute(sql)
        con.commit()
        print(cur.rowcount, "Record inserted successfully into Project table")
    except sqlite3.Error as error:
        print("Failed inserting record into Project table {}".format(error))


class todolist(object):

    def add_task(self):
        task = {
            "text": input('Input task: '),
            "due_date": input('Due date: '),
            "project_id": input('Project id (enter to skip): '),
            "user_id": input('User id (enter to skip): ')
        }

        add_task_sql(task)

    def show_tasks(self, command1="", command2=""):
        print(command1)
        commands = {
            "sort": False,
            "select": False
        }

        if "-sort" in command1 or "-sort" in command2:
            commands['sort'] = {
                "column":  input('Sort by column: '),
                "is_asc":  input('Is asc? ( yes | no): ')
            }

        if "-select" in command1 or "-select" in command2:
            commands['select'] = {
                "ids":  input('ID Tasks (Single id - Ex: 3 | multiple - Ex: 1,2,... | all = -1): '),
                "status": input("Status (complete = 1| incomplete = 0 | all = -1): ")
            }
        # print(condition)
        records = show_tasks_sql(commands)
        self.print_task(records)

    def show_tasks_project(self, project_id):
        records = show_task_by_project_sql(project_id)
        self.print_task(records)

    def mark_complete(self, id):
        if mark_complete_sql(id):
            self.show_tasks(id)

    def print_task(self, records):
        for row in records:
            isDone = 'incomplete' if row[3] == 0 else 'complete'
            print("-------------(", row[0], ")------------")
            print("| Task:", row[1])
            print("| Due date: ", row[2])
            print("| Status: ", isDone)
            print("| Project: ", row[4])
            print("| Assign: ", row[5])
            print("-------------------------------")

    def show_projects(self):
        records = show_projects_sql()
        self.print_projects(records)

    def add_projects(self):
        title_project = input("Project title: ")
        add_projects_sql(title_project)

    def print_projects(self, records):
        for row in records:
            print("-------------------------------")
            print("[", row[0], "] -", row[1])
            print("-------------------------------")

    def show_users(self):
        records = print_users_sql()
        self.print_user(records)

    def print_user(self, records):
        for row in records:
            print("-------------------------------------------------")
            print("[", row[0], "] -", row[1], "-", row[2])
            print("-------------------------------------------------")

    def add_users(self):
        user = {
            "fullname": input("Fullname: "),
            "email": input("Email: ")
        }
        add_user_sql(user)

    def assign_task(self, taskid, value):
        update_task_sql('user_id', value, taskid)


if __name__ == '__main__':
    fire.Fire(todolist)
