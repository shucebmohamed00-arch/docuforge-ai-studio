from PIL import Image, ImageDraw, ImageFont
import os

os.makedirs('data/media/overlays', exist_ok=True)

# 1. Mario Corti Soundbite with Subtitle Translation
img_corti = Image.new('RGBA', (1920, 1080), (0, 0, 0, 0))
draw = ImageDraw.Draw(img_corti)

# Top Translation Banner (Cinematic Subtitle bar)
sub_x, sub_y, sub_w, sub_h = 280, 780, 1360, 60
draw.rectangle([sub_x, sub_y, sub_x + sub_w, sub_y + sub_h], fill=(10, 12, 16, 235))
# Amber accent indicator for translation
draw.rectangle([sub_x, sub_y, sub_x + 6, sub_y + sub_h], fill=(235, 180, 45, 255))

# Lower-Third Identity Card
card_x, card_y, card_w, card_h = 60, 890, 860, 105
draw.rectangle([card_x, card_y, card_x + card_w, card_y + card_h], fill=(12, 14, 18, 235))
draw.rectangle([card_x, card_y, card_x + 8, card_y + card_h], fill=(225, 25, 30, 255))

try:
    font_bold = ImageFont.truetype('C:/Windows/Fonts/arialbd.ttf', 32)
    font_sub = ImageFont.truetype('C:/Windows/Fonts/arial.ttf', 20)
    font_trans = ImageFont.truetype('C:/Windows/Fonts/arialbd.ttf', 23)
except:
    font_bold = ImageFont.load_default()
    font_sub = ImageFont.load_default()
    font_trans = ImageFont.load_default()

# Identity text
draw.text((card_x + 28, card_y + 16), 'MARIO CORTI', fill=(255, 255, 255, 255), font=font_bold)
draw.text((card_x + 28, card_y + 60), 'CEO, SWISSAIR GROUP  |  ZURICH EMERGENCY PRESS BRIEFING', fill=(200, 205, 215, 255), font=font_sub)

# Subtitle translation text
draw.text((sub_x + 24, sub_y + 16), '[ENGLISH TRANSLATION] "We fought to the final hour... but the banks refused all emergency liquidity."', fill=(245, 245, 250, 255), font=font_trans)

img_corti.save('data/media/overlays/corti_translated_overlay.png', 'PNG')

# 2. Blick Newspaper Headline Translation Overlay
img_blick = Image.new('RGBA', (1920, 1080), (0, 0, 0, 0))
draw_b = ImageDraw.Draw(img_blick)
b_x, b_y, b_w, b_h = 380, 880, 1160, 65
draw_b.rectangle([b_x, b_y, b_x + b_w, b_y + b_h], fill=(10, 12, 16, 240))
draw_b.rectangle([b_x, b_y, b_x + 6, b_y + b_h], fill=(225, 25, 30, 255))
draw_b.text((b_x + 24, b_y + 18), 'BLICK: "DER SCHWARZE DIENSTAG"  ->  [TRANSLATION: "THE BLACK TUESDAY"]', fill=(255, 255, 255, 255), font=font_trans)
img_blick.save('data/media/overlays/blick_translated_overlay.png', 'PNG')

print('Generated translation overlays successfully!')
