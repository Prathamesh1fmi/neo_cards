import React from 'react';

type UIContext = 'sidebar' | 'command_palette' | 'editor_toolbar' | 'inspector' | 'review_actions';

export interface PluginComponent {
    id: string;
    context: UIContext;
    component: React.FC<any>;
    priority?: number;
}

class PluginRegistry {
    private components: Map<UIContext, PluginComponent[]> = new Map();

    registerComponent(pluginId: string, context: UIContext, component: React.FC<any>, priority = 0) {
        const current = this.components.get(context) || [];
        this.components.set(context, [...current, { id: pluginId, context, component, priority }].sort((a, b) => (b.priority || 0) - (a.priority || 0)));
    }

    getComponents(context: UIContext): PluginComponent[] {
        return this.components.get(context) || [];
    }
}

export const registry = new PluginRegistry();