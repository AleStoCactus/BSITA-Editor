function send(){
    Show("title")
    var gdrive = document.getElementById("gdrive").value
    var leaderboard_id = document.getElementById("leaderboard_id").value
    var profile = document.getElementById("profile").value
    var score = document.getElementById("score").value
    var desc_notes = document.getElementById("desc-notes").value
    var selected_leaderboard = document.querySelector('input[name="leaderboard"]:checked')?.value;
    eel.Generate(leaderboard_id, profile, score, gdrive, desc_notes, selected_leaderboard)
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
    document.getElementById("output").innerHTML += (str + "<br>")
    eel.Transcript(str)
}

eel.expose(print_imageprw)
function print_imageprw(url){
    document.getElementById("preview").innerHTML += ('Thumbnail Preview:<br><br><img src="' + url + '" width="240" height="135"" alt="thumb"><br>')
}

eel.expose(print_clear)
function print_clear(){
    document.getElementById("output").innerHTML = ""
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
function Videos(src, id, player, bsr){
    var Video = document.getElementById(id)
    // Extract filename from src (assumed format: 'Gui/Videos/filename.mp4')
    var filename = src.split('/').pop();
    // Create new source path
    var srcFormatted = 'Videos/' + filename;
    Video.innerHTML = '<h2>Edited Video:</h2> <video controls volume=.2 poster="Thumbnails/'+ player + '_'+ bsr +'.png"> <source src="' + srcFormatted + '" type="video/mp4" ></video>'
}


function uploadVideo() {
    var filepath = "Gui/Videos/final.mp4";  // Replace with the actual path to the video
    var outputText = document.getElementById("output").innerText;  // Get the entire output text
    var outputLines = outputText.split("\n");  // Split the output text into lines
    eel.upload_youtube_video(filepath);
}
