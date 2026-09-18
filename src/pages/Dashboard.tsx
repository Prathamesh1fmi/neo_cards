import React from "react";
import { PageContainer } from "@/components/layout/PageContainer";
import { EmptyState } from "@/components/ui/EmptyState";
import { Layers } from "lucide-react";

export function Dashboard() {
  return (
    <PageContainer title="Dashboard">
      <EmptyState 
        icon={Layers}
        title="Welcome to Dashboard"
        description="This is a premium placeholder. The business logic for this module will be implemented in future milestones."
        action={
          <button className="px-4 py-2 bg-primary text-primary-foreground rounded-md text-sm font-medium hover:bg-primary/90 transition-colors">
            Simulate Action
          </button>
        }
      />
    </PageContainer>
  );
}