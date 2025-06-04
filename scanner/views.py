from django.shortcuts import render
from .models import QRCode
import qrcode
from django.core.files.storage import FileSystemStorage
from django.core.files.storage import default_storage
from io import BytesIO
from PIL import Image
from django.core.files.base import ContentFile
from django.conf import settings
from pathlib import Path
import cv2
import numpy as np
import os

# QR code generate karne wala function
def generate_qr(request):
    qr_image_url = None

    if request.method == "POST":
        mobile_number = request.POST.get('mobile_number')
        data = request.POST.get('qr_data')

        # Mobile number valid hai ya nahi, yeh check karo
        if not mobile_number or len(mobile_number) != 10 or not mobile_number.isdigit():
            return render(request, 'scanner/generate.html', {'error': 'Invalid Mobile Number'})
        
        # QR content me data aur mobile number jodo
        qr_content = f"{data} | {mobile_number}"
        qr = qrcode.make(qr_content)

        # QR image ko memory me save karo
        qr_image_io = BytesIO()
        qr.save(qr_image_io, format='PNG')
        qr_image_io.seek(0)

        # Media folder ke andar qr_codes naam ka folder banao
        qr_storage_path = settings.MEDIA_ROOT / 'qr_codes'
        fs = FileSystemStorage(location=qr_storage_path, base_url='/media/qr_codes/')
        filename = f"{data}_{mobile_number}.png"
        qr_image_content = ContentFile(qr_image_io.read(), name=filename)
        filepath = fs.save(filename, qr_image_content)
        qr_image_url = fs.url(filename)

        # QR data ko database me store karo
        QRCode.objects.create(data=data, mobile_number=mobile_number)
        
    return render(request, 'scanner/generate.html', {'qr_image_url': qr_image_url})

def scan_qr(request):
    result = None

    if request.method == "POST":
        mobile_number = request.POST.get('mobile_number')
        qr_image = request.FILES.get('qr_image')

        if qr_image:
            # FileSystemStorage setup kar rahe hain media/qr_codes folder ke liye
            fs = FileSystemStorage(location='media/qr_codes', base_url='/media/qr_codes/')
            
            # Uploaded image ko media/qr_codes me save kar rahe hain
            filename = fs.save(qr_image.name, qr_image)
            file_path = fs.path(filename)

            try:
                # OpenCV se image read kar rahe hain
                image = cv2.imread(file_path)

                # QRCode detector initialize karna
                detector = cv2.QRCodeDetector()

                # Image me QR code detect aur decode karna
                data, bbox, straight_qrcode = detector.detectAndDecode(image)

                if data:
                    # Agar QR code mila toh data ko result me store karo
                    result = data
                else:
                    # QR code nahi mila toh ye message show karo
                    result = "No QR code found in the image."
            finally:
                # Kaam hone ke baad uploaded file delete kar do
                if os.path.exists(file_path):
                    os.remove(file_path)

    # Template ko result ke saath render kar do
    return render(request, 'scanner/scan.html', {'result': result})

