import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from tkinter import messagebox
from PIL import Image, ImageTk
import os
import time
from VisualNovelSubs.vns import subtitles
from VisualNovelSubs.vns import ocr

def get_sample_number(sample):
    
    return int(sample.split('-')[1].split('.')[0])


class VNSOCRApp:
    
    def __init__(self, root):
    
        self.root = root
    
        self.root.title("VNS OCR")

        self.status_path = "status.json"

        self.ocr_status = ocr.OCRStatus("", 5, [100, 100, 100, 100], 10)
        
        self.outputs_path = "outputs"
        self.samples_path = "samples"

        self.image_index = -1
        self.image_files = []

        self.current_rectangle = None

        self.simplify_subs = tk.BooleanVar()
        self.simplify_subs.set(True)

        self.create_folders()
        self.load_ocr_status()

        self.root.rowconfigure(0, minsize=20)
        self.root.rowconfigure(18, minsize=20)
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

        tk.Label(self.root, text="Number of samples: ").grid(row=3, column=1, sticky=tk.E)
        self.number_of_samples_entry = tk.Entry(self.root)
        self.number_of_samples_entry.insert(0, str(self.ocr_status.number_of_samples))
        self.number_of_samples_entry.grid(row=3, column=2, sticky=tk.W)
        self.number_of_samples_entry.bind("<FocusOut>", lambda event, e=self.number_of_samples_entry: self.validate_entry(e, 1))
        tk.Button(self.root, text="Generate samples", command=self.generate_sample_frames, width=15).grid(row=4, column=1, columnspan=2)

        tk.Label(self.root, text="Region:").grid(row=6, column=1, columnspan=2)
        region_parameters = ["X", "Y", "Width", "Height"]
        self.region_entries = []
        for i in range(4):
            tk.Label(self.root, text=region_parameters[i] + ": ").grid(row=(7 + i), column=1, sticky=tk.E)
            entry = tk.Entry(self.root)
            entry.insert(0, str(self.ocr_status.region[i]))
            entry.grid(row=(7 + i), column=2, sticky=tk.W)
            entry.bind("<FocusOut>", lambda event, e=entry: self.validate_entry(e, 0))
            self.region_entries.append(entry)
        tk.Button(self.root, text="Draw region", command=self.draw_region, width=15).grid(row=11, column=1, columnspan=2)

        tk.Label(self.root, text="Frame Skip: ").grid(row=13, column=1, sticky=tk.E)
        self.frame_skip_entry = tk.Entry(self.root)
        self.frame_skip_entry.insert(0, str(self.ocr_status.frame_skip))
        self.frame_skip_entry.grid(row=13, column=2, sticky=tk.W)
        self.frame_skip_entry.bind("<FocusOut>", lambda event, e=self.frame_skip_entry: self.validate_entry(e, 1))

        ttk.Checkbutton(self.root, text="Simplify subs ", variable=self.simplify_subs).grid(row=15, column=1, sticky=tk.E)
        tk.Button(self.root, text="OCR Video", command=self.ocr_video, width=15).grid(row=15, column=2, sticky=tk.W)
        
        tk.Button(self.root, text="Export to SRT", command=self.export_to_srt, width=15).grid(row=17, column=1, columnspan=2)

        self.image_label = tk.Label(self.root, text="Sample")
        self.image_label.grid(row=1, column=5, columnspan=2)

        self.canvas = tk.Canvas(self.root, width=960, height=540, bg='black')
        self.canvas.grid(row=2, column=4, rowspan=15, columnspan=4)

        tk.Button(self.root, text="Previous", command=self.previous_image, width=15).grid(row=17, column=5, sticky=tk.E)
        tk.Button(self.root, text="Next", command=self.next_image, width=15).grid(row=17, column=6, sticky=tk.W)

        self.load_samples()


    def validate_entry(self, entry, min):

        try:

            value = float(entry.get())

            value = int(value)

            if value < min:

                entry.delete(0, tk.END)

                entry.insert(0, str(min))

            else:

                entry.delete(0, tk.END)

                entry.insert(0, str(value))

        except ValueError:

            entry.delete(0, tk.END)

            entry.insert(0, str(min))


    def get_image_files(self):

        samples_video_path = os.path.join(self.samples_path, os.path.splitext(os.path.basename(self.select_video_entry.get()))[0])
        
        image_files = [f for f in os.listdir(samples_video_path) if f.lower().endswith((".png", ".jpg", ".jpeg"))]

        image_files = sorted(image_files, key=get_sample_number)
        
        return image_files


    def load_samples(self):

        self.image_index = 0
        self.image_files = []
        
        samples_video_path = os.path.join(self.samples_path, os.path.splitext(os.path.basename(self.select_video_entry.get()))[0])

        if not os.path.exists(samples_video_path):

            os.mkdir(samples_video_path)

            ocr.generate_sample_frames(self.select_video_entry.get(), samples_video_path, 5)

        self.image_files = self.get_image_files()
        
        if self.image_files:

            self.load_image()

        else:

            self.canvas.delete("all")


    def load_image(self):

        if self.image_index < 0:

            self.image_index = len(self.image_files) - 1

        elif self.image_index >= len(self.image_files):

            self.image_index = 0
            
        canvas_width = self.canvas.winfo_reqwidth()
        
        canvas_height = self.canvas.winfo_reqheight()
            
        samples_video_path = os.path.join(self.samples_path, os.path.splitext(os.path.basename(self.select_video_entry.get()))[0])

        image_path = os.path.join(samples_video_path, self.image_files[self.image_index])

        image = Image.open(image_path)

        image.thumbnail((canvas_width, canvas_height))

        self.tk_image = ImageTk.PhotoImage(image)

        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.tk_image)

        label_text = os.path.splitext(os.path.basename(image_path))[0] + "/" + str(len(self.image_files))

        self.image_label.config(text=label_text)

        if self.current_rectangle:
        
            self.draw_rectangle()


    def previous_image(self):

        if self.image_files:
        
            self.image_index -= 1
        
            self.load_image()


    def next_image(self):

        if self.image_files:
        
            self.image_index += 1
        
            self.load_image()


    def select_video(self):

        video_path = filedialog.askopenfilename(filetypes=[("mp4 files", "*.mp4")])

        if video_path:
            
            self.select_video_entry.config(state="normal")
        
            self.select_video_entry.delete(0, 'end')
        
            self.select_video_entry.insert(0, video_path)
        
            self.select_video_entry.config(state="disabled")

            self.save_ocr_status()

            self.load_samples()
    

    def generate_sample_frames(self):

        if self.select_video_entry.get():

            self.save_ocr_status()
            
            samples_video_path = os.path.join(self.samples_path, os.path.splitext(os.path.basename(self.select_video_entry.get()))[0])

            start_time = time.time()
            ocr.generate_sample_frames(self.select_video_entry.get(), samples_video_path, int(self.number_of_samples_entry.get()))
            end_time = time.time()

            print(f"Time to generate sample frames: {end_time - start_time}")

            self.load_samples()

            messagebox.showinfo("Info", "Sample frames generated.")

        else:
            messagebox.showerror("Error", "No video is selected.")


    def draw_rectangle(self):

        region = [int(entry.get()) for entry in self.region_entries]

        samples_video_path = os.path.join(self.samples_path, os.path.splitext(os.path.basename(self.select_video_entry.get()))[0])
        
        image_path = os.path.join(samples_video_path, self.image_files[self.image_index])
        
        image = Image.open(image_path)

        original_width, original_height = image.size

        x1 = (region[0] / original_width) * self.canvas.winfo_width()

        y1 = (region[1] / original_height) * self.canvas.winfo_height()
        
        x2 = ((region[0] + region[2]) / original_width) * self.canvas.winfo_width()

        y2 = ((region[1] + region[3]) / original_height) * self.canvas.winfo_height()

        self.current_rectangle = self.canvas.create_rectangle(x1, y1, x2, y2, outline="red", width=2)
        

    def draw_region(self):

        if self.image_files:

            self.save_ocr_status()

            if self.current_rectangle:
            
                self.canvas.delete(self.current_rectangle)

            self.draw_rectangle()

        else:
            messagebox.showerror("Error", "There is no sample image.")


    def ocr_video(self):

        if self.select_video_entry.get():

            self.save_ocr_status()

            video_path = self.ocr_status.video_path

            region = self.ocr_status.region

            frame_skip = self.ocr_status.frame_skip

            start_time = time.time()
            fps, frame_count, subs = ocr.read_video(video_path, region, frame_skip)
            end_time = time.time()

            print(f"Time to complete OCR: {end_time - start_time}")

            ocr_data_path = os.path.join(self.outputs_path, f'{os.path.splitext(os.path.basename(video_path))[0]}-{frame_skip}.ocrdata')

            if self.simplify_subs.get() == True:
                subs = subtitles.clean_subtitles(subs)
                subs = subtitles.simplify_subtitles(subs)

            ocr_data = ocr.OCRData(fps, frame_count, region, frame_skip, subs)

            ocr.save_ocr_data_to_json(ocr_data_path, ocr_data)

            messagebox.showinfo("Info", "OCR completed.")

        else:
            messagebox.showerror("Error", "No video is selected.")


    def create_folders(self):

        if not os.path.exists(self.outputs_path):
            os.mkdir(self.outputs_path)

        if not os.path.exists(self.samples_path):
            os.mkdir(self.samples_path)


    def save_ocr_status(self):

        self.ocr_status.video_path = self.select_video_entry.get()

        self.ocr_status.number_of_samples = int(self.number_of_samples_entry.get())

        self.ocr_status.region = [int(entry.get()) for entry in self.region_entries] 

        self.ocr_status.frame_skip = int(self.frame_skip_entry.get())
        
        ocr.save_ocr_status_to_json(self.status_path, self.ocr_status)


    def load_ocr_status(self):

        if os.path.exists(self.status_path):

            self.ocr_status = ocr.load_ocr_status_from_json(self.status_path)


    def export_to_srt(self):

        ocr_data_path = filedialog.askopenfilename(filetypes=[("ocr data files", "*.ocrdata")])

        if ocr_data_path:

            ocr_data = ocr.load_ocr_data_from_json(ocr_data_path)

            srt_path = os.path.join(self.outputs_path, f'{os.path.splitext(os.path.basename(ocr_data_path))[0]}.srt')

            subs = ocr_data.subtitles

            fps = ocr_data.fps

            subtitles.save_subtitles_to_srt(srt_path, subs, fps)

            messagebox.showinfo("Info", "SRT exported.")


if __name__ == "__main__":

    root = tk.Tk()
    
    app = VNSOCRApp(root)

    root.resizable(False,False)
    
    root.mainloop()