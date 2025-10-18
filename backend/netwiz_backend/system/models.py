from datetime import datetime

from pydantic import BaseModel, Field, constr

# Import NetlistEndpoints from netlist models
try:
    from netwiz_backend.netlist.models import NetlistEndpoints
except ImportError:
    # Fallback for when netlist models aren't available
    class NetlistEndpoints(BaseModel):
        """Netlist endpoints information"""

        upload: constr(strip_whitespace=True) = Field(
            ..., description="Upload endpoint"
        )
        list: constr(strip_whitespace=True) = Field(..., description="List endpoint")
        get: constr(strip_whitespace=True) = Field(..., description="Get endpoint")
        validate: constr(strip_whitespace=True) = Field(
            ..., description="Validate endpoint"
        )


class HealthResponse(BaseModel):
    """Health check response model"""

    status: constr(strip_whitespace=True) = Field(..., description="Service status")
    timestamp: datetime = Field(..., description="Current timestamp")
    version: constr(strip_whitespace=True) = Field(..., description="API version")
    environment: constr(strip_whitespace=True) = Field(
        ..., description="Environment (development/production)"
    )


class RootResponse(BaseModel):
    """Root endpoint response model"""

    message: constr(strip_whitespace=True) = Field(..., description="Application name")
    version: constr(strip_whitespace=True) = Field(
        ..., description="Application version"
    )
    author: constr(strip_whitespace=True) = Field(..., description="Application author")
    email: constr(strip_whitespace=True) = Field(..., description="Application email")
    license: constr(strip_whitespace=True) = Field(
        ..., description="Application license"
    )
    url: constr(strip_whitespace=True) = Field(..., description="Application URL")
    status: constr(strip_whitespace=True) = Field(..., description="Application status")
    docs: constr(strip_whitespace=True) = Field(..., description="Documentation URL")
    health: constr(strip_whitespace=True) = Field(
        ..., description="Health check endpoint"
    )
    environment: constr(strip_whitespace=True) = Field(..., description="Environment")


class ApiInfo(BaseModel):
    """API information section"""

    name: constr(strip_whitespace=True) = Field(..., description="API name")
    version: constr(strip_whitespace=True) = Field(..., description="API version")
    description: constr(strip_whitespace=True) = Field(
        ..., description="API description"
    )
    author: constr(strip_whitespace=True) = Field(..., description="API author")
    email: constr(strip_whitespace=True) = Field(..., description="API email")
    license: constr(strip_whitespace=True) = Field(..., description="API license")
    url: constr(strip_whitespace=True) = Field(..., description="API URL")
    status: constr(strip_whitespace=True) = Field(..., description="API status")


class ServiceInfo(BaseModel):
    """Service information section"""

    environment: constr(strip_whitespace=True) = Field(..., description="Environment")
    debug: bool = Field(..., description="Debug mode")
    host: constr(strip_whitespace=True) = Field(..., description="Host")
    port: int = Field(..., description="Port")


class DocumentationInfo(BaseModel):
    """Documentation endpoints information"""

    swagger_ui: constr(strip_whitespace=True) = Field(..., description="Swagger UI URL")
    redoc: constr(strip_whitespace=True) = Field(..., description="ReDoc URL")
    openapi_json: constr(strip_whitespace=True) = Field(
        ..., description="OpenAPI JSON URL"
    )


class EndpointsInfo(BaseModel):
    """Endpoints information section"""

    documentation: DocumentationInfo = Field(..., description="Documentation endpoints")
    health: constr(strip_whitespace=True) = Field(..., description="Health endpoint")
    netlist: NetlistEndpoints | None = Field(
        default=None, description="Netlist endpoints"
    )


class ApiInfoResponse(BaseModel):
    """API information response model"""

    api: ApiInfo = Field(..., description="API information")
    service: ServiceInfo = Field(..., description="Service information")
    endpoints: EndpointsInfo = Field(..., description="Available endpoints")


class KillServerResponse(BaseModel):
    """Kill server response model"""

    message: constr(strip_whitespace=True) = Field(..., description="Response message")
    timestamp: str = Field(..., description="Timestamp in ISO format")
    environment: constr(strip_whitespace=True) = Field(..., description="Environment")
