# Academic Literature Retrieval System

基于 Flask + SQL Server 构建的学术文献检索系统。

本项目实现了用户管理、文献上传、关键词检索、引用关系管理、收藏管理、检索历史统计等核心功能，可作为信息检索、数据库系统、Web 开发等课程的综合实践项目。

---

# Project Overview

Academic Literature Retrieval System is a web-based academic document management and retrieval platform developed using:

* Python Flask
* SQL Server
* HTML / CSS / JavaScript
* pyodbc

The system supports document upload, metadata management, keyword retrieval, citation relationship construction, favorites management, search history recording, and statistical analysis.

---

# System Architecture

```text
AcademicSearchSystem
│
├── app.py
│
├── templates
│   ├── index.html
│   ├── login.html
│   ├── register.html
│   ├── forgot_password.html
│   ├── search.html
│   ├── upload.html
│   ├── document.html
│   ├── history.html
│   ├── stats.html
│   ├── favorites.html
│   ├── profile.html
│   ├── my_documents.html
│   ├── citation.html
│   └── error.html
│
├── uploads
│   └── PDF files
│
├── AcademicSearchDB.sql
│
└── README.md
```

---

# Main Features

## User Management

* User Registration
* User Login
* Password Recovery
* Personal Information Management
* Email Modification
* Password Modification

---

## Document Management

* Upload PDF Documents
* View Document Details
* Download Documents
* Delete Personal Documents

Document metadata includes:

* Title
* Author
* Abstract
* Category
* Publish Date
* Keywords

---

## Literature Retrieval

Supports multiple retrieval modes:

### Title Search

Search by document title.

### Author Search

Search by author name.

### Category Search

Search by literature category.

### Keyword Search

Based on:

```text
Documents
↓
DocumentKeyword
↓
Keywords
```

to achieve keyword retrieval.

---

## Advanced Search

Supports combined filtering:

* Title
* Author
* Category
* Keyword
* Start Date
* End Date

Users can perform multi-condition retrieval.

---

## Citation Management

Users can create citation relationships between documents.

```text
Document A
    ↓
Document B
```

Features:

* Citation Search
* Citation Selection
* Citation Cancellation
* Citation Count Statistics

Constraints:

```text
No self-citation
No duplicate citation
```

---

## Favorites Management

Users can:

* Add Favorites
* Remove Favorites
* View Favorite Documents

Features:

```text
AJAX Asynchronous Update
Pagination Display
```

---

## Search History

The system automatically records search operations.

Stored information:

* User
* Search Keyword
* Search Time

Features:

* Pagination
* History Management
* Top 100 Records Retention

---

## Statistical Analysis

### Popular Search Keywords

Top searched keywords.

### Active Users Ranking

Users with the highest search frequency.

### Most Cited Documents

Documents with the highest citation count.

---

# Database Design

## Core Tables

```text
Users
Documents
Keywords
DocumentKeyword
SearchHistory
Citation
Favorites
```

### Entity Relationship

```text
Users
 │
 ├── Documents
 │
 ├── SearchHistory
 │
 └── Favorites

Documents
 │
 ├── Citation
 │
 ├── Favorites
 │
 └── DocumentKeyword

Keywords
 │
 └── DocumentKeyword
```

---

# Database Constraints

Implemented constraints include:

### Primary Keys

All core tables use primary keys.

### Foreign Keys

Maintain referential integrity.

### Unique Constraints

Examples:

```text
UserName
Email
KeywordName
(SourceDocumentID, TargetDocumentID)
(UserID, DocumentID)
```

### Check Constraints

Examples:

```text
Username Length
Password Length
Email Format
No Self Citation
TF-IDF >= 0
```

---

# Index Design

```text
IX_Documents_Title
IX_Documents_Author

IX_Keywords_Name

IX_DocumentKeyword_KeywordID

IX_SearchHistory_UserID

IX_Citation_Source
IX_Citation_Target

IX_Favorites_UserID
IX_Favorites_DocumentID
```

Indexes improve retrieval efficiency for large-scale document collections.

---

# Environment Requirements

## Python

Recommended:

```text
Python 3.11+
```

## Database

```text
Microsoft SQL Server
```

## Python Packages

Install dependencies:

```bash
pip install flask
pip install pyodbc
```

---

# Database Initialization

Execute:

```sql
AcademicSearchDB.sql
```

to create:

* Database
* Tables
* Constraints
* Indexes

---

# Run Project

```bash
python app.py
```

Open browser:

```text
http://127.0.0.1:5000
```

---

# Current Version

Version:

```text
v1.0 Freeze Release
```

Completed modules:

* User System
* Literature Upload
* Literature Retrieval
* Citation Management
* Favorites Management
* Search History
* Statistical Analysis
* Personal Center

---

# Future Improvements

Potential future enhancements:

* Full-text Search
* PDF Content Parsing
* Automatic TF-IDF Calculation
* Recommendation Algorithms
* Knowledge Graph Construction
* Elasticsearch Integration
* User Role Management
* Administrator Backend

---

# Author

Academic Literature Retrieval System

Developed with:

```text
Flask + SQL Server
```

for academic information retrieval and database system practice.
