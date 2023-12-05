import customtkinter as ctk
import filter
from CTkMessagebox import CTkMessagebox
from customtkinter import filedialog
from PIL import Image, ImageEnhance, ImageOps, ImageFilter


def clamp_max(number, max_value):
    if number < max_value:
        return number
    return max_value


# Make things look nicer
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class App:
    def __init__(self, parent):
        self.current_image_filepath = None
        self.current_image = None
        self.root = parent
        self.root.title("Lightroom for broke people")
        self.root.geometry("800x600")

        # Create main frame
        self.main_frame = ctk.CTkFrame(self.root)
        self.main_frame.pack(fill="both", expand=True)

        # Create left frame for options
        self.menu_frame = ctk.CTkFrame(self.main_frame)
        self.menu_frame.pack(fill="y", side="left", padx=10, pady=10)

        # Add options to the left frame
        self.add_options()

        # Create right frame for image display (you can replace this with your image editing components)
        self.right_frame = ctk.CTkFrame(self.main_frame)
        self.right_frame.pack(fill="both", expand=True, side="left", padx=10, pady=10)

        # Create an instance for image to display into
        self.image_label = ctk.CTkLabel(self.right_frame, text="")
        self.image_label.pack()

    def add_options(self):
        # Add your image editing options here
        label = ctk.CTkLabel(self.menu_frame, text="Image Options")
        label.pack(pady=10)

        open_file_button = ctk.CTkButton(self.menu_frame, text="Open Image", command=self.open_file_callback)
        open_file_button.pack(pady=5, padx=10)

        save_file_button = ctk.CTkButton(self.menu_frame, text="Save Image", command=self.save_file_callback)
        save_file_button.pack(pady=5, padx=10)

        flip_horizontally_button = ctk.CTkButton(self.menu_frame, text="Flip Horizontally",
                                                 command=self.flip_horizontally_callback)
        flip_horizontally_button.pack(pady=5, padx=10)

        flip_right_button = ctk.CTkButton(self.menu_frame, text="Flip Vertically",
                                          command=self.flip_vertically_callback)
        flip_right_button.pack(pady=5, padx=10)

        crop_button = ctk.CTkButton(self.menu_frame, text="Crop Image", command=self.crop_image_callback)
        crop_button.pack(pady=5, padx=10)

        enhance_button = ctk.CTkButton(self.menu_frame, text="Enhance Image", command=self.enhance_image_callback)
        enhance_button.pack(pady=5, padx=10)

        adjust_individual_color = ctk.CTkButton(self.menu_frame, text="Adjust Colors",
                                                command=self.adjust_colors_callback)
        adjust_individual_color.pack(pady=5, padx=10)

        adjust_hue = ctk.CTkButton(self.menu_frame, text="Adjust HUE", command=self.adjust_hue_callback)
        adjust_hue.pack(pady=5, padx=10)

        filter_button = ctk.CTkButton(self.menu_frame, text="Filters", command=self.filter_callback)
        filter_button.pack(pady=5, padx=10)

    def open_file_callback(self):
        self.current_image_filepath = filedialog.askopenfile(filetypes=[("Photo Files", "*.jpg;*.png;*.tiff;*.bmp")])
        if self.current_image_filepath is not None:
            self.current_image = Image.open(self.current_image_filepath.name)
            self.calculate_correct_display_image()

    def save_file_callback(self):
        if self.current_image is None:
            CTkMessagebox(title="Error", icon="cancel", message="No image is currently selected.")
            return
        save_location = filedialog.asksaveasfile(filetypes=[("Photo Files", "*.jpg;*.png;*.tiff;*.bmp")],
                                                 defaultextension=".png")
        if save_location is not None:
            self.current_image = self.current_image.save(save_location.name)

    def flip_horizontally_callback(self):
        if self.current_image is None:
            CTkMessagebox(title="Error", icon="cancel", message="No image is currently selected.")
            return
        self.current_image = self.current_image.transpose(Image.FLIP_LEFT_RIGHT)
        self.calculate_correct_display_image()

    def flip_vertically_callback(self):
        if self.current_image is None:
            CTkMessagebox(title="Error", icon="cancel", message="No image is currently selected.")
            return
        self.current_image = self.current_image.transpose(Image.FLIP_TOP_BOTTOM)
        self.calculate_correct_display_image()

    def crop_image_callback(self):
        if self.current_image is None:
            CTkMessagebox(title="Error", icon="cancel", message="No image is currently selected.")
            return
        crop_from = CropForm(self.main_frame)
        self.main_frame.wait_window(crop_from.main_frame)
        if crop_from.horizontal_resolution is not None and crop_from.vertical_resolution is not None:
            horizontal = crop_from.horizontal_resolution
            vertical = crop_from.vertical_resolution

            # This is somewhat limiting and should have more features
            self.current_image = self.current_image.crop((0, 0, horizontal, vertical))
            self.calculate_correct_display_image()

    def enhance_image_callback(self):
        if self.current_image is None:
            CTkMessagebox(title="Error", icon="cancel", message="No image is currently selected.")
            return
        enhance_form = EnhanceForm(self.main_frame)
        self.main_frame.wait_window(enhance_form.main_frame)

        brightness = enhance_form.brightness_var.get()
        contrast = enhance_form.contrast_var.get()
        sharpness = enhance_form.sharpness_var.get()

        sharpness_enhance = ImageEnhance.Sharpness(self.current_image)
        self.current_image = sharpness_enhance.enhance(sharpness / 100)

        if brightness != 100:
            brightness_enhance = ImageEnhance.Brightness(self.current_image)
            self.current_image = brightness_enhance.enhance(brightness / 100)
        elif contrast != 100:
            contrast_enhance = ImageEnhance.Contrast(self.current_image)
            self.current_image = contrast_enhance.enhance(contrast / 100)
        # This really can't be seen with such a small preview
        elif sharpness != 100:
            sharpness_enhance = ImageEnhance.Sharpness(self.current_image)
            self.current_image = sharpness_enhance.enhance(sharpness / 100)

        self.calculate_correct_display_image()

    def filter_callback(self):
        if self.current_image is None:
            CTkMessagebox(title="Error", icon="cancel", message="No image is currently selected.")
            return
        filter_form = FilterForm(self.main_frame)
        self.main_frame.wait_window(filter_form.main_frame)
        if filter_form.filter_var.get() == "Black & White":
            self.current_image = ImageOps.grayscale(self.current_image)
        elif filter_form.filter_var.get() == "Sepia":
            self.current_image = filter.convert_sepia(self.current_image)
        elif filter_form.filter_var.get() == "Emboss":
            self.current_image = self.current_image.filter(ImageFilter.EMBOSS)
        elif filter_form.filter_var.get() == "Pointilize":
            self.current_image = filter.convert_pointilize(self.current_image)
        self.calculate_correct_display_image()

    def adjust_colors_callback(self):
        if self.current_image is None:
            CTkMessagebox(title="Error", icon="cancel", message="No image is currently selected.")
            return
        adjust_color_form = ColorForm(self.main_frame)
        self.main_frame.wait_window(adjust_color_form.main_frame)
        new_image = self.current_image.convert("RGB")

        red, green, blue = new_image.split()

        red = red.point(lambda i: i * (adjust_color_form.red_var.get() / 100))
        green = green.point(lambda i: i * (adjust_color_form.green_var.get() / 100))
        blue = blue.point(lambda i: i * (adjust_color_form.blue_var.get() / 100))

        new_image = Image.merge("RGB", (red, green, blue))
        self.current_image = new_image
        self.calculate_correct_display_image()

    def adjust_hue_callback(self):
        if self.current_image is None:
            CTkMessagebox(title="Error", icon="cancel", message="No image is currently selected.")
            return
        adjust_hue_form = HueForm(self.main_frame)
        self.main_frame.wait_window(adjust_hue_form.main_frame)
        new_hue_val = adjust_hue_form.hue_var.get()
        new_hue_val = 180 - new_hue_val

        new_image = self.current_image.convert("HSV")
        h, s, v = new_image.split()
        h = h.point(lambda i: (i + new_hue_val) % 180)

        new_image = Image.merge("HSV", (h, s, v))
        self.current_image = new_image.convert("RGB")
        self.calculate_correct_display_image()

    def calculate_correct_display_image(self):
        height, width = self.current_image.size
        aspect_ratio = height / width
        max_width = clamp_max(width, 600)
        max_height = max_width * aspect_ratio
        self.image_label.configure(image=ctk.CTkImage(self.current_image, size=(max_height, max_width)))


