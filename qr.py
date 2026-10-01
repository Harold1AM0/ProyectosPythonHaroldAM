import qrcode

name="Nombre_Pagina"
url = "URL"
qr=qrcode.QRCode(
    version=1,
    box_size=25,
    border=3,
)
qr.add_data(url)
qr.make(fit=True)

img = qr.make_image(fill_color="black", back_color="white")
img.save(f"qr_{name}.png")

destino = r"c:\Users\paul_\Desktop\Programacion\Proyectos Python"
img.save(f"{destino}\\qr_{name}.png")
