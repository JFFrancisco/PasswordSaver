from cryptography.fernet import Fernet
from prettytable import PrettyTable
import sqlite3
from sqlite3 import Error


def init_crypto_file():
    """Creates The file if it doesnt exists and decode the DB"""
    try:
        decrypt_database()
    except FileNotFoundError:
        with open("key.key", "wb") as file:
            key = Fernet.generate_key()
            file.write(key)


def encrypt_message(message):
    """Take a message and encrypt it.
    :parameter: string message
    :return: bytes encrypted message"""
    with open("key.key", "rb") as files:
        key = files.read()
    encoded = message.encode()
    return Fernet(key).encrypt(encoded)


def decrypt_message(message):
    """Take a message and decrypt it.
    :parameter: bytes encrypted message
    :return: string decrypted message"""
    with open("key.key", "rb") as files:
        keys = files.read()
    decrypted = Fernet(keys).decrypt(message)
    return decrypted.decode()


def encrypt_database():
    """Loops through the database and encrypts it"""
    with open("key.key", "wb") as crypto_file:
        new_key = Fernet.generate_key()
        crypto_file.write(new_key)
    all_tables_sql = """select name from sqlite_master where type='table'"""
    tables = retrieve_passwords(all_tables_sql)
    for table in tables:
        table_name = table[0]
        table_sql = """SELECT * FROM '{}'""".format(table_name)
        table2 = retrieve_passwords(table_sql)
        for row in table2:
            if table_name == "users":
                encrypted1 = encrypt_message(row[0]).decode()
                encrypted2 = encrypt_message(row[1]).decode()
                encode_sql = """UPDATE users SET username = "{}", password = "{}" WHERE username = '{}'"""\
                    .format(encrypted1, encrypted2, row[0])
                update_credentials(encode_sql)
            else:
                encrypted1 = encrypt_message(row[0]).decode()
                encrypted2 = encrypt_message(row[1]).decode()
                encrypted3 = encrypt_message(row[2]).decode()
                encode_sql = """UPDATE '{}' SET domain = '{}', username = "{}", password = "{}" WHERE domain = '{}'""" \
                    .format(table_name, encrypted1, encrypted2, encrypted3, row[0])
                update_credentials(encode_sql)


def decrypt_database():
    """Loops through the database and decrypts it"""
    all_tables_sql = """select name from sqlite_master where type='table'"""
    tables = retrieve_passwords(all_tables_sql)
    for table in tables:
        table_name = table[0]
        table_sql = """SELECT * FROM '{}'""".format(table_name)
        table2 = retrieve_passwords(table_sql)
        for row in table2:
            if table_name == "users":
                encrypted1 = decrypt_message(row[0].encode())
                encrypted2 = decrypt_message(row[1].encode())
                decode_sql = """UPDATE users SET username = "{}", password = "{}" WHERE username = '{}'"""\
                    .format(encrypted1, encrypted2, row[0])
                update_credentials(decode_sql)
            else:
                encrypted1 = decrypt_message(row[0].encode())
                encrypted2 = decrypt_message(row[1].encode())
                encrypted3 = decrypt_message(row[2].encode())
                decode_sql = """UPDATE '{}' SET domain = '{}', username = "{}", password = "{}" WHERE domain = '{}'""" \
                    .format(table_name, encrypted1, encrypted2, encrypted3, row[0])
                update_credentials(decode_sql)


def create_conn():
    """Creates DB connection
    :return: conn """
    db = "database.sqlite"
    try:
        conn = sqlite3.connect(db)
        return conn
    except Error as e:
        print(e)


def close_conn(conn):
    """Closes DB connection
    :parameter: DB connection"""
    conn.close()


def create_table(sql_text):
    """Creates a Table to the given sql"""
    try:
        conn = create_conn()
        cur = conn.cursor()
        cur.execute(sql_text)
    except Error as e:
        print(e)


def table_exist(table_name):
    """Check if the table exists
    :parameter: str - name of the table
    :return: bool - True if it doesn't"""
    con = create_conn()
    cur = con.cursor()
    cur.execute("""SELECT COUNT(name) FROM sqlite_master WHERE TYPE='table' AND NAME=?""", (table_name,))
    if cur.fetchone()[0] > 0:
        return False
    else:
        return True


def insert_into_table(sql_text):
    """Insert data into a table with the given sql"""
    try:
        conn = create_conn()
        cur = conn.cursor()
        cur.execute(sql_text)
        conn.commit()
    except Error as e:
        print(e)


def delete_from_table(sql_text):
    """Delete info from the table"""
    conn = create_conn()
    cur = conn.cursor()
    cur.execute(sql_text)
    conn.commit()


def add_user(username):
    """ Create a table for a specific user
    :return None:"""
    add_user_sql = """CREATE TABLE IF NOT EXISTS {} ( 
    website NOT NULL,
    username NOT NULL PRIMARY KEY,
    password NOT NULL)""".format(username)
    try:
        cur = create_conn().cursor()
        cur.execute(add_user_sql)
    except Error as e:
        print(e)


def check_user(username):
    """Check if user exists and if it does gets the respective password
    :parameter: string username
    :return: tuple username and password"""
    try:
        cur = create_conn().cursor()
        cur.execute("""SELECT * FROM users WHERE username = ?""", (username,))
        print(cur.fetchall())
    except Error as e:
        print(e)


def retrieve_passwords(sql_text):
    """Retrieves the wanted data from the database
    :returns the fetched data"""
    try:
        conn = create_conn()
        cur = conn.cursor()
        cur.execute(sql_text)
        return cur.fetchall()
    except Error as e:
        print(e)


