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

    var videoForm = document.getElementById('uploadForm');
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
                originalImg.src = `/uploads/${data.original_url}`;
                originalImg.alt = 'Original Image';
                resultSection.appendChild(originalImg);
            } else {
                var originalVideo = document.createElement('video');
                originalVideo.src = `/uploads/${data.original_url}`;
                originalVideo.controls = true;
                resultSection.appendChild(originalVideo);
            }

            var originalLink = document.createElement('a');
            originalLink.href = `/uploads/${data.original_url}`;
            originalLink.textContent = 'Download Original';
            originalLink.download = true;
            resultSection.appendChild(originalLink);
        }

        if (data.forensic_watermarked_url) {
            var forensicWatermarkedHeading = document.createElement('h2');
            forensicWatermarkedHeading.textContent = 'Forensic Watermarked File';
            resultSection.appendChild(forensicWatermarkedHeading);

            if (data.forensic_watermarked_url.endsWith('png') || data.forensic_watermarked_url.endsWith('jpg') || data.forensic_watermarked_url.endsWith('jpeg')) {
                var forensicWatermarkedImg = document.createElement('img');
                forensicWatermarkedImg.src = `/detects/${data.forensic_watermarked_url}`;
                forensicWatermarkedImg.alt = 'Forensic Watermarked Image';
                resultSection.appendChild(forensicWatermarkedImg);
            } else {
                var forensicWatermarkedVideo = document.createElement('video');
                forensicWatermarkedVideo.src = `/detects/${data.forensic_watermarked_url}`;
                forensicWatermarkedVideo.controls = true;
                resultSection.appendChild(forensicWatermarkedVideo);
            }

            var forensicWatermarkedLink = document.createElement('a');
            forensicWatermarkedLink.href = `/detects/${data.forensic_watermarked_url}`;
            forensicWatermarkedLink.textContent = 'Download Forensic Watermarked';
            forensicWatermarkedLink.download = true;
            resultSection.appendChild(forensicWatermarkedLink);
        }

        if (data.forensic_highlight_url) {
            var forensicHighlightHeading = document.createElement('h2');
            forensicHighlightHeading.textContent = 'Forensic Highlight File';
            resultSection.appendChild(forensicHighlightHeading);

            if (data.forensic_highlight_url.endsWith('png') || data.forensic_highlight_url.endsWith('jpg') || data.forensic_highlight_url.endsWith('jpeg')) {
                var forensicHighlightImg = document.createElement('img');
                forensicHighlightImg.src = `/detects/${data.forensic_highlight_url}`;
                forensicHighlightImg.alt = 'Forensic Highlight Image';
                resultSection.appendChild(forensicHighlightImg);
            } else {
                var forensicHighlightVideo = document.createElement('video');
                forensicHighlightVideo.src = `/detects/${data.forensic_highlight_url}`;
                forensicHighlightVideo.controls = true;
                resultSection.appendChild(forensicHighlightVideo);
            }

            var forensicHighlightLink = document.createElement('a');
            forensicHighlightLink.href = `/detects/${data.forensic_highlight_url}`;
            forensicHighlightLink.textContent = 'Download Forensic Highlight';
            forensicHighlightLink.download = true;
            resultSection.appendChild(forensicHighlightLink);
        }

        if (data.extracted_url) {
            var extractedHeading = document.createElement('h2');
            extractedHeading.textContent = 'Extracted Watermark File';
            resultSection.appendChild(extractedHeading);

            if (data.extracted_url.endsWith('png') || data.extracted_url.endsWith('jpg') || data.extracted_url.endsWith('jpeg')) {
                var extractedImg = document.createElement('img');
                extractedImg.src = `/extracts/${data.extracted_url}`;
                extractedImg.alt = 'Extracted Watermark Image';
                resultSection.appendChild(extractedImg);
            } else {
                var extractedVideo = document.createElement('video');
                extractedVideo.src = `/extracts/${data.extracted_url}`;
                extractedVideo.controls = true;
                resultSection.appendChild(extractedVideo);
            }

            var extractedLink = document.createElement('a');
            extractedLink.href = `/extracts/${data.extracted_url}`;
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
