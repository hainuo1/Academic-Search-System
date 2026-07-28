"""
SQLAlchemy 2.0 ORM Models — 全部 17 张表
"""
from datetime import datetime
from sqlalchemy import (
    Column, Integer, BigInteger, String, Text, Float, Double, Date, DateTime,
    ForeignKey, CheckConstraint, UniqueConstraint, Index
)
from sqlalchemy.orm import relationship
from app.core.database import Base


# ══════════════════════════════════════════════════════════════
# 核心检索系统
# ══════════════════════════════════════════════════════════════

class User(Base):
    __tablename__ = "users"

    user_id        = Column(Integer, primary_key=True, autoincrement=True)
    user_name      = Column(String(50), nullable=False, unique=True)
    password       = Column(String(255), nullable=False)
    email          = Column(String(100), nullable=False, unique=True)
    question1      = Column(String(200))
    answer1_hash   = Column(String(255))
    question2      = Column(String(200))
    answer2_hash   = Column(String(255))
    failed_attempts = Column(Integer, nullable=False, default=0)
    lockout_until   = Column(DateTime, nullable=True)
    register_time   = Column(DateTime, nullable=False, default=datetime.utcnow)

    # relationships
    documents      = relationship("Document", back_populates="uploader")
    favorites      = relationship("Favorite", back_populates="user")
    search_history = relationship("SearchHistory", back_populates="user")
    browse_history = relationship("BrowseHistory", back_populates="user")
    search_count   = relationship("UserSearchCount", back_populates="user", uselist=False)


class Document(Base):
    __tablename__ = "documents"

    document_id    = Column(Integer, primary_key=True, autoincrement=True)
    title          = Column(String(500), nullable=False)
    author         = Column(String(200), nullable=False)
    abstract       = Column(Text)
    publish_date   = Column(String(50))
    category       = Column(String(100))
    file_path      = Column(String(500))
    upload_user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    keywords_text  = Column(String(1000))
    full_text      = Column(Text)
    view_count     = Column(Integer, nullable=False, default=0)
    download_count = Column(Integer, nullable=False, default=0)
    upload_time    = Column(DateTime, nullable=False, default=datetime.utcnow)

    # relationships
    uploader       = relationship("User", back_populates="documents")
    doc_keywords   = relationship("DocumentKeyword", back_populates="document")
    citations_as_source = relationship("Citation", foreign_keys="Citation.source_document_id", back_populates="source_doc")
    citations_as_target = relationship("Citation", foreign_keys="Citation.target_document_id", back_populates="target_doc")
    favorites      = relationship("Favorite", back_populates="document")
    browse_history = relationship("BrowseHistory", back_populates="document")


class Keyword(Base):
    __tablename__ = "keywords"

    keyword_id   = Column(Integer, primary_key=True, autoincrement=True)
    keyword_name = Column(String(200), nullable=False, unique=True)

    doc_keywords = relationship("DocumentKeyword", back_populates="keyword")


class DocumentKeyword(Base):
    __tablename__ = "document_keyword"

    document_id = Column(Integer, ForeignKey("documents.document_id", ondelete="CASCADE"), primary_key=True)
    keyword_id  = Column(Integer, ForeignKey("keywords.keyword_id", ondelete="CASCADE"), primary_key=True)
    tf_idf      = Column(Double, nullable=False, default=1.0)

    document = relationship("Document", back_populates="doc_keywords")
    keyword  = relationship("Keyword", back_populates="doc_keywords")


class Citation(Base):
    __tablename__ = "citation"

    source_document_id = Column(Integer, ForeignKey("documents.document_id", ondelete="CASCADE"), primary_key=True)
    target_document_id = Column(Integer, ForeignKey("documents.document_id", ondelete="CASCADE"), primary_key=True)

    __table_args__ = (
        CheckConstraint("source_document_id <> target_document_id", name="ck_citation_no_self"),
    )

    source_doc = relationship("Document", foreign_keys=[source_document_id], back_populates="citations_as_source")
    target_doc = relationship("Document", foreign_keys=[target_document_id], back_populates="citations_as_target")


class Favorite(Base):
    __tablename__ = "favorites"

    favorite_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id     = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    document_id = Column(Integer, ForeignKey("documents.document_id", ondelete="CASCADE"), nullable=False)
    create_time = Column(DateTime, nullable=False, default=datetime.utcnow)

    __table_args__ = (UniqueConstraint("user_id", "document_id"),)

    user     = relationship("User", back_populates="favorites")
    document = relationship("Document", back_populates="favorites")


class SearchHistory(Base):
    __tablename__ = "search_history"

    history_id     = Column(Integer, primary_key=True, autoincrement=True)
    user_id        = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    search_keyword = Column(String(500), nullable=False)
    search_time    = Column(DateTime, nullable=False, default=datetime.utcnow)

    user = relationship("User", back_populates="search_history")


class BrowseHistory(Base):
    __tablename__ = "browse_history"

    browse_history_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id           = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    document_id       = Column(Integer, ForeignKey("documents.document_id", ondelete="CASCADE"), nullable=False)
    view_time         = Column(DateTime, nullable=False, default=datetime.utcnow)

    user     = relationship("User", back_populates="browse_history")
    document = relationship("Document", back_populates="browse_history")


class UserSearchCount(Base):
    __tablename__ = "user_search_count"

    user_id      = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), primary_key=True)
    search_count = Column(Integer, nullable=False, default=0)

    user = relationship("User", back_populates="search_count")