def update_credentials(sql_text):
    """updates the credentials through the sql text"""
    try:
        conn = create_conn()
        cur = conn.cursor()
        cur.execute(sql_text)
        conn.commit()
    except Error as e:
        print(e)


def create_pretty_table(data):
    """"Creates a table to show the passwords
    :parameter: lists"""
    table = PrettyTable()
    table.field_names = ["Website/App", "Username", "Password"]
    for d in data:
        table.add_row(d)
    print(table)


def log_in():
    """Login to an existing user
    :return str - current user
            Bool - True if the user manage to login, false otherwise"""
    tries = 3
    user_table_sql = """CREATE TABLE IF NOT EXISTS users (username PRIMARY KEY NOT NULL, password NOT NULL)"""
    create_table(user_table_sql)
    try:
        while tries >= 0:
            username = input("What's is your username?\n>")
            password = input("What's is your password?\n>")
            sql_text = """SELECT * FROM users WHERE username = '{}' AND password = '{}'""".format(username, password)
            data = retrieve_passwords(sql_text)
            tries -= 1
            if len(data) > 0:
                print("Welcome {}".format(username))
                global current_user
                current_user = username
                return True
            elif tries == 0:
                print("You wasted all your tries. Bye!")
            else:
                print("Invalid username/password. You have {} tries left.".format(tries))
                try_again = input("Do you wanna try again?(Y/N)\n")
                if yes_no(try_again):
                    pass
                else:
                    print("Bye!")
                    return False
    except Error as e:
        print(e)


def sign_in():
    """Sign in a new user adding their information to the database"""
    print("Let's create one for you then.")
    username = input(str("What's is your username?\n>"))
    password = input(str("What's is your password?\n>"))
    try:
        user_table_sql = """CREATE TABLE IF NOT EXISTS users (username PRIMARY KEY NOT NULL, password NOT NULL)"""
        new_user_table_sql = """CREATE TABLE {} (
        domain PRIMARY KEY NOT NULL,
        username NOT NULL, 
        password NOT NULL)""".format(username)
        create_table(user_table_sql)
        if table_exist(username):
            create_table(new_user_table_sql)
        else:
            print("That user already exists, pick another one")
            sign_in()
        add_credentials_sql = """INSERT INTO users(username, password) VALUES ('{}', '{}')""".format(username, password)
        insert_into_table(add_credentials_sql)
        global current_user
        current_user = username
    except Error as e:
        print(e)


def add_credentials():
    print("Let's Store your passwords...")
    domain = input("Whats is the website/App that you wanna store your password?\n>")
    username = input("What is your username in {}\n>".format(domain))
    password = input("What about the password?\n>")
    new_credentials_sql = """INSERT INTO {} (domain, username, password) VALUES ('{}', '{}', '{}')"""\
        .format(current_user, domain, username, password)
    insert_into_table(new_credentials_sql)
    add_search_quit()


def look_credentials():
    """check if the user wants all the info or just one"""
    one_all = input("Do you want to find a specific password or all of them?\n1. One\n2. All\n>")
    try:
        answer = int(one_all)
        if answer == 1:
            domain = input("From which APP/Website do you want your passwords?\n> ")
            get_one_sql = """SELECT * FROM '{}' WHERE domain = '{}'""".format(current_user, domain)
            data = retrieve_passwords(get_one_sql)
            create_pretty_table(data)
        elif answer == 2:
            get_all_sql = """SELECT * FROM '{}'""".format(current_user)
            data = retrieve_passwords(get_all_sql)
            create_pretty_table(data)
        else:
            print("It has to be 1 or 2")
            look_credentials()
    except ValueError:
        print("You typed something that is not a number please type 1 or 2")
        look_credentials()
    add_search_quit()


def delete_credentials():
    """check what the user wants to delete"""
    one_all = input("Do you want to delete a specific password or all of them?\n1. One\n2. All\n>")
    try:
        answer = int(one_all)
        if answer == 1:
            domain = input("From which APP/Website do you want to delete your password from?\n> ")
            delete_one_sql = """DELETE FROM '{}' WHERE domain = '{}'""".format(current_user, domain)
            delete_from_table(delete_one_sql)
        elif answer == 2:
            delete_all_sql = """DELETE FROM '{}'""".format(current_user)
            delete_from_table(delete_all_sql)
        else:
            print("It has to be 1 or 2")
            delete_credentials()
    except ValueError:
        print("You typed something that is not a number please type 1 or 2")
        delete_credentials()
    add_search_quit()


def yes_no(question):
    """Check if the string is a Yes or No answer
    :parameter: str - answer
    :return: Bool - True if yes False if anything else """
    if question.upper() == "Y" or question.upper() == "YES":
        return True
    else:
        return False


def add_search_quit():
    answer = input("What do you want to do now?\n"
                   "1. ADD more credentials?\n2. Look for credentials?\n3. Delete credentials?\n4. Quit\n>")
    try:
        answer = int(answer)
        if answer == 1:
            add_credentials()
        elif answer == 2:
            look_credentials()
        elif answer == 3:
            delete_credentials()
        elif answer == 4:
            encrypt_database()
            conn = create_conn()
            conn.close()
            print("Bye!")
        else:
            print("It has to be a number between 1 and 4")
            add_search_quit()
    except ValueError:
        print("You typed something that is not a number please type something between 1 and 4")
        add_search_quit()


def main():
    init_crypto_file()
    acc_question = input("Hello, Do you already have an account?(Y/N)\n>")
    if yes_no(acc_question) and log_in():
        add_search_quit()
    elif not yes_no(acc_question):
        sign_in()
        add_credentials()
    else:
        encrypt_database()


if __name__ == "__main__":
    main()
