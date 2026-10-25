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
import borders

eel.init('Gui')

def fetch_player_name(profile, selected_leaderboard):
    try:
        if selected_leaderboard == "ss":
            return requests.get(f"https://scoresaber.com/api/v2/players/{profile}", timeout=10).json()["name"]
        if selected_leaderboard == "bl":
            return requests.get(f"https://api.beatleader.com/player/{profile}", timeout=10).json()["name"]
    except (requests.RequestException, ValueError, KeyError, TypeError):
        pass
    return None

@eel.expose
def Generate(leaderboard_id, profile, score, gdriveLink, desc_notes, selected_leaderboard, codec, encoder, custom_name, custom_border, left_color, right_color):
    eel.DisableStartButton()
    eel.Hide("editor")
    eel.Hide("uploader")
    eel.Hide("results")
    eel.Hide("thumbnail")
    eel.print_clear()

    player_name = custom_name.strip() or fetch_player_name(profile, selected_leaderboard)
    if player_name is None:
        eel.print_output("Error: Failed to retrieve player information, check the Profile ID and the selected leaderboard")
        eel.EnableStartButton()
        return

    # scoresaber code
    map_id = None
    try:
        if selected_leaderboard == "ss":
            response = requests.get(f"https://scoresaber.com/api/v2/leaderboards/{leaderboard_id}")
            response.raise_for_status()
            leaderboard_data = response.json()
            bsr = leaderboard_data["map"]["bsid"]
            song_name = leaderboard_data["map"]["songName"]
            artist_name = leaderboard_data["map"]["songAuthorName"]
            mapper = leaderboard_data["map"]["levelAuthorName"]
            thumbnail_url = leaderboard_data["map"]["coverUrl"]
            rawdiff = leaderboard_data["difficulty"]["difficulty"]
            map_id = leaderboard_data["map"]["id"]
        else:
            response = requests.get(f"https://api.beatleader.com/leaderboard/{leaderboard_id}")
            response.raise_for_status()
            leaderboard_data = response.json()
            bsr = leaderboard_data["song"]["id"]
            song_name = leaderboard_data["song"]["name"]
            artist_name = leaderboard_data["song"]["author"]
            mapper = leaderboard_data["song"]["mapper"]
            thumbnail_url = leaderboard_data["song"]["coverImage"]
            rawdiff = leaderboard_data["difficulty"]["value"]
    except (requests.RequestException, ValueError, KeyError):
        eel.print_output("Error: Failed to retrieve leaderboard information, check the Leaderboard ID")
        eel.EnableStartButton()
        return

    file_name = f"{borders.safe_name(player_name)}_{bsr}"

    # remove files if they already exist
    for path in (f"Gui/Videos/{file_name}.mp4", f"transcripts/{file_name}_transcript.txt"):
        if os.path.exists(path):
            os.remove(path)

    eel.print_output(f"Selected leaderboard: {selected_leaderboard}")
    eel.print_output(f"Player: {player_name}")
    eel.print_output(f"Song name: {song_name}")
    eel.print_output(f"BSR: {bsr}")
    if selected_leaderboard == "ss":
        eel.print_output(f"SS map ID: {map_id}")
    eel.print_output(f"Song artist: {artist_name}")
    eel.print_output(f"Mapper: {mapper}")
    eel.print_output("downloading video...")
    try:
        downloaded = gdown.download(gdriveLink, "video.mp4", quiet=False, fuzzy=True)
    except Exception:
        downloaded = None
    if downloaded is None:
        eel.print_output("Error: Failed to download the video, check the Google Drive link and its sharing settings")
        eel.EnableStartButton()
        return
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
        case _:
            difficulty = str(rawdiff)

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
    player_font = ImageFont.truetype("Metropolis-Thin.otf", 100)

    p_left, p_top, p_right, p_bottom = draw.textbbox((0, 0), player_name, font=player_font)
    text_width = p_right - p_left
    text_height = p_bottom - p_top

    text_x = (1920 - text_width) / 2
    text_y = 930
    draw.text((text_x, text_y), player_name, font=player_font, fill=(255, 255, 255, 255))
    draw.text((text_x, text_y), player_name, font=player_font, fill=(255, 255, 255, 255))

    # Save the custom colors as the player's border, otherwise use the saved border or default.png
    if custom_border:
        path = borders.save_border(player_name, left_color, right_color)
        eel.print_output(f"Border saved as {path}")
    border = borders.get_border(player_name)
    image.paste(border, (0, 0), mask=border)
    try:
        logo = Image.open(borders.LOGO).convert("RGBA")
        image.paste(logo, (0, 0), mask=logo)
    except FileNotFoundError:
        eel.print_output(f"[warning] watermark non disponibile")

    image.save(f"Gui/Thumbnails/{file_name}.png")
    eel.ShowThumbnail(f"Thumbnails/{file_name}.png")

    title = f"{player_name} | {artist_name} - {song_name} [{difficulty}] | {score}"

    description = []
    if desc_notes.strip():
        description += [f"Note aggiuntive: {desc_notes}", ""]
    if selected_leaderboard == "ss":
        description.append(f"Player: https://scoresaber.com/u/{profile}")
    elif selected_leaderboard == "bl":
        description.append(f"Player: https://beatleader.com/u/{profile}")
    description.append(f"Mappa: https://beatsaver.com/maps/{bsr}")
    description.append(f"Mapper: {mapper}")
    if selected_leaderboard == "ss":
        description.append(f"Leaderboard: https://scoresaber.com/map/{map_id}/difficulty/{leaderboard_id}")
    elif selected_leaderboard == "bl":
        description.append(f"Leaderboard: https://beatleader.com/leaderboard/global/{leaderboard_id}")
    description += [
        "",
        "Join our Discord: https://discord.gg/m6NPkrhVFy",
        "",
        "Thumbnail design by @.benna_:",
        "https://www.instagram.com/draws_by_benna/",
        "Intro Animation by @pizzi7341:",
        "https://www.youtube.com/channel/UCc6spI8nRIAhM5-GB95GQpQ",
    ]
    description = "\n".join(description)

    eel.ShowResults(title, description)
    with open(f"transcripts/{file_name}_transcript.txt", "w", encoding="utf-8") as file:
        file.write(f"Title:\n\n{title}\n\nDescription:\n\n{description}\n")

    try:
        video_editor.main("video.mp4", file_name, codec, encoder)
    finally:
        os.remove("video.mp4")

@eel.expose
def GetEncoders():
    encoders = video_editor.get_available_encoders()
    return [
        {"id": codec, "name": video_editor.CODECS[codec], "encoders": [{"id": e["id"], "name": e["name"]} for e in encoders[codec]]}
        for codec in video_editor.CODECS if codec in encoders
    ]

# The custom player name replaces the one from the leaderboard everywhere, also for the border
@eel.expose
def GetBorderColors(profile, selected_leaderboard, custom_name):
    player_name = custom_name.strip() or (profile.strip() and fetch_player_name(profile.strip(), selected_leaderboard))
    if not player_name:
        return None
    return {"player": player_name, **borders.get_border_colors(player_name)}

@eel.expose
def PreviewBorder(left_color, right_color):
    return borders.border_preview(left_color, right_color)

eel.start('index.html', mode='chrome--app')
