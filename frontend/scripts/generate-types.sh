#!/bin/bash

# Generate TypeScript types from OpenAPI schema
# This script generates TypeScript interfaces from the backend's openapi.json

echo "🔄 Generating TypeScript types from OpenAPI schema..."

# Check if openapi.json exists
if [ ! -f "../backend/openapi.json" ]; then
    echo "❌ Error: openapi.json not found in ../backend/"
    echo "   Please run 'netwiz-generate-openapi' in the backend directory first"
    exit 1
fi

# Generate types using openapi-typescript
npx openapi-typescript ../backend/openapi.json -o src/types/api.ts

if [ $? -eq 0 ]; then
    echo "✅ TypeScript types generated successfully!"
    echo "📁 Output: src/types/api.ts"
    echo ""
    echo "💡 Usage:"
    echo "   import type { components, paths } from '@/types/api'"
    echo "   const response: components['schemas']['NetlistUploadResponse'] = ..."
else
    echo "❌ Failed to generate TypeScript types"
    exit 1
fi
