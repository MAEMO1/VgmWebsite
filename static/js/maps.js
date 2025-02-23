let map;
let markers = [];

function handleMapsError() {
    const mapElements = document.querySelectorAll('[id^="mosque-map"]');
    mapElements.forEach(element => {
        element.innerHTML = `
            <div class="alert alert-warning">
                <i class="fas fa-exclamation-triangle"></i>
                <span class="ms-2">De kaart kon niet worden geladen. Hier zijn de adressen van de moskeeën:</span>
            </div>
            <div class="mosque-addresses mt-3"></div>
        `;

        // Display mosque addresses if available
        const mosqueItems = document.querySelectorAll('.mosque-item');
        const addressesContainer = element.querySelector('.mosque-addresses');
        if (mosqueItems.length > 0 && addressesContainer) {
            const addressList = document.createElement('ul');
            addressList.className = 'list-group';
            mosqueItems.forEach(item => {
                const address = item.querySelector('p').textContent;
                const name = item.querySelector('h4').textContent;
                const li = document.createElement('li');
                li.className = 'list-group-item';
                li.innerHTML = `<strong>${name}</strong><br>${address}`;
                addressList.appendChild(li);
            });
            addressesContainer.appendChild(addressList);
        }
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
                console.warn('Invalid coordinates for mosque:', item.querySelector('h4').textContent);
                return;
            }

            const title = item.querySelector('h4').textContent;
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

            // Show info window when marker is clicked
            marker.addListener('click', () => {
                markers.forEach(m => m.infoWindow.close());
                infoWindow.open(map, marker);
            });

            // Add click event to center map on mosque when list item is clicked
            item.addEventListener('click', () => {
                map.setCenter({ lat, lng });
                map.setZoom(16);
                markers.forEach(m => m.infoWindow.close());
                infoWindow.open(map, marker);
            });
        });
    } catch (error) {
        console.error('Error initializing map:', error);
        handleMapsError();
    }
}

// Handle Google Maps authentication failures
window.gm_authFailure = handleMapsError;