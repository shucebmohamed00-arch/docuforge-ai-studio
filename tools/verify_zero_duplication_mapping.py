from pathlib import Path
import collections

BASE_DIR = Path("c:/Users/Shueb/Desktop/youtu")
CLIPS = BASE_DIR / "data/media/authentic_clips"
RUNWAY = BASE_DIR / "data/media/cinematic_ai_assets"
ADV = BASE_DIR / "data/media/advanced_25d"
FIN = BASE_DIR / "data/media/financial_graphics"
REMOTION = BASE_DIR / "data/media/remotion_renders"
PAPER = BASE_DIR / "data/media/paper_assets"
PHOTO = BASE_DIR / "data/media/documentary_photos"
BROLL = BASE_DIR / "data/media/broll_cache"
ANIM = BASE_DIR / "data/media/animations/swiss-air-grounding-prod"
STAGE = BASE_DIR / "data/media/magnates_stage"

# 76 Beats strictly mapped to 100% UNIQUE assets - ZERO REPETITION GUARANTEE
ZERO_DUP_MAPPING = {
    # CHAPTER 1: THE GROUNDING SHOCK (Beats 1-16) - Zurich Airport & Tarmac Freeze
    1:  [ANIM / "anim_01_map.mp4", CLIPS / "zurich_uncut_38_foggy_morning_kloten.mp4"],
    2:  [CLIPS / "zurich_uncut_06_fuel_station.mp4", CLIPS / "zurich_uncut_45_phone_booths_busy.mp4"],
    3:  [RUNWAY / "ai_07_fuel_hose_cutoff.mp4", CLIPS / "zurich_uncut_28_md11_wingtip.mp4"],
    4:  [RUNWAY / "ai_09_cancelled_departure_board.mp4", CLIPS / "zurich_uncut_20_flight_status_red.mp4"],
    5:  [CLIPS / "politics_ubs_23_bank_teller_counter.mp4", CLIPS / "zurich_uncut_35_ticket_receipts.mp4"],
    6:  [CLIPS / "zurich_uncut_37_grounded_lineup.mp4", CLIPS / "zurich_uncut_27_wheel_chocks.mp4"],
    7:  [STAGE / "stage_03_ubs_dossier.mp4", CLIPS / "politics_ubs_06_bank_vault_doors.mp4"],
    8:  [FIN / "graphic_02_debt_spiral.mp4", CLIPS / "politics_ubs_20_financial_district_zurich.mp4"],
    9:  [CLIPS / "zurich_uncut_09_swissair_cross.mp4", CLIPS / "zurich_uncut_01_tarmac_wide.mp4"],
    10: [ANIM / "anim_07_hunter_wheel.mp4", CLIPS / "politics_ubs_13_investor_meeting.mp4"],
    11: [FIN / "graphic_01_stock_crash.mp4", CLIPS / "politics_ubs_10_stock_chart_screen.mp4"],
    12: [ADV / "doc_01_nzz_audit_stamp.mp4", PAPER / "paper_01_blick_grounded.mp4"],
    13: [ADV / "parallax_02_philippe_bruggisser.mp4", CLIPS / "politics_ubs_05_press_cameras.mp4"],
    14: [CLIPS / "zurich_uncut_11_tower_pan.mp4", CLIPS / "politics_ubs_16_swiss_flag_waving.mp4"],
    15: [CLIPS / "politics_ubs_01_bern_parliament.mp4", PHOTO / "photo_05_parliament.mp4"],
    16: [PHOTO / "photo_07_british_airways.mp4", PHOTO / "photo_08_lufthansa.mp4"],

    # CHAPTER 2: THE EUROPEAN TRAP (Beats 17-27) - Deregulation, EEA No Vote & Isolation
    17: [RUNWAY / "ai_14_referendum_ballot_box.mp4", CLIPS / "politics_ubs_24_parliament_voting_lights.mp4"],
    18: [CLIPS / "politics_ubs_26_parliament_debates_hall.mp4", CLIPS / "politics_ubs_02_politician_speech.mp4"],
    19: [CLIPS / "politics_ubs_08_bundesrat_session.mp4", CLIPS / "politics_ubs_25_swiss_crest_podium.mp4"],
    20: [CLIPS / "pixabay_runway_takeoff.mp4", CLIPS / "zurich_uncut_07_runway_distant.mp4"],
    21: [PHOTO / "photo_09_air_france.mp4", CLIPS / "politics_ubs_15_cabinet_vote.mp4"],
    22: [CLIPS / "zurich_uncut_04_cockpit_view.mp4", CLIPS / "zurich_uncut_12_jetway_empty.mp4"],
    23: [ANIM / "anim_06_hud.mp4", CLIPS / "zurich_uncut_17_radar_screens.mp4"],
    24: [ANIM / "anim_08_infographic.mp4", CLIPS / "zurich_uncut_10_docked_planes.mp4"],
    25: [CLIPS / "zurich_uncut_33_flight_attendants.mp4", CLIPS / "zurich_uncut_16_pilot_briefing.mp4"],
    26: [PAPER / "paper_02_nzz_debts.mp4", CLIPS / "politics_ubs_22_newspaper_press_rolling.mp4"],
    27: [CLIPS / "politics_ubs_28_banker_briefcase_entrance.mp4", PHOTO / "photo_06_bruggisser.mp4"],

    # CHAPTER 3: THE HUNTER STRATEGY (Beats 28-42) - Aggressive Debt Acquisitions & Sabena Bleed
    28: [REMOTION / "parallax_bruggisser.mp4", CLIPS / "politics_ubs_18_banker_handshake.mp4"],
    29: [CLIPS / "politics_ubs_27_journalist_interviews_crowd.mp4", CLIPS / "zurich_uncut_15_kloten_hangar.mp4"],
    30: [FIN / "graphic_03_hunter_network.mp4", CLIPS / "zurich_uncut_08_baggage_carts.mp4"],
    31: [CLIPS / "pixabay_airliner_departure.mp4", CLIPS / "zurich_uncut_13_cargo_doors.mp4"],
    32: [REMOTION / "kinetic_document_inspector.mp4", PAPER / "paper_06_sabena.mp4"],
    33: [CLIPS / "politics_ubs_33_ubs_trading_floor.mp4", CLIPS / "zurich_uncut_24_maintenance_truck.mp4"],
    34: [CLIPS / "zurich_uncut_02_md11_tail.mp4", CLIPS / "zurich_uncut_03_engine_close.mp4"],
    35: [CLIPS / "zurich_uncut_14_terminal_gates.mp4", CLIPS / "zurich_uncut_23_apron_buses.mp4"],
    36: [CLIPS / "zurich_uncut_29_a320_nose.mp4", CLIPS / "zurich_uncut_05_ground_crew.mp4"],
    37: [RUNWAY / "ai_15_confidential_contract_signing.mp4", STAGE / "stage_04_ubs_vault.mp4"],
    38: [PAPER / "paper_highlighter_nzz_debts.mp4", CLIPS / "politics_ubs_17_emergency_fund_doc.mp4"],
    39: [CLIPS / "politics_ubs_34_paradeplatz_aerial_view.mp4", CLIPS / "politics_ubs_35_financial_times_headline.mp4"],
    40: [CLIPS / "zurich_uncut_18_luggage_conveyor.mp4", CLIPS / "zurich_uncut_21_swissair_counter.mp4"],
    41: [CLIPS / "zurich_uncut_22_security_gate.mp4", CLIPS / "zurich_uncut_26_ground_power_unit.mp4"],
    42: [CLIPS / "zurich_uncut_25_engine_cover_wrap.mp4", CLIPS / "zurich_uncut_31_terminal_stairs.mp4"],

    # CHAPTER 4: THE 17 BILLION BLACK HOLE (Beats 43-52) - Mario Corti Arrival & Post-9/11 Shock
    43: [CLIPS / "politics_ubs_04_marcel_ospel_face.mp4", CLIPS / "zurich_uncut_32_information_desk.mp4"],
    44: [REMOTION / "parallax_mario_corti.mp4", RUNWAY / "ai_16_corti_press_conference.mp4"],
    # [05:34 AUTHENTIC 20-SECOND INTERVIEW SOUNDBITE: Mario Corti & Marcel Ospel with SRF Dok broadcast audio]
    45: [PHOTO / "photo_02_mario_corti.mp4", CLIPS / "politics_ubs_09_mario_corti_mic.mp4"],
    46: [CLIPS / "politics_ubs_30_swiss_confederation_press_room.mp4", CLIPS / "politics_ubs_31_credit_suisse_teller_line.mp4"],
    47: [CLIPS / "politics_ubs_32_moritz_leuenberger_speech.mp4", CLIPS / "zurich_uncut_36_empty_tarmac_strip.mp4"],
    48: [ANIM / "anim_02_chart.mp4", CLIPS / "pixabay_gold_vault_bars.mp4"],
    49: [BROLL / "PASSENGER_TERMINAL.mp4", CLIPS / "zurich_uncut_39_stairway_pulled_back.mp4"],
    50: [CLIPS / "zurich_uncut_40_catering_truck_idle.mp4", CLIPS / "zurich_uncut_41_swissair_livery.mp4"],
    51: [CLIPS / "politics_ubs_21_television_broadcast_room.mp4", CLIPS / "zurich_uncut_42_police_patrol_airport.mp4"],
    52: [PHOTO / "photo_01_ubs_hq.mp4", CLIPS / "politics_ubs_11_credit_suisse_sign.mp4"],

    # CHAPTER 5: PROJECT PHOENIX & THE BETRAYAL (Beats 53-64) - Secret Meetings & Cash Refusal
    53: [CLIPS / "politics_ubs_03_ubs_headquarters.mp4", PHOTO / "photo_03_marcel_ospel.mp4"],
    54: [RUNWAY / "ai_17_ubs_boardroom_night.mp4", ADV / "parallax_03_marcel_ospel.mp4"],
    55: [ADV / "parallax_04_ubs_dossier.mp4", CLIPS / "kloten_clip_01.mp4"],
    56: [CLIPS / "politics_ubs_12_crossair_moritz_suter.mp4", CLIPS / "politics_ubs_29_crossair_aircraft_taxi.mp4"],
    57: [CLIPS / "kloten_clip_02.mp4", CLIPS / "kloten_clip_03.mp4"],
    58: [FIN / "graphic_04_intraday_countdown.mp4", PAPER / "paper_03_ubs_refusal.mp4"],
    59: [CLIPS / "zurich_uncut_51_fuel_tanker_arrival.mp4", CLIPS / "zurich_uncut_52_ground_marshall_signalling.mp4"],
    60: [CLIPS / "kloten_clip_04.mp4", CLIPS / "kloten_clip_05.mp4"],
    61: [CLIPS / "zurich_uncut_53_swisssun_catering_idle.mp4", CLIPS / "zurich_uncut_54_baggage_handler_waiting.mp4"],
    62: [CLIPS / "zurich_uncut_49_apron_nightfall.mp4", CLIPS / "zurich_uncut_48_control_tower_antenna.mp4"],
    63: [CLIPS / "zurich_uncut_46_checkin_closed_sign.mp4", CLIPS / "zurich_uncut_34_departure_lounge.mp4"],
    64: [CLIPS / "zurich_uncut_55_stranded_passengers_concourse.mp4", CLIPS / "zurich_uncut_56_swissair_ticket_counter_chaos.mp4"],

    # CHAPTER 6: THE FALL, REBIRTH & TRIAL (Beats 65-76) - Grounding Day, Bailout, Rebrand, Acquittals
    65: [PAPER / "paper_04_passengers.mp4", CLIPS / "zurich_uncut_43_stranded_family.mp4"],
    66: [CLIPS / "zurich_uncut_19_passenger_cluster.mp4", CLIPS / "zurich_uncut_44_newspaper_stand_airport.mp4"],
    67: [RUNWAY / "ai_18_paradeplatz_protest.mp4", PHOTO / "photo_04_protest.mp4"],
    68: [FIN / "graphic_05_bailout_rescue.mp4", PAPER / "paper_05_bailout.mp4"],
    69: [RUNWAY / "ai_08_grounded_fleet_aerial.mp4", CLIPS / "zurich_uncut_50_static_tailfin.mp4"],
    70: [CLIPS / "zurich_uncut_30_swisssun_logo.mp4", CLIPS / "kloten_clip_06.mp4"],
    71: [CLIPS / "zurich_uncut_47_silent_runway.mp4", CLIPS / "zurich_uncut_57_swissair_hangar_doors_shut.mp4"],
    72: [CLIPS / "zurich_uncut_58_static_airbus_a330_tarmac.mp4", CLIPS / "kloten_clip_07.mp4"],
    73: [CLIPS / "politics_ubs_07_protesters_signs.mp4", CLIPS / "politics_ubs_19_protest_banner_ubs.mp4"],
    74: [ADV / "doc_02_job_loss_stamp.mp4", PAPER / "paper_highlighter_job_loss.mp4"],
    75: [CLIPS / "zurich_uncut_59_night_tarmac_reflections.mp4", CLIPS / "kloten_clip_08.mp4"],
    76: [ADV / "parallax_01_grounds.mp4", CLIPS / "zurich_uncut_60_empty_departure_gate_chairs.mp4"]
}

# AUDIT AND VERIFICATION
all_used = []
for beat, assets in ZERO_DUP_MAPPING.items():
    for a in assets:
        all_used.append(str(a.resolve()))

counts = collections.Counter(all_used)
dups = {k: v for k, v in counts.items() if v > 1}

print(f"Total Beats: {len(ZERO_DUP_MAPPING)}")
print(f"Total Assets Assigned: {len(all_used)}")
print(f"Total Unique Assets: {len(counts)}")
print(f"Duplicates: {len(dups)}")

if dups:
    print("ERROR - Found Duplicates:")
    for k, v in dups.items():
        print(f"  {v}x: {Path(k).name}")
else:
    print("SUCCESS: 100% STRICT ZERO REPETITION GUARANTEE VERIFIED!")

missing = [a for a in all_used if not Path(a).exists()]
print(f"Missing files on disk: {len(missing)}")
if missing:
    for m in missing[:5]:
        print("  Missing:", m)
else:
    print("SUCCESS: ALL ASSIGNED ASSETS EXIST ON DISK!")
