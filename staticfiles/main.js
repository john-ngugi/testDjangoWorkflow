// Select the form and button elements
const form = document.getElementById('send-layer-info');
const submitButton = document.getElementById('get-layer-btn');
const mapDiv = document.querySelector(".map");
// Add an event listener to the form submit event
form.addEventListener('submit', function(event) {
    event.preventDefault(); // Prevent the default form submission

    // Get selected values from the form
    const layerSelect = document.getElementById('layerSelect').value;
    const layerNameSelect = document.getElementById('layerNameSelect').value;
    const attributeSelect = document.getElementById('AttributeSelect').value;

    // Construct the data object to be sent
    const data = {
        layerSelect: layerSelect,
        layerNameSelect: layerNameSelect,
        attributeSelect: attributeSelect
    };

    // Make a POST request using Fetch API
    fetch('get-layer/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken') // Include CSRF token
        },
        body: JSON.stringify(data) // Convert data to JSON string
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json(); // Parse JSON response
    })
    .then(data => {
        console.log('Success:', data);
        // Handle success response here if needed
        mapDiv.innerHTML = data.map
    })
    .catch(error => {
        console.error('Error:', error);
        // Handle error here
    });
});

// Function to get CSRF token from cookie
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // Extract CSRF token from cookie
            if (cookie.startsWith(name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
