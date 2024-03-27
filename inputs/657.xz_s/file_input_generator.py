import os
import random
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import cv2
import csv
import json
import xml.etree.ElementTree as ET
import sqlite3
from faker import Faker
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from pydub import AudioSegment
from pydub.generators import WhiteNoise, Sine

fake = Faker()
Faker.seed(42)
random.seed(42)

def generate_text_file(output_folder, num_files):
    os.makedirs(output_folder, exist_ok=True)

    for i in range(num_files):
        file_path = os.path.join(output_folder, f'{f"{random.randint(1, 1000)}.".join([fake.word() for _ in range(5)])}.txt')

        with open(file_path, 'w') as file:
            file.write(f"Title: {fake.sentence()}\n")
            file.write(f"Author: {fake.name()}\n")
            file.write(f"Date: {fake.date_this_decade()}\n")
            file.write(f"Tags: {', '.join(fake.words(5))}\n\n")

            num_sections = random.randint(5, 350)

            for _ in range(num_sections):
                section_type = random.choice(
                    ['Introduction', 'Main Body', 'Conclusion'])
                file.write(f"{section_type}:\n")

                num_paragraphs = random.randint(1, 100)

                for _ in range(num_paragraphs):
                    file.write(fake.paragraph() + '\n')

                file.write('\n')

def generate_image_file(output_folder, num_files, exact_index=False, small_size=False):
    os.makedirs(output_folder, exist_ok=True)

    for i in range(num_files if exact_index is False else 1):
        if exact_index is True:
            image_path = os.path.join(
                output_folder, 'image_-1.png')
        else:
            image_path = os.path.join(output_folder, f'{f"{random.randint(1, 1000)}.".join([fake.word() for _ in range(5)])}.png')

        img_size = (random.choice(np.arange(128, 16385, 128)),
                    random.choice(np.arange(128, 16385, 128)))
        if small_size:
            img_size = (random.choice(np.arange(128, 512, 64)),
                        random.choice(np.arange(128, 512, 64)))

        image = Image.new('RGB', img_size, color='white')
        draw = ImageDraw.Draw(image)

        # Draw complex patterns and shapes
        for _ in range(random.randint(5, 50)):
            color = (np.random.randint(0, 255), np.random.randint(
                0, 255), np.random.randint(0, 255))
            shape_type = np.random.choice(
                ['rectangle', 'ellipse', 'polygon', 'line', 'circle', 'pattern'])

            if shape_type == 'rectangle':
                x1, y1, x2, y2 = np.random.randint(0, img_size[0]), np.random.randint(
                    0, img_size[1]), np.random.randint(0, img_size[0]), np.random.randint(0, img_size[1])
                draw.rectangle([x1, y1, x2, y2], fill=color)

            elif shape_type == 'ellipse':
                x1, y1, x2, y2 = np.random.randint(0, img_size[0]), np.random.randint(
                    0, img_size[1]), np.random.randint(0, img_size[0]), np.random.randint(0, img_size[1])
                draw.ellipse([x1, y1, x2, y2], fill=color)

            elif shape_type == 'polygon':
                num_points = np.random.randint(3, 8)
                points = [(np.random.randint(0, img_size[0]), np.random.randint(
                    0, img_size[1])) for _ in range(num_points)]
                draw.polygon(points, fill=color)

            elif shape_type == 'line':
                x1, y1, x2, y2 = np.random.randint(0, img_size[0]), np.random.randint(
                    0, img_size[1]), np.random.randint(0, img_size[0]), np.random.randint(0, img_size[1])
                draw.line([(x1, y1), (x2, y2)], fill=color,
                          width=np.random.randint(1, 5))

            elif shape_type == 'circle':
                center = (np.random.randint(
                    0, img_size[0]), np.random.randint(0, img_size[1]))
                radius = np.random.randint(10, 100)
                draw.ellipse([center[0] - radius, center[1] - radius,
                             center[0] + radius, center[1] + radius], fill=color)

            else:  # pattern
                pattern_size = (np.random.randint(20, 50),
                                np.random.randint(20, 50))
                pattern = Image.new('RGB', pattern_size, color=color)
                image.paste(pattern, (np.random.randint(
                    0, img_size[0] - pattern_size[0]), np.random.randint(0, img_size[1] - pattern_size[1])))

        # Add random text using Faker
        for _ in range(random.randint(5, 50)):
            text = fake.sentence()
            font_color = (np.random.randint(0, 255), np.random.randint(
                0, 255), np.random.randint(0, 255))
            font = ImageFont.load_default()
            text_position = (np.random.randint(
                0, img_size[0]/2), np.random.randint(0, img_size[1] - 50))
            draw.text(text_position, text, font=font, fill=font_color)

        image.save(image_path)

