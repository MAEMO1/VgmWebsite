import { NextRequest, NextResponse } from 'next/server';

// Mock data for mosques - in a real app this would come from a database
const mockMosques = [
  {
    id: 1,
    name: "Centrale Moskee Gent",
    address: "Kortrijksepoortstraat 1, 9000 Gent",
    latitude: 51.0543,
    longitude: 3.7174,
    capacity: 500,
    established_year: 1985,
    imam_name: "Sheikh Ahmed",
    description: "De grootste moskee in Gent met uitgebreide faciliteiten voor de gemeenschap.",
    phone: "+32 9 123 45 67",
    email: "info@centralemoskee.be",
    website: "https://centralemoskee.be",
    features: ["Parking", "Wudu faciliteiten", "Bibliotheek", "Kinderopvang"],
    prayer_times: {
      fajr: "05:30",
      dhuhr: "12:30",
      asr: "15:45",
      maghrib: "18:15",
      isha: "20:00"
    },
    is_active: true,
    created_at: "2024-01-01T00:00:00Z",
    updated_at: "2024-01-01T00:00:00Z"
  },
  {
    id: 2,
    name: "Al-Noor Moskee",
    address: "Oost-Vlaanderenstraat 25, 9000 Gent",
    latitude: 51.0569,
    longitude: 3.7298,
    capacity: 200,
    established_year: 1992,
    imam_name: "Imam Hassan",
    description: "Een warme en gastvrije moskee in het hart van de stad.",
    phone: "+32 9 234 56 78",
    email: "info@alnoor.be",
    website: "https://alnoor.be",
    features: ["Parking", "Wudu faciliteiten", "Koranlessen"],
    prayer_times: {
      fajr: "05:35",
      dhuhr: "12:35",
      asr: "15:50",
      maghrib: "18:20",
      isha: "20:05"
    },
    is_active: true,
    created_at: "2024-01-01T00:00:00Z",
    updated_at: "2024-01-01T00:00:00Z"
  },
  {
    id: 3,
    name: "Masjid Al-Rahman",
    address: "Zuidparklaan 15, 9000 Gent",
    latitude: 51.0419,
    longitude: 3.7103,
    capacity: 150,
    established_year: 1998,
    imam_name: "Sheikh Omar",
    description: "Moderne moskee met focus op onderwijs en gemeenschap.",
    phone: "+32 9 345 67 89",
    email: "info@alrahman.be",
    website: "https://alrahman.be",
    features: ["Parking", "Wudu faciliteiten", "Bibliotheek", "Arabische lessen"],
    prayer_times: {
      fajr: "05:32",
      dhuhr: "12:32",
      asr: "15:47",
      maghrib: "18:17",
      isha: "20:02"
    },
    is_active: true,
    created_at: "2024-01-01T00:00:00Z",
    updated_at: "2024-01-01T00:00:00Z"
  },
  {
    id: 4,
    name: "Masjid Al-Iman",
    address: "Wondelgemstraat 8, 9000 Gent",
    latitude: 51.0689,
    longitude: 3.7014,
    capacity: 100,
    established_year: 2005,
    imam_name: "Imam Yusuf",
    description: "Kleine gemeenschapsmoskee met persoonlijke aandacht.",
    phone: "+32 9 456 78 90",
    email: "info@aliman.be",
    features: ["Wudu faciliteiten", "Koranlessen"],
    prayer_times: {
      fajr: "05:28",
      dhuhr: "12:28",
      asr: "15:43",
      maghrib: "18:13",
      isha: "19:58"
    },
    is_active: true,
    created_at: "2024-01-01T00:00:00Z",
    updated_at: "2024-01-01T00:00:00Z"
  },
  {
    id: 5,
    name: "Masjid Al-Furqan",
    address: "Sint-Pietersnieuwstraat 42, 9000 Gent",
    latitude: 51.0444,
    longitude: 3.7267,
    capacity: 80,
    established_year: 2010,
    imam_name: "Sheikh Ibrahim",
    description: "Moderne moskee met focus op jongeren en onderwijs.",
    phone: "+32 9 567 89 01",
    email: "info@alfurqan.be",
    features: ["Wudu faciliteiten", "Jongerenprogramma's", "Arabische lessen"],
    prayer_times: {
      fajr: "05:33",
      dhuhr: "12:33",
      asr: "15:48",
      maghrib: "18:18",
      isha: "20:03"
    },
    is_active: true,
    created_at: "2024-01-01T00:00:00Z",
    updated_at: "2024-01-01T00:00:00Z"
  }
];

export async function GET(request: NextRequest) {
  try {
    // Simulate API delay
    await new Promise(resolve => setTimeout(resolve, 100));
    
    // Get query parameters
    const { searchParams } = new URL(request.url);
    const search = searchParams.get('search');
    const sort = searchParams.get('sort') || 'name';
    const limit = parseInt(searchParams.get('limit') || '50');
    
    let filteredMosques = [...mockMosques];
    
    // Apply search filter
    if (search) {
      const searchLower = search.toLowerCase();
      filteredMosques = filteredMosques.filter(mosque => 
        mosque.name.toLowerCase().includes(searchLower) ||
        mosque.address.toLowerCase().includes(searchLower) ||
        mosque.description.toLowerCase().includes(searchLower)
      );
    }
    
    // Apply sorting
    filteredMosques.sort((a, b) => {
      switch (sort) {
        case 'name':
          return a.name.localeCompare(b.name);
        case 'capacity':
          return b.capacity - a.capacity;
        case 'established':
          return b.established_year - a.established_year;
        default:
          return a.name.localeCompare(b.name);
      }
    });
    
    // Apply limit
    filteredMosques = filteredMosques.slice(0, limit);
    
    return NextResponse.json({
      success: true,
      data: filteredMosques,
      total: filteredMosques.length,
      message: 'Mosques retrieved successfully'
    });
    
  } catch (error) {
    console.error('Error fetching mosques:', error);
    return NextResponse.json(
      { 
        success: false, 
        error: 'Failed to fetch mosques',
        message: 'Er is een fout opgetreden bij het laden van de moskeeën'
      },
      { status: 500 }
    );
  }
}
