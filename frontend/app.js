const API_URL = 'https://your-render-api-url.onrender.com';

async function fetchLeaderboard() {
    const response = await fetch(`${API_URL}/api/leaderboard`);
    const leaderboard = await response.json();
    const leaderboardBody = document.getElementById('leaderboard-body');
    leaderboardBody.innerHTML = '';
    leaderboard.forEach((athlete, index) => {
        const row = `
            <tr>
                <td>${index + 1}</td>
                <td>${athlete.firstname} ${athlete.lastname}</td>
                <td>${(athlete.total_distance / 1000).toFixed(2)}</td>
            </tr>
        `;
        leaderboardBody.innerHTML += row;
    });
}

async function authorize() {
    const response = await fetch(`${API_URL}/api/authorize`);
    const data = await response.json();
    window.location.href = data.auth_url;
}

// Check if we're on the callback page
if (window.location.pathname === '/callback') {
    const urlParams = new URLSearchParams(window.location.search);
    const code = urlParams.get('code');
    const scope = urlParams.get('scope');
    
    if (code && scope) {
        fetch(`${API_URL}/api/callback?code=${code}&scope=${scope}`)
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    window.location.href = '/';
                } else {
                    alert('Authorization failed. Please try again.');
                }
            });
    }
}

// Fetch leaderboard on page load
fetchLeaderboard();