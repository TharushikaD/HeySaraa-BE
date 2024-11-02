from flask_mysqldb import MySQL


class HaircutModel:
    def __init__(self, mysql: MySQL, base_url: str):
        self.mysql = mysql
        self.base_url = base_url  # e.g., 'http://localhost:5000'

    def add_haircut(self, face_shape, haircut_name, description, image_filename):
        """Adds a new haircut entry to the database."""
        cursor = self.mysql.connection.cursor()
        cursor.execute(
            "INSERT INTO haircuts (face_shape, haircut_name, description, image_url) VALUES (%s, %s, %s, %s)",
            (face_shape, haircut_name, description, image_filename)
        )
        self.mysql.connection.commit()
        cursor.close()
        return True

    def get_all_haircuts(self):
        """Retrieves all haircuts, with full image URLs."""
        cursor = self.mysql.connection.cursor()
        cursor.execute("SELECT id, face_shape, haircut_name, description, image_url FROM haircuts")
        haircuts = cursor.fetchall()
        cursor.close()

        # Construct the haircut list with full image URLs
        haircut_list = []
        for haircut in haircuts:
            haircut_id, face_shape, name, description, image_filename = haircut
            image_url = f"{self.base_url}/images/{image_filename}" if image_filename else None
            haircut_list.append({
                'id': haircut_id,
                'face_shape': face_shape,
                'haircut_name': name,
                'description': description,
                'image_url': image_url
            })
        return haircut_list

    def get_haircut_by_id(self, haircut_id):
        """Retrieves a specific haircut by its ID with full image URL."""
        cursor = self.mysql.connection.cursor()
        cursor.execute(
            "SELECT face_shape, haircut_name, description, image_url FROM haircuts WHERE id = %s",
            (haircut_id,)
        )
        haircut = cursor.fetchone()
        cursor.close()

        if haircut:
            face_shape, name, description, image_filename = haircut
            image_url = f"{self.base_url}/images/{image_filename}" if image_filename else None
            return {
                'id': haircut_id,
                'face_shape': face_shape,
                'haircut_name': name,
                'description': description,
                'image_url': image_url
            }
        return None
    

    # def get_haircuts_by_face_shape(self, face_shape):
    #     """Retrieves haircuts that match the specified face shape."""
    #     cursor = self.mysql.connection.cursor()
    #     cursor.execute("SELECT id, face_shape, haircut_name, description, image_url FROM haircuts WHERE face_shape = %s", (face_shape,))
    #     haircuts = cursor.fetchall()
    #     cursor.close()

    #     # Construct the haircut list with full image URLs
    #     haircut_list = []
    #     for haircut in haircuts:
    #         haircut_id, face_shape, name, description, image_filename = haircut
    #         image_url = f"{self.base_url}/images/{image_filename}" if image_filename else None
    #         haircut_list.append({
    #             'id': haircut_id,
    #             'face_shape': face_shape,
    #             'haircut_name': name,
    #             'description': description,
    #             'image_url': image_url
    #         })
    #     return haircut_list
    def get_haircuts_by_face_shape(self, face_shape):
        """Retrieves haircuts that match the specified face shape."""
        cursor = self.mysql.connection.cursor()
        cursor.execute("SELECT id, face_shape, haircut_name, description, image_url FROM haircuts WHERE face_shape = %s", (face_shape,))
        haircuts = cursor.fetchall()
        cursor.close()

        # Construct the haircut list with full image URLs
        haircut_list = []
        for haircut in haircuts:
            haircut_id, face_shape, name, description, image_filename = haircut
            # Ensure image_filename only contains the file name
            image_url = f"{self.base_url}/images/{image_filename}" if image_filename else None
            haircut_list.append({
            'id': haircut_id,
            'face_shape': face_shape,
            'haircut_name': name,
            'description': description,
            'image_url': image_url  # This should point to the correct path
        })
        return haircut_list


    def update_haircut(self, haircut_id, face_shape, haircut_name, description, image_filename):
        """Updates a specific haircut entry."""
        cursor = self.mysql.connection.cursor()
        cursor.execute(
            "UPDATE haircuts SET face_shape = %s, haircut_name = %s, description = %s, image_url = %s WHERE id = %s",
            (face_shape, haircut_name, description, image_filename, haircut_id)
        )
        self.mysql.connection.commit()
        cursor.close()
        return True

    def delete_haircut(self, haircut_id):
        """Deletes a specific haircut entry."""
        cursor = self.mysql.connection.cursor()
        cursor.execute("DELETE FROM haircuts WHERE id = %s", (haircut_id,))
        self.mysql.connection.commit()
        cursor.close()
        return True

    
