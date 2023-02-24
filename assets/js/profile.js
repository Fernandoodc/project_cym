const $file = document.querySelector("#inputProfile");
$file.addEventListener("change", (event) => {
    const selectedfile = event.target.files;
    if (selectedfile.length > 0) {
        const [imageFile] = selectedfile;
        const fileReader = new FileReader();
        fileReader.onload = () => {
            const srcData = fileReader.result;
            $('#profileImg').attr('src', srcData);
        };
        fileReader.readAsDataURL(imageFile);
    }
});