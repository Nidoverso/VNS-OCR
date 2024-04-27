import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from tkinter import messagebox
from PIL import Image, ImageTk
import cv2
import os
import time
from VisualNovelSubs.vns import subtitles
from VisualNovelSubs.vns import ocr
    

class VNSOCRApp:
    
    def __init__(self, root):

        self.title = "VNS OCR"
    
        self.root = root
    
        self.root.title(self.title)

        self.status_path = "status.json"

        self.default_start_frame = 0

        self.default_end_frame = 1000000000

        self.ocr_status = ocr.OCRStatus(video_path="", number_of_sample_frames=5, sample_frames=[], region=[100, 100, 100, 100], default_start_end=True, start_frame=self.default_start_frame, end_frame=self.default_end_frame, frame_skip=10, queue=[])
        
        self.outputs_path = "outputs"

        self.video_frame_count = 0

        self.video_fps = 0

        self.video_width = 0
        
        self.video_height = 0

        self.current_rectangle = None

        self.sample_frames_index = 0

        if not os.path.exists(self.outputs_path):
            
            os.mkdir(self.outputs_path)

        self.load_ocr_status()

        if os.path.exists(self.ocr_status.video_path):

            self.open_video()

        else:

            self.ocr_status.video_path = ""

        self.default_start_end = tk.BooleanVar()
        self.default_start_end.set(self.ocr_status.default_start_end)

        self.root.rowconfigure(0, minsize=20)
        self.root.rowconfigure(20, minsize=20)
        self.root.columnconfigure(0, minsize=20)
        self.root.columnconfigure(3, minsize=40)
        self.root.columnconfigure(8, minsize=20)
        
        tk.Button(self.root, text="Select video", command=self.select_video, width=15).grid(row=1, column=1, sticky=tk.E)
        self.select_video_entry = tk.Entry(self.root, state="disabled")
        self.select_video_entry.grid(row=1, column=2, sticky=tk.W)
        
        if os.path.exists(self.ocr_status.video_path):
            self.select_video_entry.config(state="normal")
            self.select_video_entry.delete(0, 'end')
            self.select_video_entry.insert(0, self.ocr_status.video_path)
            self.select_video_entry.config(state="disabled")
        else:
            self.ocr_status.video_path = ""

        tk.Button(self.root, text="Get sample frames", command=self.get_sample_frames, width=15).grid(row=3, column=1, sticky=tk.E)
        self.number_of_sample_frames_entry = tk.Entry(self.root)
        self.number_of_sample_frames_entry.insert(0, str(self.ocr_status.number_of_sample_frames))
        self.number_of_sample_frames_entry.grid(row=3, column=2, sticky=tk.W)
        self.number_of_sample_frames_entry.bind("<FocusOut>", lambda event, e=self.number_of_sample_frames_entry: self.validate_entry(e, 1, self.video_frame_count))
        
        region_parameters = ["X", "Y", "Width", "Height"]
        self.region_entries = []
        for i in range(4):
            tk.Label(self.root, text=region_parameters[i] + ": ").grid(row=(5 + i), column=1, sticky=tk.E)
            entry = tk.Entry(self.root)
            entry.insert(0, str(self.ocr_status.region[i]))
            entry.grid(row=(5 + i), column=2, sticky=tk.W)
            if i % 2 == 0:
                entry.bind("<FocusOut>", lambda event, e=entry: self.validate_entry(e, 0, self.video_width))
            else:
                entry.bind("<FocusOut>", lambda event, e=entry: self.validate_entry(e, 0, self.video_height))
            self.region_entries.append(entry)
        tk.Button(self.root, text="Draw region", command=self.draw_region, width=15).grid(row=9, column=1, columnspan=2)

        ttk.Checkbutton(self.root, text=f"Default Start-End ({self.default_start_frame}, {self.default_end_frame})", variable=self.default_start_end, command=self.toggle_default_start_end).grid(row=11, column=1, columnspan=2)

        tk.Label(self.root, text="Start Frame: ").grid(row=12, column=1, sticky=tk.E)
        self.start_frame_entry = tk.Entry(self.root)
        self.start_frame_entry.insert(0, str(self.ocr_status.start_frame))
        self.start_frame_entry.grid(row=12, column=2, sticky=tk.W)
        self.start_frame_entry.bind("<FocusOut>", lambda event, e=self.start_frame_entry: self.validate_entry(e, self.default_start_frame, self.default_end_frame))

        tk.Label(self.root, text="End Frame: ").grid(row=13, column=1, sticky=tk.E)
        self.end_frame_entry = tk.Entry(self.root)
        self.end_frame_entry.insert(0, str(self.ocr_status.end_frame))
        self.end_frame_entry.grid(row=13, column=2, sticky=tk.W)
        self.end_frame_entry.bind("<FocusOut>", lambda event, e=self.end_frame_entry: self.validate_entry(e, self.default_start_frame, self.default_end_frame))

        tk.Label(self.root, text="Frame Skip: ").grid(row=15, column=1, sticky=tk.E)
        self.frame_skip_entry = tk.Entry(self.root)
        self.frame_skip_entry.insert(0, str(self.ocr_status.frame_skip))
        self.frame_skip_entry.grid(row=15, column=2, sticky=tk.W)
        self.frame_skip_entry.bind("<FocusOut>", lambda event, e=self.frame_skip_entry: self.validate_entry(e, 1, self.video_frame_count))

        tk.Button(self.root, text="Add to queue", command=self.add_to_queue, width=15).grid(row=17, column=1, columnspan=2)

        self.button_queue = tk.Button(self.root, text=f"Queue ({str(len(self.ocr_status.queue))})", command=self.queue, width=15)
        self.button_queue.grid(row=19, column=1, columnspan=2)

        tk.Button(self.root, text="Show Frame", command=self.show_frame, width=15).grid(row=1, column=5, sticky=tk.E)
        self.show_frame_entry = tk.Entry(self.root)
        self.show_frame_entry.insert(0, str(0))
        self.show_frame_entry.grid(row=1, column=6, sticky=tk.W)
        self.show_frame_entry.bind("<FocusOut>", lambda event, e=self.show_frame_entry: self.validate_entry(e, 0, self.video_frame_count - 1))

        self.sample_frame_label = tk.Label(self.root, text="Sample frame")
        self.sample_frame_label.grid(row=2, column=5, columnspan=2)

        self.canvas = tk.Canvas(self.root, width=960, height=540, bg='black')
        self.canvas.grid(row=3, column=4, rowspan=16, columnspan=4)

        tk.Button(self.root, text="Previous", command=self.previous_sample_frame, width=15).grid(row=19, column=5, sticky=tk.E)
        tk.Button(self.root, text="Next", command=self.next_sample_frame, width=15).grid(row=19, column=6, sticky=tk.W)

        self.toggle_default_start_end()

        if self.ocr_status.video_path and len(self.ocr_status.sample_frames) > 0:

            self.sample_frames_index = 0

            self.load_frame(self.ocr_status.video_path, self.ocr_status.sample_frames[self.sample_frames_index])
    
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)


    def on_closing(self):

        self.update_ocr_status()

        self.save_ocr_status()

        root.destroy()


    def validate_entry(self, entry, min, max):

        try:

            value = int(entry.get())

            if value < min:

                entry.delete(0, tk.END)

                entry.insert(0, str(min))

            elif value > max:

                entry.delete(0, tk.END)

                entry.insert(0, str(max))

            else:

                entry.delete(0, tk.END)

                entry.insert(0, str(value))

        except ValueError:

            entry_text = entry.get()
        
            while entry_text and not entry_text.isdigit():
        
                entry_text = entry_text[:-1]
        
            if entry_text:
        
                value = int(entry_text)
        
                if value < min:
        
                    entry.delete(0, tk.END)
        
                    entry.insert(0, str(min))
        
                elif value > max:
        
                    entry.delete(0, tk.END)
        
                    entry.insert(0, str(max))
        
                else:
        
                    entry.delete(0, tk.END)
        
                    entry.insert(0, str(value))
            else:
        
                entry.delete(0, tk.END)
        
                entry.insert(0, str(min))


    def toggle_default_start_end(self):

        if self.default_start_end.get():
        
            self.start_frame_entry.config(state=tk.DISABLED)
        
            self.end_frame_entry.config(state=tk.DISABLED)
        
        else:
        
            self.start_frame_entry.config(state=tk.NORMAL)
        
            self.end_frame_entry.config(state=tk.NORMAL)

    
    def open_video(self):

        video = cv2.VideoCapture(self.ocr_status.video_path)

        self.video_frame_count = int(video.get(cv2.CAP_PROP_FRAME_COUNT))

        self.video_fps = video.get(cv2.CAP_PROP_FPS)

        self.video_width = int(video.get(cv2.CAP_PROP_FRAME_WIDTH))

        self.video_height = int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
        root.title(f"{self.title}: {self.ocr_status.video_path} ({self.video_width}x{self.video_height}) ({self.video_fps} fps)")

        video.release()


    def update_ocr_status(self):

        self.root.focus_set()

        self.root.update()

        self.ocr_status.video_path = self.select_video_entry.get()

        self.ocr_status.number_of_sample_frames = int(self.number_of_sample_frames_entry.get())

        self.ocr_status.region = [int(entry.get()) for entry in self.region_entries] 

        self.ocr_status.default_start_end = self.default_start_end.get()

        self.ocr_status.start_frame = int(self.start_frame_entry.get())

        self.ocr_status.end_frame = int(self.end_frame_entry.get())

        self.ocr_status.frame_skip = int(self.frame_skip_entry.get())


    def save_ocr_status(self):
        
        ocr.save_ocr_status_to_json(self.status_path, self.ocr_status)


    def load_ocr_status(self):

        if os.path.exists(self.status_path):

            self.ocr_status = ocr.load_ocr_status_from_json(self.status_path)


    def resize_frame(self, frame, new_width, new_height):
            
            height, width = frame.shape[:2]

            aspect_ratio = width / height
            
            if new_width / aspect_ratio > new_height:
            
                new_width = int(new_height * aspect_ratio)
            
            else:
            
                new_height = int(new_width / aspect_ratio)

            frame = cv2.resize(frame, (new_width, new_height))

            return frame


    def load_frame(self, video_path, show_frame):

        video =  cv2.VideoCapture(video_path)

        if video.get(cv2.CAP_PROP_FRAME_COUNT) >= int(show_frame):

            video.set(cv2.CAP_PROP_POS_FRAMES, int(show_frame))

            ret, frame = video.read()
            
            if ret:

                canvas_width = self.canvas.winfo_reqwidth()
    
                canvas_height = self.canvas.winfo_reqheight()

                frame = self.resize_frame(frame, canvas_width, canvas_height)

                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
                image = Image.fromarray(frame)

                self.tk_image = ImageTk.PhotoImage(image)

                self.canvas.create_image(0, 0, anchor=tk.NW, image=self.tk_image)

                self.show_frame_entry.delete(0, tk.END)
                self.show_frame_entry.insert(tk.END, str(self.ocr_status.sample_frames[self.sample_frames_index]))

                self.sample_frame_label.config(text=f"Sample frame {self.sample_frames_index + 1}/{len(self.ocr_status.sample_frames)} (Time:{subtitles.frame_to_time(self.ocr_status.sample_frames[self.sample_frames_index], self.video_fps)})")

                if self.current_rectangle:
                
                    self.current_rectangle = self.region_rectangle(self.video_width, self.video_height, self.ocr_status.region)


    def select_video(self):

        video_path = filedialog.askopenfilename(filetypes=[("mp4 files", "*.mp4")])

        if video_path:
            
            self.select_video_entry.config(state="normal")
        
            self.select_video_entry.delete(0, 'end')
        
            self.select_video_entry.insert(0, video_path)
        
            self.select_video_entry.config(state="disabled")

            self.update_ocr_status()

            self.open_video()

            self.ocr_status.sample_frames = ocr.get_sample_frames(self.ocr_status.video_path, self.ocr_status.number_of_sample_frames)

            self.sample_frames_index = 0

            self.load_frame(self.ocr_status.video_path, self.ocr_status.sample_frames[self.sample_frames_index])
    

    def get_sample_frames(self):

        self.update_ocr_status()

        if self.ocr_status.video_path:

            video = cv2.VideoCapture(self.ocr_status.video_path)

            frame_count = int(video.get(cv2.CAP_PROP_FRAME_COUNT))

            if int(self.number_of_sample_frames_entry.get()) >= frame_count - 1:

                self.number_of_sample_frames_entry.delete(0, tk.END)
                self.number_of_sample_frames_entry.insert(tk.END, str(frame_count))

            self.update_ocr_status()

            self.ocr_status.sample_frames = ocr.get_sample_frames(self.ocr_status.video_path, self.ocr_status.number_of_sample_frames)

            self.sample_frames_index = 0

            self.load_frame(self.ocr_status.video_path, self.ocr_status.sample_frames[self.sample_frames_index])

        else:

            messagebox.showerror("Error", "No video selected.")


    def region_rectangle(self, width, height, region):

        x1 = (region[0] / width) * self.canvas.winfo_width()

        y1 = (region[1] / height) * self.canvas.winfo_height()
        
        x2 = ((region[0] + region[2]) / width) * self.canvas.winfo_width()

        y2 = ((region[1] + region[3]) / height) * self.canvas.winfo_height()

        return self.canvas.create_rectangle(x1, y1, x2, y2, outline="red", width=2)
        

    def draw_region(self):

        if len(self.ocr_status.sample_frames) > 0:

            self.update_ocr_status()

            if self.current_rectangle:
            
                self.canvas.delete(self.current_rectangle)

            self.current_rectangle = self.region_rectangle(self.video_width, self.video_height, self.ocr_status.region)

        else:

            messagebox.showerror("Error", "No sample frames.")


    def add_to_queue(self):

        if self.ocr_status.video_path:
            
            self.update_ocr_status()

            video_path = self.ocr_status.video_path

            region = self.ocr_status.region

            if self.default_start_end.get() == True:

                start_frame = self.default_start_frame

                end_frame = self.default_end_frame
            
            else:

                start_frame = self.ocr_status.start_frame

                end_frame = self.ocr_status.end_frame

            frame_skip = self.ocr_status.frame_skip

            self.ocr_status.queue.append([video_path, region, start_frame, end_frame, frame_skip])
            
            self.update_ocr_status()

            self.save_ocr_status()

            self.button_queue.config(text=f"Queue ({str(len(self.ocr_status.queue))})")

        else:

            messagebox.showerror("Error", "No video is selected.")


    def clear_queue_treeview(self):

        for item in self.queue_treeview.get_children():

            self.queue_treeview.delete(item)


    def load_queue_treeview(self, index= -1):

        self.button_queue.config(text=f"Queue ({str(len(self.ocr_status.queue))})")
        
        self.clear_queue_treeview()

        i = 0

        j = 1
        
        for q in self.ocr_status.queue:

            if i % 2 == 0:
            
                background_tag = "gray"

            else:

                background_tag = "normal"

            self.queue_treeview.insert(
                "",
                tk.END,
                text=f"{i}",
                values=(q[0], f"X-{q[1][0]} Y-{q[1][1]} W-{q[1][2]} H-{q[1][3]}", q[2], q[3], q[4]),
                tag=(background_tag)
            )

            i += 1


        if index > -1:

            self.queue_treeview.focus(self.queue_treeview.get_children()[index])
            self.queue_treeview.selection_set(self.queue_treeview.get_children()[index])


    def right_click_queue_treeview(self, event):

        if self.queue_treeview.focus():

            queue_index = self.queue_treeview.index(self.queue_treeview.selection()[0])

            self.ocr_status.queue.pop(queue_index)

            self.load_queue_treeview()


    def start_ocr(self):

        self.save_ocr_status()

        if len(self.ocr_status.queue) > 0:

            i = 0

            j = 0

            while j < len(self.ocr_status.queue):

                print(f"OCR {i + 1}, Video path: {self.ocr_status.queue[j][0]}, Region: X-{self.ocr_status.queue[j][1][0]} Y-{self.ocr_status.queue[j][1][1]} W-{self.ocr_status.queue[j][1][2]} H-{self.ocr_status.queue[j][1][3]}, Start Frame: {self.ocr_status.queue[j][2]}, End Frame: {self.ocr_status.queue[j][3]}, Frame skip: {self.ocr_status.queue[j][4]}")

                if os.path.exists(self.ocr_status.queue[j][0]):

                    start_time = time.time()
                    fps, frame_count, subs = ocr.read_video(self.ocr_status.queue[j][0], self.ocr_status.queue[j][1], self.ocr_status.queue[j][2], self.ocr_status.queue[j][3], self.ocr_status.queue[j][4])
                    end_time = time.time()

                    print(f"Time to complete OCR {i + 1}: {end_time - start_time}")

                    ocr_data_path = os.path.join(self.outputs_path, f'{os.path.splitext(os.path.basename(self.ocr_status.queue[j][0]))[0]}-x{self.ocr_status.queue[j][1][0]}-y{self.ocr_status.queue[j][1][1]}-w{self.ocr_status.queue[j][1][2]}-h{self.ocr_status.queue[j][1][3]}-sf{self.ocr_status.queue[j][2]}-ef{self.ocr_status.queue[j][3]}-fs{self.ocr_status.queue[j][4]}.ocrdata')

                    ocr_data = ocr.OCRData(fps, frame_count, self.ocr_status.queue[j][1], self.ocr_status.queue[j][4], subs)

                    ocr.save_ocr_data_to_json(ocr_data_path, ocr_data)

                    self.ocr_status.queue.pop(j)

                else:

                    print("Skipped. The video file was not found.")

                    j += 1

                i += 1

            self.button_queue.config(text=f"Queue ({str(len(self.ocr_status.queue))})")

            self.queue_window.destroy()

            messagebox.showinfo("Info", "OCR completed.")
                
        else:
            
            messagebox.showerror("Error", "No queued items.")


    def queue(self):

        self.queue_window = tk.Toplevel(self.root)

        self.queue_window.title("Queue")

        self.queue_window.rowconfigure(0, minsize=20)
        self.queue_window.rowconfigure(3, minsize=20)
        self.queue_window.columnconfigure(0, minsize=20)
        self.queue_window.columnconfigure(4, minsize=20)

        tk.Label(self.queue_window, text="Project name: ").grid(row=0, column=1, padx=10, pady=10, columnspan=2)

        self.queue_treeview = ttk.Treeview(self.queue_window, columns=("video_path", "region", "start_frame", "end_frame", "frame_skip"), height=20, selectmode="browse")
        self.queue_treeview.column("#0", minwidth=0, width=0, stretch=False)
        self.queue_treeview.column("video_path", width=400)
        self.queue_treeview.column("region", width=150)
        self.queue_treeview.column("start_frame", width=100)
        self.queue_treeview.column("end_frame", width=100)
        self.queue_treeview.column("frame_skip", width=100)
        self.queue_treeview.heading("#0", text="Index")
        self.queue_treeview.heading("video_path", text="Video path", anchor="w")
        self.queue_treeview.heading("region", text="Region", anchor="w")
        self.queue_treeview.heading("start_frame", text="Start frame", anchor="w")
        self.queue_treeview.heading("end_frame", text="End frame", anchor="w")
        self.queue_treeview.heading("frame_skip", text="Frame skip", anchor="w")
        self.queue_treeview.tag_configure('gray', background='lightgray')
        self.queue_treeview.tag_configure('normal', background='white')
        self.queue_treeview.grid(row=0, column=1, columnspan=2)
        self.queue_treeview.bind("<Button-3>", self.right_click_queue_treeview)

        self.queue_scrollbar = ttk.Scrollbar(self.queue_window, orient="vertical", command=self.queue_treeview.yview)
        
        self.queue_treeview.configure(yscrollcommand=self.queue_scrollbar.set)

        self.queue_scrollbar.grid(row=0, column=3, sticky='nse')
        
        tk.Button(self.queue_window, text="Accept", width=10, command=self.start_ocr).grid(row=2, column=1, padx=10, pady=10, sticky=tk.E)
        tk.Button(self.queue_window, text="Cancel", width=10, command=self.queue_window.destroy).grid(row=2, column=2, padx=10, pady=10, sticky=tk.W)
        
        self.queue_window.resizable(False, False)
    
        self.queue_window.grab_set()

        self.load_queue_treeview()

        self.root.wait_window(self.queue_window)


    def show_frame(self):

        self.root.focus_set()

        self.root.update()

        if self.ocr_status.video_path and self.show_frame_entry.get():

            if int(self.show_frame_entry.get()) not in self.ocr_status.sample_frames:

                video = cv2.VideoCapture(self.ocr_status.video_path)

                frame_count = int(video.get(cv2.CAP_PROP_FRAME_COUNT))

                if int(self.show_frame_entry.get()) >= frame_count:

                    self.show_frame_entry.delete(0, tk.END)
                    self.show_frame_entry.insert(tk.END, str(frame_count - 1))

                self.ocr_status.sample_frames.append(int(self.show_frame_entry.get()))

                self.ocr_status.sample_frames = sorted(self.ocr_status.sample_frames)

            self.sample_frames_index = self.ocr_status.sample_frames.index(int(self.show_frame_entry.get()))
            
            self.load_frame(self.ocr_status.video_path, self.ocr_status.sample_frames[self.sample_frames_index])


    def previous_sample_frame(self):

        if self.ocr_status.video_path and len(self.ocr_status.sample_frames) > 0:
        
            self.sample_frames_index -= 1

            if self.sample_frames_index < 0:

                self.sample_frames_index = len(self.ocr_status.sample_frames) - 1

            self.load_frame(self.ocr_status.video_path, self.ocr_status.sample_frames[self.sample_frames_index])


    def next_sample_frame(self):

        if self.ocr_status.video_path and len(self.ocr_status.sample_frames) > 0:
        
            self.sample_frames_index += 1

            if self.sample_frames_index > len(self.ocr_status.sample_frames) - 1:

                self.sample_frames_index = 0

            self.load_frame(self.ocr_status.video_path, self.ocr_status.sample_frames[self.sample_frames_index])


if __name__ == "__main__":

    root = tk.Tk()
    
    app = VNSOCRApp(root)

    root.resizable(False,False)
    
    root.mainloop()