
export type Mood = 'Melancholy' | 'Happy' | 'Dynamic' | 'Neutral';
export type Energy = 'low' | 'medium' | 'high';

export interface MusicTags {
  genres?: string[];
  instruments?: string[];
  vartags?: string[];
}

export interface AnalysisResult {
  contentType: string;
  moods: Mood[];
  instruments: string[];
  energy: Energy;
  keywords: string[];
  summary: string;
  tags?: MusicTags;
}

export type SortOrder = 
  | 'popularity_total_desc'  // Total popularity descending
  | 'popularity_total_asc'   // Total popularity ascending
  | 'listens_desc'            // Listens descending
  | 'listens_asc'            // Listens ascending
  | 'downloads_desc'         // Downloads descending
  | 'downloads_asc'          // Downloads ascending
  | 'rating_desc'            // Rating descending
  | 'rating_asc'             // Rating ascending
  | 'releasedate_desc'       // Release date descending (newest)
  | 'releasedate_asc'        // Release date ascending (oldest)
  | 'relevance_desc'         // Relevance descending (default)
  | 'relevance_asc';         // Relevance ascending

export interface MusicTrack {
  id: string;
  title: string;
  artist: string;
  duration: number;
  previewUrl: string;
  sourceUrl: string;
  license: string;
  tags: string[];
  bpm?: number;
  cover?: string;
  audiodownload?: string;
  audiodownloadAllowed?: boolean;
  position?: number;         // Search result position (lower = higher rank)
  releasedate?: string;       // Release date
}

export interface AudioStats {
  frequencyData: Uint8Array;
  averageFrequency: number;
  bass: number;
  mid: number;
  treble: number;
}

export interface UserPreferences {
  genres?: string[];      // Genre preferences
  instruments?: string[]; // Instrument preferences
  vartags?: string[];    // Theme/scenario preferences
}

export type VisualizerTheme = 
  | 'stars'      // Stars (default)
  | 'rain'       // Rain
  | 'snow'       // Snow
  | 'halo'       // Halo
  | 'rainGlass'  // Rain glass with bokeh lights
  | 'aurora';    // Aurora sky

export interface Collection {
  id: string;
  name: string;
  tracks: MusicTrack[];
  createdAt: number;
  updatedAt: number;
}
