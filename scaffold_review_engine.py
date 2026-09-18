import os
import json
from pathlib import Path

base = Path('.')

dirs = [
    'src-tauri/src/application/review',
    'src-tauri/src/commands/review',
    'src/features/study/components',
    'src/features/study/api',
    'src/features/study/hooks',
    'src/pages',
]

for d in dirs:
    (base / d).mkdir(parents=True, exist_ok=True)

scripts = {}

# 1. Update Cargo.toml to include the official FSRS crate
cargo_path = base / 'src-tauri/Cargo.toml'
if cargo_path.exists():
    cargo = cargo_path.read_text()
    if 'fsrs =' not in cargo:
        cargo = cargo.replace('[dependencies]', '[dependencies]\nfsrs = "1.0"\n')
        cargo_path.write_text(cargo)

# 2. Rust Scheduler Abstraction
scripts['src-tauri/src/application/review/scheduler.rs'] = r'''use serde::{Serialize, Deserialize};

#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
pub enum Rating {
    Again = 1,
    Hard = 2,
    Good = 3,
    Easy = 4,
}

#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
pub enum CardState {
    New = 0,
    Learning = 1,
    Review = 2,
    Relearning = 3,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SchedulingInfo {
    pub card_id: String,
    pub next_due: i64,
    pub new_interval: i32,
    pub new_ease: f64,
    pub new_state: CardState,
    pub reps: i32,
    pub lapses: i32,
}

/// Abstract Scheduler Service. NeoCards depends on this trait, NOT FSRS directly.
pub trait SchedulerService {
    fn calculate_next_review(
        &self, 
        card_id: &str, 
        current_state: CardState, 
        rating: Rating, 
        current_interval: i32, 
        current_ease: f64, 
        reps: i32, 
        lapses: i32
    ) -> Result<SchedulingInfo, String>;
}

/// FSRS Implementation of the Scheduler Service
pub struct FsrsScheduler {
    // Internally, this wraps the `fsrs::FSRS` struct
    // For scaffolding, we mock the mathematical calculations to prove the architecture
}

impl FsrsScheduler {
    pub fn new() -> Self {
        Self {}
    }
}

impl SchedulerService for FsrsScheduler {
    fn calculate_next_review(
        &self, 
        card_id: &str, 
        current_state: CardState, 
        rating: Rating, 
        current_interval: i32, 
        current_ease: f64, 
        reps: i32, 
        lapses: i32
    ) -> Result<SchedulingInfo, String> {
        // MOCK FSRS CALCULATION FOR ARCHITECTURE VALIDATION
        let mut new_reps = reps + 1;
        let mut new_lapses = lapses;
        let mut next_due = chrono::Utc::now().timestamp();
        let mut new_state = CardState::Review;
        
        let new_interval = match rating {
            Rating::Again => {
                new_lapses += 1;
                new_state = if current_state == CardState::New { CardState::Learning } else { CardState::Relearning };
                0
            },
            Rating::Hard => (current_interval as f64 * 1.2) as i32,
            Rating::Good => (current_interval as f64 * 2.5) as i32,
            Rating::Easy => (current_interval as f64 * 3.1) as i32,
        };

        if new_interval > 0 {
            next_due += (new_interval as i64) * 86400; // days to seconds
        }

        Ok(SchedulingInfo {
            card_id: card_id.to_string(),
            next_due,
            new_interval: std::cmp::max(new_interval, 1),
            new_ease: current_ease, // FSRS calculates stability/difficulty internally
            new_state,
            reps: new_reps,
            lapses: new_lapses,
        })
    }
}
'''

# 3. Session & Queue Manager
scripts['src-tauri/src/application/review/session.rs'] = r'''use crate::domain::card::Card;
use crate::application::review::scheduler::{Rating, SchedulerService};
use rusqlite::Connection;

pub struct QueueManager {
    // Queues
    pub new_queue: Vec<Card>,
    pub learning_queue: Vec<Card>,
    pub review_queue: Vec<Card>,
}

impl QueueManager {
    pub fn build(conn: &Connection, deck_id: &str) -> Result<Self, String> {
        // MOCK: In production, query cards WHERE deck_id = ? AND due_date <= NOW()
        Ok(Self {
            new_queue: Vec::new(),
            learning_queue: Vec::new(),
            review_queue: Vec::new(),
        })
    }

    pub fn get_next_card(&mut self) -> Option<Card> {
        // Prioritize Learning > Review > New
        if !self.learning_queue.is_empty() {
            return Some(self.learning_queue.remove(0));
        }
        if !self.review_queue.is_empty() {
            return Some(self.review_queue.remove(0));
        }
        if !self.new_queue.is_empty() {
            return Some(self.new_queue.remove(0));
        }
        None
    }
}
'''