class CropForm:
    def __init__(self, parent):
        self.main_frame = ctk.CTkToplevel(parent)
        self.main_frame.title("Crop")
        self.main_frame.grab_set()
        self.label = ctk.CTkLabel(self.main_frame, text="This crops from the top left corner!")

        self.horizontal_resolution_label = ctk.CTkLabel(self.main_frame, text="Enter your horizontal resolution:")
        self.horizontal_resolution_entry = ctk.CTkEntry(self.main_frame)

        self.vertical_resolution_label = ctk.CTkLabel(self.main_frame, text="Enter your vertical resolution:")
        self.vertical_resolution_entry = ctk.CTkEntry(self.main_frame)

        self.submit_button = ctk.CTkButton(self.main_frame, text="Submit", command=self.submit)

        # Grid layout for form elements

        self.label.grid(row=0, padx=10, pady=10)

        self.horizontal_resolution_label.grid(row=1, column=0, padx=10, pady=10)
        self.horizontal_resolution_entry.grid(row=2, column=0, padx=10, pady=10)

        self.vertical_resolution_label.grid(row=1, column=1, padx=10, pady=10)
        self.vertical_resolution_entry.grid(row=2, column=1, padx=10, pady=10)

        self.submit_button.grid(row=3, padx=10, pady=10)

        self.horizontal_resolution = None
        self.vertical_resolution = None

    def submit(self):
        should_be_horizontal = self.horizontal_resolution_entry.get()
        should_be_vertical = self.vertical_resolution_entry.get()
        if should_be_horizontal.isdigit() and should_be_vertical.isdigit():
            self.horizontal_resolution = int(should_be_horizontal)
            self.vertical_resolution = int(should_be_vertical)
            self.main_frame.destroy()
        else:
            CTkMessagebox(title="Error", icon="warning", message="Input received is not a number.")


