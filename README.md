# AcademicSearchSystem

基于 Flask + SQL Server 构建的学术文献检索系统。

南京农业大学信息与计算科学专业毕业设计项目。

本项目实现了用户管理、文献上传、多维度检索、引用关系管理、收藏管理、检索历史统计等核心功能，可作为信息检索、数据库系统、Web 开发等课程的综合实践项目。

---

# Project Overview

Academic Literature Retrieval System is a web-based academic document management and retrieval platform developed using:

* Python Flask
* Microsoft SQL Server
* HTML / CSS / JavaScript
* pyodbc

The system supports:

* Document Upload
* Metadata Management
* Keyword Retrieval
* TF-IDF Ranking
* Citation Relationship Construction
* Favorites Management
* Search History Recording
* Statistical Analysis

---

# System Architecture

```text
AcademicSearchSystem
│
├── app.py
│
├── templates/
│   ├── base.html
│   ├── citation.html
│   ├── document.html
│   ├── error.html
│   ├── favorites.html
│   ├── forgot_password.html
│   ├── history.html
│   ├── index.html
│   ├── login.html
│   ├── my_documents.html
│   ├── profile.html
│   ├── register.html
│   ├── search.html
│   ├── stats.html
│   └── upload.html
│
├── uploads/
│
├── AcademicSearchDB表创建.sql
├── AcademicSearchDB数据库表的设计.md
├── requirements.txt
├── LICENSE
└── README.md
```

---

# Main Features

## 1. User Management

* User Registration
* User Login
* Password Recovery
* Personal Information Management
* Email Modification
* Password Modification

---

## 2. Document Management

* Upload PDF Documents
* View Document Details
* Download Documents
* Delete Personal Documents

Supported Metadata:

* Title
* Author
* Abstract
* Category
* Publish Date
* Keywords

---

## 3. Literature Retrieval

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

Combined with TF-IDF weighting to sort results by relevance.

### Advanced Search

Supports combined filtering by:

* Title
* Author
* Category
* Keyword
* Start Date
* End Date

---

## 4. Citation Management

Users can create citation relationships between documents.

Functions:

* Citation Search
* Citation Selection
* Citation Cancellation
* Citation Count Statistics

Constraints:

* No Self-Citation
* No Duplicate Citation

---

## 5. Favorites Management

* Add Favorites
* Remove Favorites
* AJAX Asynchronous Update
* Pagination Display

---

## 6. Search History

The system automatically records:

* User
* Search Keyword
* Search Time

Features:

* Automatic Cleanup after 100 Records
* Pagination Management

---

## 7. Statistical Analysis

* Popular Search Keywords
* Active Users Ranking
* Most Cited Documents

---

# Database Design

## Core Tables

| Table Name      | Description                |
| --------------- | -------------------------- |
| Users           | User Information           |
| Documents       | Literature Information     |
| Keywords        | Keywords                   |
| DocumentKeyword | Literature-Keyword Mapping |
| SearchHistory   | Search History             |
| Citation        | Citation Relationship      |
| Favorites       | User Favorites             |

---

## Key Constraints

* Primary Keys
* Foreign Keys
* Unique Constraints
* Check Constraints

Including:

```text
UserName
Email
KeywordName
(SourceDocumentID, TargetDocumentID)
(UserID, DocumentID)
```

Additional Constraints:

```text
No Self-Citation
TF-IDF >= 0
Password Length Validation
Email Format Validation
```

---

## Index Design

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

Indexes improve retrieval performance for large-scale document collections.

---

# Environment Requirements

## Python

```text
Python 3.11+
```

## Database

```text
Microsoft SQL Server
```

---

# Installation

Install dependencies:

```bash
pip install -r requirements.txt
```

---

# Deployment

## Step 1: Initialize Database

Execute:

```text
AcademicSearchDB表创建.sql
```

This script automatically creates:

* Database AcademicSearchDB
* All Tables
* Constraints
* Indexes

---

## Step 2: Configure Database Connection

Modify the connection string in:

```python
app.py
```

Example:

```python
conn = pyodbc.connect(
    'DRIVER={ODBC Driver 17 for SQL Server};'
    'SERVER=YOUR_SERVER_NAME;'
    'DATABASE=AcademicSearchDB;'
    'UID=YOUR_USERNAME;'
    'PWD=YOUR_PASSWORD;'
)
```

---

## Step 3: Run Application

```bash
python app.py
```

Open browser:

```text
http://127.0.0.1:5000
```

---

# Current Version

```text
Version: v1.0 Freeze Release
```

Status:

```text
All Core Functions Implemented
System Tested Successfully
Project Archived for Graduation Design
```

---

# Future Improvements

Potential future work:

* Elasticsearch Full-Text Retrieval
* PDF Content Parsing
* Automatic TF-IDF Calculation
* Recommendation Algorithms
* Knowledge Graph Construction
* Administrator Backend
* Role-Based Access Control (RBAC)

---

# License

This project is currently maintained as an academic graduation project repository.

License information can be found in:

```text
LICENSE
```

---

# Author

Academic Literature Retrieval System

Developed with:

* Flask
* SQL Server
* HTML / CSS / JavaScript

For Academic Information Retrieval and Database System Practice.
