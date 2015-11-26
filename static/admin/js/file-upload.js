'use strict';

var fileUpload = {

    init: function init() {
        // Bind to all file inputs.
        var fileElements = document.querySelectorAll('[type="file"]');
        for (var i = fileElements.length - 1; i >= 0; i--) {
            fileElements[i].addEventListener('change', fileUpload.fileElmOnChange);
        };
    },

    fileElmOnChange: function fileElmOnChange(e) {
        // Start the upload of file.
        fileUpload.uploadFile(e.target);
    },

    uploadFile: function uploadFile(fileElm) {
        // Create form data object and add the files to it.
        var fd = new FormData();
        for (var i = fileElm.files.length - 1; i >= 0; i--) {
            fd.append('file_' + String(i), fileElm.files[i]);
        };
        // Make a request to backend with the URL given in the file element action-attribute.
        var request = new XMLHttpRequest();
        request.open("POST", fileElm.getAttribute('data-action'));
        request.addEventListener('load', fileUpload.uploadComplete.bind(fileElm));
        request.addEventListener('error', fileUpload.uploadError);
        request.send(fd);
    },

    uploadComplete: function uploadComplete(e) {
        console.log(e, this);
        // this is fileElement
        try {
            // Yolo json parse.
            var fileKeys = JSON.parse(e.target.response).data.files;
            // Put the keys in a input field that is given by the file element attribute.
            var keyInputId = this.getAttribute('data-key-input-id');
            var keyInputElm = document.getElementById(keyInputId);
            keyInputElm.value = fileKeys.toString();

        } catch(e) {
            console.log('Something went wrong when parsing response for file upload', e);
            return;
        }
    },

    uploadError: function uploadError(e) {
        console.log('Upload failed', e);
    }
}
window.fileUpload = fileUpload;
window.fileUpload.init();
