# Changelog

## [2024-09-15]

### Added
- **GET Route:**([https://github.com/Namrata-sut/fastapi/pull/1/commits/504a8aae0a3943a13a6cc8fa76c2c8f4f7a824aa])
  - Added sorting based on the 'id' column in ascending or descending order as per user input.
  - Implemented keyword search for a specified column (default column is 'name').
  - Added pagination to results.
  - Allowed users to limit the number of results per page, with a default value set.

## [2024-09-27]

### Fixed
- **ID Increment:**([https://github.com/Namrata-sut/fastapi/pull/1/commits/f932aa1a6d33826190cac34a85e1304ff1a5960b])
  - Fixed logic for Pokémon ID assignment. IDs are now auto-incremented based on the maximum existing ID in the dataset, avoiding nested loops for improved performance.

### Refactored 
- **Import Statements:**([https://github.com/Namrata-sut/fastapi/pull/1/commits/f932aa1a6d33826190cac34a85e1304ff1a5960b])
  - Reordered import statements in alphabetical order for better readability.

### Removed
- Removed `/` GET route.([https://github.com/Namrata-sut/fastapi/pull/1/commits/f932aa1a6d33826190cac34a85e1304ff1a5960b])

### Changed
- **Validation:**([https://github.com/Namrata-sut/fastapi/pull/1/commits/f932aa1a6d33826190cac34a85e1304ff1a5960b])
  - Added validation to check if the provided column exists for search operations.
  - Added data type validation for search keywords to ensure proper searches in integer or string-type columns.

### Fixed
- **Delete Route:**[https://github.com/Namrata-sut/fastapi/pull/1/commits/93a17da6de6770c0c538d28503f56dba1c888f9c])
  - Updated delete route with enhanced error handling.

### Added
- **Added fiel:**
  - Added all SQL queries for creating the table, inserting data, and deleting records.