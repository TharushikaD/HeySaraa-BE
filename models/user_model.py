from flask_mysqldb import MySQL
from werkzeug.security import generate_password_hash, check_password_hash

class UserModel:
    def __init__(self, mysql: MySQL):
        self.mysql = mysql

    def register_user(self, name, email, password, role):
        hashed_password = generate_password_hash(password)
        cursor = self.mysql.connection.cursor()
        cursor.execute(
            "INSERT INTO users (name, email, password, role) VALUES (%s, %s, %s, %s)", 
            (name, email, hashed_password, role)
        )
        self.mysql.connection.commit()
        cursor.close()
        return True

    def find_user_by_name(self, name):
        cursor = self.mysql.connection.cursor()
        cursor.execute("SELECT id, password, role FROM users WHERE name = %s", (name,))
        user = cursor.fetchone()
        cursor.close()
        return user
    
    def get_user_by_id(self, user_id):
        cursor = self.mysql.connection.cursor()
        cursor.execute("SELECT name, email, role FROM users WHERE id = %s", (user_id,))
        user = cursor.fetchone()
        cursor.close()
        return user
    
    def update_user_name(self, user_id, name):
        cursor = self.mysql.connection.cursor()
        cursor.execute("UPDATE users SET name = %s WHERE id = %s", (name, user_id))
        self.mysql.connection.commit()
        cursor.close()

    def update_user_email(self, user_id, email):
        cursor = self.mysql.connection.cursor()
        cursor.execute("UPDATE users SET email = %s WHERE id = %s", (email, user_id))
        self.mysql.connection.commit()
        cursor.close()

    def update_user_password(self, user_id, password):
        hashed_password = generate_password_hash(password)
        cursor = self.mysql.connection.cursor()
        cursor.execute("UPDATE users SET password = %s WHERE id = %s", (hashed_password, user_id))
        self.mysql.connection.commit()
        cursor.close()

    def get_users_by_role(self, role):
        cursor = self.mysql.connection.cursor()
        cursor.execute("SELECT id, name, email FROM users WHERE role = %s", (role,))
        users = cursor.fetchall()
        cursor.close()
        return users
    
    def delete_user(self, user_id):
        try:
            cursor = self.mysql.connection.cursor()
            cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
            self.mysql.connection.commit()
            cursor.close()
            return True
        except Exception as e:
            print(f"Error deleting user: {e}")
            return False


    def verify_password(self, hashed_password, password):
        return check_password_hash(hashed_password, password)