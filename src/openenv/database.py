from sqlalchemy import Column, Integer, String, JSON, Float, DateTime, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime
import json

Base = declarative_base()


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    name = Column(String, nullable=False)
    role = Column(String, nullable=False)  # seeker or recruiter
    created_at = Column(DateTime, default=datetime.utcnow)
    profile_data = Column(JSON, default={})


class UserProfile(Base):
    __tablename__ = "profiles"
    id = Column(String, primary_key=True)
    data = Column(JSON)


class JobPosting(Base):
    __tablename__ = "jobs"
    id = Column(String, primary_key=True)
    title = Column(String, nullable=False)
    company = Column(String, default="Unknown")
    location = Column(String, default="Remote")
    job_type = Column(String, default="Full-time")  # fulltime, parttime, contract
    salary_range = Column(String, default="Competitive")
    description = Column(String, nullable=False)
    requirements = Column(JSON, default={})
    posted_by = Column(String, default="")  # recruiter email
    posted_date = Column(DateTime, default=datetime.utcnow)
    status = Column(String, default="Active")  # active, closed, draft


class Application(Base):
    __tablename__ = "applications"
    id = Column(Integer, primary_key=True, autoincrement=True)
    profile_id = Column(String, nullable=False)  # seeker email
    job_id = Column(String, nullable=False)
    status = Column(String, default="Applied")  # applied, reviewed, interview, offered, rejected
    documents = Column(JSON, default={})
    applied_date = Column(DateTime, default=datetime.utcnow)
    notes = Column(String, default="")


class UserFeedback(Base):
    __tablename__ = "user_feedback"
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String, nullable=False)
    action = Column(String, nullable=False)  # job_id or candidate_id
    feedback_type = Column(String, nullable=False)  # click, apply, skip, star, reject
    reward = Column(Float, default=0.0)
    timestamp = Column(DateTime, default=datetime.utcnow)


