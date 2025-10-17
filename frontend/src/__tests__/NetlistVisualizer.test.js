/**
 * Frontend unit tests for NetlistVisualizer component
 */
import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import NetlistVisualizer from '../components/NetlistVisualizer';

// Mock D3 to avoid DOM manipulation issues in tests
jest.mock('d3', () => ({
  select: jest.fn(() => ({
    append: jest.fn(() => ({
      attr: jest.fn(() => ({
        style: jest.fn(() => ({
          on: jest.fn()
        }))
      }))
    }))
  }))
}));

describe('NetlistVisualizer', () => {
  const mockNetlist = {
    components: [
      { id: 'U1', type: 'IC', pins: ['1', '2', '3', '4'] },
      { id: 'R1', type: 'RESISTOR', pins: ['1', '2'] }
    ],
    nets: [
      { id: 'VCC', connections: [{ component: 'U1', pin: '1' }] },
      { id: 'GND', connections: [{ component: 'U1', pin: '4' }, { component: 'R1', pin: '2' }] }
    ]
  };

  test('renders visualization container', () => {
    render(<NetlistVisualizer netlist={mockNetlist} />);
    expect(screen.getByTestId('netlist-visualization')).toBeInTheDocument();
  });

  test('displays component nodes', () => {
    render(<NetlistVisualizer netlist={mockNetlist} />);
    expect(screen.getByText('U1')).toBeInTheDocument();
    expect(screen.getByText('R1')).toBeInTheDocument();
  });

  test('handles empty netlist gracefully', () => {
    render(<NetlistVisualizer netlist={{ components: [], nets: [] }} />);
    expect(screen.getByText('No netlist data to display')).toBeInTheDocument();
  });
});
