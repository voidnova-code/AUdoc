import os
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
from django.conf import settings
from django.utils import timezone
import textwrap

def get_font(font_name, size):
    base_dir = os.path.join(settings.BASE_DIR, 'app', 'static', 'fonts')
    font_path = os.path.join(base_dir, font_name)
    try:
        return ImageFont.truetype(font_path, size)
    except IOError:
        # Fallback to default if font is missing
        return ImageFont.load_default()

def generate_prescription_png(medical_history):
    """
    Generates a PNG byte buffer for a given MedicalHistory object and its prescriptions.
    """
    # ── Configuration ──
    WIDTH = 1200
    HEIGHT = 1600 # Starting height, can be cropped later if too tall
    BG_COLOR = "#FFFFFF"
    PRIMARY_COLOR = "#4a7c59" # Green theme as requested
    TEXT_COLOR = "#333333"
    MUTED_COLOR = "#666666"
    
    img = Image.new("RGB", (WIDTH, HEIGHT), BG_COLOR)
    draw = ImageDraw.Draw(img)
    
    # ── Fonts ──
    try:
        font_title = get_font("Inter-Bold.ttf", 48)
        font_header = get_font("Inter-SemiBold.ttf", 32)
        font_body = get_font("Inter-Regular.ttf", 28)
        font_small = get_font("Inter-Regular.ttf", 22)
        font_bold = get_font("Inter-Bold.ttf", 28)
    except Exception:
        font_title = font_header = font_body = font_small = font_bold = ImageFont.load_default()

    # ── Header ──
    draw.rectangle([0, 0, WIDTH, 150], fill=PRIMARY_COLOR)
    draw.text((50, 45), "AUdoc Clinic - Digital Prescription", font=font_title, fill="#FFFFFF")
    
    # ── Patient & Doctor Details ──
    y_offset = 180
    date_str = medical_history.appointment_date.strftime("%d %B %Y") if medical_history.appointment_date else timezone.now().strftime("%d %B %Y")
    
    # Left column: Patient
    draw.text((50, y_offset), "Patient Details:", font=font_header, fill=PRIMARY_COLOR)
    draw.text((50, y_offset + 50), f"Student ID: {medical_history.student_id}", font=font_body, fill=TEXT_COLOR)
    draw.text((50, y_offset + 90), f"Illness: {medical_history.illness}", font=font_body, fill=TEXT_COLOR)
    
    # Right column: Doctor & Date
    draw.text((700, y_offset), "Consultation Details:", font=font_header, fill=PRIMARY_COLOR)
    draw.text((700, y_offset + 50), f"Doctor: {medical_history.doctor_name}", font=font_body, fill=TEXT_COLOR)
    draw.text((700, y_offset + 90), f"Date: {date_str}", font=font_body, fill=TEXT_COLOR)
    
    y_offset += 160
    
    # Symptoms
    draw.text((50, y_offset), "Symptoms:", font=font_header, fill=PRIMARY_COLOR)
    
    # Text wrap for symptoms
    wrapper = textwrap.TextWrapper(width=80)
    symptoms_lines = wrapper.wrap(medical_history.symptoms or "N/A")
    for line in symptoms_lines:
        y_offset += 40
        draw.text((50, y_offset), line, font=font_body, fill=TEXT_COLOR)
        
    y_offset += 80
    
    # ── Prescription List ──
    draw.line([50, y_offset, WIDTH-50, y_offset], fill=PRIMARY_COLOR, width=2)
    y_offset += 30
    draw.text((50, y_offset), "Prescribed Medicines:", font=font_header, fill=PRIMARY_COLOR)
    y_offset += 50
    
    medicines = medical_history.prescribedmedicine_set.all()
    
    if not medicines:
        draw.text((50, y_offset), "No medicines prescribed.", font=font_body, fill=MUTED_COLOR)
        y_offset += 40
    else:
        for i, pm in enumerate(medicines, 1):
            if y_offset > HEIGHT - 150:
                # If we run out of space, just stop for now (or could extend image height)
                draw.text((50, y_offset), "... (more medicines truncated)", font=font_body, fill=MUTED_COLOR)
                y_offset += 40
                break
                
            med_title = f"{i}. {pm.medicine.name}"
            draw.text((50, y_offset), med_title, font=font_bold, fill=TEXT_COLOR)
            
            # Details: Dosage | Route | Duration
            details = []
            if pm.dosage:
                details.append(f"Dosage: {pm.dosage}")
            if pm.route:
                details.append(f"Route: {pm.get_route_display()}")
            if pm.duration_days:
                details.append(f"Duration: {pm.duration_days} days")
                
            details_str = " | ".join(details)
            draw.text((50, y_offset + 35), details_str, font=font_small, fill=MUTED_COLOR)
            
            # Timing & Food
            timing_str = f"Timing: {pm.frequency_pattern} ({pm.get_food_timing_display()})"
            draw.text((50, y_offset + 65), timing_str, font=font_small, fill=TEXT_COLOR)
            
            if pm.instructions:
                draw.text((50, y_offset + 95), f"Instructions: {pm.instructions}", font=font_small, fill=MUTED_COLOR)
                y_offset += 140
            else:
                y_offset += 110
                
    y_offset += 50
    
    # ── Footer ──
    draw.line([50, y_offset, WIDTH-50, y_offset], fill=PRIMARY_COLOR, width=2)
    y_offset += 30
    draw.text((50, y_offset), "Note: This is a system generated digital prescription.", font=font_small, fill=MUTED_COLOR)
    
    # Crop image to actual content height + margin
    final_height = min(y_offset + 100, HEIGHT)
    img = img.crop((0, 0, WIDTH, final_height))
    
    buf = BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return buf.getvalue()
