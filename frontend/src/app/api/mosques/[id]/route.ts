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
    description: "De grootste moskee in Gent met uitgebreide faciliteiten voor de gemeenschap. Deze moskee biedt dagelijkse gebeden, vrijdaggebeden, Koranlessen en verschillende gemeenschapsactiviteiten.",
    phone: "+32 9 123 45 67",
    email: "info@centralemoskee.be",
    website: "https://centralemoskee.be",
    features: ["Parking", "Wudu faciliteiten", "Bibliotheek", "Kinderopvang", "Koranlessen", "Arabische lessen"],
    prayer_times: {
      fajr: "05:30",
      dhuhr: "12:30",
      asr: "15:45",
      maghrib: "18:15",
      isha: "20:00"
    },
    events: [
      {
        id: 1,
        title: "Vrijdaggebed",
        description: "Wekelijks vrijdaggebed met khutbah in het Nederlands",
        date: "2024-10-25",
        time: "13:00",
        location: "Centrale Moskee Gent",
        type: "prayer"
      },
      {
        id: 2,
        title: "Koranstudie",
        description: "Wekelijkse Koranstudie voor alle leeftijden",
        date: "2024-10-27",
        time: "10:00",
        location: "Centrale Moskee Gent",
        type: "education"
      }
    ],
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
    description: "Een warme en gastvrije moskee in het hart van de stad. We verwelkomen alle leden van de gemeenschap voor gebeden en activiteiten.",
    phone: "+32 9 234 56 78",
    email: "info@alnoor.be",
    website: "https://alnoor.be",
    features: ["Parking", "Wudu faciliteiten", "Koranlessen", "Gemeenschapsruimte"],
    prayer_times: {
      fajr: "05:35",
      dhuhr: "12:35",
      asr: "15:50",
      maghrib: "18:20",
      isha: "20:05"
    },
    events: [
      {
        id: 3,
        title: "Gemeenschapsbijeenkomst",
        description: "Maandelijkse bijeenkomst voor gemeenschapsactiviteiten",
        date: "2024-11-02",
        time: "15:00",
        location: "Al-Noor Moskee",
        type: "community"
      }
    ],
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
    description: "Moderne moskee met focus op onderwijs en gemeenschap. We bieden verschillende educatieve programma's en activiteiten.",
    phone: "+32 9 345 67 89",
    email: "info@alrahman.be",
    website: "https://alrahman.be",
    features: ["Parking", "Wudu faciliteiten", "Bibliotheek", "Arabische lessen", "Koranlessen"],
    prayer_times: {
      fajr: "05:32",
      dhuhr: "12:32",
      asr: "15:47",
      maghrib: "18:17",
      isha: "20:02"
    },
    events: [],
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
    description: "Kleine gemeenschapsmoskee met persoonlijke aandacht voor alle leden.",
    phone: "+32 9 456 78 90",
    email: "info@aliman.be",
    features: ["Wudu faciliteiten", "Koranlessen", "Persoonlijke begeleiding"],
    prayer_times: {
      fajr: "05:28",
      dhuhr: "12:28",
      asr: "15:43",
      maghrib: "18:13",
      isha: "19:58"
    },
    events: [],
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
    description: "Moderne moskee met focus op jongeren en onderwijs. We bieden speciale programma's voor jongeren.",
    phone: "+32 9 567 89 01",
    email: "info@alfurqan.be",
    features: ["Wudu faciliteiten", "Jongerenprogramma's", "Arabische lessen", "Sportactiviteiten"],
    prayer_times: {
      fajr: "05:33",
      dhuhr: "12:33",
      asr: "15:48",
      maghrib: "18:18",
      isha: "20:03"
    },
    events: [],
    is_active: true,
    created_at: "2024-01-01T00:00:00Z",
    updated_at: "2024-01-01T00:00:00Z"
  }
];

export async function GET(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    const mosqueId = parseInt(params.id);
    
    if (isNaN(mosqueId)) {
      return NextResponse.json(
        { 
          success: false, 
          error: 'Invalid mosque ID',
          message: 'Ongeldig moskee ID'
        },
        { status: 400 }
      );
    }
    
    // Simulate API delay
    await new Promise(resolve => setTimeout(resolve, 100));
    
    const mosque = mockMosques.find(m => m.id === mosqueId);
    
    if (!mosque) {
      return NextResponse.json(
        { 
          success: false, 
          error: 'Mosque not found',
          message: 'Moskee niet gevonden'
        },
        { status: 404 }
      );
    }
    
    return NextResponse.json({
      success: true,
      data: mosque,
      message: 'Mosque details retrieved successfully'
    });
    
  } catch (error) {
    console.error('Error fetching mosque details:', error);
    return NextResponse.json(
      { 
        success: false, 
        error: 'Failed to fetch mosque details',
        message: 'Er is een fout opgetreden bij het laden van de moskee details'
      },
      { status: 500 }
    );
  }
}
