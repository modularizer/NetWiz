/**
 * Graph Visualization Component
 *
 * A D3.js-based component for visualizing netlist schematics:
 * - Interactive graph with components as nodes and nets as edges
 * - Zoom and pan functionality
 * - Component and net highlighting
 * - Error/warning visualization
 */

import React, { useRef, useEffect } from 'react'
import * as d3 from 'd3'
import { useBasePath } from '@/contexts/BasePathContext'
import type { Netlist, ValidationResult } from '@/types/netlist'

interface GraphVisualizationProps {
  netlist: Netlist | null
  validationResult?: ValidationResult | null
}

const GraphVisualization: React.FC<GraphVisualizationProps> = ({ netlist, validationResult }) => {
  const svgRef = useRef<SVGSVGElement>(null)
  const { withBasePath } = useBasePath()

  useEffect(() => {
    if (!netlist || !svgRef.current) return

    const svg = d3.select(svgRef.current)
    svg.selectAll('*').remove() // Clear previous content

    const width = 800
    const height = 600

    // Set up SVG
    svg.attr('width', width).attr('height', height)

    // Create zoom behavior
    const zoom = d3.zoom<SVGSVGElement, unknown>()
      .scaleExtent([0.1, 4])
      .on('zoom', (event) => {
        g.attr('transform', event.transform)
      })

    svg.call(zoom)

    // Create main group for zoomable content
    const g = svg.append('g')

    // Create nodes (components) with proper D3 structure
    const nodes = netlist.components.map(component => ({
      id: component.name,
      ...component
    }))

    // Create links by finding connections between components through nets
    const links: Array<{source: string, target: string, net: any}> = []

    netlist.nets.forEach(net => {
      const connectedComponents = new Set<string>()

      net.connections.forEach(connection => {
        connectedComponents.add(connection.component)
      })

      // Create links between all pairs of connected components
      const componentArray = Array.from(connectedComponents)
      for (let i = 0; i < componentArray.length; i++) {
        for (let j = i + 1; j < componentArray.length; j++) {
          links.push({
            source: componentArray[i],
            target: componentArray[j],
            net: net
          })
        }
      }
    })

    // Create force simulation
    const simulation = d3.forceSimulation(nodes as any)
      .force('link', d3.forceLink(links as any).id((d: any) => d.id))
      .force('charge', d3.forceManyBody().strength(-300))
      .force('center', d3.forceCenter(width / 2, height / 2))

    // Create links (nets)
    const link = g.append('g')
      .selectAll('line')
      .data(links)
      .enter().append('line')
      .attr('stroke', '#999')
      .attr('stroke-opacity', 0.6)
      .attr('stroke-width', 2)

    // Create nodes (components)
    const node = g.append('g')
      .selectAll('circle')
      .data(nodes)
      .enter().append('circle')
      .attr('r', 20)
      .attr('fill', '#69b3a2')
      .attr('stroke', '#fff')
      .attr('stroke-width', 2)
      .call(d3.drag<SVGCircleElement, any>()
        .on('start', dragstarted)
        .on('drag', dragged)
        .on('end', dragended))

    // Add labels
    const label = g.append('g')
      .selectAll('text')
      .data(nodes)
      .enter().append('text')
      .text((d: any) => d.name)
      .attr('text-anchor', 'middle')
      .attr('dy', 5)
      .attr('font-size', '12px')
      .attr('fill', '#333')

    // Update positions on simulation tick
    simulation.on('tick', () => {
      link
        .attr('x1', (d: any) => d.source.x)
        .attr('y1', (d: any) => d.source.y)
        .attr('x2', (d: any) => d.target.x)
        .attr('y2', (d: any) => d.target.y)

      node
        .attr('cx', (d: any) => d.x)
        .attr('cy', (d: any) => d.y)

      label
        .attr('x', (d: any) => d.x)
        .attr('y', (d: any) => d.y)
    })

    // Drag functions
    function dragstarted(event: any, d: any) {
      if (!event.active) simulation.alphaTarget(0.3).restart()
      d.fx = d.x
      d.fy = d.y
    }

    function dragged(event: any, d: any) {
      d.fx = event.x
      d.fy = event.y
    }

    function dragended(event: any, d: any) {
      if (!event.active) simulation.alphaTarget(0)
      d.fx = null
      d.fy = null
    }

    // Cleanup
    return () => {
      simulation.stop()
    }
  }, [netlist, validationResult])

  if (!netlist) {
    return (
      <div className="h-full flex items-center justify-center bg-gray-100">
        <div className="text-center">
          <div className="w-16 h-16 mx-auto mb-4 bg-gray-200 rounded-full flex items-center justify-center">
            <img
              src={withBasePath('logo.svg')}
              alt="NetWiz Logo"
              className="w-8 h-8"
            />
          </div>
          <p className="text-gray-500">No netlist loaded</p>
          <p className="text-sm text-gray-400">Upload a JSON file or enter netlist data to see the visualization</p>
        </div>
      </div>
    )
  }

  return (
    <div className="h-full bg-white">
      <svg ref={svgRef} className="w-full h-full" />
    </div>
  )
}

export default GraphVisualization