class EnhanceForm:
    def __init__(self, parent):
        self.main_frame = ctk.CTkToplevel(parent)
        self.main_frame.title = "Enhance"
        self.main_frame.grab_set()

        self.label = ctk.CTkLabel(self.main_frame, text="Change only one variable at a time!")

        # Create initial frames that act like containers for the rest of the elements
        self.brightness_frame = ctk.CTkFrame(self.main_frame)
        self.contrast_frame = ctk.CTkFrame(self.main_frame)
        self.sharpness_frame = ctk.CTkFrame(self.main_frame)

        self.brightness_var = ctk.IntVar()
        self.contrast_var = ctk.IntVar()
        self.sharpness_var = ctk.IntVar()

        self.brightness_label = ctk.CTkLabel(self.brightness_frame, text="Brightness Value:")
        self.brightness_slider = ctk.CTkSlider(self.brightness_frame, from_=0, to=200, variable=self.brightness_var)
        self.brightness_slider.set(100)

        self.contrast_label = ctk.CTkLabel(self.contrast_frame, text="Contrast Value:")
        self.contrast_slider = ctk.CTkSlider(self.contrast_frame, from_=0, to=200, variable=self.contrast_var)
        self.contrast_slider.set(100)

        self.sharpness_label = ctk.CTkLabel(self.sharpness_frame, text="Sharpness Value: ")
        self.sharpness_slider = ctk.CTkSlider(self.sharpness_frame, from_=0, to=200, variable=self.sharpness_var)
        self.sharpness_slider.set(100)

        self.submit_button = ctk.CTkButton(self.main_frame, text="Submit", command=self.submit)

        self.brightness_label.pack(side="top", padx=10, pady=10)
        self.brightness_slider.pack(side="top", padx=10, pady=10)

        self.contrast_label.pack(side="top", padx=10, pady=10)
        self.contrast_slider.pack(side="top", padx=10, pady=10)

        self.sharpness_label.grid(row=0, column=0, padx=10, pady=10)
        self.sharpness_slider.grid(row=1, column=0, padx=10, pady=10)

        self.label.pack(side="top", padx=5, pady=5)

        self.brightness_frame.pack(side="top", padx=10, pady=10)
        self.contrast_frame.pack(side="top", padx=10, pady=10)
        self.sharpness_frame.pack(side="top", padx=10, pady=10)

        self.submit_button.pack(side="top", padx=10, pady=10)

    def submit(self):
        self.main_frame.destroy()


