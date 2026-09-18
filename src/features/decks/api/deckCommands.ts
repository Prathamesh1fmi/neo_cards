import { invoke } from '@tauri-apps/api/tauri';

export interface Deck {
  id: string;
  parent_id: string | null;
  name: string;
  created_at: number;
}

export interface DeckTree {
  deck: Deck;
  children: DeckTree[];
}

export const deckApi = {
  getDeckTree: () => invoke<DeckTree[]>('get_deck_tree'),
  createDeck: (name: string, parentId?: string) => invoke<Deck>('create_deck', { name, parentId }),
  deleteDeck: (id: string) => invoke<void>('delete_deck', { id }),
};