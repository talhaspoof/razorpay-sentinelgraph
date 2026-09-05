import React, { useEffect, useRef, useState } from 'react';
import { Network } from 'vis-network';
import { DataSet } from 'vis-data/standalone';
import { Shield, ZoomIn, ZoomOut, RefreshCw, Eye, Lock, Pin } from 'lucide-react';

export default function GraphViewer({ graphData, onSelectNode, selectedNodeId }) {
  const containerRef = useRef(null);
  const networkRef = useRef(null);
  const nodesDataSetRef = useRef(null);
  const edgesDataSetRef = useRef(null);
  const [physicsEnabled, setPhysicsEnabled] = useState(true);

  const getNodeColor = (type, isQuarantined) => {
    if (isQuarantined) return { background: '#EF4444', border: '#B91C1C', highlight: '#DC2626' };
    switch (type) {
      case 'user': return { background: '#3B82F6', border: '#1D4ED8', highlight: '#60A5FA' };
      case 'device': return { background: '#8B5CF6', border: '#6D28D9', highlight: '#A78BFA' };
      case 'ip': return { background: '#F97316', border: '#C2410C', highlight: '#FB923C' };
      case 'payment_method': return { background: '#10B981', border: '#047857', highlight: '#34D399' };
      case 'address': return { background: '#06B6D4', border: '#0E7490', highlight: '#22D3EE' };
      case 'merchant': return { background: '#64748B', border: '#334155', highlight: '#94A3B8' };
      default: return { background: '#94A3B8', border: '#475569', highlight: '#CBD5E1' };
    }
  };

  const getNodeShape = (type) => {
    switch (type) {
      case 'user': return 'dot';
      case 'device': return 'hexagon';
      case 'ip': return 'square';
      case 'payment_method': return 'diamond';
      case 'address': return 'triangle';
      case 'merchant': return 'box';
      default: return 'dot';
    }
  };

  // 1. Initialize Network & DataSets ONCE on Mount
  useEffect(() => {
    if (!containerRef.current) return;

    const nodesDataSet = new DataSet([]);
    const edgesDataSet = new DataSet([]);
    nodesDataSetRef.current = nodesDataSet;
    edgesDataSetRef.current = edgesDataSet;

    const data = { nodes: nodesDataSet, edges: edgesDataSet };
    const options = {
      nodes: {
        scaling: { min: 12, max: 32 }
      },
      edges: {
        arrows: { to: { enabled: false } }
      },
      physics: {
        enabled: physicsEnabled,
        solver: 'forceAtlas2Based',
        forceAtlas2Based: {
          gravitationalConstant: -60,
          centralGravity: 0.003, // Almost zero central pull so nodes don't drift to center
          springLength: 120,
          springConstant: 0.06,
          damping: 0.55,
          avoidOverlap: 0.8
        },
        minVelocity: 0.75, // Quickly goes to sleep when idle
        stabilization: {
          iterations: 150,
          updateInterval: 25
        }
      },
      interaction: {
        hover: true,
        hoverConnectedEdges: true,
        selectConnectedEdges: true,
        tooltipDelay: 100,
        zoomView: true,
        dragView: true,
        dragNodes: true,
        keyboard: false
      }
    };

    const network = new Network(containerRef.current, data, options);
    networkRef.current = network;

    network.on('click', (params) => {
      if (params.nodes.length > 0) {
        onSelectNode && onSelectNode(params.nodes[0]);
      }
    });

    // When dragging ends, leave the node right where it was dragged
    network.on('dragEnd', (params) => {
      if (params.nodes.length > 0) {
        const nodeId = params.nodes[0];
        // Allow it to settle naturally without snapping back
        network.storePositions();
      }
    });

    return () => {
      network.destroy();
      networkRef.current = null;
    };
  }, []);

  // 2. Incremental Data Updates (Prevents layout reset or repositioning)
  useEffect(() => {
    if (!nodesDataSetRef.current || !edgesDataSetRef.current || !graphData || !graphData.nodes) return;

    const nodesDS = nodesDataSetRef.current;
    const edgesDS = edgesDataSetRef.current;

    const currentVisNodes = graphData.nodes.map(n => ({
      id: n.id,
      label: n.label || n.id,
      title: `${n.type ? n.type.toUpperCase() : 'NODE'}: ${n.id}\nConnections: ${n.degree || 1}${n.is_quarantined ? ' (QUARANTINED)' : ''}`,
      shape: getNodeShape(n.type),
      size: n.is_quarantined ? 24 : (n.type === 'user' ? 18 : 14),
      color: getNodeColor(n.type, n.is_quarantined),
      font: { 
        color: '#F8FAFC', 
        size: 11, 
        face: 'Plus Jakarta Sans',
        strokeWidth: 3,
        strokeColor: '#0B0F19'
      },
      borderWidth: n.id === selectedNodeId ? 3 : 1.5,
      shadow: n.is_quarantined 
        ? { enabled: true, color: '#EF4444', size: 12, x: 0, y: 0 } 
        : { enabled: true, color: 'rgba(0,0,0,0.5)', size: 6, x: 2, y: 2 }
    }));

    const currentVisEdges = graphData.edges.map(e => ({
      id: e.id,
      from: e.source,
      to: e.target,
      label: e.relation || '',
      font: { 
        color: '#FFFFFF', 
        size: 9, 
        align: 'top', 
        face: 'Plus Jakarta Sans',
        strokeWidth: 3,
        strokeColor: '#0B0F19'
      },
      color: { 
        color: 'rgba(71, 85, 105, 0.65)', 
        highlight: '#38BDF8', 
        hover: '#60A5FA',
        opacity: 0.8
      },
      width: 1.5,
      selectionWidth: 2.5,
      hoverWidth: 2,
      smooth: { 
        type: 'cubicBezier', 
        forceDirection: 'none', 
        roundness: 0.25 
      }
    }));

    // Update DataSets without clearing existing node positions
    nodesDS.update(currentVisNodes);
    edgesDS.update(currentVisEdges);

    // Remove nodes that are no longer present
    const incomingNodeIds = new Set(graphData.nodes.map(n => n.id));
    const existingNodeIds = nodesDS.getIds();
    const toRemove = existingNodeIds.filter(id => !incomingNodeIds.has(id));
    if (toRemove.length > 0) {
      nodesDS.remove(toRemove);
    }

    // Immediately wake up physics and redraw canvas so new injected nodes appear instantly
    if (networkRef.current) {
      networkRef.current.redraw();
      networkRef.current.startSimulation();
    }
  }, [graphData, selectedNodeId]);

  // 3. Physics Toggle
  useEffect(() => {
    if (networkRef.current) {
      networkRef.current.setOptions({ physics: { enabled: physicsEnabled } });
    }
  }, [physicsEnabled]);

  const handleZoomIn = () => {
    if (networkRef.current) {
      const scale = networkRef.current.getScale();
      networkRef.current.moveTo({ scale: scale * 1.3 });
    }
  };

  const handleZoomOut = () => {
    if (networkRef.current) {
      const scale = networkRef.current.getScale();
      networkRef.current.moveTo({ scale: scale * 0.7 });
    }
  };

  const handleFit = () => {
    if (networkRef.current) {
      networkRef.current.fit({ animation: { duration: 600, easingFunction: 'easeInOutQuad' } });
    }
  };

  return (
    <div className="relative w-full h-[540px] bg-[#0d1322] rounded-2xl border border-slate-800 overflow-hidden shadow-2xl">
      {/* Legend Header */}
      <div className="absolute top-4 left-4 z-10 flex items-center gap-2 bg-[#111827]/90 backdrop-blur-md px-3 py-2 rounded-xl border border-slate-700/80 text-xs shadow-lg">
        <div className="flex items-center gap-1.5"><span className="w-2.5 h-2.5 rounded-full bg-blue-500"></span> User</div>
        <div className="flex items-center gap-1.5"><span className="w-2.5 h-2.5 bg-purple-500"></span> Device</div>
        <div className="flex items-center gap-1.5"><span className="w-2.5 h-2.5 bg-orange-500"></span> IP</div>
        <div className="flex items-center gap-1.5"><span className="w-2.5 h-2.5 bg-emerald-500 rotate-45"></span> Card</div>
        <div className="flex items-center gap-1.5"><span className="w-2.5 h-2.5 rounded-full bg-red-500 animate-pulse"></span> Quarantined</div>
      </div>

      {/* Control Buttons */}
      <div className="absolute top-4 right-4 z-10 flex items-center gap-1.5 bg-[#111827]/90 backdrop-blur-md p-1.5 rounded-xl border border-slate-700/80 shadow-lg">
        <button onClick={handleZoomIn} title="Zoom In" className="p-2 text-slate-300 hover:text-white hover:bg-slate-800 rounded-lg transition">
          <ZoomIn className="w-4 h-4" />
        </button>
        <button onClick={handleZoomOut} title="Zoom Out" className="p-2 text-slate-300 hover:text-white hover:bg-slate-800 rounded-lg transition">
          <ZoomOut className="w-4 h-4" />
        </button>
        <button onClick={handleFit} title="Fit View" className="p-2 text-slate-300 hover:text-white hover:bg-slate-800 rounded-lg transition">
          <RefreshCw className="w-4 h-4" />
        </button>
        <button
          onClick={() => setPhysicsEnabled(!physicsEnabled)}
          title={physicsEnabled ? "Freeze Physics" : "Enable Physics"}
          className={`p-2 rounded-lg transition ${physicsEnabled ? 'text-blue-400 bg-blue-500/10' : 'text-slate-400 hover:bg-slate-800'}`}
        >
          <Lock className="w-4 h-4" />
        </button>
      </div>

      {/* Canvas Container */}
      <div ref={containerRef} className="w-full h-full cursor-grab active:cursor-grabbing" />
      
      {/* Node Count Overlay */}
      <div className="absolute bottom-4 left-4 z-10 text-[11px] mono-text text-slate-400 bg-slate-900/80 px-2.5 py-1.5 rounded-lg border border-slate-800">
        Nodes: {graphData?.nodes?.length || 0} | Edges: {graphData?.edges?.length || 0} | Status: <span className="text-emerald-400">Live Graph Stream</span>
      </div>
    </div>
  );
}
