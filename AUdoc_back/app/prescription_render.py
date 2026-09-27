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

def draw_rounded_rectangle(draw, xy, radius, fill):
    """Draws a rounded rectangle"""
    x1, y1, x2, y2 = xy
    draw.rectangle(
        [(x1, y1 + radius), (x2, y2 - radius)],
        fill=fill
    )
    draw.rectangle(
        [(x1 + radius, y1), (x2 - radius, y2)],
        fill=fill
    )
    draw.pieslice([(x1, y1), (x1 + radius * 2, y1 + radius * 2)], 180, 270, fill=fill)
    draw.pieslice([(x2 - radius * 2, y1), (x2, y1 + radius * 2)], 270, 360, fill=fill)
    draw.pieslice([(x1, y2 - radius * 2), (x1 + radius * 2, y2)], 90, 180, fill=fill)
    draw.pieslice([(x2 - radius * 2, y2 - radius * 2), (x2, y2)], 0, 90, fill=fill)

def generate_prescription_png(medical_history):
    """
    Generates a beautifully designed PNG byte buffer for a given MedicalHistory object.
    Matches the premium reference design.
    """
    # ── Configuration ──
    WIDTH = 800
    HEIGHT = 1600 # Starting height, will be cropped
    BG_COLOR = "#FAFAFA"
    CARD_BG = "#FFFFFF"
    PRIMARY_COLOR = "#3d6343"
    SECONDARY_BG = "#F1EBE1"
    TEXT_MAIN = "#1A1A1A"
    TEXT_MUTED = "#737373"
    TEXT_LIGHT = "#A3A3A3"
    ACCENT_WARN = "#D97706"
    
    img = Image.new("RGB", (WIDTH, HEIGHT), BG_COLOR)
    draw = ImageDraw.Draw(img)
    
    # ── Fonts ──
    try:
        font_logo = get_font("Inter-Bold.ttf", 32)
        font_logo_sub = get_font("Inter-Medium.ttf", 14)
        font_rx_small = get_font("Georgia-Bold.ttf", 20)
        
        font_bold_l = get_font("Inter-Bold.ttf", 22)
        font_bold_m = get_font("Inter-Bold.ttf", 18)
        font_bold_s = get_font("Inter-Bold.ttf", 14)
        
        font_reg_m = get_font("Inter-Regular.ttf", 16)
        font_reg_s = get_font("Inter-Regular.ttf", 14)
        font_reg_xs = get_font("Inter-Regular.ttf", 12)
        
        font_italic_s = get_font("Inter-Italic.ttf", 14)
    except Exception:
        # Extreme fallback
        font_logo = font_logo_sub = font_rx_small = ImageFont.load_default()
        font_bold_l = font_bold_m = font_bold_s = ImageFont.load_default()
        font_reg_m = font_reg_s = font_reg_xs = font_italic_s = ImageFont.load_default()

    # ── Main Content Area (White Card) ──
    card_margin = 0
    # Actually, the reference is a full card. Let's make the whole background white
    draw.rectangle([0, 0, WIDTH, HEIGHT], fill=CARD_BG)

    # ── Header ──
    draw.rectangle([0, 0, WIDTH, 100], fill=PRIMARY_COLOR)
    draw.text((40, 25), "AUdoc", font=font_logo, fill="#FFFFFF")
    draw.text((40, 65), "Assam University Silchar • Student Health Center", font=font_logo_sub, fill="#E5E7EB")
    
    # ── Sub-header (Date / ID) ──
    draw.rectangle([0, 100, WIDTH, 140], fill="#F3F4F6")
    date_str = medical_history.appointment_date.strftime("%d %b %Y") if medical_history.appointment_date else timezone.now().strftime("%d %b %Y")
    rx_id = f"RX-{medical_history.appointment_date.year if medical_history.appointment_date else timezone.now().year}-{medical_history.id:04d}"
    draw.text((40, 110), rx_id, font=font_reg_s, fill=TEXT_MUTED)
    draw.text((WIDTH - 200, 110), f"Issued {date_str}", font=font_reg_s, fill=TEXT_MUTED)

    # ── Grid Info (Patient & Doctor) ──
    y_offset = 170
    
    # Left: Patient
    draw.text((40, y_offset), "PATIENT", font=font_bold_s, fill=TEXT_LIGHT)
    student_name = medical_history.student_id  # fallback
    # Let's try to get full name if the student ID exists in the system, but medical_history is passed.
    # In absence of full name, we'll just display student ID as name, and maybe generic text below.
    draw.text((40, y_offset + 25), str(student_name), font=font_bold_l, fill=TEXT_MAIN)
    draw.text((40, y_offset + 55), "Assam University Student", font=font_reg_s, fill=TEXT_MUTED)
    
    # Right: Doctor
    draw.text((WIDTH // 2 + 20, y_offset), "ATTENDING DOCTOR", font=font_bold_s, fill=TEXT_LIGHT)
    doctor_name = medical_history.doctor_name or "General Physician"
    if not doctor_name.startswith("Dr."):
        doctor_name = f"Dr. {doctor_name}"
    draw.text((WIDTH // 2 + 20, y_offset + 25), doctor_name, font=font_bold_l, fill=TEXT_MAIN)
    draw.text((WIDTH // 2 + 20, y_offset + 55), "General Physician • AUdoc Health Center", font=font_reg_s, fill=TEXT_MUTED)
    
    y_offset += 100
    
    # ── Dashed Line Separator ──
    def draw_dashed_line(y, color="#E5E7EB", width=1):
        for x in range(40, WIDTH - 40, 10):
            draw.line([(x, y), (x+5, y)], fill=color, width=width)
            
    draw_dashed_line(y_offset)
    y_offset += 25
    
    # ── Diagnosis ──
    draw.text((40, y_offset), "DIAGNOSIS", font=font_bold_s, fill=TEXT_LIGHT)
    draw.text((40, y_offset + 25), str(medical_history.illness), font=font_bold_m, fill=PRIMARY_COLOR)
    
    wrapper = textwrap.TextWrapper(width=85)
    symptoms_lines = wrapper.wrap(medical_history.symptoms or "No specific symptoms recorded.")
    sym_y = y_offset + 55
    for line in symptoms_lines:
        draw.text((40, sym_y), line, font=font_reg_s, fill=TEXT_MUTED)
        sym_y += 20
        
    y_offset = sym_y + 15
    draw_dashed_line(y_offset)
    y_offset += 25
    
    # ── Medicines ──
    draw.text((40, y_offset), "R", font=font_rx_small, fill=TEXT_LIGHT)
    draw.text((65, y_offset + 3), "MEDICINES PRESCRIBED", font=font_bold_s, fill=TEXT_LIGHT)
    y_offset += 45
    
    medicines = medical_history.prescribedmedicine_set.all()
    
    if not medicines:
        draw.text((40, y_offset), "No medicines prescribed.", font=font_reg_m, fill=TEXT_MUTED)
        y_offset += 40
    else:
        for i, pm in enumerate(medicines, 1):
            if y_offset > HEIGHT - 300:
                draw.text((40, y_offset), "... (more medicines truncated)", font=font_reg_m, fill=TEXT_MUTED)
                y_offset += 40
                break
                
            # Number Circle
            draw.ellipse([40, y_offset, 65, y_offset + 25], fill=PRIMARY_COLOR)
            draw.text((48, y_offset + 4), str(i), font=font_bold_s, fill="#FFFFFF")
            
            # Medicine Name & Dosage
            med_name = pm.medicine.name
            draw.text((80, y_offset + 2), med_name, font=font_bold_m, fill=TEXT_MAIN)
            
            # Calculate width of medicine name to place dosage next to it
            try:
                name_width = font_bold_m.getlength(med_name)
            except AttributeError:
                name_width = font_bold_m.getsize(med_name)[0]
                
            dosage = pm.dosage if pm.dosage else ""
            if dosage:
                draw.text((80 + name_width + 10, y_offset + 4), dosage, font=font_reg_s, fill=TEXT_LIGHT)
            
            y_offset += 35
            
            # Badges (Timing, Food, Duration, Qty)
            badge_x = 80
            
            # Timing badge
            timings = []
            if pm.take_morning: timings.append("Morning")
            if pm.take_afternoon: timings.append("Afternoon")
            if pm.take_evening: timings.append("Evening")
            if pm.take_night: timings.append("Night")
            timing_str = ", ".join(timings) if timings else pm.frequency_pattern
            
            if timing_str:
                try: timing_w = font_reg_xs.getlength(timing_str)
                except: timing_w = font_reg_xs.getsize(timing_str)[0]
                draw_rounded_rectangle(draw, [badge_x, y_offset, badge_x + timing_w + 20, y_offset + 25], 12, "#ECFDF5")
                draw.text((badge_x + 10, y_offset + 5), timing_str, font=font_bold_s, fill=PRIMARY_COLOR)
                badge_x += timing_w + 30
                
            # Food badge
            food_str = pm.get_food_timing_display()
            if food_str:
                try: food_w = font_reg_xs.getlength(food_str)
                except: food_w = font_reg_xs.getsize(food_str)[0]
                draw_rounded_rectangle(draw, [badge_x, y_offset, badge_x + food_w + 20, y_offset + 25], 12, "#F3F4F6")
                draw.text((badge_x + 10, y_offset + 5), food_str, font=font_bold_s, fill=PRIMARY_COLOR)
                badge_x += food_w + 30
                
            # Duration badge
            if pm.duration_days:
                dur_str = f"{pm.duration_days} days"
                try: dur_w = font_reg_xs.getlength(dur_str)
                except: dur_w = font_reg_xs.getsize(dur_str)[0]
                draw_rounded_rectangle(draw, [badge_x, y_offset, badge_x + dur_w + 20, y_offset + 25], 12, "#F3F4F6")
                draw.text((badge_x + 10, y_offset + 5), dur_str, font=font_bold_s, fill=PRIMARY_COLOR)
                badge_x += dur_w + 30
                
            # Qty badge
            if pm.quantity:
                qty_str = f"Qty: {pm.quantity}"
                try: qty_w = font_reg_xs.getlength(qty_str)
                except: qty_w = font_reg_xs.getsize(qty_str)[0]
                draw_rounded_rectangle(draw, [badge_x, y_offset, badge_x + qty_w + 20, y_offset + 25], 12, "#F3F4F6")
                draw.text((badge_x + 10, y_offset + 5), qty_str, font=font_bold_s, fill=PRIMARY_COLOR)
                
            y_offset += 35
            
            # Instructions / Note
            if pm.instructions:
                draw.text((80, y_offset), f"Note: {pm.instructions}", font=font_italic_s, fill=ACCENT_WARN)
                y_offset += 25
                
            y_offset += 15
            # Divider between medicines
            if i < len(medicines):
                draw.line([(80, y_offset), (WIDTH - 40, y_offset)], fill="#F3F4F6", width=1)
                y_offset += 20
                
    # ── Footer ──
    # Create a nice gray background block for the footer
    footer_start_y = y_offset + 30
    draw.rectangle([0, footer_start_y, WIDTH, HEIGHT], fill="#F9FAFB")
    draw.line([(0, footer_start_y), (WIDTH, footer_start_y)], fill="#E5E7EB", width=1)
    
    y_offset = footer_start_y + 30
    
    # Advice text
    advice = "General advice: Complete the full course as prescribed. Stay hydrated and rest. Contact the health center if symptoms worsen or persist beyond 3 days."
    advice_lines = textwrap.wrap(advice, width=90)
    for line in advice_lines:
        draw.text((40, y_offset), line, font=font_reg_s, fill=TEXT_MUTED)
        y_offset += 20
        
    y_offset += 40
    
    # Signature
    try:
        font_sig = get_font("CedarvilleCursive-Regular.ttf", 36) # Needs a cursive font if available, fallback to italic
    except:
        font_sig = font_italic_s
        
    draw.text((WIDTH - 250, y_offset), doctor_name, font=font_sig, fill=PRIMARY_COLOR)
    draw.line([(WIDTH - 250, y_offset + 40), (WIDTH - 40, y_offset + 40)], fill="#E5E7EB", width=1)
    draw.text((WIDTH - 250, y_offset + 45), doctor_name, font=font_bold_s, fill=TEXT_MAIN)
    draw.text((WIDTH - 250, y_offset + 65), "General Physician", font=font_reg_xs, fill=TEXT_MUTED)
    
    # Verification link
    verify_link = f"Scan/verify at {getattr(settings, 'SITE_URL', 'audoc.onrender.com')}/rx/{rx_id}"
    draw.text((40, y_offset + 65), verify_link, font=font_reg_xs, fill=TEXT_LIGHT)
    
    y_offset += 120
    
    # Very bottom line
    draw.line([(40, y_offset), (WIDTH - 40, y_offset)], fill="#E5E7EB", width=1)
    y_offset += 15
    footer_msg = "Digitally generated by AUdoc — valid without a physical signature. Please retain for your records."
    
    try: msg_w = font_reg_xs.getlength(footer_msg)
    except: msg_w = font_reg_xs.getsize(footer_msg)[0]
    
    draw.text(((WIDTH - msg_w) // 2, y_offset), footer_msg, font=font_reg_xs, fill=TEXT_LIGHT)
    
    y_offset += 40
    
    # Crop image to actual content height + margin
    final_height = min(y_offset, HEIGHT)
    img = img.crop((0, 0, WIDTH, final_height))
    
    buf = BytesIO()
    img.save(buf, format="PNG", quality=95)
    buf.seek(0)
    return buf.getvalue()