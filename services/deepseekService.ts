import { AnalysisResult, UserPreferences } from '../types';
import { callDeepSeek, getApiKey } from './aiService';

interface DeepSeekAnalysisResponse {
  contentType?: string;
  moods?: string[];
  instruments?: string[];
  energy?: string;
  keywords?: string[];
  summary?: string;
  tags?: {
    genres?: string[];
    instruments?: string[];
    vartags?: string[];
  };
}

export async function analyzeInput(
  text: string,
  mode: 'script' | 'keyword',
  userPreferences?: UserPreferences,
  selectedTags?: string[]
): Promise<AnalysisResult> {
  if (!getApiKey()) {
    console.error('DeepSeek API key not found');
    return getDefaultResult();
  }

  const prompt = buildAnalysisPrompt(text, mode, userPreferences, selectedTags);

  try {
    const result = await callDeepSeek<DeepSeekAnalysisResponse>(prompt);

    return {
      contentType: result.contentType || 'General',
      moods: Array.isArray(result.moods) ? result.moods : ['Neutral'],
      instruments: Array.isArray(result.instruments) ? result.instruments : [],
      energy: result.energy || 'medium',
      keywords: Array.isArray(result.keywords) ? result.keywords : [],
      summary: result.summary || 'AI analysis completed.',
      tags: result.tags || {
        genres: result.keywords?.slice(0, 3) || [],
        instruments: result.instruments || [],
        vartags: [],
      },
    };
  } catch (e) {
    console.error('DeepSeek analysis failed:', e);
    return getDefaultResult();
  }
}

function buildAnalysisPrompt(
  text: string,
  mode: 'script' | 'keyword',
  userPreferences?: UserPreferences,
  selectedTags?: string[]
): string {
  let prompt = '';

  if (mode === 'script') {
    prompt = `Analyze the following video script and extract music tags for BGM recommendation. Return structured tags including genres (e.g., "lofi", "chillhop", "piano", "electronic"), instruments (e.g., "piano", "guitar", "synthesizer"), and vartags (e.g., "peaceful", "happy", "energetic", "calm", "uplifting").`;

    if (selectedTags && selectedTags.length > 0) {
      prompt += `\n\nUser selected keywords for reference: ${selectedTags.join(', ')}. Please consider these keywords when analyzing.`;
    }

    if (userPreferences) {
      prompt += `\n\nUser preferences: genres=${userPreferences.genres?.join(', ') || 'none'}, instruments=${userPreferences.instruments?.join(', ') || 'none'}, vartags=${userPreferences.vartags?.join(', ') || 'none'}. Please consider these preferences when generating tags.`;
    }

    prompt += `\n\nScript: "${text}"`;
  } else {
    prompt = `Given the keywords "${text}", extract structured BGM search tags including genres, instruments, and vartags (mood/emotion tags).`;

    if (userPreferences) {
      prompt += `\n\nUser preferences: genres=${userPreferences.genres?.join(', ') || 'none'}, instruments=${userPreferences.instruments?.join(', ') || 'none'}, vartags=${userPreferences.vartags?.join(', ') || 'none'}. Please consider these preferences.`;
    }
  }

  prompt += `\n\nReturn a JSON object with this exact structure:
{
  "contentType": "string",
  "moods": ["Melancholy" | "Happy" | "Dynamic" | "Neutral"],
  "instruments": ["string"],
  "energy": "low" | "medium" | "high",
  "keywords": ["string"],
  "summary": "string",
  "tags": {
    "genres": ["string"],
    "instruments": ["string"],
    "vartags": ["string"]
  }
}`;

  return prompt;
}

function getDefaultResult(): AnalysisResult {
  return {
    contentType: 'General',
    moods: ['Neutral'],
    instruments: ['Piano'],
    energy: 'medium',
    keywords: ['background music'],
    summary: 'AI analysis failed, returning defaults.',
    tags: {
      genres: ['ambient'],
      instruments: ['piano'],
      vartags: ['neutral'],
    },
  };
}
