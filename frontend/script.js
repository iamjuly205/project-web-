const backendUrl = 'http://localhost:5000';

function setLoading(on) {
    const el = document.getElementById('loadingOverlay');
    if (!el) return;
    el.style.display = on ? 'flex' : 'none';
}

function getImageFile() {
    const input = document.getElementById('imageInput');
    if (!input.files.length) {
        alert('Vui lòng chọn ảnh!');
        return null;
    }
    return input.files[0];
}

// Show preview when user selects a file
document.getElementById('imageInput').addEventListener('change', function(e){
    const file = this.files && this.files[0];
    const preview = document.getElementById('previewImg');
    if (!file) { preview.src = ''; preview.style.display = 'none'; return; }
    const url = URL.createObjectURL(file);
    preview.src = url;
    preview.style.display = 'block';
});

function showResize() {
    document.getElementById('resizeForm').style.display = 'block';
    document.getElementById('cropForm').style.display = 'none';
}

function showCrop() {
    document.getElementById('resizeForm').style.display = 'none';
    document.getElementById('cropForm').style.display = 'block';
}

function setDownloadLink(blob) {
    const url = URL.createObjectURL(blob);
    const img = document.getElementById('resultImg');
    img.src = url;
    img.style.display = 'block';
    const downloadBtn = document.getElementById('downloadBtn');
    downloadBtn.href = url;
    downloadBtn.style.display = 'inline-flex';
}

function removeBg() {
    const file = getImageFile();
    if (!file) return;
    const formData = new FormData();
    formData.append('image', file);
    setLoading(true);
    fetch(backendUrl + '/remove-bg', {
        method: 'POST',
        body: formData
    })
    .then(res => res.blob())
    .then(blob => {
        setDownloadLink(blob);
        setLoading(false);
    });
}

function resizeImage() {
    const file = getImageFile();
    if (!file) return;
    const width = document.getElementById('resizeWidth').value;
    const height = document.getElementById('resizeHeight').value;
    if (!width || !height) { alert('Nhập width và height!'); return; }
    const formData = new FormData();
    formData.append('image', file);
    formData.append('width', width);
    formData.append('height', height);
    fetch(backendUrl + '/resize', {
        method: 'POST',
        body: formData
    })
    .then(res => res.blob())
    .then(blob => {
        setDownloadLink(blob);
        setLoading(false);
    });
}

function cropImage() {
    const file = getImageFile();
    if (!file) return;
    const ratio = document.getElementById('cropRatio').value;
    const formData = new FormData();
    formData.append('image', file);
    formData.append('ratio', ratio);
    fetch(backendUrl + '/crop', {
        method: 'POST',
        body: formData
    })
    .then(res => res.blob())
    .then(blob => {
        setDownloadLink(blob);
        setLoading(false);
    });
}
// Login/register removed — this script now only handles image processing features
