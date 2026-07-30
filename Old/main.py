import requests
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from io import BytesIO
from moviepy.editor import VideoFileClip
import numpy as np
import textwrap
import eel
import gdown
import os
import video_editor

eel.init('Gui')

@eel.expose
def Generate(leaderboard_id, map_id, player_name, score, gdriveLink):
    global player
    player = player_name
    global bsr
    bsr = map_id
    eel.DisableStartButton()
    eel.Hide("editor")
    eel.Hide("uploader")
    eel.print_clear()

    # remove files if they already exist
    if os.path.exists(f"Gui\\Videos\\{player_name}_{map_id}.mp4"):
        os.remove(f"Gui\\Videos\\{player_name}_{map_id}.mp4")
    if os.path.exists(f"transcripts\\{player_name}_{map_id}_transcript.txt"):
        os.remove(f"transcripts\\{player_name}_{map_id}_transcript.txt")
    
    eel.print_output("downloading video...")
    gdown.download(gdriveLink, "video.mp4", quiet=False, fuzzy=True)
    eel.print_output("download complete")

    response = requests.get(f"https://scoresaber.com/api/leaderboard/by-id/{leaderboard_id}/info")
    if response.status_code != 200:
        eel.print_output("Error: Failed to retrieve leaderboard information")
    leaderboard_data = response.json()
    song_name = leaderboard_data["songName"]
    artist_name = leaderboard_data["songAuthorName"]
    thumbnail_url = leaderboard_data["coverImage"]
    rawdiff = leaderboard_data["difficulty"]["difficulty"]
    scoresaber_url = ""

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
    wrapped_song_name_width, wrapped_song_name_height = draw.textsize(wrapped_song_name, font=song_font)
    draw.text((600, 490), wrapped_song_name, font=song_font, fill=(255, 255, 255, 255), stroke_width=text_outline_width, stroke_fill=(255, 255, 255, 255))
    draw.text((600, 490 + wrapped_song_name_height + 15), artist_name, font=artist_font, fill=(255, 255, 255, 255))


    # Draw player name in the bottom-center of the image
    player_font = ImageFont.truetype("Metropolis-Thin.otf", 100)
    text_width, text_height = draw.textsize(player_name, font=player_font)
    text_x = (1920 - text_width) / 2
    text_y = 930
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
    image.save(f"Gui/Thumbnails/{player_name}_{map_id}.png")


    eel.print_output("")
    eel.print_output("Title:")
    eel.print_output("")
    if player_name == "Bennaaexe":
        player_name = "Benna"
    eel.print_output(f"{player_name} | {artist_name} - {song_name} [{difficulty}] | {score}")
    eel.print_output("")
    player_name = player_name.lower()

    match player_name:
        case "arbo_5418":
            scoresaber_url = "https://scoresaber.com/u/76561198298655923"
        case "bevilix":
            scoresaber_url = "https://scoresaber.com/u/76561199162096058"
        case "bennaaexe":
            scoresaber_url = "https://scoresaber.com/u/2150907071653816"
        case "bucciax":
            scoresaber_url = "https://scoresaber.com/u/76561198084852852"
        case "fabrix10":
            scoresaber_url = "https://scoresaber.com/u/76561198245740794"
        case "lisuccia":
            scoresaber_url = "https://scoresaber.com/u/76561198124196184"
        case "mercury":
            scoresaber_url = "https://scoresaber.com/u/76561198996666820"
        case "wdg_mysticxl":
            scoresaber_url = "https://scoresaber.com/u/76561199237410901"
        case "rylee":
            scoresaber_url = "https://scoresaber.com/u/76561198271943341"
        case "sionpizzi":
            scoresaber_url = "https://scoresaber.com/u/2102558539788298"
        case "spledgey":
            scoresaber_url = "https://scoresaber.com/u/76561198180343681"
        case "yoshi":
            scoresaber_url = "https://scoresaber.com/u/76561199075594377"
        case "mrsuperqwerasd":
            scoresaber_url = "https://scoresaber.com/u/76561198054519035"
        case "xoomies":
            scoresaber_url = "https://scoresaber.com/u/76561199253219625"
        case "ivy":
            scoresaber_url = "https://scoresaber.com/u/76561198828027917"
        case "praunt":
            scoresaber_url = "https://scoresaber.com/u/76561198826094646"
        case "gio":
            scoresaber_url = "https://scoresaber.com/u/76561198171051938"

    eel.print_output("Description:")
    eel.print_output("")
    eel.print_output(f"Player: {scoresaber_url}")
    eel.print_output(f"Mappa: https://beatsaver.com/maps/{map_id}")
    eel.print_output(f"Leaderboard: https://scoresaber.com/map/{map_id}/difficulty/{leaderboard_id}")
    eel.print_output("")
    eel.print_output("Join our Discord: https://discord.gg/m6NPkrhVFy")
    eel.print_output("")
    eel.print_output("Thumbnail design by Benna:")
    eel.print_output("https://www.instagram.com/draws_by_benna/")
    eel.print_output("Intro Animation by Pizzi#0255:")
    eel.print_output("https://www.youtube.com/channel/UCc6spI8nRIAhM5-GB95GQpQ")
    eel.print_output("")
    video_editor.main("video.mp4", player_name, map_id)
    os.remove("video.mp4")

@eel.expose
def Transcript(line):
    with open(f"transcripts/{player}_{bsr}_transcript.txt", "a") as file:
        file.write(f"{line}\n")

eel.start('index.html', mode='chrome--app')