class Database:
    def __init__(self, db_url="sqlite:///openenv.db"):
        self.engine = create_engine(db_url, echo=False)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)

    def create_user(self, email, password_hash, name, role):
        session = self.Session()
        try:
            user = User(email=email, password_hash=password_hash, name=name, role=role)
            session.add(user)
            session.commit()
            return True
        except Exception:
            session.rollback()
            return False
        finally:
            session.close()

    def get_user(self, email):
        session = self.Session()
        user = session.query(User).filter_by(email=email).first()
        result = None
        if user:
            result = {
                "id": user.id, "email": user.email,
                "password_hash": user.password_hash, "name": user.name,
                "role": user.role, "profile_data": user.profile_data or {}
            }
        session.close()
        return result

    def get_all_users(self):
        session = self.Session()
        users = session.query(User).order_by(User.created_at.desc()).all()
        result = [{
            "id": u.id,
            "email": u.email,
            "name": u.name,
            "role": u.role,
            "created_at": str(u.created_at),
            "profile_data": u.profile_data or {},
        } for u in users]
        session.close()
        return result

    def update_user_role(self, email, role):
        session = self.Session()
        user = session.query(User).filter_by(email=email).first()
        if user:
            user.role = role
            session.commit()
            session.close()
            return True
        session.close()
        return False

    def update_user_profile(self, email, profile_data):
        session = self.Session()
        user = session.query(User).filter_by(email=email).first()
        if user:
            user.profile_data = profile_data
            session.commit()
        session.close()

   #profile 
    def store_profile(self, profile_id, data):
        session = self.Session()
        profile = session.query(UserProfile).filter_by(id=profile_id).first()
        if profile:
            profile.data = data
        else:
            profile = UserProfile(id=profile_id, data=data)
            session.add(profile)
        session.commit()
        session.close()

    def get_profile(self, profile_id):
        session = self.Session()
        profile = session.query(UserProfile).filter_by(id=profile_id).first()
        data = profile.data if profile else None
        session.close()
        return data

    #job board
    def store_job(self, job_id, title, description, requirements,
                  company="Unknown", location="Remote", job_type="Full-time",
                  salary_range="Competitive", posted_by="", status="Active"):
        session = self.Session()
        job = session.query(JobPosting).filter_by(id=job_id).first()
        if job:
            job.title = title
            job.description = description
            job.requirements = requirements
            job.company = company
            job.location = location
            job.job_type = job_type
            job.salary_range = salary_range
            job.posted_by = posted_by
            job.status = status
        else:
            job = JobPosting(
                id=job_id, title=title, description=description,
                requirements=requirements, company=company, location=location,
                job_type=job_type, salary_range=salary_range,
                posted_by=posted_by, status=status
            )
            session.add(job)
        session.commit()
        session.close()

    def get_job(self, job_id):
        session = self.Session()
        job = session.query(JobPosting).filter_by(id=job_id).first()
        result = None
        if job:
            result = {
                "id": job.id, "title": job.title, "company": job.company,
                "location": job.location, "job_type": job.job_type,
                "salary_range": job.salary_range, "description": job.description,
                "requirements": job.requirements, "posted_by": job.posted_by,
                "posted_date": str(job.posted_date), "status": job.status
            }
        session.close()
        return result

    def get_all_jobs(self, status_filter=None):
        session = self.Session()
        query = session.query(JobPosting)
        if status_filter:
            query = query.filter_by(status=status_filter)
        jobs = query.order_by(JobPosting.posted_date.desc()).all()
        result = [{
            "id": j.id, "title": j.title, "company": j.company,
            "location": j.location, "job_type": j.job_type,
            "salary_range": j.salary_range, "description": j.description,
            "requirements": j.requirements, "posted_by": j.posted_by,
            "posted_date": str(j.posted_date), "status": j.status
        } for j in jobs]
        session.close()
        return result

    def get_jobs_by_recruiter(self, recruiter_email):
        session = self.Session()
        jobs = session.query(JobPosting).filter_by(posted_by=recruiter_email).all()
        result = [{
            "id": j.id, "title": j.title, "company": j.company,
            "location": j.location, "job_type": j.job_type,
            "salary_range": j.salary_range, "description": j.description,
            "requirements": j.requirements, "posted_by": j.posted_by,
            "posted_date": str(j.posted_date), "status": j.status
        } for j in jobs]
        session.close()
        return result

   #application methods
    def store_application(self, profile_id, job_id, status="Applied", documents=None):
        session = self.Session()

        existing = session.query(Application).filter_by(
            profile_id=profile_id, job_id=job_id
        ).first()
        if existing:
            session.close()
            return existing.id

        app = Application(
            profile_id=profile_id, job_id=job_id,
            status=status, documents=documents or {}
        )
        session.add(app)
        session.commit()
        app_id = app.id
        session.close()
        return app_id

    def get_applications_by_user(self, profile_id):
        session = self.Session()
        apps = session.query(Application).filter_by(profile_id=profile_id).all()
        result = [{
            "id": a.id, "profile_id": a.profile_id, "job_id": a.job_id,
            "status": a.status, "documents": a.documents,
            "applied_date": str(a.applied_date), "notes": a.notes
        } for a in apps]
        session.close()
        return result

    def get_applications_by_job(self, job_id):
        session = self.Session()
        apps = session.query(Application).filter_by(job_id=job_id).all()
        result = [{
            "id": a.id, "profile_id": a.profile_id, "job_id": a.job_id,
            "status": a.status, "documents": a.documents,
            "applied_date": str(a.applied_date), "notes": a.notes
        } for a in apps]
        session.close()
        return result

    def update_application_status(self, app_id, new_status, notes=""):
        session = self.Session()
        app = session.query(Application).filter_by(id=app_id).first()
        if app:
            app.status = new_status
            if notes:
                app.notes = notes
            session.commit()
        session.close()

    def get_all_applications(self):
        session = self.Session()
        apps = session.query(Application).all()
        result = [{
            "id": a.id, "profile_id": a.profile_id, "job_id": a.job_id,
            "status": a.status, "documents": a.documents,
            "applied_date": str(a.applied_date), "notes": a.notes
        } for a in apps]
        session.close()
        return result


    def record_feedback(self, user_id, action, feedback_type, reward):
        session = self.Session()
        fb = UserFeedback(
            user_id=user_id, action=action,
            feedback_type=feedback_type, reward=reward
        )
        session.add(fb)
        session.commit()
        session.close()

    def get_feedback_history(self, user_id=None, limit=200):
        session = self.Session()
        query = session.query(UserFeedback)
        if user_id:
            query = query.filter_by(user_id=user_id)
        feedbacks = query.order_by(UserFeedback.timestamp.desc()).limit(limit).all()
        result = [{
            "id": f.id, "user_id": f.user_id, "action": f.action,
            "feedback_type": f.feedback_type, "reward": f.reward,
            "timestamp": str(f.timestamp)
        } for f in feedbacks]
        session.close()
        return result

    def get_reward_stats(self):
        session = self.Session()
        feedbacks = session.query(UserFeedback).all()
        if not feedbacks:
            session.close()
            return {"total": 0, "avg_reward": 0, "positive": 0, "negative": 0}
        rewards = [f.reward for f in feedbacks]
        result = {
            "total": len(rewards),
            "avg_reward": round(sum(rewards) / len(rewards), 3),
            "positive": sum(1 for r in rewards if r > 0),
            "negative": sum(1 for r in rewards if r < 0),
        }
        session.close()
        return result
