document.addEventListener('DOMContentLoaded', () => {
    const banner = document.getElementById('cookie-banner');
    const acceptBtn = document.getElementById('accept-cookies');
    if (!localStorage.getItem('cookies_accepted')) {
        banner.classList.remove('d-none');
    }
    acceptBtn.addEventListener('click', () => {
        localStorage.setItem('cookies_accepted', 'true');
        banner.classList.add('d-none');
    });
});
