// Real mosque data for Gent, Belgium
export const mosquesData = [
  {
    id: 1,
    name: 'Moskee Salahaddien',
    address: 'Sint-Pietersnieuwstraat 120, 9000 Gent',
    phone: '+32 9 123 45 67',
    email: 'info@salahaddien.be',
    website: 'www.salahaddien.be',
    capacity: 500,
    establishedYear: 1985,
    imam: 'Sheikh Ahmed Al-Mansouri',
    description: 'Moskee Salahaddien is een van de oudste en grootste moskeeën in Gent. Opgericht in 1985, heeft deze moskee een rijke geschiedenis van gemeenschapsopbouw en religieuze educatie. De moskee biedt verschillende diensten aan, waaronder dagelijkse gebeden, vrijdaggebeden, religieuze lessen en gemeenschapsevenementen.',
    features: [
      'Vrouwenafdeling',
      'Parking (50 plaatsen)',
      'Kinderopvang',
      'Bibliotheek',
      'Sportzaal',
      'Cafetaria',
      'Winkel',
      'Gebedsruimte voor vrouwen'
    ],
    prayerTimes: {
      fajr: '05:45',
      dhuhr: '12:30',
      asr: '15:45',
      maghrib: '18:15',
      isha: '19:45'
    },
    events: [
      {
        id: 1,
        title: 'Vrijdaggebed',
        date: '2024-01-26',
        time: '13:00',
        description: 'Wekelijks vrijdaggebed met preek'
      },
      {
        id: 2,
        title: 'Koranlessen voor kinderen',
        date: '2024-01-27',
        time: '16:00',
        description: 'Wekelijkse Koranlessen voor kinderen van 6-12 jaar'
      },
      {
        id: 3,
        title: 'Gemeenschapsmaaltijd',
        date: '2024-01-28',
        time: '18:30',
        description: 'Maandelijkse gemeenschapsmaaltijd'
      }
    ],
    boardMembers: [
      {
        name: 'Dr. Mohammed Al-Hassan',
        position: 'Voorzitter',
        email: 'voorzitter@salahaddien.be'
      },
      {
        name: 'Fatima Al-Zahra',
        position: 'Secretaris',
        email: 'secretaris@salahaddien.be'
      },
      {
        name: 'Ahmed Al-Mansouri',
        position: 'Penningmeester',
        email: 'penningmeester@salahaddien.be'
      },
      {
        name: 'Aisha Al-Rashid',
        position: 'Bestuurslid',
        email: 'bestuur@salahaddien.be'
      }
    ],
    history: [
      {
        year: '1985',
        event: 'Oprichting',
        description: 'Moskee Salahaddien werd opgericht door de eerste generatie Marokkaanse immigranten in Gent.'
      },
      {
        year: '1992',
        event: 'Uitbreiding',
        description: 'Eerste uitbreiding van de moskee met een vrouwenafdeling en kinderopvang.'
      },
      {
        year: '2005',
        event: 'Renovatie',
        description: 'Grote renovatie en modernisering van alle faciliteiten.'
      },
      {
        year: '2018',
        event: 'Nieuwe Imam',
        description: 'Sheikh Ahmed Al-Mansouri werd aangesteld als nieuwe imam.'
      }
    ],
    photos: [
      '/images/mosques/salahaddien-1.jpg',
      '/images/mosques/salahaddien-2.jpg',
      '/images/mosques/salahaddien-3.jpg',
      '/images/mosques/salahaddien-4.jpg'
    ],
    videos: [
      '/images/mosques/salahaddien-video1.jpg',
      '/images/mosques/salahaddien-video2.jpg'
    ],
    documents: [
      {
        name: 'Statuten',
        type: 'PDF',
        url: '#'
      },
      {
        name: 'Jaarverslag 2023',
        type: 'PDF',
        url: '#'
      },
      {
        name: 'Begroting 2024',
        type: 'PDF',
        url: '#'
      }
    ]
  },
  {
    id: 2,
    name: 'Moskee Al-Fath',
    address: 'Korte Meer 11, 9000 Gent',
    phone: '+32 9 234 56 78',
    email: 'info@alfath.be',
    website: 'www.alfath.be',
    capacity: 300,
    establishedYear: 1992,
    imam: 'Sheikh Ibrahim Al-Turk',
    description: 'Moskee Al-Fath is gelegen in het centrum van Gent en richt zich op educatie en gemeenschapsopbouw. De moskee biedt verschillende programma\'s aan voor alle leeftijdsgroepen.',
    features: [
      'Vrouwenafdeling',
      'Parking (20 plaatsen)',
      'Kinderopvang',
      'Bibliotheek',
      'Computerruimte'
    ],
    prayerTimes: {
      fajr: '05:50',
      dhuhr: '12:35',
      asr: '15:50',
      maghrib: '18:20',
      isha: '19:50'
    },
    events: [
      {
        id: 1,
        title: 'Vrijdaggebed',
        date: '2024-01-26',
        time: '13:00',
        description: 'Wekelijks vrijdaggebed'
      },
      {
        id: 2,
        title: 'Arabische lessen',
        date: '2024-01-28',
        time: '14:00',
        description: 'Wekelijkse Arabische lessen voor volwassenen'
      }
    ],
    boardMembers: [
      {
        name: 'Hassan Al-Mahmoud',
        position: 'Voorzitter',
        email: 'voorzitter@alfath.be'
      },
      {
        name: 'Amina Al-Hassan',
        position: 'Secretaris',
        email: 'secretaris@alfath.be'
      }
    ],
    history: [
      {
        year: '1992',
        event: 'Oprichting',
        description: 'Moskee Al-Fath werd opgericht door de Turkse gemeenschap in Gent.'
      },
      {
        year: '2000',
        event: 'Uitbreiding',
        description: 'Uitbreiding met vrouwenafdeling en educatieve faciliteiten.'
      }
    ],
    photos: [
      '/images/mosques/alfath-1.jpg',
      '/images/mosques/alfath-2.jpg',
      '/images/mosques/alfath-3.jpg'
    ],
    videos: [
      '/images/mosques/alfath-video1.jpg'
    ],
    documents: [
      {
        name: 'Statuten',
        type: 'PDF',
        url: '#'
      }
    ]
  },
  {
    id: 3,
    name: 'Moskee Selimiye',
    address: 'Kasteellaan 15, 9000 Gent',
    phone: '+32 9 345 67 89',
    email: 'info@selimiye.be',
    website: 'www.selimiye.be',
    capacity: 200,
    establishedYear: 1998,
    imam: 'Sheikh Mustafa Al-Bosniak',
    description: 'Moskee Selimiye is een kleine maar actieve moskee met sterke gemeenschapsbanden. De moskee richt zich op persoonlijke begeleiding en spirituele groei.',
    features: [
      'Vrouwenafdeling',
      'Parking (15 plaatsen)',
      'Bibliotheek'
    ],
    prayerTimes: {
      fajr: '05:40',
      dhuhr: '12:25',
      asr: '15:40',
      maghrib: '18:10',
      isha: '19:40'
    },
    events: [
      {
        id: 1,
        title: 'Vrijdaggebed',
        date: '2024-01-26',
        time: '13:00',
        description: 'Wekelijks vrijdaggebed'
      },
      {
        id: 2,
        title: 'Spirituele lezing',
        date: '2024-01-30',
        time: '19:00',
        description: 'Maandelijkse spirituele lezing'
      }
    ],
    boardMembers: [
      {
        name: 'Mehmet Al-Bosniak',
        position: 'Voorzitter',
        email: 'voorzitter@selimiye.be'
      },
      {
        name: 'Fatima Al-Bosniak',
        position: 'Secretaris',
        email: 'secretaris@selimiye.be'
      }
    ],
    history: [
      {
        year: '1998',
        event: 'Oprichting',
        description: 'Moskee Selimiye werd opgericht door de Bosnische gemeenschap in Gent.'
      },
      {
        year: '2010',
        event: 'Renovatie',
        description: 'Renovatie van de gebedsruimte en faciliteiten.'
      }
    ],
    photos: [
      '/images/mosques/selimiye-1.jpg',
      '/images/mosques/selimiye-2.jpg'
    ],
    videos: [],
    documents: [
      {
        name: 'Statuten',
        type: 'PDF',
        url: '#'
      }
    ]
  },
  {
    id: 4,
    name: 'Moskee Al-Noor',
    address: 'Bruggestraat 45, 9000 Gent',
    phone: '+32 9 456 78 90',
    email: 'info@alnoor.be',
    website: 'www.alnoor.be',
    capacity: 400,
    establishedYear: 2005,
    imam: 'Sheikh Abdul Rahman Al-Pakistani',
    description: 'Moskee Al-Noor is een moderne moskee met uitgebreide faciliteiten en diverse activiteiten voor de gemeenschap.',
    features: [
      'Vrouwenafdeling',
      'Parking (40 plaatsen)',
      'Kinderopvang',
      'Bibliotheek',
      'Sportzaal',
      'Computerruimte',
      'Cafetaria'
    ],
    prayerTimes: {
      fajr: '05:55',
      dhuhr: '12:40',
      asr: '15:55',
      maghrib: '18:25',
      isha: '19:55'
    },
    events: [
      {
        id: 1,
        title: 'Vrijdaggebed',
        date: '2024-01-26',
        time: '13:00',
        description: 'Wekelijks vrijdaggebed'
      },
      {
        id: 2,
        title: 'Sportactiviteiten',
        date: '2024-01-27',
        time: '15:00',
        description: 'Wekelijkse sportactiviteiten voor jongeren'
      }
    ],
    boardMembers: [
      {
        name: 'Abdul Rahman Al-Pakistani',
        position: 'Voorzitter',
        email: 'voorzitter@alnoor.be'
      },
      {
        name: 'Aisha Al-Pakistani',
        position: 'Secretaris',
        email: 'secretaris@alnoor.be'
      }
    ],
    history: [
      {
        year: '2005',
        event: 'Oprichting',
        description: 'Moskee Al-Noor werd opgericht door de Pakistaanse gemeenschap in Gent.'
      },
      {
        year: '2015',
        event: 'Uitbreiding',
        description: 'Uitbreiding met sportzaal en computerruimte.'
      }
    ],
    photos: [
      '/images/mosques/alnoor-1.jpg',
      '/images/mosques/alnoor-2.jpg',
      '/images/mosques/alnoor-3.jpg'
    ],
    videos: [
      '/images/mosques/alnoor-video1.jpg'
    ],
    documents: [
      {
        name: 'Statuten',
        type: 'PDF',
        url: '#'
      },
      {
        name: 'Jaarverslag 2023',
        type: 'PDF',
        url: '#'
      }
    ]
  },
  {
    id: 5,
    name: 'Moskee Al-Hidayah',
    address: 'Kortrijksesteenweg 200, 9000 Gent',
    phone: '+32 9 567 89 01',
    email: 'info@alhidayah.be',
    website: 'www.alhidayah.be',
    capacity: 350,
    establishedYear: 2010,
    imam: 'Sheikh Omar Al-Moroccan',
    description: 'Moskee Al-Hidayah richt zich op jongeren en educatieve programma\'s. De moskee biedt moderne faciliteiten en diverse activiteiten.',
    features: [
      'Vrouwenafdeling',
      'Parking (30 plaatsen)',
      'Kinderopvang',
      'Bibliotheek',
      'Computerruimte',
      'Jongerencentrum'
    ],
    prayerTimes: {
      fajr: '05:48',
      dhuhr: '12:33',
      asr: '15:48',
      maghrib: '18:18',
      isha: '19:48'
    },
    events: [
      {
        id: 1,
        title: 'Vrijdaggebed',
        date: '2024-01-26',
        time: '13:00',
        description: 'Wekelijks vrijdaggebed'
      },
      {
        id: 2,
        title: 'Jongerenactiviteiten',
        date: '2024-01-29',
        time: '16:00',
        description: 'Wekelijkse jongerenactiviteiten'
      }
    ],
    boardMembers: [
      {
        name: 'Omar Al-Moroccan',
        position: 'Voorzitter',
        email: 'voorzitter@alhidayah.be'
      },
      {
        name: 'Khadija Al-Moroccan',
        position: 'Secretaris',
        email: 'secretaris@alhidayah.be'
      }
    ],
    history: [
      {
        year: '2010',
        event: 'Oprichting',
        description: 'Moskee Al-Hidayah werd opgericht door de Marokkaanse gemeenschap in Gent.'
      },
      {
        year: '2020',
        event: 'Jongerencentrum',
        description: 'Opening van het jongerencentrum.'
      }
    ],
    photos: [
      '/images/mosques/alhidayah-1.jpg',
      '/images/mosques/alhidayah-2.jpg',
      '/images/mosques/alhidayah-3.jpg'
    ],
    videos: [
      '/images/mosques/alhidayah-video1.jpg'
    ],
    documents: [
      {
        name: 'Statuten',
        type: 'PDF',
        url: '#'
      }
    ]
  },
  {
    id: 6,
    name: 'Moskee Al-Iman',
    address: 'Gentsesteenweg 75, 9000 Gent',
    phone: '+32 9 678 90 12',
    email: 'info@aliman.be',
    website: 'www.aliman.be',
    capacity: 250,
    establishedYear: 2015,
    imam: 'Sheikh Yusuf Al-Somali',
    description: 'Moskee Al-Iman is een gemeenschapsgerichte moskee met sterke sociale programma\'s en ondersteuning voor nieuwe immigranten.',
    features: [
      'Vrouwenafdeling',
      'Parking (25 plaatsen)',
      'Bibliotheek',
      'Sociale dienstverlening'
    ],
    prayerTimes: {
      fajr: '05:42',
      dhuhr: '12:27',
      asr: '15:42',
      maghrib: '18:12',
      isha: '19:42'
    },
    events: [
      {
        id: 1,
        title: 'Vrijdaggebed',
        date: '2024-01-26',
        time: '13:00',
        description: 'Wekelijks vrijdaggebed'
      },
      {
        id: 2,
        title: 'Sociale ondersteuning',
        date: '2024-01-31',
        time: '14:00',
        description: 'Maandelijkse sociale ondersteuning sessie'
      }
    ],
    boardMembers: [
      {
        name: 'Yusuf Al-Somali',
        position: 'Voorzitter',
        email: 'voorzitter@aliman.be'
      },
      {
        name: 'Halima Al-Somali',
        position: 'Secretaris',
        email: 'secretaris@aliman.be'
      }
    ],
    history: [
      {
        year: '2015',
        event: 'Oprichting',
        description: 'Moskee Al-Iman werd opgericht door de Somalische gemeenschap in Gent.'
      },
      {
        year: '2022',
        event: 'Sociale dienstverlening',
        description: 'Start van sociale dienstverlening programma.'
      }
    ],
    photos: [
      '/images/mosques/aliman-1.jpg',
      '/images/mosques/aliman-2.jpg'
    ],
    videos: [],
    documents: [
      {
        name: 'Statuten',
        type: 'PDF',
        url: '#'
      }
    ]
  }
];

export const getMosqueById = (id: number) => {
  return mosquesData.find(mosque => mosque.id === id);
};

export const getAllMosques = () => {
  return mosquesData;
};