class ColorForm:
    def __init__(self, parent):
        self.main_frame = ctk.CTkToplevel(parent)
        self.main_frame.title("Adjust RGB values")
        self.main_frame.grab_set()

        self.red_frame = ctk.CTkFrame(self.main_frame)
        self.green_frame = ctk.CTkFrame(self.main_frame)
        self.blue_frame = ctk.CTkFrame(self.main_frame)

        self.red_label = ctk.CTkLabel(self.red_frame, text="Red Value:")
        self.green_label = ctk.CTkLabel(self.green_frame, text="Green Value:")
        self.blue_label = ctk.CTkLabel(self.blue_frame, text="Blue Value:")

        self.red_var = ctk.IntVar()
        self.green_var = ctk.IntVar()
        self.blue_var = ctk.IntVar()

        self.red_slider = ctk.CTkSlider(self.red_frame, from_=0, to=200, variable=self.red_var)
        self.green_slider = ctk.CTkSlider(self.green_frame, from_=0, to=200, variable=self.green_var)
        self.blue_slider = ctk.CTkSlider(self.blue_frame, from_=0, to=200, variable=self.blue_var)

        self.red_slider.set(100)
        self.green_slider.set(100)
        self.blue_slider.set(100)

        self.submit_button = ctk.CTkButton(self.main_frame, text="Submit", command=self.submit)

        self.red_frame.pack(side="top", padx=10, pady=10)
        self.green_frame.pack(side="top", padx=10, pady=10)
        self.blue_frame.pack(side="top", padx=10, pady=10)

        self.red_label.pack(side="top", padx=10, pady=10)
        self.red_slider.pack(side="top", padx=10, pady=10)

        self.green_label.pack(side="top", padx=10, pady=10)
        self.green_slider.pack(side="top", padx=10, pady=10)

        self.blue_label.pack(side="top", padx=10, pady=10)
        self.blue_slider.pack(side="top", padx=10, pady=10)

        self.submit_button.pack(side="top", padx=10, pady=10)

    def submit(self):
        self.main_frame.destroy()


class FilterForm:
    def __init__(self, parent):
        self.main_frame = ctk.CTkToplevel(parent)
        self.main_frame.title("Filters")
        self.main_frame.grab_set()

        self.filter_var = ctk.StringVar()

        self.label = ctk.CTkLabel(self.main_frame, text="Filters:")
        self.combobox = ctk.CTkComboBox(self.main_frame,
                                        values=["Black & White",
                                                "Sepia",
                                                "Emboss",
                                                "Pointilize"],
                                        variable=self.filter_var, state="readonly")
        self.combobox.set("Black & White")
        self.submit_button = ctk.CTkButton(self.main_frame, text="Submit", command=self.submit)

        self.label.pack(side="top", padx=10, pady=10)
        self.combobox.pack(side="top", padx=10, pady=10)
        self.submit_button.pack(side="top", padx=10, pady=10)

    def submit(self):
        self.main_frame.destroy()


class HueForm:
    def __init__(self, parent):
        self.main_frame = ctk.CTkToplevel(parent)
        self.main_frame.title("Adjust HUE")
        self.main_frame.grab_set()
        self.hue_var = ctk.IntVar()

        self.label = ctk.CTkLabel(self.main_frame, text="Hue:")
        self.slider = ctk.CTkSlider(self.main_frame, from_=0, to=360, variable=self.hue_var)
        self.slider.set(180)
        self.submit_button = ctk.CTkButton(self.main_frame, text="Submit", command=self.submit)

        self.label.pack(side="top", padx=10, pady=10)
        self.slider.pack(side="top", padx=10, pady=10)
        self.submit_button.pack(side="top", padx=10, pady=10)

    def submit(self):
        self.main_frame.destroy()


if __name__ == "__main__":
    root = ctk.CTk()
    app = App(root)
    root.mainloop()
