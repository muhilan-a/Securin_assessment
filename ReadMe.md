# CVE Dashboard

A Flask-based web application to fetch, store, and display CVE (Common Vulnerabilities and Exposures) data from the NVD (National Vulnerability Database) API.We have used Python as our primary programming language ,sqlite for database storage,flask for backend synchronisation and html,css and javascript for front end .

## Features
- Fetches CVE data from NVD API with pagination
- Stores data in SQLite database
- Data synchronization with periodic updates
- Web UI with filtering/pagination
- Detailed CVE view with CVSS metrics
- Server-side sorting and filtering
- API endpoints for data access
- Unit tests
- Error handling and logging

## Problem Statement & Logical Approach
### Problem Statement
1. Consume CVE data from NVD API and store in database
2. Implement data cleansing/de-duplication
3. Periodic synchronization
4. Develop filtering API endpoints
5. Create web UI with table display
6. Prepare API documentation
7. Write unit tests

### Logical Approach
1. **API Consumption**: 
   - Use offset-based pagination (`startIndex`/`resultsPerPage`)
   - Handle rate limits (6s delay between requests)
   - Process data in batches (2000 records/batch)

2. **Data Processing**:
   - Clean data (handle missing fields)
   - Convert dates to datetime objects
   - Extract CVSS metrics from nested JSON
   - Validate mandatory fields (CVE ID, dates)

3. **Database Design**:
   - SQLite for simplicity
   - Table: `cve` with relationships
   - Indexes on frequently queried fields

4. **Synchronization**:
   - Full refresh mode
   - Track last modified dates
  

5. **API Endpoints**:
   - Filter by CVE ID/year/score/modified date
   - Pagination support
   - Sorting parameters

6. **Web UI**:
   - Table view with server-side rendering
   - Clickable rows for details
   - Dynamic pagination controls

7. **Testing**:
   - Unit tests for API parsing
   - Database operation tests
   - UI component tests




## File Explanations

### 1. `app/__init__.py`
Initializes Flask application and database connection by creating a flask app instance and configures sqlAlchemy.



### 2. `app/config.py`
Contains configuration settings for the application such as the database uri,api endpoints,rate limiting etc



### 3. `app/models.py`
Defines database models using SQLAlchemy ORM.



###    
   
