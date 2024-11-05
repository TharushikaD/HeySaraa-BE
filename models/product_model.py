from flask_mysqldb import MySQL
import os

class ProductModel:
    def __init__(self, mysql: MySQL, base_url: str):
        self.mysql = mysql
        self.base_url = base_url  

    def add_product(self, product_name, description, category, price, image_filename):
        cursor = self.mysql.connection.cursor()
        cursor.execute(
            "INSERT INTO products (product_name, description, category, price, image_url) VALUES (%s, %s, %s, %s, %s)", 
            (product_name, description, category, price, image_filename)
        )
        self.mysql.connection.commit()
        cursor.close()
        return True

    def get_all_products(self):
        cursor = self.mysql.connection.cursor()
        cursor.execute("SELECT product_id, product_name, description, category, price, image_url FROM products")
        products = cursor.fetchall()
        cursor.close()

        
        product_list = []
        for product in products:
            product_id, name, description, category, price, image_filename = product
            image_url = f"{self.base_url}/images/{image_filename}" if image_filename else None
            product_list.append({
                'id': product_id,
                'product_name': name,
                'description': description,
                'category': category,
                'price': price,
                'image_url': image_url
            })
        return product_list

    def get_product_by_id(self, product_id):
        cursor = self.mysql.connection.cursor()
        cursor.execute("SELECT product_id, product_name, description, category, price, image_url FROM products WHERE product_id = %s", (product_id,))
        product = cursor.fetchone()
        cursor.close()

        if product:
            product_id, name, description, category, price, image_filename = product
            image_url = f"{self.base_url}/images/{image_filename}" if image_filename else None
            return {
                'id': product_id,
                'product_name': name,
                'description': description,
                'category': category,
                'price': price,
                'image_url': image_url
            }
        return None

    def update_product(self, product_id, product_name, description, category, price, image_filename):
        cursor = self.mysql.connection.cursor()
        cursor.execute(
            "UPDATE products SET product_name = %s, description = %s, category = %s, price = %s, image_url = %s WHERE product_id = %s",
            (product_name, description, category, price, image_filename, product_id)
        )
        self.mysql.connection.commit()
        cursor.close()
        return True

    def delete_product(self, product_id):
        cursor = self.mysql.connection.cursor()
        cursor.execute("DELETE FROM products WHERE product_id = %s", (product_id,))
        self.mysql.connection.commit()
        cursor.close()
        return True
