# Databricks Table Append Application

A web application that simplifies the process of appending data to existing Databricks tables. Built with Dash and integrated with Unity Catalog, this application provides an intuitive interface for data upload operations.

## Core Features

### 1. File Upload and Preview
- Upload CSV files through a drag-and-drop interface
- Instant preview of file contents in a tabular format
- Support for various file encodings and formats

### 2. Advanced CSV Settings
- Customize delimiter settings (comma, semicolon, tab, etc.)
- Configure quote characters
- Set header row options
- Choose file encoding (UTF-8, ASCII, ISO-8859-1, etc.)

### 3. Unity Catalog Integration
- Browse through catalogs, schemas, and tables
- Hierarchical navigation:
  - Select catalog
  - Choose schema
  - Pick target table
- View table schema and sample data before upload

### 4. Data Validation
- Preview data before appending
- Compare source data structure with target table
- Validate data types and formats

### 5. User Feedback
- Real-time status updates during upload
- Success/error notifications
- Progress indicators for long operations
- Clear feedback on operation completion

## How It Works

1. **Initial Upload**
   - Click "Upload file to append table" or drag and drop your file
   - File is automatically previewed with default settings

2. **Configure Settings (Optional)**
   - Click "Advanced Attributes" to customize CSV parsing
   - Adjust settings and see immediate preview updates

3. **Select Target Table**
   - Navigate through Unity Catalog hierarchy
   - View table schema and sample data
   - Confirm table selection

4. **Review and Append**
   - Verify data preview matches expectations
   - Click "Confirm and Append Data"
   - Monitor progress and receive completion notification

The application provides a streamlined workflow for data upload operations while maintaining the flexibility to handle various file formats and data structures.