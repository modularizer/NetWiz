/**
 * Frontend unit tests for FileUpload component
 */
import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import FileUpload from '../components/FileUpload';

// Mock axios for API calls
jest.mock('axios');
import axios from 'axios';

describe('FileUpload', () => {
  test('renders upload area', () => {
    render(<FileUpload onUpload={jest.fn()} />);
    expect(screen.getByText(/drag.*drop.*file/i)).toBeInTheDocument();
  });

  test('handles file selection', async () => {
    const mockOnUpload = jest.fn();
    render(<FileUpload onUpload={mockOnUpload} />);
    
    const file = new File(['{"components": []}'], 'test.json', { type: 'application/json' });
    const input = screen.getByLabelText(/upload/i);
    
    fireEvent.change(input, { target: { files: [file] } });
    
    await waitFor(() => {
      expect(mockOnUpload).toHaveBeenCalled();
    });
  });

  test('validates file type', async () => {
    const mockOnUpload = jest.fn();
    render(<FileUpload onUpload={mockOnUpload} />);
    
    const file = new File(['test'], 'test.txt', { type: 'text/plain' });
    const input = screen.getByLabelText(/upload/i);
    
    fireEvent.change(input, { target: { files: [file] } });
    
    await waitFor(() => {
      expect(screen.getByText(/invalid file type/i)).toBeInTheDocument();
    });
  });
});
