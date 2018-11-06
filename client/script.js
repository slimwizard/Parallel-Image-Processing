let uploadedImage;
const serviceUrl = "http://localhost:5000/upload"

const button = document.getElementById('submit')

const readImage = (input) => {
    if (input.files && input.files[0]) {
        var reader = new FileReader();
        reader.onload = function (e) {
            const image = document.getElementById('uploaded-image')
            image.src = e.target.result
            image.height = 200
            image.width = 300
        };
        reader.readAsDataURL(input.files[0]);
        uploadedImage = input;
    }
}

// handleResponse will handle response(duh) from server and create DOM elements
// to display prediction and possibly other relevant data.
const handleResponse = (response) => {
    var probability_text = document.getElementById("probabilities");
    console.log(response);
    probability_text.innerHTML = response.key;
    button.value = "SUBMIT"
}

const sendImage = (form) => {
	button.value = "SENDING..."

    	fetch(serviceUrl, {
            method: "POST",
            enctype: 'multipart/form-data',
            body: form,
        }).then(response => response.json()).then(data=>{ handleResponse(data) })
}

const getPrediction = () => {
    if (uploadedImage){
        let form = new FormData()
        form.append("file", uploadedImage.files[0])
        sendImage(form)
    } else { console.log("no image uploaded")}
}
