import React from "react";
import { motion } from "framer-motion";

export function PageContainer({ children, title }: { children: React.ReactNode, title?: string }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -10 }}
      transition={{ duration: 0.2 }}
      className="p-6 max-w-6xl mx-auto w-full"
    >
      {title && <h1 className="text-3xl font-bold tracking-tight mb-6 text-foreground">{title}</h1>}
      {children}
    </motion.div>
  );
}