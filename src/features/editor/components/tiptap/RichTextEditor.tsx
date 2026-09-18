import React, { useEffect } from 'react';
import { useEditor, EditorContent } from '@tiptap/react';
import StarterKit from '@tiptap/starter-kit';
import Placeholder from '@tiptap/extension-placeholder';

interface RichTextEditorProps {
  content: string;
  onChange: (content: string) => void;
  placeholder?: string;
  autoFocus?: boolean;
}

export function RichTextEditor({ content, onChange, placeholder, autoFocus }: RichTextEditorProps) {
  const editor = useEditor({
    extensions: [
      StarterKit,
      Placeholder.configure({ placeholder: placeholder || "Type '/' for commands..." }),
    ],
    content,
    autofocus: autoFocus,
    onUpdate: ({ editor }) => {
      onChange(editor.getHTML());
    },
    editorProps: {
      attributes: {
        class: 'prose prose-sm dark:prose-invert max-w-none focus:outline-none min-h-[100px] w-full p-3 bg-transparent',
      },
    },
  });

  useEffect(() => {
    if (editor && editor.getHTML() !== content) {
      editor.commands.setContent(content, false);
    }
  }, [content, editor]);

  if (!editor) return null;

  return (
    <div className="border border-border rounded-md focus-within:ring-1 focus-within:ring-primary overflow-hidden bg-card transition-all">
      <div className="bg-muted/50 border-b border-border p-1.5 flex gap-1">
        {/* Placeholder toolbar: B, I, Code, Math */}
        <button className="px-2 py-1 text-xs font-medium rounded hover:bg-muted text-muted-foreground">B</button>
        <button className="px-2 py-1 text-xs font-medium rounded hover:bg-muted text-muted-foreground">I</button>
      </div>
      <EditorContent editor={editor} />
    </div>
  );
}