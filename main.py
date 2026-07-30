import requests
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from io import BytesIO
from moviepy import VideoFileClip
import numpy as np
import textwrap
import eel
import gdown
import os
import video_editor

eel.init('Gui')

@eel.expose
def Generate(leaderboard_id, profile, score, gdriveLink, selected_leaderboard):
    global player_name
    if selected_leaderboard == "ss":
        playerRequest = requests.get(f"https://scoresaber.com/api/v2/players/{profile}").json()
        player_name = playerRequest["playerNameInGame"]
    elif selected_leaderboard == "bl":
        playerRequest = requests.get(f"https://api.beatleader.com/player/{profile}").json()
        player_name = playerRequest["badges"][0]["player"]["name"]
    else:
        eel.print_output("Error: could not get selected leaderboard")

    global bsr
    global map_id
    global mapper
    
    # scoresaber code
    if selected_leaderboard == "ss":
        response = requests.get(f"https://scoresaber.com/api/v2/leaderboards/{leaderboard_id}")
        if response.status_code != 200:
            eel.print_output("Error: Failed to retrieve leaderboard information")
        leaderboard_data = response.json()
        bsr = leaderboard_data["map"]["bsid"]
        song_name = leaderboard_data["map"]["songName"]
        artist_name = leaderboard_data["map"]["songAuthorName"]
        mapper = leaderboard_data["map"]["levelAuthorName"]
        thumbnail_url = leaderboard_data["map"]["coverUrl"]
        rawdiff = leaderboard_data["difficulty"]["difficulty"]
        map_id = leaderboard_data["map"]["id"]
    elif selected_leaderboard == "bl":
        response = requests.get(f"https://api.beatleader.com/leaderboard/{leaderboard_id}")
        if response.status_code != 200:
            eel.print_output("Error: Failed to retrieve leaderboard information")
        leaderboard_data = response.json()
        bsr = leaderboard_data["song"]["id"]
        song_name = leaderboard_data["song"]["name"]
        artist_name = leaderboard_data["song"]["author"]
        mapper = leaderboard_data["song"]["mapper"]
        thumbnail_url = leaderboard_data["song"]["coverImage"]
        rawdiff = leaderboard_data["difficulty"]["value"]
    else:
        eel.print_output("Error: could not get selected leaderboard")
    
    eel.DisableStartButton()
    eel.Hide("editor")
    eel.Hide("uploader")
    eel.print_clear()

    # remove files if they already exist
    if os.path.exists(f"Gui\\Videos\\{player_name}_{bsr}.mp4"):
        os.remove(f"Gui\\Videos\\{player_name}_{bsr}.mp4")
    if os.path.exists(f"transcripts\\{player_name}_{bsr}_transcript.txt"):
        os.remove(f"transcripts\\{player_name}_{bsr}_transcript.txt")

    eel.print_output(f"Selected leaderboard: {selected_leaderboard}")
    eel.print_output(f"Player: {player_name}")
    eel.print_output(f"Song name: {song_name}")
    eel.print_output(f"BSR: {bsr}")
    if selected_leaderboard == "ss":
        eel.print_output(f"SS map ID: {map_id}")
    eel.print_output(f"Song artist: {artist_name}")
    eel.print_output(f"Mapper: {mapper}")
    eel.print_output("downloading video...")
    gdown.download(gdriveLink, "video.mp4", quiet=False)
    eel.print_output("download complete")

    
    match rawdiff:
        case 1:
           difficulty = "Easy" 
        case 3:
            difficulty = "Normal"
        case 5:
            difficulty = "Hard"
        case 7:
            difficulty = "Expert"
        case 9:
            difficulty = "Expert+"

    response = requests.get(thumbnail_url)
    if response.status_code != 200:
        eel.print_output("Error: Failed to download thumbnail image")
    
    thumbnail = Image.open(BytesIO(response.content)).convert("RGBA")
    thumbnail = thumbnail.resize((500, 500))
    clip = VideoFileClip("video.mp4")
    frame = clip.get_frame(clip.duration * np.random.random())
    clip.close()
    image = Image.fromarray(frame)
    background = image.resize((1920, 1080))
    background = background.convert("RGBA")
    background = background.filter(ImageFilter.GaussianBlur(radius = 10))
    draw = ImageDraw.Draw(background)


    # Create a new image with the same size as the background
    image = Image.new("RGBA", (1920, 1080))
    
    # Paste the background image onto the new image
    image.paste(background, (0, 0))
    thumbnail_pos = (75, 300)
    image.paste(thumbnail, thumbnail_pos, thumbnail)
    if len(song_name) < 25:
        song_font_size = 85
        artist_font_size = 60
    else:
        song_font_size = 70
        artist_font_size = 45
    # Draw song name and artist
    text_outline_width = 4
    song_font = ImageFont.truetype("Metropolis-Thin.otf", song_font_size)
    artist_font = ImageFont.truetype("Metropolis-Thin.otf", artist_font_size)
    draw = ImageDraw.Draw(image)
    wrapped_song_name = textwrap.fill(song_name, 30)

    # Get the bounding box tuple: (left, top, right, bottom)
    left, top, right, bottom = draw.multiline_textbbox(
        (0, 0), wrapped_song_name, font=song_font
    )

    # Calculate width and height
    wrapped_song_name_width = right - left
    wrapped_song_name_height = bottom - top

    # Render text
    draw.text(
        (600, 490),
        wrapped_song_name,
        font=song_font,
        fill=(255, 255, 255, 255),
        stroke_width=text_outline_width,
        stroke_fill=(255, 255, 255, 255),
    )
    draw.text(
        (600, 490 + wrapped_song_name_height + 15),
        artist_name,
        font=artist_font,
        fill=(255, 255, 255, 255),
    )


    # Draw player name in the bottom-center of the image
    # Draw player name in the bottom-center of the image
    player_font = ImageFont.truetype("Metropolis-Thin.otf", 100)
    
    # Get bounding box: (left, top, right, bottom)
    p_left, p_top, p_right, p_bottom = draw.textbbox((0, 0), player_name, font=player_font)
    text_width = p_right - p_left
    text_height = p_bottom - p_top

    text_x = (1920 - text_width) / 2
    text_y = 930
    draw.text((text_x, text_y), player_name, font=player_font, fill=(255, 255, 255, 255))
    draw.text((text_x, text_y), player_name, font=player_font, fill=(255, 255, 255, 255))

    if player_name in ["arbo_5418", "bevilix", "fabrix10", "sionpizzi", "ivy"]:
        border_path = f"borders/default.png"
    else:
        border_path = f"borders/{player_name}.png"
    logo_path = f"borders/logo.png"
    try:
        border = Image.open(border_path)
        image.paste(border, (0, 0), mask=border)

    except FileNotFoundError:
        eel.print_output(f"[warning] No border found for player {player_name}")
    try:
        logo = Image.open(logo_path)
        image.paste(logo, (0, 0), mask=logo)
    except FileNotFoundError:
        eel.print_output(f"[warning] watermark non disponibile")
    

    # Save the image to a file
    eel.print_clear()
    image.save(f"Gui/Thumbnails/{player_name}_{bsr}.png")


    eel.print_output("")
    eel.print_output("Title:")
    eel.print_output("")
    eel.print_output(f"{player_name} | {artist_name} - {song_name} [{difficulty}] | {score}")
    eel.print_output("")
    player_name = player_name.lower()

    eel.print_output("Description:")
    eel.print_output("")
    eel.print_output(f"Player: https://scoresaber.com/u/{profile}")
    eel.print_output(f"Mappa: https://beatsaver.com/maps/{bsr}")
    eel.print_output(f"Mapper: {mapper}")
    if selected_leaderboard == "ss":
        eel.print_output(f"Leaderboard: https://scoresaber.com/map/{map_id}/difficulty/{leaderboard_id}")
    elif selected_leaderboard == "bl":
        eel.print_output(f"Leaderboard: https://beatleader.com/leaderboard/global/{leaderboard_id}")
    eel.print_output("")
    eel.print_output("Join our Discord: https://discord.gg/m6NPkrhVFy")
    eel.print_output("")
    eel.print_output("Thumbnail design by @.benna_:")
    eel.print_output("https://www.instagram.com/draws_by_benna/")
    eel.print_output("Intro Animation by @pizzi7341:")
    eel.print_output("https://www.youtube.com/channel/UCc6spI8nRIAhM5-GB95GQpQ")
    eel.print_output("")
    video_editor.main("video.mp4", player_name, bsr)
    os.remove("video.mp4")

@eel.expose
def Transcript(line):
    with open(f"transcripts/{player_name}_{bsr}_transcript.txt", "a") as file:
        file.write(f"{line}\n")

eel.start('index.html', mode='chrome--app')
