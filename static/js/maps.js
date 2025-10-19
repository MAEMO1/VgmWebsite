let map;
let markers = [];

function handleMapsError() {
    const mapElements = document.querySelectorAll('[id^="mosque-map"]');
    mapElements.forEach(element => {
        element.innerHTML = `
            <div class="alert alert-info h-100 d-flex flex-column justify-content-center text-center">
                <i class="fas fa-map-marked-alt fa-3x mb-3"></i>
                <h4>Map Currently Unavailable</h4>
                <p class="mb-0">You can still view all mosque details in the list.</p>
            </div>
        `;
    });
}

function initMap() {
    try {
        // Center on Ghent
        const ghent = { lat: 51.0543, lng: 3.7174 };

        map = new google.maps.Map(document.getElementById("mosque-map"), {
            zoom: 13,
            center: ghent,
            styles: [
                {
                    featureType: "poi.business",
                    stylers: [{ visibility: "off" }]
                }
            ]
        });

        // Add markers for each mosque
        document.querySelectorAll('.mosque-item').forEach(item => {
            const lat = parseFloat(item.dataset.lat);
            const lng = parseFloat(item.dataset.lng);
            if (isNaN(lat) || isNaN(lng)) {
                console.warn('Invalid coordinates for mosque:', item.querySelector('h5').textContent);
                return;
            }

            const title = item.querySelector('h5').textContent;
            const address = item.querySelector('p').textContent;

            const marker = new google.maps.Marker({
                position: { lat, lng },
                map: map,
                title: title,
                icon: {
                    url: 'https://maps.google.com/mapfiles/kml/shapes/mosque.png',
                    scaledSize: new google.maps.Size(32, 32)
                }
            });

            // Add info window with mosque details
            const infoWindow = new google.maps.InfoWindow({
                content: `
                    <div class="info-window">
                        <h5>${title}</h5>
                        <p>${address}</p>
                    </div>
                `
            });

            markers.push({ marker, infoWindow });

            // Navigate to mosque detail page when marker is clicked
            marker.addListener('click', () => {
                // Navigate to mosque detail page
                window.location.href = `/mosque/${item.dataset.mosqueId || 'unknown'}`;
            });
        });
    } catch (error) {
        console.error('Error initializing map:', error);
        handleMapsError();
    }
}

// Handle Google Maps authentication failures
window.gm_authFailure = handleMapsError;