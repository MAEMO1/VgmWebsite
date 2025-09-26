// Prayer times calculation and API integration
// Based on Islamic Society of North America (ISNA) method with Diyanet API fallback

export interface PrayerTimes {
  fajr: string;
  sunrise: string;
  dhuhr: string;
  asr: string;
  maghrib: string;
  isha: string;
  date: string;
}

export interface PrayerTimesResponse {
  success: boolean;
  data?: PrayerTimes;
  error?: string;
  source: 'diyanet' | 'calculation';
}

// Diyanet API configuration
const DIYANET_API_BASE = 'https://ezanvakti.herokuapp.com';

// Gent coordinates
const GENT_COORDINATES = {
  latitude: 51.0543,
  longitude: 3.7174,
  timezone: 'Europe/Brussels'
};

// Calculation parameters for ISNA method
const CALCULATION_PARAMS = {
  fajr: 15, // degrees
  isha: 15, // degrees
  asr: 1, // Hanafi method
  highLat: 'AngleBased' // High latitude adjustment method
};

/**
 * Calculate prayer times using astronomical formulas
 * Based on ISNA (Islamic Society of North America) method
 */
export function calculatePrayerTimes(date: Date = new Date()): PrayerTimes {
  const lat = GENT_COORDINATES.latitude;
  const lng = GENT_COORDINATES.longitude;
  const timezone = 1; // UTC+1 for Belgium (CET)
  
  // Convert to radians
  const latRad = (lat * Math.PI) / 180;
  const lngRad = (lng * Math.PI) / 180;
  
  // Get day of year
  const dayOfYear = Math.floor((date.getTime() - new Date(date.getFullYear(), 0, 0).getTime()) / (1000 * 60 * 60 * 24));
  
  // Calculate sun declination
  const declination = 23.45 * Math.sin((284 + dayOfYear) * Math.PI / 180 * Math.PI / 180);
  const declRad = (declination * Math.PI) / 180;
  
  // Calculate equation of time
  const B = (dayOfYear - 81) * 2 * Math.PI / 365;
  const equationOfTime = 9.87 * Math.sin(2 * B) - 7.53 * Math.cos(B) - 1.5 * Math.sin(B);
  
  // Calculate time correction
  const timeCorrection = equationOfTime + 4 * (lng - 15 * timezone);
  
  // Calculate sun angle for each prayer
  const fajrAngle = -CALCULATION_PARAMS.fajr;
  const ishaAngle = -CALCULATION_PARAMS.isha;
  
  // Calculate prayer times
  const fajrTime = calculatePrayerTime(fajrAngle, latRad, declRad, timeCorrection);
  const sunriseTime = calculatePrayerTime(-0.833, latRad, declRad, timeCorrection);
  const dhuhrTime = 12 + timeCorrection / 60;
  const asrTime = calculateAsrTime(latRad, declRad, timeCorrection);
  const maghribTime = calculatePrayerTime(-0.833, latRad, declRad, timeCorrection);
  const ishaTime = calculatePrayerTime(ishaAngle, latRad, declRad, timeCorrection);
  
  return {
    fajr: formatTime(fajrTime),
    sunrise: formatTime(sunriseTime),
    dhuhr: formatTime(dhuhrTime),
    asr: formatTime(asrTime),
    maghrib: formatTime(maghribTime),
    isha: formatTime(ishaTime),
    date: date.toISOString().split('T')[0]
  };
}

function calculatePrayerTime(angle: number, latRad: number, declRad: number, timeCorrection: number): number {
  const angleRad = (angle * Math.PI) / 180;
  const hourAngle = Math.acos((Math.sin(angleRad) - Math.sin(latRad) * Math.sin(declRad)) / (Math.cos(latRad) * Math.cos(declRad)));
  
  if (isNaN(hourAngle)) {
    return 0;
  }
  
  const time = 12 + (hourAngle * 180 / Math.PI) / 15 + timeCorrection / 60;
  return time;
}

function calculateAsrTime(latRad: number, declRad: number, timeCorrection: number): number {
  const shadowLength = 1 + CALCULATION_PARAMS.asr;
  const angle = Math.atan(1 / shadowLength);
  return calculatePrayerTime(angle * 180 / Math.PI, latRad, declRad, timeCorrection);
}

function formatTime(time: number): string {
  const hours = Math.floor(time);
  const minutes = Math.round((time - hours) * 60);
  const adjustedHours = hours % 24;
  return `${adjustedHours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}`;
}

/**
 * Fetch prayer times from Diyanet API
 */
