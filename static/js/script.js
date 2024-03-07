var fileList = [];
const url = './';
const xhttp = new XMLHttpRequest();

var model = 'optical_flow';
let current_view = 'demo';

function choose_model(value) {
    model = document.getElementById("input_model").value;
}

//
// function reload(value) {
//     let right = document.getElementById('btn-right');
//     let left = document.getElementById('btn-left');
//     let button = document.getElementById('upload');
//     let check_view = document.getElementById('check_videos');
//     current_view = value;
//     if (current_view === 'demo') {
//         right.classList.add('btn-active');
//         right.classList.remove('btn-unactive');
//         left.classList.add('btn-unactive');
//         left.classList.remove('btn-active');
//         button.innerText = 'Check';
//     } else if (current_view === 'videos') {
//         let load_videos = document.getElementById('load_videos');
//         let load_results = document.getElementById('load_results');
//         left.classList.add('btn-active');
//         left.classList.remove('btn-unactive');
//         right.classList.add('btn-unactive');
//         right.classList.remove('btn-active');
//     }
//     checkFromServer();
// }


// Works fine
function deleteFromServer(id) {
    let r = confirm("Are you sure? There is no way o recover it!");
    if (r == true) {
        let value = document.getElementById(id).getAttribute("name");
        xhttp.open('GET', `${url}/delete?name=${value}&time=${Date.now()}`, true);
        xhttp.onreadystatechange = function () {
            if (this.readyState == 4 && this.status == 200) {
                checkFromServer();
            }
        };
        xhttp.setRequestHeader('Cache-Control', 'no-cache');
        xhttp.send();
    }
}

// Works fine
function downloadImg(name) {
    if (model === 'optical_flow') {
        let urlNew = `${url}/download?name=${name}&time=${Date.now()}`;
        document.getElementById('iframe').src = urlNew;
    } else {
        let urlNew = `${url}/download?name=${name}&ed=true&time=${Date.now()}`;
        document.getElementById('iframe').src = urlNew;
    }
}


var current_page = 1;
var record_per_page = 5;
var objJson = [];
var objJsonCheck = [];
var valname = "";

function prevPage() {
    if (current_page > 1) {
        current_page--;
        changePage(current_page);
    }
}

function nextPage() {
    if (current_page < numPages()) {
        current_page++;
        changePage(current_page);
    }
}

function changePage(page) {
    var btn_next = document.getElementById('btn_next');
    var btn_prev = document.getElementById('btn_prev');
    var page_span = document.getElementById('page_span');
    var listing_table = document.getElementById('modal-body-id');
    var val = "";
    if (page < 1) page = 1;
    if (page > numPages()) page = numPages();

    listing_table.innerHTML = "";
    if (current_view === 'demo') {
        for (var i = (page - 1) * record_per_page; i < (page * record_per_page) && i < objJson.length; i++) {
            val = objJson[i].substring(objJson[i].lastIndexOf("/") + 1,);
            listing_table.innerHTML += `<div class="general col-lm-4">
                                            <p class="img-title">${val}</p>
                                            <div style="width: 330px; height: 240px">
                                                <video width="320" height="240" controls>
                                                    <source src="${url}/thumb?name=${objJson[i]}&time=${Date.now()}" type="video/mp4">
                                                    Your browser does not support the video tag.
                                                </video>
                                            </div>    
                                        </div>`;
        }
    }

    page_span.innerHTML = page + "/" + numPages();


    if (page == 1) {
        btn_prev.style.visibility = "hidden";
    } else {
        btn_prev.style.visibility = "visible";
    }

    if (page == numPages()) {
        btn_next.style.visibility = "hidden";
    } else {
        btn_next.style.visibility = "visible";
    }
}

function numPages() {
    return Math.ceil(objJson.length / record_per_page);
}

