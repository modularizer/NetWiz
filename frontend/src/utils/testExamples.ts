export const testExamples = [
  {
    id: 'simple-valid',
    name: 'Simple Valid',
    description: 'Basic valid netlist with IC and resistor',
    filename: 'simple-valid.json',
    category: 'Valid',
    complexity: 'Simple'
  },
  {
    id: 'complex-valid',
    name: 'Complex Valid',
    description: 'Advanced netlist with microcontroller, sensor, and supporting components',
    filename: 'complex-valid.json',
    category: 'Valid',
    complexity: 'Complex'
  },
  {
    id: 'blank-names',
    name: 'Blank Names',
    description: 'Netlist with blank component and net names (validation errors)',
    filename: 'blank-names.json',
    category: 'Invalid',
    complexity: 'Simple'
  },
  {
    id: 'duplicate-names',
    name: 'Duplicate Names',
    description: 'Netlist with duplicate component and net names (validation errors)',
    filename: 'duplicate-names.json',
    category: 'Invalid',
    complexity: 'Simple'
  },
  {
    id: 'misnamed-ground',
    name: 'Misnamed Ground',
    description: 'Netlist with GND net incorrectly typed as power (validation warning)',
    filename: 'misnamed-ground.json',
    category: 'Warning',
    complexity: 'Simple'
  },
  {
    id: 'auto-fill-example',
    name: 'Auto-fill Example',
    description: 'Netlist with missing net types that can be auto-filled',
    filename: 'auto-fill-example.json',
    category: 'Auto-fill',
    complexity: 'Simple'
  }
] as const

export type TestExample = typeof testExamples[number]
