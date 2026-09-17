import customtkinter as ctk
from tkinter import filedialog, messagebox
import qrcode
from PIL import Image, ImageTk
import io
import os

ctk.set_appearance_mode("System")  # Modes: "System" (standard), "Dark", "Light"
ctk.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Generador QR Profesional")
        self.geometry("500x750")
        
        self.logo_path = None
        self.qr_image_pil = None

        # Title
        self.title_label = ctk.CTkLabel(self, text="Generador de Código QR", font=ctk.CTkFont(size=24, weight="bold"))
        self.title_label.pack(pady=(20, 10))

        # Data Input
        self.data_entry = ctk.CTkTextbox(self, height=100, corner_radius=8)
        self.data_entry.insert("0.0", "Introduce el texto o URL aquí...")
        self.data_entry.pack(pady=10, padx=20, fill="x")
        # Clear placeholder on click
        self.data_entry.bind("<FocusIn>", self.clear_placeholder)

        # Logo Selection
        self.logo_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.logo_frame.pack(pady=10, padx=20, fill="x")
        
        self.logo_label = ctk.CTkLabel(self.logo_frame, text="Ícono/Logo opcional: Ninguno", anchor="w")
        self.logo_label.pack(side="left", padx=(0, 10))
        
        self.logo_btn = ctk.CTkButton(self.logo_frame, text="Seleccionar Logo", command=self.select_logo)
        self.logo_btn.pack(side="right")
        
        self.remove_logo_btn = ctk.CTkButton(self.logo_frame, text="Quitar", command=self.remove_logo, width=50, fg_color="#C0392B", hover_color="#922B21")

        # Generate Button
        self.generate_btn = ctk.CTkButton(self, text="Generar QR", font=ctk.CTkFont(size=16, weight="bold"), height=40, command=self.generate_qr)
        self.generate_btn.pack(pady=20, padx=20, fill="x")

        # QR Preview Label
        self.preview_label = ctk.CTkLabel(self, text="Previsualización del QR aparecerá aquí", width=300, height=300, corner_radius=8, fg_color=("gray85", "gray25"))
        self.preview_label.pack(pady=10)

        # Save Button
        self.save_btn = ctk.CTkButton(self, text="Guardar QR", font=ctk.CTkFont(size=16, weight="bold"), height=40, command=self.save_qr, state="disabled", fg_color="#27AE60", hover_color="#1E8449")
        self.save_btn.pack(pady=20, padx=20, fill="x")

    def clear_placeholder(self, event):
        current_text = self.data_entry.get("0.0", "end-1c")
        if current_text == "Introduce el texto o URL aquí...":
            self.data_entry.delete("0.0", "end")

    def select_logo(self):
        filetypes = (
            ('Imágenes', '*.png *.jpg *.jpeg *.bmp'),
            ('Todos los archivos', '*.*')
        )
        filename = filedialog.askopenfilename(title='Selecciona un ícono o logo', initialdir='/', filetypes=filetypes)
        if filename:
            self.logo_path = filename
            short_name = os.path.basename(filename)
            self.logo_label.configure(text=f"Logo: {short_name}")
            self.remove_logo_btn.pack(side="right", padx=10)

    def remove_logo(self):
        self.logo_path = None
        self.logo_label.configure(text="Ícono/Logo opcional: Ninguno")
        self.remove_logo_btn.pack_forget()

    def generate_qr(self):
        data = self.data_entry.get("0.0", "end-1c").strip()
        if not data or data == "Introduce el texto o URL aquí...":
            messagebox.showwarning("Advertencia", "Por favor introduce algún texto o URL.")
            return

        try:
            # Generate QR Code
            qr = qrcode.QRCode(
                version=1, # it will auto scale up if needed
                error_correction=qrcode.constants.ERROR_CORRECT_H if self.logo_path else qrcode.constants.ERROR_CORRECT_M,
                box_size=10,
                border=4,
            )
            qr.add_data(data)
            qr.make(fit=True)

            img_qr = qr.make_image(fill_color="black", back_color="white").convert('RGB')

            # Add Logo if selected
            if self.logo_path:
                try:
                    logo = Image.open(self.logo_path)
                    
                    # Calculate max logo size (about 1/3 of the QR code width)
                    basewidth = int(img_qr.size[0] / 3.5)
                    wpercent = (basewidth / float(logo.size[0]))
                    hsize = int((float(logo.size[1]) * float(wpercent)))
                    
                    # Resize logo using high quality downsampling
                    logo = logo.resize((basewidth, hsize), Image.Resampling.LANCZOS)
                    
                    # Paste logo in the center
                    pos = ((img_qr.size[0] - logo.size[0]) // 2, (img_qr.size[1] - logo.size[1]) // 2)
                    img_qr.paste(logo, pos)
                except Exception as e:
                    messagebox.showerror("Error de Logo", f"No se pudo cargar el logo: {e}")
                    return

            self.qr_image_pil = img_qr

            # Update preview
            # Resize for preview so it fits nicely
            preview_img = self.qr_image_pil.copy()
            preview_img.thumbnail((300, 300), Image.Resampling.LANCZOS)
            
            ctk_img = ctk.CTkImage(light_image=preview_img, dark_image=preview_img, size=(300, 300))
            self.preview_label.configure(image=ctk_img, text="")
            self.preview_label.image = ctk_img # Keep a reference

            self.save_btn.configure(state="normal")

        except Exception as e:
            messagebox.showerror("Error", f"Ocurrió un error al generar el QR: {e}")

    def save_qr(self):
        if not self.qr_image_pil:
            return

        filetypes = (
            ('PNG Image', '*.png'),
            ('Todos los archivos', '*.*')
        )
        filename = filedialog.asksaveasfilename(title='Guardar Código QR', defaultextension=".png", filetypes=filetypes)
        
        if filename:
            try:
                self.qr_image_pil.save(filename, format="PNG")
                messagebox.showinfo("Éxito", "El código QR se ha guardado correctamente.")
            except Exception as e:
                messagebox.showerror("Error al guardar", f"No se pudo guardar la imagen: {e}")

if __name__ == "__main__":
    app = App()
    app.mainloop()
