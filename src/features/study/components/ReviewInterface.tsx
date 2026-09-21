import React, { useState, useEffect, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { invoke } from '@tauri-apps/api/tauri';
import { CheckCircle2, LayoutGrid } from 'lucide-react';
import { useSearchParams } from 'react-router-dom';

interface CardDto {
  card: { id: string };
  front_html: string;
  back_html: string;
}

export function ReviewInterface() {
  const [currentCard, setCurrentCard] = useState<CardDto | null>(null);
  const [isFlipped, setIsFlipped] = useState(false);
  const [loading, setLoading] = useState(true);

  const [searchParams] = useSearchParams();
  const deckId = searchParams.get("deckId") || "default_deck";
  
  const fetchNextCard = useCallback(async () => {
    setLoading(true);
    try {
      const card = await invoke<CardDto | null>('get_next_card', { deckId });
      setCurrentCard(card);
      setIsFlipped(false);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  }, [deckId]);

  useEffect(() => {
    fetchNextCard();
  }, [fetchNextCard]);

  const submitReview = useCallback(async (rating: number) => {
    if (!currentCard) return;
    try {
      await invoke('submit_review', { 
        req: { card_id: currentCard.card.id, rating, time_taken_ms: 1500 } 
      });
      fetchNextCard();
    } catch (e) {
      console.error(e);
    }
  }, [currentCard, fetchNextCard]);

  // Global Keyboard Shortcuts
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (!currentCard) return;
      
      if (!isFlipped && (e.code === 'Space' || e.code === 'Enter')) {
        e.preventDefault();
        setIsFlipped(true);
      } else if (isFlipped) {
        switch (e.code) {
          case 'Digit1': e.preventDefault(); submitReview(1); break;
          case 'Digit2': e.preventDefault(); submitReview(2); break;
          case 'Digit3': e.preventDefault(); submitReview(3); break;
          case 'Digit4': e.preventDefault(); submitReview(4); break;
          case 'Space': 
          case 'Enter':
            e.preventDefault(); 
            submitReview(3); // Default to Good
            break;
        }
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isFlipped, currentCard, submitReview]);

  if (loading) return <div className="flex h-full items-center justify-center animate-pulse">Loading queue...</div>;

  if (!currentCard) return (
    <div className="flex flex-col h-full items-center justify-center gap-4 text-center">
      <CheckCircle2 size={48} className="text-green-500" />
      <h2 className="text-2xl font-semibold">Congratulations!</h2>
      <p className="text-muted-foreground">You have finished this deck for now.</p>
    </div>
  );

  return (
    <div className="flex flex-col h-full max-w-3xl mx-auto w-full pt-10 pb-6 px-4">
      {/* Progress Bar */}
      <div className="flex items-center gap-2 mb-8 select-none">
        <div className="flex gap-1 text-xs font-medium">
          <span className="text-blue-500">12</span>
          <span className="text-red-500">3</span>
          <span className="text-green-500">45</span>
        </div>
        <div className="flex-1 h-1.5 bg-muted rounded-full overflow-hidden">
          <div className="h-full bg-primary w-1/3"></div>
        </div>
      </div>

      {/* Card Render */}
      <div className="flex-1 relative flex flex-col items-center justify-center min-h-[400px]">
        <motion.div 
          layout
          className="w-full bg-card border border-border shadow-sm rounded-2xl p-8 sm:p-12 text-foreground"
        >
          {/* FRONT */}
          <div dangerouslySetInnerHTML={{ __html: currentCard.front_html }} className="prose dark:prose-invert max-w-none focus:outline-none" />
          
          {/* BACK */}
          <AnimatePresence>
            {isFlipped && (
              <motion.div
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                className="mt-8 pt-8 border-t border-border"
              >
                <div dangerouslySetInnerHTML={{ __html: currentCard.back_html }} className="prose dark:prose-invert max-w-none focus:outline-none" />
              </motion.div>
            )}
          </AnimatePresence>
        </motion.div>
      </div>

      {/* Controls */}
      <div className="h-24 flex items-center justify-center shrink-0 mt-4 select-none">
        {!isFlipped ? (
          <button 
            onClick={() => setIsFlipped(true)}
            className="px-8 py-3 bg-primary text-primary-foreground rounded-lg font-medium hover:bg-primary/90 transition-colors shadow-sm w-full sm:w-auto"
          >
            Show Answer <span className="opacity-50 ml-2 text-xs">SPACE</span>
          </button>
        ) : (
          <motion.div 
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            className="flex gap-3 w-full sm:w-auto"
          >
            <AnswerButton rating={1} label="Again" time="< 1m" color="bg-red-500/10 text-red-500 border-red-500/20 hover:bg-red-500/20" />
            <AnswerButton rating={2} label="Hard" time="2d" color="bg-orange-500/10 text-orange-500 border-orange-500/20 hover:bg-orange-500/20" />
            <AnswerButton rating={3} label="Good" time="5d" color="bg-green-500/10 text-green-500 border-green-500/20 hover:bg-green-500/20" />
            <AnswerButton rating={4} label="Easy" time="8d" color="bg-blue-500/10 text-blue-500 border-blue-500/20 hover:bg-blue-500/20" />
          </motion.div>
        )}
      </div>
    </div>
  );
}

function AnswerButton({ rating, label, time, color }: any) {
  return (
    <button className={`flex flex-col items-center justify-center px-6 py-2 rounded-lg border transition-colors flex-1 sm:flex-none ${color}`}>
      <span className="text-xs font-semibold opacity-70 mb-0.5">{time}</span>
      <span className="font-bold text-sm tracking-wide uppercase">{label}</span>
      <span className="text-[10px] opacity-40 mt-1">{rating}</span>
    </button>
  );
}