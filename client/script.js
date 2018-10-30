let uploadedImage;
const serviceUrl = "http://localhost:5000/upload"

// TODO: return data from Request server and display prediction underneath picture.

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
    return true
}

const sendImage = (form) => {
    fetch(serviceUrl, {
            method: "POST",
            mode: "no-cors",
            enctype: 'multipart/form-data',
            body: form,
        }).then(response => handleResponse(response))
}

const getPrediction = () => {
    if (uploadedImage){
        let form = new FormData()
        form.append("file", uploadedImage.files[0])
        sendImage(form)
    } else { console.log("no image uploaded")}
}
