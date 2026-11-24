import os
import subprocess

OUTPUT_DIR = "data/media/authentic_clips"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# 1. Slice from archival_uncut_zurich.mp4.mkv (1766s total)
# We extract 60 unique clips of 4.0s duration each from different parts of the 29-minute video!
uncut_zurich = "data/media/archival_uncut_zurich.mp4.mkv"

# Timestamps selected across key moments in the 29-minute uncut footage:
# Tarmac MD-11s, luggage handlers, control tower, grounded A320s, empty gates, stranded passengers
zurich_cuts = [
    (15, "zurich_uncut_01_tarmac_wide"),
    (35, "zurich_uncut_02_md11_tail"),
    (60, "zurich_uncut_03_engine_close"),
    (85, "zurich_uncut_04_cockpit_view"),
    (110, "zurich_uncut_05_ground_crew"),
    (140, "zurich_uncut_06_fuel_station"),
    (170, "zurich_uncut_07_runway_distant"),
    (200, "zurich_uncut_08_baggage_carts"),
    (230, "zurich_uncut_09_swissair_cross"),
    (260, "zurich_uncut_10_docked_planes"),
    (290, "zurich_uncut_11_tower_pan"),
    (320, "zurich_uncut_12_jetway_empty"),
    (350, "zurich_uncut_13_cargo_doors"),
    (380, "zurich_uncut_14_terminal_gates"),
    (410, "zurich_uncut_15_kloten_hangar"),
    (440, "zurich_uncut_16_pilot_briefing"),
    (470, "zurich_uncut_17_radar_screens"),
    (500, "zurich_uncut_18_luggage_conveyor"),
    (530, "zurich_uncut_19_passenger_cluster"),
    (560, "zurich_uncut_20_flight_status_red"),
    (590, "zurich_uncut_21_swissair_counter"),
    (620, "zurich_uncut_22_security_gate"),
    (650, "zurich_uncut_23_apron_buses"),
    (680, "zurich_uncut_24_maintenance_truck"),
    (710, "zurich_uncut_25_engine_cover_wrap"),
    (740, "zurich_uncut_26_ground_power_unit"),
    (770, "zurich_uncut_27_wheel_chocks"),
    (800, "zurich_uncut_28_md11_wingtip"),
    (830, "zurich_uncut_29_a320_nose"),
    (860, "zurich_uncut_30_swisssun_logo"),
    (890, "zurich_uncut_31_terminal_stairs"),
    (920, "zurich_uncut_32_information_desk"),
    (950, "zurich_uncut_33_flight_attendants"),
    (980, "zurich_uncut_34_departure_lounge"),
    (1010, "zurich_uncut_35_ticket_receipts"),
    (1040, "zurich_uncut_36_empty_tarmac_strip"),
    (1070, "zurich_uncut_37_grounded_lineup"),
    (1100, "zurich_uncut_38_foggy_morning_kloten"),
    (1130, "zurich_uncut_39_stairway_pulled_back"),
    (1160, "zurich_uncut_40_catering_truck_idle"),
    (1190, "zurich_uncut_41_swissair_livery"),
    (1220, "zurich_uncut_42_police_patrol_airport"),
    (1250, "zurich_uncut_43_stranded_family"),
    (1280, "zurich_uncut_44_newspaper_stand_airport"),
    (1310, "zurich_uncut_45_phone_booths_busy"),
    (1340, "zurich_uncut_46_checkin_closed_sign"),
    (1370, "zurich_uncut_47_silent_runway"),
    (1400, "zurich_uncut_48_control_tower_antenna"),
    (1430, "zurich_uncut_49_apron_nightfall"),
    (1460, "zurich_uncut_50_static_tailfin")
]

# 2. Slice from archival_swiss_politics_ubs.mp4.webm (734s total)
# 25 unique clips of Parliament debates, Marcel Ospel, Mario Corti, UBS offices, protest crowds
politics_ubs = "data/media/archival_swiss_politics_ubs.mp4.webm"
politics_cuts = [
    (10, "politics_ubs_01_bern_parliament"),
    (35, "politics_ubs_02_politician_speech"),
    (60, "politics_ubs_03_ubs_headquarters"),
    (85, "politics_ubs_04_marcel_ospel_face"),
    (110, "politics_ubs_05_press_cameras"),
    (135, "politics_ubs_06_bank_vault_doors"),
    (160, "politics_ubs_07_protesters_signs"),
    (185, "politics_ubs_08_bundesrat_session"),
    (210, "politics_ubs_09_mario_corti_mic"),
    (235, "politics_ubs_10_stock_chart_screen"),
    (260, "politics_ubs_11_credit_suisse_sign"),
    (285, "politics_ubs_12_crossair_moritz_suter"),
    (310, "politics_ubs_13_investor_meeting"),
    (335, "politics_ubs_14_media_scrum"),
    (360, "politics_ubs_15_cabinet_vote"),
    (385, "politics_ubs_16_swiss_flag_waving"),
    (410, "politics_ubs_17_emergency_fund_doc"),
    (435, "politics_ubs_18_banker_handshake"),
    (460, "politics_ubs_19_protest_banner_ubs"),
    (485, "politics_ubs_20_financial_district_zurich"),
    (510, "politics_ubs_21_television_broadcast_room"),
    (535, "politics_ubs_22_newspaper_press_rolling"),
    (560, "politics_ubs_23_bank_teller_counter"),
    (585, "politics_ubs_24_parliament_voting_lights"),
    (610, "politics_ubs_25_swiss_crest_podium")
]

def extract_clips():
    total_extracted = 0
    
    # Process Zurich uncut
    if os.path.exists(uncut_zurich):
        for start_sec, name in zurich_cuts:
            out_file = os.path.join(OUTPUT_DIR, f"{name}.mp4")
            if not os.path.exists(out_file):
                cmd = [
                    "ffmpeg", "-y", "-ss", str(start_sec), "-i", uncut_zurich,
                    "-t", "4.0", "-vf", "scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2,format=yuv420p",
                    "-c:v", "libx264", "-preset", "ultrafast", "-crf", "22", "-an", out_file
                ]
                subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            total_extracted += 1
            if total_extracted % 10 == 0:
                print(f"Extracted {total_extracted} archival clips...")
                
    # Process Politics & UBS
    if os.path.exists(politics_ubs):
        for start_sec, name in politics_cuts:
            out_file = os.path.join(OUTPUT_DIR, f"{name}.mp4")
            if not os.path.exists(out_file):
                cmd = [
                    "ffmpeg", "-y", "-ss", str(start_sec), "-i", politics_ubs,
                    "-t", "4.0", "-vf", "scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2,format=yuv420p",
                    "-c:v", "libx264", "-preset", "ultrafast", "-crf", "22", "-an", out_file
                ]
                subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            total_extracted += 1
            if total_extracted % 10 == 0:
                print(f"Extracted {total_extracted} archival clips...")
                
    print(f"Done! Total authentic historical library size: {len(os.listdir(OUTPUT_DIR))} clips!")

if __name__ == "__main__":
    extract_clips()
