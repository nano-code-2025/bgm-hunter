import { MusicTrack, MusicTags, SortOrder } from '../types';

const CLIENT_ID = 'f2567443';
const BASE_URL = 'https://api.jamendo.com/v3.0';

interface JamendoMusicInfo {
  tags?: {
    genres?: string[];
    instruments?: string[];
    vartags?: string[];
  };
}

interface JamendoTrackResponse {
  id: number;
  name: string;
  artist_name: string;
  duration: number;
  audio: string;
  shareurl?: string;
  license_ccurl?: string;
  image?: string;
  album_image?: string;
  audiodownload?: string;
  audiodownload_allowed?: boolean;
  position?: number;
  releasedate?: string;
  musicinfo?: JamendoMusicInfo;
}

interface JamendoApiResponse {
  results?: JamendoTrackResponse[];
}

export async function searchTracks(
  tagsOrQuery: MusicTags | string,
  limit: number = 10,
  sortOrder: SortOrder = 'popularity_total_desc',
  filterAvailable: boolean = true
): Promise<MusicTrack[]> {
  const url = new URL(`${BASE_URL}/tracks/`);
  url.searchParams.set('client_id', CLIENT_ID);
  url.searchParams.set('format', 'json');
  // Fetch more results when filtering, to ensure enough pass the filter
  const searchLimit = filterAvailable ? Math.min(limit * 3, 50) : limit;
  url.searchParams.set('limit', searchLimit.toString());
  url.searchParams.set('include', 'musicinfo');
  url.searchParams.set('orderby', sortOrder);

  let searchQuery = '';
  if (typeof tagsOrQuery === 'string') {
    searchQuery = tagsOrQuery;
  } else {
    const { genres = [], instruments = [], vartags = [] } = tagsOrQuery;
    searchQuery = [...genres, ...instruments, ...vartags].join(' ');
  }

  url.searchParams.set('search', searchQuery);

  try {
    const response = await fetch(url.toString());
    const data: JamendoApiResponse = await response.json();

    if (!data.results) return [];

    let tracks: MusicTrack[] = data.results.map((track) => {
      const musicinfo = track.musicinfo || {};
      const tags = musicinfo.tags || {};

      const allTags = [
        ...(tags.genres || []),
        ...(tags.instruments || []),
        ...(tags.vartags || []),
      ];

      return {
        id: track.id.toString(),
        title: track.name,
        artist: track.artist_name,
        duration: track.duration,
        previewUrl: track.audio,
        sourceUrl: track.shareurl || '#',
        license: track.license_ccurl || 'Unknown',
        tags: allTags,
        cover: track.image || track.album_image || `https://picsum.photos/seed/${track.id}/400/400`,
        bpm: 0,
        audiodownload: track.audiodownload,
        audiodownloadAllowed: track.audiodownload_allowed || false,
        position: track.position,
        releasedate: track.releasedate,
      };
    });

    // Filter to only playable and downloadable tracks
    if (filterAvailable) {
      tracks = tracks.filter(
        (track) => track.audiodownloadAllowed && track.audiodownload && track.previewUrl
      );
    }

    return tracks.slice(0, limit);
  } catch (error) {
    console.error('Jamendo search failed:', error);
    return [];
  }
}
