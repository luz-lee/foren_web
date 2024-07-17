function switchLanguage(lang) {
    document.documentElement.lang = lang;
    if (lang === 'ko') {
        document.getElementById('title').innerText = '워터마킹 애플리케이션';
        document.getElementById('dragDropTextImage').innerText = '여기에 이미지 파일을 드롭하세요';
        document.getElementById('submit').value = '업로드';
    } else {
        document.getElementById('title').innerText = 'Watermark Application';
        document.getElementById('dragDropTextImage').innerText = 'Drag & Drop your image here';
        document.getElementById('submit').value = 'Upload';
    }
}

document.addEventListener('DOMContentLoaded', function() {
    var imageDropArea = document.getElementById('image-drop-area');

    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
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

        if (file.type.startsWith('image/')) {
            var img = document.createElement('img');
            img.id = previewId;
            img.src = URL.createObjectURL(file);
            img.style.maxWidth = '100%';
            img.style.height = 'auto';
            dropArea.appendChild(img);
        }
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

            var originalImg = document.createElement('img');
            originalImg.src = data.original_url;
            originalImg.alt = 'Original Image';
            resultSection.appendChild(originalImg);

            var originalLink = document.createElement('a');
            originalLink.href = data.original_url;
            originalLink.textContent = 'Download Original';
            originalLink.download = true;
            resultSection.appendChild(originalLink);
        }

        if (data.forensic_watermarked_url) {
            var forensicWatermarkedHeading = document.createElement('h2');
            forensicWatermarkedHeading.textContent = 'Forensic Watermarked File';
            resultSection.appendChild(forensicWatermarkedHeading);

            var forensicWatermarkedImg = document.createElement('img');
            forensicWatermarkedImg.src = data.forensic_watermarked_url;
            forensicWatermarkedImg.alt = 'Forensic Watermarked Image';
            resultSection.appendChild(forensicWatermarkedImg);

            var forensicWatermarkedLink = document.createElement('a');
            forensicWatermarkedLink.href = data.forensic_watermarked_url;
            forensicWatermarkedLink.textContent = 'Download Forensic Watermarked';
            forensicWatermarkedLink.download = true;
            resultSection.appendChild(forensicWatermarkedLink);
        }

        if (data.forensic_highlight_url) {
            var forensicHighlightHeading = document.createElement('h2');
            forensicHighlightHeading.textContent = 'Forensic Highlight File';
            resultSection.appendChild(forensicHighlightHeading);

            var forensicHighlightImg = document.createElement('img');
            forensicHighlightImg.src = data.forensic_highlight_url;
            forensicHighlightImg.alt = 'Forensic Highlight Image';
            resultSection.appendChild(forensicHighlightImg);

            var forensicHighlightLink = document.createElement('a');
            forensicHighlightLink.href = data.forensic_highlight_url;
            forensicHighlightLink.textContent = 'Download Forensic Highlight';
            forensicHighlightLink.download = true;
            resultSection.appendChild(forensicHighlightLink);
        }
    }
});
