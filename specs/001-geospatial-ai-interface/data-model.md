# Data Model: GeoMind AI Core

This document describes the key data entities for the GeoMind AI Core feature, as identified in the feature specification. This is a conceptual model; it does not represent a database schema to be implemented by the project, but rather the entities the system will interact with in the OpenWorks database.

## Well

Represents a wellbore in the OpenWorks database.

- **Key Attributes**:
    - `Well Name`: The unique identifier for the well.
    - `Location`: The surface or bottom-hole location of the well.
    - `Status`: The current operational status of the well (e.g., drilling, completed, abandoned).
    - `Field`: The oil or gas field the well belongs to.
- **Relationships**:
    - A `Well` can have many `Logs`.

## Seismic Survey

Represents a collection of seismic data.

- **Key Attributes**:
    - `Survey Name`: The unique identifier for the survey.
    - `Survey Type`: The type of seismic survey (e.g., 2D, 3D).
    - `Acquisition Date`: The date the survey was acquired.
- **Relationships**:
    - A `Seismic Survey` can be associated with many `Wells`.

## Log

Represents a well log, containing measurements from a well.

- **Key Attributes**:
    - `Log Name`: The name of the log (e.g., GR, RHOB).
    - `Curve Data`: The measurement data for the log.
- **Relationships**:
    - A `Log` belongs to one `Well`.

## User

Represents a user of the GeoMind AI system. This entity is for the application's own user management and is separate from the OpenWorks database.

- **Key Attributes**:
    - `User ID`: A unique identifier for the user.
    - `Username`: The user's login name.
    - `Role`: The user's role within the system (e.g., 'geoscientist', 'data_manager', 'admin').
- **Relationships**:
    - A `User` has one `Role`, which determines their permissions.