// 
function preview(name) {
    var modal = document.getElementById('myModal');
    modal.style.display = "block";
    var span = document.getElementsByClassName('close')[0];
    span.onclick = function () {
        changePage(1);
        modal.style.display = "none";
    }
    window.onclick = function (event) {
        if (event.target == modal) {
            modal.style.display = "none";
        }
    }
    xhttp.open('GET', `${url}/getList?name=${name}&time=${Date.now()}`, true);

    xhttp.onreadystatechange = function () {
        if (this.readyState == 4 && this.status == 200) {
            let thumbs = JSON.parse(this.responseText);
            objJson = thumbs;
            valname = name;
            changePage(1);
            current_page = 1;
        }
    }
    xhttp.setRequestHeader('Cache-Control', 'no-cache');
    xhttp.send();
}


function isIterable(obj) {
    // checks for null and undefined
    if (obj == null) {
        return false;
    }
    return typeof obj[Symbol.iterator] === 'function';
}


// Works fine
function checkFromServer() {
    xhttp.open('GET', `${url}/check?time=${Date.now()}`, true);
    xhttp.onreadystatechange = function () {
        if (this.readyState == 4 && this.status == 200) {
            document.getElementById("table-body").innerHTML = "";
            let zips = JSON.parse(this.responseText);
            let i = 0;
            if (isIterable(zips)) {
                for (zip of zips) {
                    i++;
                    document.getElementById('table-body').innerHTML +=
                        `<tr>
                            <th class="text-center" scope="row">${i}</th>
                            <td class="text-center">${zip[0]}</td>
                            <td class="text-center">${formatBytes(zip[1])}</td>
                            <td class="text-center"><a class="btn-to-disable" name="${zip[0]}" onclick="downloadImg(this.name)" alt="Download" download target="_blank"><i class="fas fa-download red-text"></i></a></td>
                            <td class="text-center"><a class="btn-to-disable" id="preview-${i}" name="${zip[0]}" onclick="preview(this.name)" alt="Preview"><i class="fas fa-external-link-alt red-text"></i></a></td>
                            <td class="text-center"><a class="btn-to-disable" id="${i}" name="${zip[0]}" onclick="deleteFromServer(this.id)" alt="Delete"><i class="fas fa-trash-alt red-text"></i></a></td>
                        </tr>`;
                }
            }
        }
    };
    xhttp.setRequestHeader('Cache-Control', 'no-cache');
    xhttp.send();
}


function emptyArray() {
    let files = document.getElementById("file-list");
    files.value = "";
    onChange([]);
}

function updateUI(list) {
    if (list.length == 0) {
        document.getElementById('inner-btn').innerHTML = ``;
        document.getElementById('inner-txt').innerHTML = `
            <img src="/static/./img/upload.png" alt="upload">
            <h5 class="gray mt40">Drag here some files</h5>
            <h5 class="gray">or</h5>
            <h5 class="gray">click to upload</h5>
        `;
    } else {
        document.getElementById('inner-txt').innerHTML = `
            <h5 class="gray">You loaded ${list.length} files</h5>
            <br>
            <h5 class="gray">Click here to upload more videos</h5>
            <h5 class="gray">otherwise</h5>
            <h5 class="gray">click the action button</h5>
            `;
        document.getElementById('inner-btn').innerHTML = `<a onclick="emptyArray()" ><i class="fas fa-times-circle" style="color:#9a9a9a;"></i></a>`;

    }
}


function formatBytes(bytes) {
    if (bytes < 1024) return bytes + " Bytes";
    else if (bytes < 1048576) return (bytes / 1024).toFixed(2) + " KB";
    else if (bytes < 1073741824) return (bytes / 1048576).toFixed(2) + " MB";
    else return (bytes / 1073741824).toFixed(2) + " GB";
}