export async function fetchDiyanetPrayerTimes(date: Date = new Date()): Promise<PrayerTimesResponse> {
  try {
    const dateStr = date.toISOString().split('T')[0];
    
    // First, get the city ID for Gent
    const citiesResponse = await fetch(`${DIYANET_API_BASE}/sehirler`);
    if (!citiesResponse.ok) {
      throw new Error('Failed to fetch cities');
    }
    
    const cities = await citiesResponse.json();
    const gentCity = cities.find((city: any) => 
      city.SehirAdi.toLowerCase().includes('gent') || 
      city.SehirAdi.toLowerCase().includes('ghent')
    );
    
    if (!gentCity) {
      throw new Error('Gent not found in Diyanet cities');
    }
    
    // Get prayer times for the city
    const prayerTimesResponse = await fetch(
      `${DIYANET_API_BASE}/vakitler/${gentCity.SehirID}`
    );
    
    if (!prayerTimesResponse.ok) {
      throw new Error('Failed to fetch prayer times');
    }
    
    const prayerTimesData = await prayerTimesResponse.json();
    
    // Find today's prayer times
    const todayTimes = prayerTimesData.find((item: any) => 
      item.MiladiTarihKisa === dateStr
    );
    
    if (!todayTimes) {
      throw new Error('Prayer times not found for today');
    }
    
    return {
      success: true,
      data: {
        fajr: todayTimes.Imsak,
        sunrise: todayTimes.Gunes,
        dhuhr: todayTimes.Ogle,
        asr: todayTimes.Ikindi,
        maghrib: todayTimes.Aksam,
        isha: todayTimes.Yatsi,
        date: dateStr
      },
      source: 'diyanet'
    };
  } catch (error) {
    console.warn('Diyanet API failed, falling back to calculation:', error);
    return {
      success: false,
      error: error instanceof Error ? error.message : 'Unknown error',
      source: 'diyanet'
    };
  }
}

/**
 * Get prayer times with fallback to calculation
 */
export async function getPrayerTimes(date: Date = new Date()): Promise<PrayerTimesResponse> {
  // Try Diyanet API first
  const diyanetResult = await fetchDiyanetPrayerTimes(date);
  
  if (diyanetResult.success && diyanetResult.data) {
    return diyanetResult;
  }
  
  // Fallback to calculation
  const calculatedTimes = calculatePrayerTimes(date);
  
  return {
    success: true,
    data: calculatedTimes,
    source: 'calculation'
  };
}

/**
 * Get next prayer time
 */
export function getNextPrayerTime(prayerTimes: PrayerTimes): { name: string; time: string; isNext: boolean }[] {
  const now = new Date();
  const currentTime = now.getHours() * 60 + now.getMinutes();
  
  const prayers = [
    { name: 'Fajr', time: prayerTimes.fajr, key: 'fajr' },
    { name: 'Sunrise', time: prayerTimes.sunrise, key: 'sunrise' },
    { name: 'Dhuhr', time: prayerTimes.dhuhr, key: 'dhuhr' },
    { name: 'Asr', time: prayerTimes.asr, key: 'asr' },
    { name: 'Maghrib', time: prayerTimes.maghrib, key: 'maghrib' },
    { name: 'Isha', time: prayerTimes.isha, key: 'isha' }
  ];
  
  return prayers.map(prayer => {
    const [hours, minutes] = prayer.time.split(':').map(Number);
    const prayerTime = hours * 60 + minutes;
    
    return {
      name: prayer.name,
      time: prayer.time,
      isNext: prayerTime > currentTime
    };
  });
}

/**
 * Get current prayer status
 */
export function getCurrentPrayerStatus(prayerTimes: PrayerTimes): {
  current: string | null;
  next: string | null;
  timeUntilNext: string | null;
} {
  const now = new Date();
  const currentTime = now.getHours() * 60 + now.getMinutes();
  
  const prayers = [
    { name: 'Fajr', time: prayerTimes.fajr },
    { name: 'Sunrise', time: prayerTimes.sunrise },
    { name: 'Dhuhr', time: prayerTimes.dhuhr },
    { name: 'Asr', time: prayerTimes.asr },
    { name: 'Maghrib', time: prayerTimes.maghrib },
    { name: 'Isha', time: prayerTimes.isha }
  ];
  
  let currentPrayer: string | null = null;
  let nextPrayer: string | null = null;
  
  for (let i = 0; i < prayers.length; i++) {
    const [hours, minutes] = prayers[i].time.split(':').map(Number);
    const prayerTime = hours * 60 + minutes;
    
    if (prayerTime <= currentTime) {
      currentPrayer = prayers[i].name;
    } else {
      nextPrayer = prayers[i].name;
      break;
    }
  }
  
  // If no next prayer found, next is tomorrow's Fajr
  if (!nextPrayer) {
    nextPrayer = 'Fajr (Tomorrow)';
  }
  
  // Calculate time until next prayer
  let timeUntilNext: string | null = null;
  if (nextPrayer && nextPrayer !== 'Fajr (Tomorrow)') {
    const nextPrayerIndex = prayers.findIndex(p => p.name === nextPrayer);
    if (nextPrayerIndex !== -1) {
      const [hours, minutes] = prayers[nextPrayerIndex].time.split(':').map(Number);
      const nextPrayerTime = hours * 60 + minutes;
      const timeDiff = nextPrayerTime - currentTime;
      
      if (timeDiff > 0) {
        const hoursLeft = Math.floor(timeDiff / 60);
        const minutesLeft = timeDiff % 60;
        timeUntilNext = `${hoursLeft}h ${minutesLeft}m`;
      }
    }
  }
  
  return {
    current: currentPrayer,
    next: nextPrayer,
    timeUntilNext
  };
}
