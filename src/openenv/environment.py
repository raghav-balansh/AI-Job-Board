from .database import Database


class Environment:
    """
    OpenEnv Environment.
    Central hub for all agent communication. Agents interact only through
    defined read/write operations — never direct function calls.
    """

    def __init__(self, db_url="sqlite:///openenv.db"):
        self.db = Database(db_url)
        self.events = []

    def publish_event(self, source_agent, event_type, payload):
        event = {"source": source_agent, "type": event_type, "payload": payload}
        self.events.append(event)

    def get_events(self):
        return self.events

    def create_user(self, email, password_hash, name, role):
        return self.db.create_user(email, password_hash, name, role)

    def get_user(self, email):
        return self.db.get_user(email)

    def update_user_profile(self, email, profile_data):
        self.db.update_user_profile(email, profile_data)

    
    
    def store_profile(self, profile_id, data):
        self.db.store_profile(profile_id, data)
        self.publish_event("Environment", "ProfileUpdated", {"profile_id": profile_id})

    def get_profile(self, profile_id):
        return self.db.get_profile(profile_id)

    #  job methods
    def store_job(self, job_id, title, description, requirements, **kwargs):
        self.db.store_job(job_id, title, description, requirements, **kwargs)
        self.publish_event("Environment", "JobPosted", {"job_id": job_id})

    def get_job(self, job_id):
        return self.db.get_job(job_id)

    def get_all_jobs(self, status_filter=None):
        return self.db.get_all_jobs(status_filter)

    def get_jobs_by_recruiter(self, recruiter_email):
        return self.db.get_jobs_by_recruiter(recruiter_email)

    # application 
    def store_application(self, profile_id, job_id, status="Applied", documents=None):
        app_id = self.db.store_application(profile_id, job_id, status, documents)
        self.publish_event("Environment", "ApplicationSubmitted", {
            "application_id": app_id, "profile_id": profile_id, "job_id": job_id
        })
        return app_id

    def get_applications_by_user(self, profile_id):
        return self.db.get_applications_by_user(profile_id)

    def get_applications_by_job(self, job_id):
        return self.db.get_applications_by_job(job_id)

    def update_application_status(self, app_id, new_status, notes=""):
        self.db.update_application_status(app_id, new_status, notes)
        self.publish_event("Environment", "ApplicationStatusChanged", {
            "application_id": app_id, "new_status": new_status
        })

    def get_all_applications(self):
        return self.db.get_all_applications()


    def record_feedback(self, user_id, action, feedback_type, reward):
        """Store user interaction as a reward signal for RL training."""
        self.db.record_feedback(user_id, action, feedback_type, reward)
        self.publish_event("RLEnvironment", "FeedbackRecorded", {
            "user_id": user_id, "feedback_type": feedback_type, "reward": reward
        })

    def get_feedback_history(self, user_id=None, limit=200):
        return self.db.get_feedback_history(user_id, limit)

    def get_reward_stats(self):
        return self.db.get_reward_stats()
