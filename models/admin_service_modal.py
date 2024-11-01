from flask_mysqldb import MySQL

class AdminServiceModel:
    def __init__(self, mysql: MySQL):
        self.mysql = mysql

    def add_service(self, name, description, price):
        cursor = self.mysql.connection.cursor()
        cursor.execute(
            "INSERT INTO services (name, description, price) VALUES (%s, %s, %s)", 
            (name, description, price)
        )
        self.mysql.connection.commit()
        cursor.close()
        return True

    def update_service(self, service_id, name=None, description=None, price=None):
        cursor = self.mysql.connection.cursor()
        update_fields = []
        values = []

        if name:
            update_fields.append("name = %s")
            values.append(name)
        if description:
            update_fields.append("description = %s")
            values.append(description)
        if price:
            update_fields.append("price = %s")
            values.append(price)
        
        values.append(service_id)
        sql_query = f"UPDATE services SET {', '.join(update_fields)} WHERE id = %s"
        cursor.execute(sql_query, tuple(values))
        self.mysql.connection.commit()
        cursor.close()
        return True

    def delete_service(self, service_id):
        cursor = self.mysql.connection.cursor()
        cursor.execute("DELETE FROM services WHERE id = %s", (service_id,))
        self.mysql.connection.commit()
        cursor.close()
        return True

    def get_service_by_id(self, service_id):
        cursor = self.mysql.connection.cursor()
        cursor.execute("SELECT id, name, description, price FROM services WHERE id = %s", (service_id,))
        service = cursor.fetchone()
        cursor.close()
        return service

    def get_all_services(self):
        cursor = self.mysql.connection.cursor()
        cursor.execute("SELECT id, name, description, price FROM services")
        services = cursor.fetchall()
        cursor.close()
        return services