def generate_video_file(output_folder, num_files):
    os.makedirs(output_folder, exist_ok=True)

    for i in range(num_files):
        video_path = os.path.join(output_folder, f'{f"{random.randint(1, 1000)}.".join([fake.word() for _ in range(5)])}.mp4')
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        video_size = (random.choice(np.arange(64, 1025, 64)),
                      random.choice(np.arange(64, 1025, 64)))
        fps = random.randint(20, 60)
        video_writer = cv2.VideoWriter(
            video_path, fourcc, fps, video_size, isColor=True)

        number_of_frames = random.randint(fps*5, fps*20)
        for _ in range(number_of_frames):
            # Note the order of dimensions (height, width, channels)
            frame = np.full(
                (video_size[1], video_size[0], 3), 255, dtype=np.uint8)
            draw = ImageDraw.Draw(Image.fromarray(frame))

            # Inside the loop where shapes are drawn
            for _ in range(random.randint(2, 50)):
                color = (np.random.randint(0, 255), np.random.randint(
                    0, 255), np.random.randint(0, 255))
                shape_type = np.random.choice(
                    ['rectangle', 'ellipse', 'polygon', 'line', 'circle', 'pattern'])

                # Draw multiple shapes in each iteration
                for _ in range(random.randint(2, 15)):
                    if shape_type == 'rectangle':
                        x1, y1, x2, y2 = np.random.randint(0, video_size[0]//2), np.random.randint(0, video_size[1]//2), np.random.randint(
                            video_size[0]//2, video_size[0]), np.random.randint(video_size[1]//2, video_size[1])
                        draw.rectangle([x1, y1, x2, y2], fill=color)

                    elif shape_type == 'ellipse':
                        x1, y1, x2, y2 = np.random.randint(0, video_size[0]//2), np.random.randint(0, video_size[1]//2), np.random.randint(
                            video_size[0]//2, video_size[0]), np.random.randint(video_size[1]//2, video_size[1])
                        draw.ellipse([x1, y1, x2, y2], fill=color)

                    elif shape_type == 'polygon':
                        num_points = np.random.randint(3, 8)
                        points = [(np.random.randint(0, video_size[0]), np.random.randint(
                            0, video_size[1])) for _ in range(num_points)]
                        draw.polygon(points, fill=color)

                    elif shape_type == 'line':
                        x1, y1, x2, y2 = np.random.randint(0, video_size[0]//2), np.random.randint(0, video_size[1]//2), np.random.randint(
                            video_size[0]//2, video_size[0]), np.random.randint(video_size[1]//2, video_size[1])
                        draw.line([(x1, y1), (x2, y2)], fill=color,
                                  width=np.random.randint(1, 5))

                    elif shape_type == 'circle':
                        center = (np.random.randint(
                            video_size[0]//2, video_size[0]), np.random.randint(video_size[1]//2, video_size[1]))
                        radius = np.random.randint(10, 100)
                        draw.ellipse([center[0] - radius, center[1] - radius,
                                     center[0] + radius, center[1] + radius], fill=color)

                    else:  # pattern
                        pattern_size = (np.random.randint(
                            50, video_size[0]), np.random.randint(50, video_size[1]))
                        pattern = Image.new('RGB', pattern_size, color=color)

                        frame_pil = Image.fromarray(frame)
                        frame_pil.paste(pattern, (np.random.randint(
                            0, video_size[0] - pattern_size[0]), np.random.randint(0, video_size[1] - pattern_size[1])))
                        frame = np.array(frame_pil)

            # Add random text using Faker
            text = fake.sentence()
            font_color = (np.random.randint(0, 255), np.random.randint(
                0, 255), np.random.randint(0, 255))
            font = ImageFont.load_default()
            text_position = (np.random.randint(
                0, video_size[0]/2), np.random.randint(0, video_size[1] - 50))
            draw.text(text_position, text, font=font, fill=font_color)

            frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
            video_writer.write(frame)

        video_writer.release()

def generate_pdf_file(output_path, num_files):
    for i in range(num_files):
        # Create a PDF canvas
        output_path = os.path.join(output_folder, f'{f"{random.randint(1, 1000)}.".join([fake.word() for _ in range(5)])}.pdf')
        c = canvas.Canvas(output_path, pagesize=letter)

        # Set up styles for text
        styles = getSampleStyleSheet()

        # Generate random number of paragraphs and texts
        num_paragraphs = random.randint(20, 500)
        y_position = inch * 10  # Initial y position
        for _ in range(num_paragraphs):
            # Check if there's enough space for the text on the current page
            if y_position < inch:
                # Start a new page if there's not enough space
                c.showPage()
                y_position = inch * 10  # Reset y position for the new page

            text = fake.paragraph()
            style = styles['BodyText']
            c.setFont(style.fontName, style.fontSize)
            c.setFillColor(colors.black)

            # Calculate the remaining width on the page
            remaining_width = letter[0] - 2 * inch
            c.setLineWidth(remaining_width)

            # Check if there's enough space for the text horizontally
            if c.stringWidth(text, style.fontName, style.fontSize) > remaining_width:
                # Start a new line if there's not enough space horizontally
                y_position -= style.leading  # Move to the next line
                y_position -= style.fontSize

            c.drawString(inch, y_position, text)
            y_position -= (style.leading * 0.5)  # Move to the next line
            y_position -= style.fontSize  # Add some space between paragraphs

        c.showPage()
        y_position = inch * 10 + 200  # Reset y position for the new page

        # Generate random number of images
        num_images = random.randint(1, 50)
        for _ in range(num_images):
            if y_position < inch:
                # Start a new page if there's not enough space
                c.showPage()
                y_position = inch * 10 + 250  # Reset y position for the new page

            generate_image_file(
                output_folder, 1, exact_index=True, small_size=True)
            image_path = output_folder + '/image_-1.png'

            # Draw the image on the PDF
            c.drawInlineImage(image_path, inch, y_position,
                              width=200, height=150)
            y_position -= 150 + inch

        os.remove(image_path)  # Remove the temporary image file

        # Save the PDF
        c.save()

def generate_audio_file(output_folder, num_files):
    os.makedirs(output_folder, exist_ok=True)

    for i in range(num_files):
        audio_path = os.path.join(output_folder, f'{f"{random.randint(1, 1000)}.".join([fake.word() for _ in range(5)])}.mp3')

        # Generate a random duration for the audio (between 10 and 30 seconds)
        duration = random.uniform(5, 200)

        # Create an empty audio segment
        audio = AudioSegment.silent(duration=int(
            duration) * 1000)  # Duration in milliseconds

        # Add multiple tones with random frequencies and volumes
        for _ in range(random.randint(5, 50)):
            frequency = random.randint(100, 3000)
            volume = random.randint(-20, 20)  # in dB

            # Random duration for each tone
            tone_duration = random.uniform(0.1, 2)
            tone = Sine(freq=frequency).to_audio_segment(
                duration=int(tone_duration * 1000))
            tone = tone - volume  # Adjust volume

            # Randomly insert the tone into the audio segment
            # Random start time in milliseconds
            start_time = random.randint(0, int(duration) * 900)
            audio = audio.overlay(tone, position=start_time)

        # Add white noise with random volume and duration
        noise = WhiteNoise().to_audio_segment(duration=random.uniform(1, 5) * 1000)
        audio = audio.overlay(noise)

        # Apply random audio effects
        audio = audio.fade_in(random.randint(500, 5000)).fade_out(
            random.randint(500, 5000))

        # Export the audio segment to an MP3 file
        audio.export(audio_path, format="mp3")

def generate_csv_file(output_folder, num_files):
    os.makedirs(output_folder, exist_ok=True)

    for i in range(num_files):
        csv_path = os.path.join(output_folder, f'{f"{random.randint(1, 1000)}.".join([fake.word() for _ in range(5)])}.csv')
        with open(csv_path, 'w', newline='') as csv_file:
            csv_writer = csv.writer(csv_file)
            csv_writer.writerow(
                ['Name', 'Age', 'Country', 'Date', 'Description'])
            for _ in range(random.randint(100, 25000)):
                csv_writer.writerow([fake.name(), fake.random_int(
                    min=20, max=60, step=1), fake.country(), fake.date_this_decade(), fake.paragraph()])

def generate_json_file(output_folder, num_files):
    os.makedirs(output_folder, exist_ok=True)

    for i in range(num_files):
        json_path = os.path.join(output_folder, f'{f"{random.randint(1, 1000)}.".join([fake.word() for _ in range(5)])}.json')
        data = []
        for _ in range(random.randint(100, 10000)):
            data.append({
                'name': fake.name(),
                'age': fake.random_int(min=20, max=60, step=1),
                'country': fake.country(),
                'date': str(fake.date_this_decade()),
                'description': fake.paragraph(),
                'tags': fake.words(5),
                'sections': {section: fake.paragraph() for section in ['Introduction', 'Main Body', 'Conclusion']},
                'images': [fake.image_url() for _ in range(random.randint(1, 5))]
            })

        with open(json_path, 'w') as json_file:
            json.dump(data, json_file, indent=4)

def generate_xml_file(output_folder, num_files):
    os.makedirs(output_folder, exist_ok=True)

    for i in range(num_files):
        xml_path = os.path.join(output_folder, f'{f"{random.randint(1, 1000)}.".join([fake.word() for _ in range(5)])}.xml')
        main_root = ET.Element("People")
        for _ in range(random.randint(100, 25000)):
            person = ET.SubElement(main_root, "Person")
            ET.SubElement(person, "Name").text = fake.name()
            ET.SubElement(person, "Age").text = str(fake.random_int(
                min=20, max=60, step=1))
            ET.SubElement(person, "Country").text = fake.country()
            ET.SubElement(person, "Date").text = str(fake.date_this_decade())
            ET.SubElement(person, "Description").text = fake.paragraph()
            ET.SubElement(person, "Tags").text = ', '.join(fake.words(5))
        tree = ET.ElementTree(main_root)
        ET.indent(tree, space="\t", level=0)
        tree.write(xml_path, encoding='utf-8', xml_declaration=True, method='xml')

def generate_sqlite_database(output_folder, num_files):
    os.makedirs(output_folder, exist_ok=True)

    for i in range(num_files):
        db_path = os.path.join(output_folder, f'{f"{random.randint(1, 1000)}.".join([fake.word() for _ in range(5)])}.db')
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                age INTEGER,
                country TEXT,
                date TEXT,
                description TEXT,
                tags TEXT
            )
        ''')
        for _ in range(random.randint(100, 50000)):
            cursor.execute('''
                INSERT INTO users (name, age, country, date, description, tags) VALUES (?, ?, ?, ?, ?, ?)
            ''', (fake.name(), fake.random_int(min=20, max=60, step=1), fake.country(),
                  str(fake.date_this_decade()), fake.paragraph(), ', '.join(fake.words(5))))
        conn.commit()
        conn.close()

if __name__ == "__main__":
    output_folder = "compression_inputs"
    num_files = 3000

    generate_text_file(output_folder, num_files)
    print("Text files generated")

    generate_image_file(output_folder, num_files)
    print("Image files generated")
    
    generate_video_file(output_folder, num_files)
    print("Video files generated")

    generate_pdf_file(output_folder, num_files)
    print("PDF files generated")

    generate_audio_file(output_folder, num_files)
    print("Audio files generated")

    generate_csv_file(output_folder, num_files)
    print("CSV files generated")

    generate_json_file(output_folder, num_files)
    print("JSON files generated")

    generate_xml_file(output_folder, num_files)
    print("XML files generated")

    generate_sqlite_database(output_folder, num_files)
    print("SQLite databases generated")
