import os
from flask import Flask, render_template, request, send_file, redirect, url_for
import qrcode
from PIL import Image
import glob
import time

app = Flask(__name__)

# Delete PNG files that were created more than 5 minutes ago
def delete_old_files():
    current_time = time.time()
    ten_minutes_ago = current_time - 5 * 60

    static_folder = app.static_folder
    files = glob.glob(os.path.join(static_folder, '*.png'))
    for f in files:
        file_modified_time = os.path.getmtime(f)
        if file_modified_time < ten_minutes_ago:
            with open(f, 'rb') as file:  # Open the file in binary mode
                file_contents = file.read()  # Read the file as bytes
            os.remove(f)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        email = request.form['email']
        company = request.form['company']
        title = request.form['title']
        role = request.form['role']
        url = request.form['url']
        mobile_number = request.form['mobile_number']
        work_number = request.form['work_number']
        
        # Generate QR code data
        #f"LOGO:https://upload.wikimedia.org/wikipedia/commons/thumb/9/96/NEC_logo.svg/220px-NEC_logo.svg.png\n" \
        qr_code_data = f"BEGIN:VCARD\n" \
                      f"VERSION:2.1\n" \
                      f"N:{last_name};{first_name}\n" \
                      f"EMAIL;PREF;WORK:{email}\n" \
                      f"ORG:{company}\n" \
                      f"TITLE:{title}\n" \
                      f"ROLE:{role}\n"  \
                      f"URL:{url}\n" \
                      f"TEL;CELL:{mobile_number}\n" \
                      f"TEL;WORK:{work_number}\n" \
                      f"END:VCARD"
        
        # Create the QR code
        qr_code = qrcode.QRCode()
        qr_code.add_data(qr_code_data)
        qr_code.border = 0
        qr_code.box_size = 10
        qr_code.make(fit=True)

        # Create the QR code image with default colors
        qr_image = qr_code.make_image(fill_color="black", back_color="white")

        # Convert the QR code image to RGBA mode for color manipulation
        qr_image = qr_image.convert("RGBA")

        # Get the image data as a list of tuples
        qr_data = list(qr_image.getdata())

        # Modify white pixels to green and black pixels to blue
        # modified_data = [
          #  (20, 20, 156, item[3]) if item[:3] == (0, 0, 0) else (0, 90, 171, item[3]) if item[:3] == (255, 255, 255) else item

        modified_data = [
             (255,255,255, item[3]) if item[:3] == (0, 0, 0) else (0,90,171, item[3]) if item[:3] == (255, 255, 255) else item
            for item in qr_data
        ]

        # Update the QR code image data
        qr_image.putdata(modified_data)

        # Save the QR code image locally
        qr_filename = f'{first_name}_{last_name}.png'
        qr_filepath = os.path.join(app.static_folder, qr_filename)
        qr_image.save(qr_filepath)
        
        # Delete PNG files that were created more then 5 minutes ago
        delete_old_files()

        # Return the result template
        return redirect(url_for('result', first_name=first_name, last_name=last_name))

    return render_template('form.html')

@app.route('/result')

def result():
    first_name = request.args.get('first_name')
    last_name = request.args.get('last_name')
    qr_filename = f'{first_name}_{last_name}.png'  # Add this line to generate the QR code filename
    return render_template('result.html', qr_filename=qr_filename)

@app.route('/download/<filename>')
def download(filename):
    qr_filepath = os.path.join(app.static_folder, filename)
    if os.path.exists(qr_filepath):
        return send_file(qr_filepath, as_attachment=True)
    else:
        return "QR code file not found."


if __name__ == '__main__':
    # Delete PNG files that were created more than 5 minutes ago
    delete_old_files()

    app.run(host='0.0.0.0', debug=True)
