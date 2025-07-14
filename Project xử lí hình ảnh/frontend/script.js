const backendUrl = 'http://localhost:5000';

function getImageFile() {
    const input = document.getElementById('imageInput');
    if (!input.files.length) {
        alert('Vui lòng chọn ảnh!');
        return null;
    }
    return input.files[0];
}

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
    const downloadBtn = document.getElementById('downloadBtn');
    downloadBtn.href = url;
    downloadBtn.style.display = 'inline-block';
}

function removeBg() {
    const file = getImageFile();
    if (!file) return;
    const formData = new FormData();
    formData.append('image', file);
    fetch(backendUrl + '/remove-bg', {
        method: 'POST',
        body: formData
    })
    .then(res => res.blob())
    .then(blob => {
        setDownloadLink(blob);
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
    });
}
function registerUser() {
    const name = document.querySelector('.sign-up input[placeholder="Name"]').value;
    const email = document.querySelector('.sign-up input[placeholder="Email"]').value;
    const password = document.querySelector('.sign-up input[placeholder="Password"]').value;
    fetch('http://localhost:5000/register', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({name, email, password})
    })
    .then(res => res.json())
    .then(data => alert(data.msg));
}
function loginUser() {
    const email = document.querySelector('.sign-in input[placeholder="Email"]').value;
    const password = document.querySelector('.sign-in input[placeholder="Password"]').value;
    fetch('http://localhost:5000/login', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({email, password})
    })
    .then(res => res.json())
    .then(data => {
        if (data.access_token) {
            localStorage.setItem('token', data.access_token);
            document.body.classList.add('logged-in');
        } else {
            alert('Sai tài khoản hoặc mật khẩu!');
        }
    });
}
// Thêm logic chuyển đổi giao diện login/register
const container = document.getElementById('container');
const registerBtn = document.getElementById('register');
const loginBtn = document.getElementById('login');

if (registerBtn && loginBtn && container) {
    registerBtn.addEventListener('click', () => {
        container.classList.add("active");
    });
    loginBtn.addEventListener('click', () => {
        container.classList.remove("active");
    });
}

// Gắn sự kiện cho nút đăng ký và đăng nhập
// Đảm bảo form không reload trang khi submit

document.querySelectorAll('.sign-up form').forEach(form => {
    form.addEventListener('submit', function(e) {
        e.preventDefault();
        registerUser();
    });
});
document.querySelectorAll('.sign-in form').forEach(form => {
    form.addEventListener('submit', function(e) {
        e.preventDefault();
        loginUser();
    });
});
