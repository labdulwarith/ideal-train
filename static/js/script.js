document.addEventListener('DOMContentLoaded', function () {
    const isLoggedIn = ; // Change this based on actual authentication state
    const authButtons = document.querySelector('.auth-buttons');

    if (isLoggedIn) {
        authButtons.innerHTML = `
            <a href="{% url 'user-profile' user.id %}">Profile</a>
            <a href="{% url 'logout' %}">Logout</a>
        `;
    } else {
        authButtons.innerHTML = `
            <a href="{% url 'login' %}">Login</a>
            <a href="{% url 'register' %}">Register</a>
        `;
    }
});