# 4. IPC Commands
scripts['src-tauri/src/commands/review/mod.rs'] = r'''pub mod session_commands;'''

scripts['src-tauri/src/commands/review/session_commands.rs'] = r'''use tauri::State;
use crate::db::connection::DbState;
use crate::application::review::scheduler::{Rating, FsrsScheduler, SchedulerService, CardState};
use crate::domain::card::Card;
use serde::{Deserialize, Serialize};

#[derive(Serialize)]
pub struct ReviewCardDto {
    pub card: Card,
    pub front_html: String,
    pub back_html: String,
}

#[tauri::command]
pub fn get_next_card(deck_id: String, state: State<DbState>) -> Result<Option<ReviewCardDto>, String> {
    // MOCK: Fetch next card from QueueManager, render templates, return HTML
    Ok(None)
}

#[derive(Deserialize)]
pub struct SubmitReviewRequest {
    pub card_id: String,
    pub rating: Rating,
    pub time_taken_ms: i32,
}

#[tauri::command]
pub fn submit_review(req: SubmitReviewRequest, state: State<DbState>) -> Result<(), String> {
    let mut conn = state.conn.lock().unwrap();
    let tx = conn.transaction().map_err(|e| e.to_string())?;

    // 1. Fetch current card
    // let card = fetch_card(&tx, &req.card_id);
    
    // 2. Scheduler Calculation
    let scheduler = FsrsScheduler::new();
    let result = scheduler.calculate_next_review(
        &req.card_id, 
        CardState::Review, 
        req.rating, 
        10, 
        2.5, 
        1, 
        0
    )?;

    // 3. Update Card in DB
    // update_card(&tx, result);

    // 4. Insert RevLog
    // insert_revlog(&tx, req, result);

    tx.commit().map_err(|e| e.to_string())?;
    Ok(())
}
'''

# 5. React Review Interface (Desktop-first, Keyboard-first)
scripts['src/features/study/components/ReviewInterface.tsx'] = r'''import React, { useState, useEffect, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { invoke } from '@tauri-apps/api/tauri';
import { CheckCircle2, LayoutGrid } from 'lucide-react';

interface CardDto {
  card: { id: string };
  front_html: string;
  back_html: string;
}

export function ReviewInterface() {
  const [currentCard, setCurrentCard] = useState<CardDto | null>(null);
  const [isFlipped, setIsFlipped] = useState(false);
  const [loading, setLoading] = useState(true);

  // MOCK DATA for architectural scaffolding
  useEffect(() => {
    setTimeout(() => {
      setCurrentCard({
        card: { id: "mock-1" },
        front_html: "<div class='text-xl text-center font-serif'>La biblioteca</div>",
        back_html: "<div class='text-xl text-center font-serif text-primary mb-4'>The library</div><hr class='border-border my-4'/><div class='text-sm text-muted-foreground'>Noun, feminine.</div>"
      });
      setLoading(false);
    }, 300);
  }, []);

  const submitReview = useCallback((rating: number) => {
    // invoke('submit_review', { req: { card_id: currentCard.card.id, rating, time_taken_ms: 1500 } })
    setCurrentCard(null); // Move to next card
  }, [currentCard]);

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
'''

# 6. Page route
scripts['src/pages/Review.tsx'] = r'''import React from "react";
import { ReviewInterface } from "@/features/study/components/ReviewInterface";

export function Review() {
  return (
    <div className="h-full w-full bg-background">
      <ReviewInterface />
    </div>
  );
}
'''

for filepath, content in scripts.items():
    (base / filepath).write_text(content.strip(), encoding='utf-8')

print("Review Engine Scaffolding complete.")

