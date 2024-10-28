import tkinter as tk
from tkinter import messagebox, scrolledtext, Label
from pymongo import MongoClient
from PIL import Image, ImageTk
from io import BytesIO
import base64

class VehicleDatabaseApp:
    def __init__(self, root):
        self.root = root
        self.root.title('Vehicle Database Viewer')

        # MongoDB connection with error handling
        try:
            self.client = MongoClient('mongodb://localhost:27017/')
            self.db = self.client['my_vehicle_db']
            self.collection = self.db['vehicles']
        except Exception as e:
            messagebox.showerror("Database Error", f"Failed to connect to MongoDB: {e}")
            root.destroy()  # Close the app if the database connection fails
            return

        # Create GUI elements
        self.display_data_button = tk.Button(root, text='Display Vehicle Data', command=self.display_data)
        self.display_data_button.pack(pady=10)

        self.data_text = scrolledtext.ScrolledText(root, wrap='word', height=10, width=50)
        self.data_text.pack(padx=10, pady=10)

        self.image_label = Label(root)  # Label to display images
        self.image_label.pack(padx=10, pady=10)

        # Ensure MongoDB connection is closed when the window is closed
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def display_data(self):
        self.data_text.delete(1.0, tk.END)  # Clear existing text
        self.image_label.config(image='')  # Clear existing image

        try:
            vehicles = self.collection.find().distinct('vehicle_id')  # Get unique vehicle IDs

            if vehicles:
                for vehicle_id in vehicles:
                    vehicle = self.collection.find_one({'vehicle_id': vehicle_id})

                    # Extract vehicle information
                    vehicle_info = (
                        f"ID: {vehicle.get('vehicle_id', 'N/A')}, "
                        f"Class: {vehicle.get('class', 'N/A')}, "
                        f"Speed: {vehicle.get('speed', 'N/A')} km/h\n"
                    )
                    self.data_text.insert(tk.END, vehicle_info)

                    # Display the vehicle's image if available
                    image_data = vehicle.get('image')  # Assuming 'image' contains the Base64 string or binary data
                    if image_data:
                        self.display_image(image_data)
            else:
                messagebox.showinfo("Info", "No data found.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to retrieve data: {e}")

    def display_image(self, image_data):
        """Convert image data to a Tkinter-compatible image and display it."""
        try:
            # If the image is stored as Base64, decode it
            if isinstance(image_data, str):
                image_data = base64.b64decode(image_data)

            # Convert the binary data to an Image object
            image = Image.open(BytesIO(image_data))
            image = image.resize((300, 200))  # Resize for better display
            tk_image = ImageTk.PhotoImage(image)

            # Update the label with the new image
            self.image_label.config(image=tk_image)
            self.image_label.image = tk_image  # Keep a reference to prevent garbage collection
        except Exception as e:
            messagebox.showerror("Error", f"Failed to display image: {e}")

    def on_close(self):
        """Close MongoDB connection and exit the application."""
        self.client.close()
        self.root.destroy()


if __name__ == '__main__':
    root = tk.Tk()
    app = VehicleDatabaseApp(root)
    root.mainloop()

