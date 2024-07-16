function switchLanguage(lang) {
    document.documentElement.lang = lang;
    if (lang === 'ko') {
        document.getElementById('title').innerText = '워터마킹 애플리케이션';
        document.getElementById('dragDropTextVideo').innerText = '여기에 비디오 파일을 드롭하세요';
        document.getElementById('dragDropTextImage').innerText = '여기에 이미지 파일을 드롭하세요';
        document.getElementById('submit').value = '업로드';
    } else {
        document.getElementById('title').innerText = 'Watermark Application';
        document.getElementById('dragDropTextVideo').innerText = 'Drag & Drop your video here';
        document.getElementById('dragDropTextImage').innerText = 'Drag & Drop your image here';
        document.getElementById('submit').value = 'Upload';
    }
}

document.addEventListener('DOMContentLoaded', function() {
    var videoDropArea = document.getElementById('video-drop-area');
    var imageDropArea = document.getElementById('image-drop-area');

    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }

    if (videoDropArea) {
        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            videoDropArea.addEventListener(eventName, preventDefaults, false);
        });

        videoDropArea.addEventListener('click', function(event) {
            if (event.target.tagName.toLowerCase() !== 'video') {
                document.getElementById('video_file').click();
            }
        });

        document.getElementById('video_file').addEventListener('change', function(e) {
            var file = this.files[0];
            updatePreview(file, 'video-preview', 'video-drop-area');
        });
    }

    if (imageDropArea) {
        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            imageDropArea.addEventListener(eventName, preventDefaults, false);
        });

        imageDropArea.addEventListener('click', function(event) {
            document.getElementById('image_file').click();
        });

        document.getElementById('image_file').addEventListener('change', function(e) {
            var file = this.files[0];
            updatePreview(file, 'image-preview', 'image-drop-area');
        });
    }

    function updatePreview(file, previewId, dropAreaId) {
        var preview = document.getElementById(previewId);
        var dropArea = document.getElementById(dropAreaId);

        if (preview) {
            preview.remove();
        }

        if (file.type.startsWith('video/')) {
            var video = document.createElement('video');
            video.id = previewId;
            video.src = URL.createObjectURL(file);
            video.controls = true;
            video.style.maxWidth = '100%';
            video.style.height = 'auto';
            dropArea.appendChild(video);
        } else if (file.type.startsWith('image/')) {
            var img = document.createElement('img');
            img.id = previewId;
            img.src = URL.createObjectURL(file);
            img.style.maxWidth = '100%';
            img.style.height = 'auto';
            dropArea.appendChild(img);
        }
    }

    var videoForm = document.getElementById('uploadVideoForm');
    if (videoForm) {
        videoForm.addEventListener('submit', function(event) {
            event.preventDefault();

            var formData = new FormData(this);
            fetch('/upload', {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                displayResults(data);
            })
            .catch(error => {
                console.error('Error:', error);
            });
        });
    }

    var imageForm = document.getElementById('uploadImageForm');
    if (imageForm) {
        imageForm.addEventListener('submit', function(event) {
            event.preventDefault();

            var formData = new FormData(this);
            fetch('/upload', {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                displayResults(data);
            })
            .catch(error => {
                console.error('Error:', error);
            });
        });
    }

    function displayResults(data) {
        var resultSection = document.getElementById('result');
        resultSection.innerHTML = '';

        if (data.original_url) {
            var originalHeading = document.createElement('h2');
            originalHeading.textContent = 'Original File';
            resultSection.appendChild(originalHeading);

            if (data.original_url.endsWith('png') || data.original_url.endsWith('jpg') || data.original_url.endsWith('jpeg')) {
                var originalImg = document.createElement('img');
                originalImg.src = data.original_url;
                originalImg.alt = 'Original Image';
                resultSection.appendChild(originalImg);
            } else {
                var originalVideo = document.createElement('video');
                originalVideo.src = data.original_url;
                originalVideo.controls = true;
                resultSection.appendChild(originalVideo);
            }

            var originalLink = document.createElement('a');
            originalLink.href = data.original_url;
            originalLink.textContent = 'Download Original';
            originalLink.download = true;
            resultSection.appendChild(originalLink);
        }

        if (data.watermarked_url) {
            var watermarkedHeading = document.createElement('h2');
            watermarkedHeading.textContent = 'Watermarked File';
            resultSection.appendChild(watermarkedHeading);

            if (data.watermarked_url.endsWith('png') || data.watermarked_url.endsWith('jpg') || data.watermarked_url.endsWith('jpeg')) {
                var watermarkedImg = document.createElement('img');
                watermarkedImg.src = data.watermarked_url;
                watermarkedImg.alt = 'Watermarked Image';
                resultSection.appendChild(watermarkedImg);
            } else {
                var watermarkedVideo = document.createElement('video');
                watermarkedVideo.src = data.watermarked_url;
                watermarkedVideo.controls = true;
                resultSection.appendChild(watermarkedVideo);
            }

            var watermarkedLink = document.createElement('a');
            watermarkedLink.href = data.watermarked_url;
            watermarkedLink.textContent = 'Download Watermarked';
            watermarkedLink.download = true;
            resultSection.appendChild(watermarkedLink);
        }

        if (data.highlighted_url) {
            var highlightedHeading = document.createElement('h2');
            highlightedHeading.textContent = 'Highlighted Watermark File';
            resultSection.appendChild(highlightedHeading);

            if (data.highlighted_url.endsWith('png') || data.highlighted_url.endsWith('jpg') || data.highlighted_url.endsWith('jpeg')) {
                var highlightedImg = document.createElement('img');
                highlightedImg.src = data.highlighted_url;
                highlightedImg.alt = 'Highlighted Watermark Image';
                resultSection.appendChild(highlightedImg);
            } else {
                var highlightedVideo = document.createElement('video');
                highlightedVideo.src = data.highlighted_url;
                highlightedVideo.controls = true;
                resultSection.appendChild(highlightedVideo);
            }

            var highlightedLink = document.createElement('a');
            highlightedLink.href = data.highlighted_url;
            highlightedLink.textContent = 'Download Highlighted';
            highlightedLink.download = true;
            resultSection.appendChild(highlightedLink);
        }

        if (data.extracted_url) {
            var extractedHeading = document.createElement('h2');
            extractedHeading.textContent = 'Extracted Watermark File';
            resultSection.appendChild(extractedHeading);

            if (data.extracted_url.endsWith('png') || data.extracted_url.endsWith('jpg') || data.extracted_url.endsWith('jpeg')) {
                var extractedImg = document.createElement('img');
                extractedImg.src = data.extracted_url;
                extractedImg.alt = 'Extracted Watermark Image';
                resultSection.appendChild(extractedImg);
            } else {
                var extractedVideo = document.createElement('video');
                extractedVideo.src = data.extracted_url;
                extractedVideo.controls = true;
                resultSection.appendChild(extractedVideo);
            }

            var extractedLink = document.createElement('a');
            extractedLink.href = data.extracted_url;
            extractedLink.textContent = 'Download Extracted Watermark';
            extractedLink.download = true;
            resultSection.appendChild(extractedLink);
        }

        if (data.watermark_positions) {
            var positionsHeading = document.createElement('h2');
            positionsHeading.textContent = 'Watermark Positions';
            resultSection.appendChild(positionsHeading);

            var positionsList = document.createElement('ul');
            data.watermark_positions.forEach(position => {
                var positionItem = document.createElement('li');
                positionItem.textContent = `x: ${position[0]}, y: ${position[1]}, width: ${position[2]}, height: ${position[3]}`;
                positionsList.appendChild(positionItem);
            });
            resultSection.appendChild(positionsList);
        }
    }
});
