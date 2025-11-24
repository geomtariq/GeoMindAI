'use client';

import { useState } from 'react';
import { Panel, PanelGroup, PanelResizeHandle } from 'react-resizable-panels';
import { GripVertical } from 'lucide-react';

interface ResizablePanelsProps {
    leftPanel: React.ReactNode;
    rightPanel: React.ReactNode;
    defaultLeftSize?: number;
}

export default function ResizablePanels({
    leftPanel,
    rightPanel,
    defaultLeftSize = 35
}: ResizablePanelsProps) {
    return (
        <PanelGroup direction="horizontal" className="h-full w-full">
            {/* Left Panel - Chat */}
            <Panel
                defaultSize={defaultLeftSize}
                minSize={25}
                maxSize={50}
                className="h-full"
            >
                {leftPanel}
            </Panel>

            {/* Resize Handle */}
            <PanelResizeHandle className="w-2 bg-border hover:bg-primary/20 transition-colors relative group">
                <div className="absolute inset-y-0 left-1/2 -translate-x-1/2 w-1 bg-border group-hover:bg-primary/40 transition-colors" />
                <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 bg-background border border-border rounded-full p-1 opacity-0 group-hover:opacity-100 transition-opacity">
                    <GripVertical className="w-3 h-3 text-muted-foreground" />
                </div>
            </PanelResizeHandle>

            {/* Right Panel - Data Visualization */}
            <Panel
                defaultSize={100 - defaultLeftSize}
                minSize={50}
                className="h-full"
            >
                {rightPanel}
            </Panel>
        </PanelGroup>
    );
}
