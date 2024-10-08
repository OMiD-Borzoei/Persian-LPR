import matplotlib
import matplotlib.pyplot as plt

matplotlib.use('tkAGg')

import tkinter as tk
from tkinterdnd2 import TkinterDnD, DND_FILES
from PIL import Image, ImageTk
import cv2
from threading import Thread
from time import sleep
import numpy as np

print('Loading Model')
from main import get_licence_plate

print('Model Loaded Successfully')
size = (500, 300)

persian_to_english = {
    '0': '0',
    '1': '1',
    '2': '2',
    '3': '3',
    '4': '4',
    '5': '5',
    '6': '6',
    '7': '7',
    '8': '8',
    '9': '9',
    'ب': 'B',
    'د': 'D',
    'ع': 'Ein',
    14: '',
    'ج': 'J',
    'ق': 'Quf',
    'ه': 'H',
    'ل': 'L',
    'م': 'M',
    '\u267F': '\u267F',  # Disabled People
    'ن': 'N',
    'س': 'Sin',
    'ص': 'Saw',
    'ت': 'T',
    'ط': 'Taw',
    'و': 'V',
    'ی': 'Y',
}


class ImageDropperApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Image Dropper")

        # Create GUI components
        self.label = tk.Label(root, text="Drag and drop an image here:")
        self.label.pack(pady=5)

        # Create a canvas to display the dropped image
        self.canvas = tk.Canvas(root, width=size[0], height=size[1], bg="white")
        self.canvas.pack(pady=5)

        # Create canvases for additional images (im1 and im2)
        self.canvas_im1 = tk.Canvas(root, width=size[0], height=size[1], bg="white")
        self.canvas_im1.pack(pady=5)

        # Create a text entry field
        self.entry_var = tk.StringVar()
        self.entry = tk.Entry(root, textvariable=self.entry_var, width=40)
        self.entry.pack(pady=5)

        # Allow dropping files on the label and canvas
        self.label.drop_target_register(DND_FILES)
        self.label.dnd_bind('<<Drop>>', self.on_drop)
        self.canvas.drop_target_register(DND_FILES)
        self.canvas.dnd_bind('<<Drop>>', self.on_drop)
        self.end_of_load = False
        self.last_load = False
        self.file_path = ''

    def on_drop(self, event):
        self.end_of_load = False
        self.last_load = False
        file_path = event.data
        # Remove curly braces from the file path
        self.file_path = file_path.strip('{}')
        self.display_image(file_path)

        # Clear the text entry field
        self.entry_var.set("")

    def display_image(self, file_path):
        # Open the image using PIL
        img = Image.open(self.file_path)




        # Start the processing thread
        t1 = Thread(target=self.process_image, args=(img,))
        t1.start()

        img.thumbnail(size)  # Resize the image to fit the canvas

        img_tk = ImageTk.PhotoImage(img)
        # Clear the canvas and display the image
        self.canvas.delete("all")
        self.canvas.create_image(size[0] // 2, size[1] // 2, anchor=tk.CENTER, image=img_tk)
        self.canvas.image = img_tk  # Keep a reference to prevent garbage collection


    def display_im1(self, img):
        # Perform your processing logic for im1
        # Example: im1 = some_processing_function(img_cv2)
        img = cv2.resize(img, size)
        # Convert the processed image to a Tkinter PhotoImage
        im1_tk = ImageTk.PhotoImage(image=Image.fromarray(img))

        # Display im1 on the canvas_im1
        self.canvas_im1.delete("all")
        self.canvas_im1.create_image(size[0] // 2, size[1] // 2, anchor=tk.CENTER, image=im1_tk)
        self.canvas_im1.image = im1_tk

    def display_main_im(self, img):
        # Convert PIL Image to Tkinter PhotoImage
        img = cv2.resize(img, size)
        img_tk = ImageTk.PhotoImage(image=Image.fromarray(img))

        # Clear the canvas and display the image
        self.canvas.delete("all")
        self.canvas.create_image(size[0] // 2, size[1] // 2, anchor=tk.CENTER, image=img_tk)
        self.canvas.image = img_tk  # Keep a reference to prevent garbage collection

    def process_image(self, img):
        # Update the loading animation during processing
        self.update_loading()
        img_cv2 = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
        img_cv2 = cv2.cvtColor(img_cv2, cv2.COLOR_BGR2RGB)
        # plt.imshow(img_cv2)
        # plt.show()
        # Simulate some processing (replace this with your actual processing logic)
        try:
            lp, im1, im2 = get_licence_plate(img=img_cv2)
            self.display_main_im(im1)
            lp = [persian_to_english[i] for i in lp]

            try:
                st_lp = str(lp[0]) + str(lp[1]) + ' ' + str(lp[2]) + ' ' + str(lp[3]) + str(lp[4]) + str(
                    lp[5]) + ' | ' + str(
                    lp[6]) + str(lp[7])
                # Update the entry field when processing is done
                self.end_of_load = True
                sleep(0.5)
                self.entry_var.set(f'Licence Plate: --{st_lp}--')
                self.display_im1(im2)

            except:
                self.end_of_load = True
                sleep(0.5)
                self.entry_var.set('Failed to find all characters')


        except:
            self.end_of_load = True
            sleep(0.5)
            self.entry_var.set('No Licence Plate Found')






    def update_loading(self, count=0):
        # Update the loading text in the entry field
        loading_text = "Loading" + "." * count
        self.entry_var.set(loading_text)

        # Schedule the next update after 500 milliseconds
        if not self.end_of_load:
            self.root.after(500, self.update_loading, (count + 1) % 4)
        else:
            self.last_load = True


if __name__ == "__main__":
    # Create the main Tkinter window
    print('Window Is Gonna Pop Now')
    root = TkinterDnD.Tk()
    app = ImageDropperApp(root)
    root.mainloop()
