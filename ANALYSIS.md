# VGM Iftar-kaart Analyse

## 1. Kernproblemen

De VGM Iftar-kaart applicatie kampt momenteel met twee hoofdproblemen:

1. **Dubbele Iftar Events**
   - Terugkerende events worden meerdere keren weergegeven in de kalender
   - De recurrence-logica werkt niet correct bij wekelijkse events
   - Events verschijnen soms op verkeerde datums

2. **Inconsistente Gebedstijden**
   - Gebedstijden komen niet altijd overeen met externe API's
   - Synchronisatieproblemen tussen verschillende bronnen (Diyanet, Mawaqit)
   - Timing-issues bij het laden van gebedstijden

## 2. Technologische Stack

### Backend Framework: Flask
- Gekozen voor snelle ontwikkeling en flexibiliteit
- Modulaire opbouw via Blueprints
- Async support via flask[async] voor betere performance
- Eenvoudige integratie met SQLAlchemy en andere extensions

### Database: PostgreSQL
- Robuuste dataopslag voor gebruikers- en moskeegegevens
- Goede ondersteuning voor complexe queries
- Betrouwbare transacties voor event management
- Schaalbaarheid voor groeiende datasets

### Externe API Integraties
- Diyanet API (via Aladhan) voor gebedstijden
- Mawaqit API als backup/alternatief
- Google Maps API voor locatie visualisatie

### AI Component: Claude 3.7
- Analyse van kalenderlogica en duplicaten
- Architectuurvoorstellen en evaluaties
- Monitoring van data-inconsistenties

### Frontend
- Bootstrap voor responsive design
- JavaScript voor interactieve kaart en kalender
- AJAX voor dynamische updates

### Internationalisatie
- Flask-Babel voor meertalige ondersteuning
- Ondersteuning voor Nederlands, Arabisch en Engels

## 3. Huidige Architectuur

### Modulaire Opzet
- Ramadan Blueprint voor iftar-gerelateerde routes
- Aparte services voor gebedstijden en AI-analyse
- Gedeelde modellen voor gebruikers en events

### Data Flow
1. Event Management
   - Creatie van single/recurring events
   - Verwerking via IfterCalendar klasse
   - Filtering en weergave in verschillende views

2. Gebedstijden Integratie
   - Ophalen via externe API's
   - Caching en synchronisatie
   - Koppeling met events

3. Gebruikersinteractie
   - Filtering op type/periode/moskee
   - Kaart- en kalenderweergave
   - Real-time updates

## 4. Huidige Uitdagingen

### Technisch
- Complexe recurrence-logica leidt tot duplicaten
- Asynchrone operaties in Flask vereisen specifieke handling
- Data-consistentie tussen verschillende bronnen

### Architecturaal
- Sterke koppeling tussen componenten
- Complexe integratie van externe diensten
- Uitdagingen in schaalbaarheid

### Gebruikerservaring
- Verwarrende weergave door dubbele events
- Inconsistente informatie over gebedstijden
- Performance-issues bij grote datasets

Deze analyse legt de basis voor verdere discussie over mogelijke verbeteringen, zonder specifieke oplossingen voor te stellen.
