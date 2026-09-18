// NeoCards Plugin SDK Example
import { ui, events, notifications } from '@neocards/sdk';
import React, { useState, useEffect } from 'react';

const PomodoroWidget = () => {
    const [timeLeft, setTimeLeft] = useState(25 * 60);
    
    useEffect(() => {
        const timer = setInterval(() => setTimeLeft(t => Math.max(0, t - 1)), 1000);
        return () => clearInterval(timer);
    }, []);

    useEffect(() => {
        if (timeLeft === 0) {
            notifications.show({ title: "Pomodoro Complete!", body: "Time for a 5 minute break." });
        }
    }, [timeLeft]);

    return (
        <div style={{ padding: '8px', border: '1px solid var(--border)', borderRadius: '8px', textAlign: 'center' }}>
            <div style={{ fontSize: '12px', fontWeight: 'bold' }}>Pomodoro</div>
            <div>{Math.floor(timeLeft / 60)}:{(timeLeft % 60).toString().padStart(2, '0')}</div>
        </div>
    );
};

export function activate(context) {
    console.log("Pomodoro Plugin Activated!");
    
    // Register UI Component in the Sidebar
    ui.registerComponent('sidebar', PomodoroWidget, 100);

    // Listen to backend events
    events.on('CardReviewed', (event) => {
        console.log(`Card ${event.card_id} was reviewed!`);
    });
}

export function deactivate() {
    console.log("Pomodoro Plugin Deactivated.");
}