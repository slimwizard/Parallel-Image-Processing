
let uploadedImage;
const serviceUrl = "http://localhost:42658/api/request"

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




const getPrediction =()=> {
    console.log(uploadedImage.files[0])
    let form = new FormData()

    form.append("file", uploadedImage.files[0])


    if (uploadedImage){
        fetch(serviceUrl, 
            {
                method: "POST", // *GET, POST, PUT, DELETE, etc.
                mode: "no-cors", // no-cors, cors, *same-origin
                enctype: 'multipart/form-data',
                body: form,
            }).then(response => console.log(response))




    } else { console.log("error")}
}
