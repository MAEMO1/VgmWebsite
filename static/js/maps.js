function initMap() {
    // Default mosque location (example coordinates)
    const mosqueLocation = { lat: 51.0504, lng: 3.7101 };
    
    const map = new google.maps.Map(document.getElementById('mosque-map'), {
        zoom: 15,
        center: mosqueLocation,
        styles: [
            {
                "featureType": "poi.place_of_worship",
                "elementType": "geometry",
                "stylers": [
                    { "visibility": "on" },
                    { "color": "#e9e9e9" }
                ]
            }
        ]
    });

    const marker = new google.maps.Marker({
        position: mosqueLocation,
        map: map,
        title: 'Our Mosque',
        icon: {
            path: google.maps.SymbolPath.CIRCLE,
            scale: 10,
            fillColor: '#4CAF50',
            fillOpacity: 0.8,
            strokeWeight: 2,
            strokeColor: '#fff'
        }
    });

    const infoWindow = new google.maps.InfoWindow({
        content: `
            <div class="map-info-window">
                <h3>Our Mosque</h3>
                <p>Address: 123 Mosque Street</p>
                <p>Phone: (123) 456-7890</p>
            </div>
        `
    });

    marker.addListener('click', () => {
        infoWindow.open(map, marker);
    });
}
