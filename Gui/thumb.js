function send(){
    Show("log")
    var gdrive = document.getElementById("gdrive").value
    var leaderboard_id = document.getElementById("leaderboard_id").value
    var profile = document.getElementById("profile").value
    var score = document.getElementById("score").value
    var desc_notes = document.getElementById("desc-notes").value
    var selected_leaderboard = document.querySelector('input[name="leaderboard"]:checked')?.value;
    var codec = document.getElementById("codec").value
    var encoder = document.getElementById("encoder").value
    var custom_name = document.getElementById("custom-name").value
    var custom_border = document.getElementById("custom-border").checked
    var left_color = document.getElementById("left-color").value
    var right_color = document.getElementById("right-color").value
    eel.Generate(leaderboard_id, profile, score, gdrive, desc_notes, selected_leaderboard, codec, encoder, custom_name, custom_border, left_color, right_color)
}

var codecs = []

// Fill the codec list with the codecs that have at least one encoder working on this machine
function LoadEncoders(){
    eel.GetEncoders()(function(result){
        codecs = result
        var select = document.getElementById("codec")
        select.innerHTML = ""
        codecs.forEach(function(codec){
            var option = document.createElement("option")
            option.value = codec.id
            option.text = codec.name
            select.add(option)
        })
        UpdateEncoders()
    })
}

// Fill the encoder list with the encoders of the selected codec
function UpdateEncoders(){
    var codecId = document.getElementById("codec").value
    var codec = codecs.find(function(c){ return c.id == codecId })
    var select = document.getElementById("encoder")
    select.innerHTML = ""
    if(!codec) return
    var auto = document.createElement("option")
    auto.value = "auto"
    auto.text = "Auto: " + codec.encoders[0].name
    select.add(auto)
    codec.encoders.forEach(function(encoder){
        var option = document.createElement("option")
        option.value = encoder.id
        option.text = encoder.name
        select.add(option)
    })
}

// Load the colors of the player's border, or of default.png if the player has none
function LoadBorderColors(){
    var profile = document.getElementById("profile").value
    var custom_name = document.getElementById("custom-name").value
    var selected_leaderboard = document.querySelector('input[name="leaderboard"]:checked')?.value;
    var status = document.getElementById("border-status")
    if(!profile.trim() && !custom_name.trim()){
        status.innerText = "Enter the Profile ID or the player name to load the player's border"
        return
    }
    status.innerText = "Loading the player's border..."
    eel.GetBorderColors(profile, selected_leaderboard, custom_name)(function(result){
        if(!result){
            status.innerText = "Player not found, using the colors of the default border"
            return
        }
        document.getElementById("left-color").value = result.left
        document.getElementById("right-color").value = result.right
        if(result.custom){
            status.innerText = "Loaded the border of " + result.player
        } else {
            status.innerText = result.player + " has no border yet, pick the colors and save them"
        }
        document.getElementById("custom-border").checked = !result.custom
        UpdateBorderPreview()
    })
}

function UpdateBorderPreview(){
    var left_color = document.getElementById("left-color").value
    var right_color = document.getElementById("right-color").value
    eel.PreviewBorder(left_color, right_color)(function(url){
        document.getElementById("border-preview").src = url
    })
}

function ColorChanged(){
    // Changing a color means the player wants these colors saved
    document.getElementById("custom-border").checked = true
    UpdateBorderPreview()
}

document.addEventListener("DOMContentLoaded", function(){
    LoadEncoders()
    UpdateBorderPreview()
    document.getElementById("codec").addEventListener("change", UpdateEncoders)
    document.getElementById("profile").addEventListener("change", LoadBorderColors)
    document.getElementById("custom-name").addEventListener("change", LoadBorderColors)
    document.querySelectorAll('input[name="leaderboard"]').forEach(function(radio){
        radio.addEventListener("change", LoadBorderColors)
    })
    document.getElementById("left-color").addEventListener("input", ColorChanged)
    document.getElementById("right-color").addEventListener("input", ColorChanged)
})

function copyField(id, button){
    var field = document.getElementById(id)
    navigator.clipboard.writeText(field.value).catch(function(){
        field.select()
        document.execCommand("copy")
    })
    button.innerText = "Copied!"
    setTimeout(function(){ button.innerText = "Copy" }, 1500)
}

eel.expose(DisableStartButton)
function DisableStartButton(){
    const button = document.getElementById("start")
    button.disabled = true;
}

eel.expose(EnableStartButton)
function EnableStartButton(){
    const button = document.getElementById("start")
    button.disabled = false;
}


eel.expose(print_output)
function print_output(str){
    var line = document.createElement("span")
    line.innerText = str
    var output = document.getElementById("output")
    output.appendChild(line)
    output.appendChild(document.createElement("br"))
}

eel.expose(print_clear)
function print_clear(){
    document.getElementById("output").innerHTML = ""
}

eel.expose(ShowResults)
function ShowResults(title, description){
    document.getElementById("result-title").value = title
    document.getElementById("result-description").value = description
    Show("results")
}

eel.expose(ShowThumbnail)
function ShowThumbnail(src){
    // Add a timestamp so the browser doesn't show an older thumbnail with the same name
    var url = src + "?t=" + Date.now()
    document.getElementById("thumbnail-img").src = url
    document.getElementById("thumbnail-link").href = url
    Show("thumbnail")
}

eel.expose(Show)
function Show(id){
    var Element = document.getElementById(id)
    Element.classList.add("show")
    Element.classList.remove("hidden")
}
eel.expose(Hide)
function Hide(id){
    var Element = document.getElementById(id)
    if(Element.classList.contains("show")){
        Element.classList.add("hidden")
        Element.classList.remove("show")
    }
}

eel.expose(Videos)
function Videos(src, id, file_name){
    var Video = document.getElementById(id)
    // Extract filename from src (assumed format: 'Gui/Videos/filename.mp4')
    var filename = src.split('/').pop();
    // Create new source path
    var srcFormatted = 'Videos/' + encodeURIComponent(filename) + "?t=" + Date.now();
    var poster = 'Thumbnails/' + encodeURIComponent(file_name) + '.png?t=' + Date.now();
    Video.innerHTML = '<h2>Edited Video:</h2> <video controls volume=.2 poster="' + poster + '"> <source src="' + srcFormatted + '" type="video/mp4" ></video>' +
        '<a class="button" href="' + srcFormatted + '" download="' + filename + '">Download Video</a>'
}


function uploadVideo() {
    var filepath = "Gui/Videos/final.mp4";  // Replace with the actual path to the video
    var outputText = document.getElementById("output").innerText;  // Get the entire output text
    var outputLines = outputText.split("\n");  // Split the output text into lines
    eel.upload_youtube_video(filepath);
}
