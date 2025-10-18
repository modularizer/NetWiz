/**
 * Custom Type Definitions for NetWiz Frontend
 *
 * These types define the expected structure for our frontend components,
 * which may differ from the generated OpenAPI types in some cases.
 */

// LocationInfo type that matches the backend LocationInfo model
export interface LocationInfo {
  parents: LocationInfo[]
  key: string
  kind: 'key' | 'object' | 'list' | 'null' | 'string' | 'boolean' | 'number'
  start_character_number: number
  start_line_number: number
  start_line_character_number: number
  end_character_number: number
  end_line_number: number
  end_line_character_number: number
}

// ValidationErrorType type that matches the backend ValidationErrorType model
export interface ValidationErrorType {
  name: string
  description: string
}

// Custom ValidationError type that matches our backend model
export interface ValidationError {
  error_type: ValidationErrorType
  message: string
  component_id?: string | null
  net_id?: string | null
  severity: 'error' | 'warning'
  location?: LocationInfo | null
}

// Custom ValidationResult type
export interface ValidationResult {
  is_valid: boolean
  errors: ValidationError[]
  warnings: ValidationError[]
  validation_timestamp: string
  validation_rules_applied: ValidationErrorType[]
  auto_fill_suggestions?: Array<{
    net_name: string
    suggested_type: string
    reason: string
  }>
}

// Custom Netlist type (using the generated types as base)
export interface Netlist {
  components: Component[]
  nets: Net[]
  metadata?: Record<string, any> | null
}

// Custom Component type
export interface Component {
  name: string
  type: 'IC' | 'RESISTOR' | 'CAPACITOR' | 'INDUCTOR' | 'DIODE' | 'TRANSISTOR' | 'CONNECTOR' | 'OTHER'
  pins: Pin[]
  value?: string | null
  package?: string | null
  manufacturer?: string | null
  part_number?: string | null
}

// Custom Net type
export interface Net {
  name: string
  connections: NetConnection[]
  net_type?: 'power' | 'ground' | 'signal' | 'clock' | 'analog' | 'digital' | 'data' | 'control' | 'other' | null
}

// Custom Pin type
export interface Pin {
  number: string
  name?: string | null
  type?: 'input' | 'output' | 'bidirectional' | 'power' | 'ground' | 'passive' | 'analog' | 'digital' | 'clock' | 'reset' | 'other' | null
}

// Custom NetConnection type
export interface NetConnection {
  component: string
  pin: string
}

// API Request/Response types
export interface NetlistUploadRequest {
  netlist: Netlist
  user_id?: string | null
  filename?: string | null
}

export interface NetlistUploadResponse {
  submission_id: string
  message: string
  validation_result: ValidationResult
}

export interface ValidationRequest {
  netlist: Netlist
}

export interface ValidationResponse {
  validation_result: ValidationResult
}