class KeywordSearchCount(Base):
    __tablename__ = "keyword_search_count"

    keyword      = Column(String(200), primary_key=True)
    search_count = Column(Integer, nullable=False, default=0)


# ══════════════════════════════════════════════════════════════
# 台风模块
# ══════════════════════════════════════════════════════════════

class TyphoonInfo(Base):
    __tablename__ = "typhoon_info"

    typhoon_id   = Column(String(50), primary_key=True)
    typhoon_name = Column(String(100), nullable=False)
    season       = Column(Integer, nullable=False)
    basin        = Column(String(50), default="WP")
    max_wind     = Column(Double, default=0)
    min_pressure = Column(Double, default=9999)
    total_points = Column(Integer, default=0)
    start_time   = Column(DateTime, nullable=True)
    end_time     = Column(DateTime, nullable=True)

    tracks       = relationship("TyphoonTrack", back_populates="typhoon")
    analyses     = relationship("TyphoonAIAnalysis", back_populates="typhoon")


class TyphoonTrack(Base):
    __tablename__ = "typhoon_track"

    track_id           = Column(Integer, primary_key=True, autoincrement=True)
    typhoon_id         = Column(String(50), ForeignKey("typhoon_info.typhoon_id", ondelete="CASCADE"), nullable=False)
    date_time          = Column(DateTime, nullable=False)
    latitude           = Column(Double, nullable=False)
    longitude          = Column(Double, nullable=False)
    max_sustained_wind = Column(Double, default=0)
    min_pressure       = Column(Double, default=9999)
    storm_category     = Column(String(50), default="")
    wind_radius7_ne    = Column(Double, default=0)
    wind_radius7_se    = Column(Double, default=0)
    wind_radius7_sw    = Column(Double, default=0)
    wind_radius7_nw    = Column(Double, default=0)
    wind_radius10_ne   = Column(Double, default=0)
    wind_radius10_se   = Column(Double, default=0)
    wind_radius10_sw   = Column(Double, default=0)
    wind_radius10_nw   = Column(Double, default=0)

    typhoon = relationship("TyphoonInfo", back_populates="tracks")


class TyphoonAIAnalysis(Base):
    __tablename__ = "typhoon_ai_analysis"

    typhoon_id    = Column(String(50), ForeignKey("typhoon_info.typhoon_id", ondelete="CASCADE"), primary_key=True)
    analysis_type = Column(String(20), primary_key=True)
    content       = Column(Text, nullable=False)
    created_at    = Column(DateTime, default=datetime.utcnow)

    typhoon = relationship("TyphoonInfo", back_populates="analyses")


# ══════════════════════════════════════════════════════════════
# 地震模块
# ══════════════════════════════════════════════════════════════

class EarthquakeInfo(Base):
    __tablename__ = "earthquake_info"

    event_id         = Column(String(30), primary_key=True)
    date_time        = Column(DateTime, nullable=False)
    latitude         = Column(Double, nullable=False)
    longitude        = Column(Double, nullable=False)
    depth            = Column(Double, default=0)
    magnitude        = Column(Double, default=0)
    mag_type         = Column(String(10), default="")
    place            = Column(String(300), default="")
    status           = Column(String(20), default="")
    tsunami          = Column(Integer, default=0)
    alert            = Column(String(20), default="")
    significance     = Column(Integer, default=0)
    gap              = Column(Double, default=0)
    dmin             = Column(Double, default=0)
    rms              = Column(Double, default=0)
    nst              = Column(Integer, default=0)
    horizontal_error = Column(Double, default=0)
    depth_error      = Column(Double, default=0)
    mag_error        = Column(Double, default=0)
    mag_nst          = Column(Integer, default=0)
    updated          = Column(DateTime, nullable=True)

    analyses = relationship("EarthquakeAIAnalysis", back_populates="earthquake")


class EarthquakeAIAnalysis(Base):
    __tablename__ = "earthquake_ai_analysis"

    event_id      = Column(String(30), ForeignKey("earthquake_info.event_id", ondelete="CASCADE"), primary_key=True)
    analysis_type = Column(String(20), primary_key=True)
    content       = Column(Text, nullable=False)
    created_at    = Column(DateTime, default=datetime.utcnow)

    earthquake = relationship("EarthquakeInfo", back_populates="analyses")


# ══════════════════════════════════════════════════════════════
# 龙卷风模块
# ══════════════════════════════════════════════════════════════

class TornadoInfo(Base):
    __tablename__ = "tornado_info"

    event_id   = Column(Integer, primary_key=True, autoincrement=True)
    date_time  = Column(DateTime, nullable=False)
    latitude   = Column(Double, nullable=False)
    longitude  = Column(Double, nullable=False)
    place      = Column(String(200), default="")
    province   = Column(String(50), default="")
    ef_scale   = Column(String(10), default="")
    magnitude  = Column(Integer, default=0)
    casualties = Column(Integer, default=0)
    deaths     = Column(Integer, default=0)
    injuries   = Column(Integer, default=0)
    damage     = Column(String(500), default="")
    confidence = Column(String(20), default="")
    source     = Column(String(100), default="")

    analyses = relationship("TornadoAIAnalysis", back_populates="tornado")


class TornadoAIAnalysis(Base):
    __tablename__ = "tornado_ai_analysis"

    event_id      = Column(Integer, ForeignKey("tornado_info.event_id", ondelete="CASCADE"), primary_key=True)
    analysis_type = Column(String(20), primary_key=True)
    content       = Column(Text, nullable=False)
    created_at    = Column(DateTime, default=datetime.utcnow)

    tornado = relationship("TornadoInfo", back_populates="analyses")
