export interface Mosque {
  id: number;
  name: string;
  address: string;
  latitude?: number | null;
  longitude?: number | null;
  phone?: string | null;
  email?: string | null;
  website?: string | null;
  capacity?: number | null;
  description?: string | null;
  established_year?: number | null;
  imam_name?: string | null;
}

export interface EventItem {
  id: number;
  title: string;
  description?: string | null;
  event_date: string;
  event_time: string;
  event_type?: string | null;
  mosque_id?: number | null;
  mosque_name?: string | null;
  is_active?: number | boolean;
  created_at?: string;
  max_attendees?: number | null;
}

export interface NewsArticle {
  id: number;
  title: string;
  excerpt?: string | null;
  content?: string | null;
  published_at: string;
  author_id?: number | null;
  first_name?: string | null;
  last_name?: string | null;
}

export interface Campaign {
  id: number;
  title: string;
  description?: string | null;
  start_date: string;
  end_date?: string | null;
  target_amount?: number | null;
  current_amount?: number | null;
  status?: string | null;
  mosque_id?: number | null;
  mosque_name?: string | null;
}

export interface SearchResult {
  mosques: Mosque[];
  events: EventItem[];
  news: NewsArticle[];
  campaigns: Campaign[];
  total_results: number;
  page: number;
  per_page: number;
  total_pages: number;
}
