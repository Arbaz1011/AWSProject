// AWS Configuration
const API_ENDPOINT = '/api';
let currentUser = null;

// DOM Elements
const authNav = document.getElementById('auth-nav');
const userInfo = document.getElementById('user-info');
const authButtons = document.getElementById('auth-buttons');
const authForms = document.getElementById('auth-forms');
const loginForm = document.getElementById('login-form');
const signupForm = document.getElementById('signup-form');
const appointmentForm = document.getElementById('appointment-form');
const appointmentsList = document.getElementById('appointments-list');
const userEmailSpan = document.getElementById('user-email');

// Auth Form Handlers
document.getElementById('login-btn').addEventListener('click', () => {
    authForms.style.display = 'block';
    document.getElementById('login-section').style.display = 'block';
    document.getElementById('signup-section').style.display = 'none';
});

document.getElementById('signup-btn').addEventListener('click', () => {
    authForms.style.display = 'block';
    document.getElementById('login-section').style.display = 'none';
    document.getElementById('signup-section').style.display = 'block';
});

document.getElementById('logout-btn').addEventListener('click', async () => {
    try {
        await fetch(`${API_ENDPOINT}/auth/logout`, { method: 'POST' });
        currentUser = null;
        updateAuthUI();
    } catch (error) {
        showError('Logout failed. Please try again.');
    }
});

loginForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const formData = new FormData(loginForm);
    
    try {
        const response = await fetch(`${API_ENDPOINT}/auth/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                email: formData.get('email'),
                password: formData.get('password')
            })
        });

        const data = await response.json();
        if (!response.ok) {
            throw new Error(data.error || 'Login failed');
        }
        
        // Store the token in localStorage
        localStorage.setItem('token', data.token);
        currentUser = data.user;
        updateAuthUI();
        loadUserAppointments();
        showSuccess('Logged in successfully!');
    } catch (error) {
        showError(error.message || 'Login failed. Please check your credentials.');
    }
});

signupForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const formData = new FormData(signupForm);
    
    // Debug log
    console.log('Form data:', {
        email: formData.get('email'),
        password: formData.get('password')
    });
    
    if (formData.get('password') !== formData.get('confirm-password')) {
        showError('Passwords do not match');
        return;
    }

    const data = {
        email: formData.get('email'),
        password: formData.get('password')
    };

    // Debug log
    console.log('Sending data:', data);

    try {
        const response = await fetch(`${API_ENDPOINT}/auth/signup`, {
            method: 'POST',
            headers: { 
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            },
            body: JSON.stringify(data)
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || 'Signup failed');
        }
        
        showSuccess('Account created Successfully!');
        document.getElementById('login-btn').click();
    } catch (error) {
        showError(error.message || 'Signup failed. Please try again.');
    }
});

// Appointment Form Handler
appointmentForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    if (!currentUser) {
        showError('Please login to book an appointment');
        return;
    }

    const formData = new FormData(appointmentForm);
    
    try {
        // Handle image upload first if a file was selected
        let imageUrl = '';
        const imageFile = formData.get('car-image');
        if (imageFile && imageFile.size > 0) {
            imageUrl = await uploadImage(imageFile);
        }

        const appointmentData = {
            carMake: formData.get('car-make'),
            carModel: formData.get('car-model'),
            carYear: formData.get('car-year'),
            serviceType: formData.get('service-type'),
            date: formData.get('date'),
            time: formData.get('time'),
            description: formData.get('description'),
            notificationPreference: formData.get('notification-preference') === 'on',
            imageUrl: imageUrl  // Add the image URL to the appointment data
        };

        const token = localStorage.getItem('token');
        if (!token) {
            throw new Error('Please login to book an appointment');
        }

        const response = await fetch('/api/appointments', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': token
            },
            body: JSON.stringify(appointmentData)
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || 'Failed to book appointment');
        }

        showSuccess('Appointment booked successfully!');
        appointmentForm.reset();
        await loadUserAppointments();
    } catch (error) {
        showError(error.message);
    }
});

// Update the Image Upload Handler
async function uploadImage(file) {
    try {
        const token = localStorage.getItem('token');
        if (!token) {
            throw new Error('Please login to upload images');
        }

        // Get presigned URL
        const response = await fetch(`${API_ENDPOINT}/upload-url`, {
            method: 'POST',
            headers: { 
                'Content-Type': 'application/json',
                'Authorization': token
            },
            body: JSON.stringify({ 
                fileName: file.name, 
                fileType: file.type 
            })
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || 'Failed to get upload URL');
        }
        
        const { uploadUrl, imageUrl } = await response.json();

        // Upload to S3 using the presigned URL
        const uploadResponse = await fetch(uploadUrl, {
            method: 'PUT',
            body: file,
            headers: { 'Content-Type': file.type }
        });

        if (!uploadResponse.ok) {
            throw new Error('Failed to upload image');
        }

        return imageUrl;
    } catch (error) {
        console.error('Image upload error:', error);
        throw new Error('Image upload failed: ' + error.message);
    }
}

// Load User Appointments
async function loadUserAppointments() {
    if (!currentUser) return;

    try {
        const token = localStorage.getItem('token');
        if (!token) {
            throw new Error('No authentication token found');
        }

        const response = await fetch(`${API_ENDPOINT}/appointments`, {
            method: 'GET',
            headers: {
                'Authorization': token,
                'Content-Type': 'application/json'
            }
        });

        if (!response.ok) throw new Error('Failed to load appointments');

        const appointments = await response.json();
        displayAppointments(appointments);
    } catch (error) {
        showError('Failed to load appointments: ' + error.message);
    }
}

// Display Appointments
function displayAppointments(appointments) {
    const container = document.getElementById('appointments-container');
    container.innerHTML = '';

    appointments.forEach(appointment => {
        const card = document.createElement('div');
        card.className = 'appointment-card fade-in';
        card.innerHTML = `
            <h3>${appointment.serviceType}</h3>
            <p><strong>Vehicle:</strong> ${appointment.carYear} ${appointment.carMake} ${appointment.carModel}</p>
            <p><strong>Date:</strong> ${formatDate(appointment.date)}</p>
            <p><strong>Time:</strong> ${appointment.time}</p>
            <p><strong>Status:</strong> <span class="status-${appointment.status.toLowerCase()}">${appointment.status}</span></p>
            <p><strong>Description:</strong> ${appointment.description || 'No description provided'}</p>
        `;
        container.appendChild(card);
    });

    appointmentsList.style.display = appointments.length ? 'block' : 'none';
}

// UI Helpers
function updateAuthUI() {
    if (currentUser) {
        userInfo.style.display = 'block';
        authButtons.style.display = 'none';
        authForms.style.display = 'none';
        userEmailSpan.textContent = currentUser.email;
        appointmentsList.style.display = 'block';
    } else {
        userInfo.style.display = 'none';
        authButtons.style.display = 'block';
        appointmentsList.style.display = 'none';
    }
}

function showError(message) {
    const errorDiv = document.createElement('div');
    errorDiv.className = 'error fade-in';
    errorDiv.textContent = message;
    document.querySelector('main').insertBefore(errorDiv, document.querySelector('main').firstChild);
    setTimeout(() => errorDiv.remove(), 5000);
}

function showSuccess(message) {
    const successDiv = document.createElement('div');
    successDiv.className = 'success fade-in';
    successDiv.textContent = message;
    document.querySelector('main').insertBefore(successDiv, document.querySelector('main').firstChild);
    setTimeout(() => successDiv.remove(), 5000);
}

function formatDate(dateString) {
    return new Date(dateString).toLocaleDateString('en-US', {
        weekday: 'long',
        year: 'numeric',
        month: 'long',
        day: 'numeric'
    });
}

// Initialize
updateAuthUI();