// Works fine
function uploadServer(formData, callback) {
    $('#file-list').attr('disabled', 'disabled');
    $('#upload').attr('disabled', 'disabled');
    $('.btn-to-disable').addClass('disabled');
    $('#load').show();

    if (model === 'optical_flow') {
        xhttp.open('POST', `${url}/upload-optical_flow?time=${Date.now()}`, true);
    } else if (model === 'deepfake') {
        xhttp.open('POST', `${url}/upload-deepfake?time=${Date.now()}`, true);
    } else if (model === 'face2face') {
        xhttp.open('POST', `${url}/upload-face2face?time=${Date.now()}`, true);
    } else if (model === 'faceswap') {
        xhttp.open('POST', `${url}/upload-faceswap?time=${Date.now()}`, true);
    } else if (model === 'neuraltextures') {
        xhttp.open('POST', `${url}/upload-neuraltextures?time=${Date.now()}`, true);
    } else if (model === 'rgb') {
        xhttp.open('POST', `${url}/upload-rgb?time=${Date.now()}`, true);
    } else if (model === 'deepfake_rgb') {
        xhttp.open('POST', `${url}/upload-deepfake_rgb?time=${Date.now()}`, true);
    } else if (model === 'face2face_rgb') {
        xhttp.open('POST', `${url}/upload-face2face_rgb?time=${Date.now()}`, true);
    } else if (model === 'faceswap_rgb') {
        xhttp.open('POST', `${url}/upload-faceswap_rgb?time=${Date.now()}`, true);
    } else {
        //(model === 'neuraltextures_rgb')
        xhttp.open('POST', `${url}/upload-neuraltextures_rgb?time=${Date.now()}`, true);
    }

    xhttp.onreadystatechange = function () {
        if (this.readyState == 4 && this.status == 200) {
            callback()
        }
        $('#load').hide();
        $('#upload').removeAttr('disabled');
        $('#file-list').removeAttr('disabled');
        $('.btn-to-disable').removeClass('disabled');
    };
    xhttp.setRequestHeader('Cache-Control', 'no-cache');
    xhttp.send(formData);
}

function onChange(files) {
    let fileInput = document.getElementById("file-list");
    if (files.length === 0) {
        fileList = [];
        updateUI(files);
    } else {
        for (file of Array.from(fileInput.files)) {
            fileList.push(file);
        }
        updateUI(fileList);
    }
}

$(document).ready(function () {
    let fileInput = document.getElementById("file-list");
    let dropArea = document.getElementById('drop-area');
    const url = 'http://localhost:5000';
    const xhttp = new XMLHttpRequest();
    checkFromServer()
    $('#load').hide();
    fileInput.addEventListener('change', onChange);

    ;['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        dropArea.addEventListener(eventName, preventDefaults, false)
    })

    function preventDefaults(e) {
        e.preventDefault()
        e.stopPropagation()
    }
    ;['dragenter', 'dragover'].forEach(eventName => {
        dropArea.addEventListener(eventName, highlight, false)
    })

    ;['dragleave', 'drop'].forEach(eventName => {
        dropArea.addEventListener(eventName, unhighlight, false)
    })

    function highlight(e) {
        dropArea.classList.add('highlight')
    }

    function unhighlight(e) {
        dropArea.classList.remove('highlight')
    }

    dropArea.addEventListener('drop', handleDrop, false)

    function handleDrop(e) {
        let dt = e.dataTransfer
        fileInput.files = dt.files;
        onChange(fileInput.files);
    }

    $("#upload").click(function () {
        if (fileList.length == 0) {
            alert("Select a video!");
        } else {
            let classes = ['optical_flow', 'deepfake', 'face2face', 'faceswap', 'neuraltextures',]
            let name = prompt("How do you want to name the folder?")
            if (name === null || name === "") {
                alert("Insert a valid name");
            } else if (classes.includes(model) && fileList.length % 2 != 0) {
                alert("For Optical Flow models you should upload the flow video with its RGB counterpart! Flow videos should be renaimed as 'flow_videos_XXXX' and RGB videos should be renaimed as 'videos_XXXX'");
            } else {
                const formData = new FormData();
                formData.append('name', name);
                if (fileList.length != 0) {
                    for (video of fileList) {
                        formData.append('videos[]', video);
                    }
                    uploadServer(formData, checkFromServer);
                }
            }
        }
    })
});
