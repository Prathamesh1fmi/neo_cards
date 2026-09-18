import React, { useEffect, useState } from 'react';
import { useEditor, EditorContent } from '@tiptap/react';
import StarterKit from '@tiptap/starter-kit';
import Placeholder from '@tiptap/extension-placeholder';
import Image from '@tiptap/extension-image';
import Table from '@tiptap/extension-table';
import TableRow from '@tiptap/extension-table-row';
import TableCell from '@tiptap/extension-table-cell';
import TableHeader from '@tiptap/extension-table-header';
import Link from '@tiptap/extension-link';
import CharacterCount from '@tiptap/extension-character-count';

interface AdvancedEditorProps {
  initialContent: any; // JSON
  onChange: (json: any) => void;
  placeholder?: string;
}

export function AdvancedEditor({ initialContent, onChange, placeholder }: AdvancedEditorProps) {
  const editor = useEditor({
    extensions: [
      StarterKit,
      Placeholder.configure({ placeholder: placeholder || "Type '/' for commands..." }),
      Image,
      Table.configure({ resizable: true }),
      TableRow,
      TableHeader,
      TableCell,
      Link.configure({ openOnClick: false }),
      CharacterCount,
    ],
    content: initialContent,
    onUpdate: ({ editor }) => {
      onChange(editor.getJSON());
    },
    editorProps: {
      attributes: {
        class: 'prose prose-sm dark:prose-invert max-w-none focus:outline-none min-h-[150px] w-full p-4',
      },
      handleDrop: (view, event, slice, moved) => {
        // Intercept image drops here to hash and save via Tauri FS API, 
        // then insert a media reference node.
        return false;
      },
    },
  });

  if (!editor) return null;

  return (
    <div className="border border-border rounded-md focus-within:ring-1 focus-within:ring-primary overflow-hidden bg-card transition-all flex flex-col h-full">
      <div className="bg-muted/30 border-b border-border p-1.5 flex gap-1 flex-wrap shrink-0">
        <button onClick={() => editor.chain().focus().toggleBold().run()} className="px-2 py-1 text-xs hover:bg-accent rounded">B</button>
        <button onClick={() => editor.chain().focus().toggleItalic().run()} className="px-2 py-1 text-xs hover:bg-accent rounded">I</button>
        <button onClick={() => editor.chain().focus().toggleCodeBlock().run()} className="px-2 py-1 text-xs hover:bg-accent rounded">Code</button>
        <button onClick={() => editor.chain().focus().toggleBlockquote().run()} className="px-2 py-1 text-xs hover:bg-accent rounded">Quote</button>
        <div className="flex-1"></div>
        <div className="text-[10px] text-muted-foreground self-center px-2">
          {editor.storage.characterCount.words()} words
        </div>
      </div>
      <div className="flex-1 overflow-y-auto">
        <EditorContent editor={editor} className="h-full" />
      </div>
    </div>
  );
}