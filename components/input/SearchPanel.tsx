import { useState } from 'react';
import { motion } from 'framer-motion';
import { Sparkles, ChevronRight } from 'lucide-react';
import { TAG_GROUPS, ADVANCED_TAG_GROUPS } from '../../constants';

interface SearchPanelProps {
  onSearch: (data: { text: string; selectedTags: string[]; mode: 'script' | 'keyword' }) => void;
  isLoading: boolean;
}

export const SearchPanel: React.FC<SearchPanelProps> = ({ onSearch, isLoading }) => {
  const [mode, setMode] = useState<'script' | 'keyword'>('script');
  const [text, setText] = useState('');
  const [selectedTags, setSelectedTags] = useState<string[]>([]);

  const handleSubmit = (e?: React.FormEvent) => {
    e?.preventDefault();
    // Validate input: keyword mode needs tags or text, script mode needs text
    const hasInput = mode === 'keyword'
      ? (selectedTags.length > 0 || text.trim().length > 0)
      : text.trim().length > 0;

    if (hasInput) {
      onSearch({ text, selectedTags, mode });
    }
  };

  const toggleTag = (tag: string) => {
    setSelectedTags(prev =>
      prev.includes(tag) ? prev.filter(t => t !== tag) : [...prev, tag]
    );
  };

  return (
    <motion.div
      layoutId="search-container"
      className="w-full max-w-2xl glass rounded-[2.5rem] p-8 md:p-12 shadow-2xl relative overflow-hidden"
    >
      <div className="flex flex-col gap-8">
        <div className="flex items-center justify-between">
          <div className="flex gap-4">
            <button
              onClick={() => setMode('script')}
              className={`text-sm font-medium transition-colors ${mode === 'script' ? 'text-white' : 'text-neutral-500'}`}
            >
              Script Analysis
            </button>
            <button
              onClick={() => setMode('keyword')}
              className={`text-sm font-medium transition-colors ${mode === 'keyword' ? 'text-white' : 'text-neutral-500'}`}
            >
              Keywords
            </button>
          </div>
          {isLoading && (
            <motion.div
              animate={{ rotate: 360 }}
              transition={{ repeat: Infinity, duration: 2, ease: "linear" }}
              className="text-purple-500"
            >
              <Sparkles className="w-5 h-5" />
            </motion.div>
          )}
        </div>

        <div className="relative">
          {mode === 'script' ? (
            <div className="flex flex-col gap-6">
              <textarea
                value={text}
                onChange={(e) => setText(e.target.value)}
                placeholder="Paste your video script here... Let AI find the perfect mood."
                className="w-full h-40 bg-transparent border-none text-xl md:text-2xl text-white placeholder:text-neutral-700 resize-none focus:outline-none"
              />
              <div className="flex flex-col gap-4">
                <div className="flex flex-wrap gap-2">
                  <span className="text-xs text-neutral-500 px-2">Optional: Select keywords to guide AI analysis</span>
                  {TAG_GROUPS.flatMap(group =>
                    group.tags.map(tag => (
                      <button
                        key={`${group.category}-${tag}`}
                        onClick={() => toggleTag(tag)}
                        className={`px-3 py-1.5 rounded-full text-xs transition-all ${
                          selectedTags.includes(tag)
                            ? 'bg-white text-black border-white'
                            : 'bg-white/5 text-neutral-500 border-white/10 border hover:border-white/30'
                        }`}
                      >
                        {tag}
                      </button>
                    ))
                  )}
                </div>
                {/* Advanced Options */}
                <details className="text-xs text-neutral-500">
                  <summary className="cursor-pointer hover:text-neutral-400">Advanced Options</summary>
                  <div className="flex flex-wrap gap-2 mt-2">
                    {ADVANCED_TAG_GROUPS.flatMap(group =>
                      group.tags.map(tag => (
                        <button
                          key={`adv-${group.category}-${tag}`}
                          onClick={() => toggleTag(tag)}
                          className={`px-3 py-1.5 rounded-full text-xs transition-all ${
                            selectedTags.includes(tag)
                              ? 'bg-white text-black border-white'
                              : 'bg-white/5 text-neutral-500 border-white/10 border hover:border-white/30'
                          }`}
                        >
                          {tag}
                        </button>
                      ))
                    )}
                  </div>
                </details>
              </div>
            </div>
          ) : (
            <div className="flex flex-col gap-6">
              <input
                type="text"
                value={text}
                onChange={(e) => setText(e.target.value)}
                placeholder="Type custom keywords..."
                className="w-full bg-transparent border-none text-xl md:text-2xl text-white placeholder:text-neutral-700 focus:outline-none"
                onKeyDown={(e) => e.key === 'Enter' && handleSubmit()}
              />
              <div className="flex flex-col gap-4">
                {/* Main Categories */}
                <div className="flex flex-wrap gap-2">
                  {TAG_GROUPS.flatMap(group =>
                    group.tags.map(tag => (
                      <button
                        key={`${group.category}-${tag}`}
                        onClick={() => toggleTag(tag)}
                        className={`px-3 py-1.5 rounded-full text-xs transition-all ${
                          selectedTags.includes(tag)
                            ? 'bg-white text-black border-white'
                            : 'bg-white/5 text-neutral-500 border-white/10 border hover:border-white/30'
                        }`}
                      >
                        {tag}
                      </button>
                    ))
                  )}
                </div>
                {/* Advanced Options */}
                <details className="text-xs text-neutral-500">
                  <summary className="cursor-pointer hover:text-neutral-400">Advanced Options</summary>
                  <div className="flex flex-wrap gap-2 mt-2">
                    {ADVANCED_TAG_GROUPS.flatMap(group =>
                      group.tags.map(tag => (
                        <button
                          key={`adv-${group.category}-${tag}`}
                          onClick={() => toggleTag(tag)}
                          className={`px-3 py-1.5 rounded-full text-xs transition-all ${
                            selectedTags.includes(tag)
                              ? 'bg-white text-black border-white'
                              : 'bg-white/5 text-neutral-500 border-white/10 border hover:border-white/30'
                          }`}
                        >
                          {tag}
                        </button>
                      ))
                    )}
                  </div>
                </details>
              </div>
            </div>
          )}
        </div>

        <div className="flex justify-end">
          <button
            onClick={() => handleSubmit()}
            disabled={isLoading || (mode === 'keyword' && !text.trim() && selectedTags.length === 0) || (mode === 'script' && !text.trim())}
            className="group flex items-center gap-3 bg-white text-black px-6 py-4 rounded-2xl font-semibold hover:bg-neutral-200 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isLoading ? 'Analyzing...' : 'Find Matches'}
            <ChevronRight className="w-5 h-5 transition-transform group-hover:translate-x-1" />
          </button>
        </div>
      </div>
    </motion.div>
  );
};
