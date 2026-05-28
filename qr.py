import qrcode

drive_url = "https://drive.google.com/file/d/1Qn6yugPC225NipLO9QuU3Fjft-tLXwA1/view?usp=sharing"

qr = qrcode.QRCode(
    version=1,
    error_correction=qrcode.constants.ERROR_CORRECT_H,
    box_size=10,
    border=4,
)

qr.add_data(drive_url)
qr.make(fit=True)

img = qr.make_image(fill_color="black", back_color="white")
img.save("qr_drive.png")

print("QR generado correctamente: qr_drive.png")